"""OIDC token validation and claims-to-principal mapping."""

from __future__ import annotations

import base64
import json
import threading
from collections.abc import Callable, Mapping
from typing import Protocol
from urllib.parse import urlparse

import httpx
import jwt
from jwt import PyJWKClient
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.provider import AccessToken

from shaper.application.estates import EstateRepository
from shaper.domain import CollectionRole, Principal


class Authenticator(Protocol):
    """Bearer-token authentication boundary."""

    def authenticate(self, token: str) -> Principal:
        """Validate a token and return its application principal."""


class ClaimsPrincipalMapper:
    """Map validated OIDC claims into explicit collection roles."""

    def map(self, claims: Mapping[str, object]) -> Principal:
        """Return a principal from validated token claims."""
        subject = claims.get("sub")
        tenant = claims.get("tid") or claims.get("tenant_id")
        raw_roles = claims.get("roles", [])
        if not isinstance(subject, str) or not subject:
            raise PermissionError("OIDC token has no valid subject claim")
        if not isinstance(tenant, str) or not tenant:
            raise PermissionError("OIDC token has no valid tenant claim")
        if not isinstance(raw_roles, list) or not all(isinstance(role, str) for role in raw_roles):
            raise PermissionError("OIDC roles claim must be a string array")
        collection_roles: dict[str, set[CollectionRole]] = {}
        for raw_role in raw_roles:
            parts = raw_role.split(":")
            if len(parts) != 3 or parts[0] != "shaper":
                continue
            try:
                role = CollectionRole(parts[2])
            except ValueError as error:
                raise PermissionError(
                    f"OIDC token contains an unknown Shaper role: {raw_role}"
                ) from error
            collection_roles.setdefault(parts[1], set()).add(role)
        return Principal(
            principal_id=subject,
            tenant_id=tenant,
            collection_roles={
                collection_id: frozenset(roles) for collection_id, roles in collection_roles.items()
            },
        )


class RequestPrincipalResolver:
    """Resolve exactly one bearer or trusted-ingress identity mode."""

    def __init__(
        self,
        *,
        authenticator: Authenticator,
        grants: EstateRepository,
        trust_ingress_identity: bool = False,
    ) -> None:
        self._authenticator = authenticator
        self._grants = grants
        self._trust_ingress_identity = trust_ingress_identity

    def resolve(
        self,
        *,
        authorization: str | None,
        ingress_principal: str | None,
    ) -> Principal:
        """Fail closed for mixed, malformed, missing, or untrusted identities."""
        has_bearer = authorization is not None
        has_ingress = ingress_principal is not None
        if has_bearer and has_ingress:
            raise PermissionError("Bearer and ingress identities cannot be combined")
        if has_bearer:
            prefix = "Bearer "
            if authorization is None or not authorization.startswith(prefix):
                raise PermissionError("Authorization header must use Bearer")
            return self._authenticator.authenticate(authorization.removeprefix(prefix))
        if has_ingress:
            if not self._trust_ingress_identity:
                raise PermissionError("Ingress identity is not trusted by this deployment")
            return self._ingress_principal(ingress_principal or "")
        raise PermissionError("Authentication is required")

    def _ingress_principal(self, encoded: str) -> Principal:
        try:
            padding = "=" * (-len(encoded) % 4)
            raw = base64.b64decode(encoded + padding, validate=True)
            payload = json.loads(raw)
        except (ValueError, json.JSONDecodeError) as error:
            raise PermissionError("Ingress principal header is malformed") from error
        if not isinstance(payload, dict) or not isinstance(payload.get("claims"), list):
            raise PermissionError("Ingress principal header has no claims array")
        claims: dict[str, str] = {}
        for item in payload["claims"]:
            if not isinstance(item, dict):
                raise PermissionError("Ingress principal claim is malformed")
            name = item.get("typ")
            value = item.get("val")
            if isinstance(name, str) and isinstance(value, str):
                claims[name] = value
        principal_id = (
            claims.get("oid")
            or claims.get("http://schemas.microsoft.com/identity/claims/objectidentifier")
            or claims.get("sub")
        )
        tenant_id = claims.get("tid") or claims.get(
            "http://schemas.microsoft.com/identity/claims/tenantid"
        )
        if not principal_id or not tenant_id:
            raise PermissionError("Ingress principal lacks tenant or object identity")
        grants = self._grants.grants_for(tenant_id, principal_id)
        return Principal(
            principal_id=principal_id,
            tenant_id=tenant_id,
            collection_roles={grant.collection_id: grant.roles for grant in grants},
        )


