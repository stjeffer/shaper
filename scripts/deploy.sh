#!/usr/bin/env bash
# Copyright (c) Microsoft Corporation.
# SPDX-License-Identifier: MIT
#
# deploy.sh
# Build and deploy Shaper to one Azure Container Apps replica.

set -euo pipefail

readonly SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly MINIMUM_CHAT_TPM=50000

usage() {
  echo "Usage: ${0##*/} --resource-group NAME --prefix NAME [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  --environment NAME  dev, test, or prod (default: dev)"
  echo "  --image-tag TAG     Container image tag (default: current UTC timestamp)"
  echo "  --location REGION   Azure region (default: eastus2)"
  echo "  --resource-group RG Azure resource group name"
  echo "  --prefix NAME       Resource name prefix"
  echo "  --help, -h          Show this help"
}

err() {
  printf "ERROR: %s\n" "$1" >&2
  exit 1
}

require_command() {
  command -v "$1" &>/dev/null || err "'$1' command is required but not installed"
}

require_environment() {
  local name="$1"
  [[ -n "$(printenv "${name}")" ]] || err "${name} must be set"
}

main() {
  local environment_name="dev"
  local image_tag
  local location="eastus2"
  local prefix=""
  local resource_group=""
  image_tag="$(date -u +%Y%m%d%H%M%S)"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --environment)
        environment_name="${2:-}"
        shift 2
        ;;
      --image-tag)
        image_tag="${2:-}"
        shift 2
        ;;
      --location)
        location="${2:-}"
        shift 2
        ;;
      --prefix)
        prefix="${2:-}"
        shift 2
        ;;
      --resource-group)
        resource_group="${2:-}"
        shift 2
        ;;
      --help|-h)
        usage
        return 0
        ;;
      *)
        err "Unknown option: $1"
        ;;
    esac
  done

  [[ "${environment_name}" =~ ^(dev|test|prod)$ ]] \
    || err "--environment must be dev, test, or prod"
  [[ -n "${prefix}" ]] || err "--prefix is required"
  [[ -n "${resource_group}" ]] || err "--resource-group is required"

  require_command az
  require_command curl
  require_command python3
  require_environment SHAPER_AZURE_OPENAI_ACCOUNT
  require_environment SHAPER_AZURE_OPENAI_CHAT_DEPLOYMENT
  require_environment SHAPER_AZURE_OPENAI_EMBEDDING_DEPLOYMENT
  require_environment SHAPER_AZURE_OPENAI_RESOURCE_GROUP
  require_environment SHAPER_COLLECTION_ID
  require_environment SHAPER_OIDC_AUDIENCE
  require_environment SHAPER_OIDC_ISSUER
  require_environment SHAPER_SCANNER_IMAGE

  az account show --output none
  local chat_tpm
  chat_tpm="$(az cognitiveservices account deployment show \
    --resource-group "${SHAPER_AZURE_OPENAI_RESOURCE_GROUP}" \
    --name "${SHAPER_AZURE_OPENAI_ACCOUNT}" \
    --deployment-name "${SHAPER_AZURE_OPENAI_CHAT_DEPLOYMENT}" \
    --query "properties.rateLimits[?key == 'token'] | [0].count" \
    --output tsv)"
  [[ "${chat_tpm}" =~ ^[0-9]+([.][0-9]+)?$ ]] \
    || err "Azure OpenAI chat deployment returned no token rate limit"
  local chat_tpm_integer="${chat_tpm%%.*}"
  (( chat_tpm_integer >= MINIMUM_CHAT_TPM )) \
    || err "Azure OpenAI chat deployment requires at least ${MINIMUM_CHAT_TPM} TPM"

  if [[ -z "$(printenv SHAPER_ENTRA_CLIENT_ID || true)" ]]; then
    export SHAPER_ENTRA_CLIENT_ID="${SHAPER_OIDC_AUDIENCE#api://}"
  fi
  if [[ -z "$(printenv SHAPER_ENTRA_CLIENT_SECRET || true)" ]]; then
    export SHAPER_ENTRA_CLIENT_SECRET
    SHAPER_ENTRA_CLIENT_SECRET="$(az ad app credential reset \
      --id "${SHAPER_ENTRA_CLIENT_ID}" \
      --append \
      --display-name "shaper-${environment_name}-container-app" \
      --years 1 \
      --query password \
      --output tsv)"
  fi
  if [[ -z "$(printenv SHAPER_POSTGRES_ADMIN_PASSWORD || true)" ]]; then
    export SHAPER_POSTGRES_ADMIN_PASSWORD
    SHAPER_POSTGRES_ADMIN_PASSWORD="$(python3 -c \
      'import secrets; print(secrets.token_urlsafe(36))')"
  fi
  if [[ -z "$(printenv SHAPER_BOOTSTRAP_TENANT_ID || true)" ]]; then
    export SHAPER_BOOTSTRAP_TENANT_ID
    SHAPER_BOOTSTRAP_TENANT_ID="$(az account show --query tenantId --output tsv)"
  fi
  if [[ -z "$(printenv SHAPER_BOOTSTRAP_PRINCIPAL_ID || true)" ]]; then
    export SHAPER_BOOTSTRAP_PRINCIPAL_ID
    SHAPER_BOOTSTRAP_PRINCIPAL_ID="$(az ad signed-in-user show --query id --output tsv)"
  fi

  local secure_parameter_file
  secure_parameter_file="$(mktemp)"
  chmod 600 "${secure_parameter_file}"
  trap 'rm -f "${secure_parameter_file:-}"' EXIT
  python3 - "${secure_parameter_file}" <<'PY'
