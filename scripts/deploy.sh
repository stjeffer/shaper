#!/usr/bin/env bash
# Copyright (c) Microsoft Corporation.
# SPDX-License-Identifier: MIT
#
# deploy.sh
# Build and deploy Shaper to one Azure Container Apps replica.

set -euo pipefail

readonly SCRIPT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

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
  require_environment SHAPER_SMOKE_TOKEN

  az account show --output none
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
    --parameters "${common_parameters[@]}" shouldDeployApp=false \
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

  local container_app_name="ca-${prefix}-${environment_name}"
  if az containerapp show \
    --name "${container_app_name}" \
    --resource-group "${resource_group}" \
    --output none 2>/dev/null; then
    local active_revisions
    active_revisions="$(az containerapp revision list \
      --name "${container_app_name}" \
      --resource-group "${resource_group}" \
      --query "[?properties.active].name" \
      --output tsv)"
    while IFS= read -r active_revision; do
      [[ -z "${active_revision}" ]] && continue
      az containerapp revision deactivate \
        --name "${container_app_name}" \
        --resource-group "${resource_group}" \
        --revision "${active_revision}" \
        --output none
    done <<<"${active_revisions}"
  fi

  az deployment group create \
    --name "${deployment_name}" \
    --resource-group "${resource_group}" \
    --template-file "${SCRIPT_ROOT}/bicep/main.bicep" \
    --parameters "${common_parameters[@]}" shouldDeployApp=true \
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
  curl --fail --silent --show-error --retry 20 --retry-all-errors \
    --retry-delay 10 "${service_url}/health/live" >/dev/null
  curl --fail --silent --show-error --retry 20 --retry-all-errors \
    --retry-delay 10 "${service_url}/health/ready" >/dev/null

  local header_file
  local response_file
  header_file="$(mktemp)"
  response_file="$(mktemp)"
  trap 'rm -f "${header_file:-}" "${response_file:-}"' EXIT
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

  printf "Deployment complete\n"
  printf "Image digest: %s\n" "${image_digest}"
  printf "Revision: %s\n" "${revision}"
  printf "Service URL: %s\n" "${service_url}"
  printf "Pitch prototype: %s/concept/\n" "${service_url}"
}

main "$@"