def load_oidc_metadata(url: str) -> Mapping[str, object]:
    """Load one OpenID configuration document with a bounded timeout."""
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError) as error:
        raise RuntimeError(f"Could not load OpenID configuration from {url!r}") from error
    if not isinstance(payload, dict):
        raise RuntimeError("OpenID configuration must be a JSON object")
    return payload


def discover_jwks_uri(
    issuer: str,
    *,
    metadata_loader: Callable[[str], Mapping[str, object]] = load_oidc_metadata,
) -> str:
    """Resolve and validate the signing-key URI for one configured issuer."""
    normalized_issuer = issuer.rstrip("/")
    metadata_url = f"{normalized_issuer}/.well-known/openid-configuration"
    metadata = metadata_loader(metadata_url)
    discovered_issuer = metadata.get("issuer")
    if not isinstance(discovered_issuer, str) or discovered_issuer.rstrip("/") != normalized_issuer:
        raise RuntimeError("OpenID configuration issuer does not match the configured issuer")
    jwks_uri = metadata.get("jwks_uri")
    if not isinstance(jwks_uri, str) or not jwks_uri:
        raise RuntimeError("OpenID configuration does not contain a valid jwks_uri")
    parsed = urlparse(jwks_uri)
    if parsed.scheme != "https" or not parsed.netloc:
        raise RuntimeError("OpenID jwks_uri must be an absolute HTTPS URL")
    return jwks_uri


class OIDCAuthenticator:
    """Validate signed OIDC JWTs from one configured issuer and audience."""

    def __init__(
        self,
        *,
        issuer: str,
        audience: str,
        metadata_loader: Callable[[str], Mapping[str, object]] = load_oidc_metadata,
    ) -> None:
        self._issuer = issuer.rstrip("/")
        self._audience = audience
        self._metadata_loader = metadata_loader
        self._keys: PyJWKClient | None = None
        self._keys_lock = threading.Lock()
        self._mapper = ClaimsPrincipalMapper()

    def authenticate(self, token: str) -> Principal:
        """Validate signature, issuer, audience, lifetime, and application claims."""
        signing_key = self._key_client().get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=self._audience,
            issuer=self._issuer,
            options={"require": ["exp", "iat", "sub"]},
        )
        return self._mapper.map(claims)

    def _key_client(self) -> PyJWKClient:
        if self._keys is None:
            with self._keys_lock:
                if self._keys is None:
                    self._keys = PyJWKClient(
                        discover_jwks_uri(
                            self._issuer,
                            metadata_loader=self._metadata_loader,
                        )
                    )
        return self._keys


class McpOIDCTokenVerifier:
    """Adapt OIDC validation to the MCP resource-server verifier contract."""

    def __init__(self, authenticator: OIDCAuthenticator) -> None:
        self._authenticator = authenticator

    async def verify_token(self, token: str) -> AccessToken | None:
        """Return MCP access context for a valid OIDC token."""
        try:
            principal = self._authenticator.authenticate(token)
        except (PermissionError, jwt.PyJWTError):
            return None
        scopes = [f"tenant:{principal.tenant_id}"]
        scopes.extend(
            f"shaper:{collection_id}:{role.value}"
            for collection_id, roles in principal.collection_roles.items()
            for role in sorted(roles, key=lambda item: item.value)
        )
        return AccessToken(
            token=token,
            client_id=principal.principal_id,
            scopes=scopes,
        )


def current_mcp_principal() -> Principal:
    """Reconstruct a principal from MCP's validated access-token context."""
    access = get_access_token()
    if access is None:
        raise PermissionError("MCP request has no validated access token")
    tenant_scopes = [
        scope.removeprefix("tenant:") for scope in access.scopes if scope.startswith("tenant:")
    ]
    if len(tenant_scopes) != 1:
        raise PermissionError("MCP access token must resolve to exactly one tenant")
    roles = [scope for scope in access.scopes if scope.startswith("shaper:")]
    return ClaimsPrincipalMapper().map(
        {
            "sub": access.client_id,
            "tid": tenant_scopes[0],
            "roles": roles,
        }
    )