import json
import os
import sys

payload = {
    "$schema": (
        "https://schema.management.azure.com/schemas/"
        "2019-04-01/deploymentParameters.json#"
    ),
    "contentVersion": "1.0.0.0",
    "parameters": {
        "entraClientSecret": {"value": os.environ["SHAPER_ENTRA_CLIENT_SECRET"]},
        "postgresAdministratorPassword": {
            "value": os.environ["SHAPER_POSTGRES_ADMIN_PASSWORD"]
        },
    },
}
with open(sys.argv[1], "w", encoding="utf-8") as stream:
    json.dump(payload, stream)
PY

  az bicep build --file "${SCRIPT_ROOT}/bicep/main.bicep" --stdout >/dev/null
  az group create \
    --name "${resource_group}" \
    --location "${location}" \
    --output none

  local deployment_name="shaper-${environment_name}"
  local common_parameters=(
    "azureOpenAIAccountName=${SHAPER_AZURE_OPENAI_ACCOUNT}"
    "azureOpenAIChatDeployment=${SHAPER_AZURE_OPENAI_CHAT_DEPLOYMENT}"
    "azureOpenAIEmbeddingDeployment=${SHAPER_AZURE_OPENAI_EMBEDDING_DEPLOYMENT}"
    "azureOpenAIResourceGroupName=${SHAPER_AZURE_OPENAI_RESOURCE_GROUP}"
    "collectionId=${SHAPER_COLLECTION_ID}"
    "environmentName=${environment_name}"
    "entraClientId=${SHAPER_ENTRA_CLIENT_ID}"
    "bootstrapPrincipalId=${SHAPER_BOOTSTRAP_PRINCIPAL_ID}"
    "bootstrapTenantId=${SHAPER_BOOTSTRAP_TENANT_ID}"
    "imageTag=${image_tag}"
    "oidcAudience=${SHAPER_OIDC_AUDIENCE}"
    "oidcIssuer=${SHAPER_OIDC_ISSUER}"
    "prefix=${prefix}"
    "scannerImage=${SHAPER_SCANNER_IMAGE}"
  )

  az deployment group create \
    --name "${deployment_name}-foundation" \
    --resource-group "${resource_group}" \
    --template-file "${SCRIPT_ROOT}/bicep/main.bicep" \
    --parameters "${common_parameters[@]}" "@${secure_parameter_file}" shouldDeployApp=false \
    --output none

  local registry_name
  registry_name="$(az deployment group show \
    --name "${deployment_name}-foundation" \
    --resource-group "${resource_group}" \
    --query properties.outputs.registryName.value \
    --output tsv)"
  [[ -n "${registry_name}" ]] || err "Foundation deployment returned no registry"

  az acr build \
    --registry "${registry_name}" \
    --image "shaper:${image_tag}" \
    "${SCRIPT_ROOT}"

  local image_digest
  image_digest="$(az acr manifest show-metadata \
    --registry "${registry_name}" \
    --name "shaper:${image_tag}" \
    --query digest \
    --output tsv)"
  [[ -n "${image_digest}" ]] || err "Built image digest could not be resolved"

  az deployment group create \
    --name "${deployment_name}" \
    --resource-group "${resource_group}" \
    --template-file "${SCRIPT_ROOT}/bicep/main.bicep" \
    --parameters "${common_parameters[@]}" "@${secure_parameter_file}" shouldDeployApp=true \
    --output none

  local fqdn
  local revision
  fqdn="$(az deployment group show \
    --name "${deployment_name}" \
    --resource-group "${resource_group}" \
    --query properties.outputs.applicationFqdn.value \
    --output tsv)"
  revision="$(az deployment group show \
    --name "${deployment_name}" \
    --resource-group "${resource_group}" \
    --query properties.outputs.applicationRevision.value \
    --output tsv)"
  [[ -n "${fqdn}" && -n "${revision}" ]] \
    || err "Application deployment returned incomplete outputs"

  local service_url="https://${fqdn}"
  az ad app update \
    --id "${SHAPER_ENTRA_CLIENT_ID}" \
    --enable-id-token-issuance true \
    --web-redirect-uris "${service_url}/.auth/login/aad/callback" \
    --output none

  curl --fail --silent --show-error --retry 20 --retry-all-errors \
    --retry-delay 10 "${service_url}/health/live" >/dev/null
  curl --fail --silent --show-error --retry 20 --retry-all-errors \
    --retry-delay 10 "${service_url}/health/ready" >/dev/null

  if [[ -n "$(printenv SHAPER_SMOKE_TOKEN || true)" ]]; then
  local header_file
  local response_file
  header_file="$(mktemp)"
  response_file="$(mktemp)"
  trap 'rm -f "${secure_parameter_file:-}" "${header_file:-}" "${response_file:-}"' EXIT
  printf "Authorization: Bearer %s\n" "${SHAPER_SMOKE_TOKEN}" >"${header_file}"
  chmod 600 "${header_file}"
  curl --fail --silent --show-error \
    --header "Accept: application/json, text/event-stream" \
    --header "@${header_file}" \
    --header "Content-Type: application/json" \
    --data '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"deploy-smoke","version":"1.0"}}}' \
    "${service_url}/mcp/" >"${response_file}"
  python3 -c \
    'import json,sys; from pathlib import Path; value=json.loads(Path(sys.argv[1]).read_text()); assert "result" in value' \
    "${response_file}"

  curl --fail --silent --show-error \
    --header "Accept: application/json, text/event-stream" \
    --header "@${header_file}" \
    --header "Content-Type: application/json" \
    --data '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' \
    "${service_url}/mcp/" >"${response_file}"
  python3 -c \
    'import json,sys; from pathlib import Path; value=json.loads(Path(sys.argv[1]).read_text()); names={tool["name"] for tool in value["result"]["tools"]}; required={"knowledge.query","estate.list","estate.discovery.start","estate.transformation.start","estate.artifact.approve","estate.evaluation.list"}; assert required <= names' \
    "${response_file}"

  curl --fail --silent --show-error \
    --header "Accept: application/json, text/event-stream" \
    --header "@${header_file}" \
    --header "Content-Type: application/json" \
    --data "$(printf '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"estate.list","arguments":{"collection_id":"%s"}}}' "${SHAPER_COLLECTION_ID}")" \
    "${service_url}/mcp/" >"${response_file}"
  python3 -c \
    'import json,sys; from pathlib import Path; value=json.loads(Path(sys.argv[1]).read_text()); assert value["result"].get("isError") is not True' \
    "${response_file}"

  curl --fail --silent --show-error \
    --header "Accept: application/json, text/event-stream" \
    --header "@${header_file}" \
    --header "Content-Type: application/json" \
    --data "$(printf '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"estate.list","arguments":{"collection_id":"%s-denied"}}}' "${SHAPER_COLLECTION_ID}")" \
    "${service_url}/mcp/" >"${response_file}"
  python3 -c \
    'import json,sys; from pathlib import Path; value=json.loads(Path(sys.argv[1]).read_text()); assert value["result"].get("isError") is True' \
    "${response_file}"
  fi

  printf "Deployment complete\n"
  printf "Image digest: %s\n" "${image_digest}"
  printf "Revision: %s\n" "${revision}"
  printf "Service URL: %s\n" "${service_url}"
  printf "Knowledge estates: %s/concept/\n" "${service_url}"
}

main "$@"
