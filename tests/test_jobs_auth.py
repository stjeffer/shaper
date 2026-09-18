"""Compile quota and OIDC claim mapping tests."""

from __future__ import annotations

import base64
import json

import pytest

from shaper.application.jobs import (
    CompileJobService,
    CompileJobWorker,
    InMemoryJobStore,
    QuotaExceededError,
)
from shaper.domain import CollectionGrant, CollectionRole, JobState, OutputRef, Principal, SourceRef
from shaper.domain.models import OutputKind, SourceKind
from shaper.interfaces.auth import (
    ClaimsPrincipalMapper,
    OIDCAuthenticator,
    RequestPrincipalResolver,
    discover_jwks_uri,
)


def principal() -> Principal:
    """Return a compile principal."""
    return Principal(
        principal_id="person-1",
        tenant_id="tenant-1",
        collection_roles={"collection-1": frozenset({CollectionRole.COMPILE})},
    )


class StaticAuthenticator:
    """Return one deterministic bearer principal."""

    def __init__(self, value: Principal) -> None:
        self._value = value

    def authenticate(self, token: str) -> Principal:
        assert token == "valid"
        return self._value


class EmptyGrantRepository:
    """Provide no persisted grants for an app-only ingress identity."""

    def grants_for(
        self,
        tenant_id: str,
        principal_id: str,
    ) -> tuple[CollectionGrant, ...]:
        assert tenant_id
        assert principal_id
        return ()


def ingress_identity(*, principal_id: str, tenant_id: str = "tenant-1") -> str:
    """Encode the identity header emitted by Container Apps authentication."""
    payload = {
        "claims": [
            {"typ": "sub", "val": principal_id},
            {"typ": "tid", "val": tenant_id},
        ]
    }
    return base64.b64encode(json.dumps(payload).encode()).decode()


def test_given_matching_bearer_and_ingress_when_resolved_then_bearer_roles_are_used() -> None:
    bearer = principal()
    resolver = RequestPrincipalResolver(
        authenticator=StaticAuthenticator(bearer),
        grants=EmptyGrantRepository(),
        trust_ingress_identity=True,
    )

    resolved = resolver.resolve(
        authorization="Bearer valid",
        ingress_principal=ingress_identity(principal_id=bearer.principal_id),
    )

    assert resolved == bearer


def test_given_mismatched_bearer_and_ingress_when_resolved_then_access_is_denied() -> None:
    resolver = RequestPrincipalResolver(
        authenticator=StaticAuthenticator(principal()),
        grants=EmptyGrantRepository(),
        trust_ingress_identity=True,
    )

    with pytest.raises(PermissionError, match="do not match"):
        resolver.resolve(
            authorization="Bearer valid",
            ingress_principal=ingress_identity(principal_id="other-person"),
        )


def test_given_untrusted_matching_ingress_when_resolved_then_access_is_denied() -> None:
    resolver = RequestPrincipalResolver(
        authenticator=StaticAuthenticator(principal()),
        grants=EmptyGrantRepository(),
        trust_ingress_identity=False,
    )

    with pytest.raises(PermissionError, match="not trusted"):
        resolver.resolve(
            authorization="Bearer valid",
            ingress_principal=ingress_identity(principal_id="person-1"),
        )


def source() -> SourceRef:
    """Return a compile source."""
    return SourceRef(
        tenant_id="tenant-1",
        collection_id="collection-1",
        kind=SourceKind.UPLOAD,
        locator="asset-1",
    )


def output() -> OutputRef:
    """Return a compile output."""
    return OutputRef(kind=OutputKind.FILESYSTEM, root_id="local")


def test_given_duplicate_idempotency_key_when_submitted_then_original_job_is_returned() -> None:
    # Arrange
    service = CompileJobService(InMemoryJobStore())

    # Act
    first = service.submit(
        principal=principal(),
        source=source(),
        output=output(),
        idempotency_key="same",
        requested_token_budget=100,
    )
    second = service.submit(
        principal=principal(),
        source=source(),
        output=output(),
        idempotency_key="same",
        requested_token_budget=100,
    )

    # Assert
    assert first.job_id == second.job_id


def test_given_active_collection_job_when_second_submitted_then_quota_rejects() -> None:
    # Arrange
    service = CompileJobService(InMemoryJobStore())
    service.submit(
        principal=principal(),
        source=source(),
        output=output(),
        idempotency_key="first",
        requested_token_budget=100,
    )

    # Act & Assert
    with pytest.raises(QuotaExceededError, match="Collection"):
        service.submit(
            principal=principal(),
            source=source(),
            output=output(),
            idempotency_key="second",
            requested_token_budget=100,
        )


def test_given_valid_oidc_roles_when_mapped_then_collection_roles_are_explicit() -> None:
    # Act
    mapped = ClaimsPrincipalMapper().map(
        {
            "sub": "person-1",
            "tid": "tenant-1",
            "roles": ["shaper:collection-1:query", "shaper:collection-1:compile"],
        }
    )

    # Assert
    assert mapped.collection_roles["collection-1"] == {
        CollectionRole.QUERY,
        CollectionRole.COMPILE,
    }


def test_given_v2_issuer_when_discovered_then_metadata_jwks_uri_is_used() -> None:
    issuer = "https://login.microsoftonline.com/tenant-1/v2.0"
    requested: list[str] = []

    def load(url: str) -> dict[str, object]:
        requested.append(url)
        return {
            "issuer": issuer,
            "jwks_uri": "https://login.microsoftonline.com/tenant-1/discovery/v2.0/keys",
        }

    result = discover_jwks_uri(issuer, metadata_loader=load)

    assert requested == [f"{issuer}/.well-known/openid-configuration"]
    assert result == "https://login.microsoftonline.com/tenant-1/discovery/v2.0/keys"


def test_given_mismatched_metadata_issuer_when_discovered_then_validation_fails() -> None:
    with pytest.raises(RuntimeError, match="does not match"):
        discover_jwks_uri(
            "https://login.microsoftonline.com/tenant-1/v2.0",
            metadata_loader=lambda _url: {
                "issuer": "https://login.microsoftonline.com/other/v2.0",
                "jwks_uri": "https://login.microsoftonline.com/other/discovery/v2.0/keys",
            },
        )


def test_given_authenticator_when_created_then_oidc_discovery_is_deferred() -> None:
    requested: list[str] = []

    def load(url: str) -> dict[str, object]:
        requested.append(url)
        return {}

    OIDCAuthenticator(
        issuer="https://login.microsoftonline.com/tenant-1/v2.0",
        audience="api-client",
        metadata_loader=load,
    )

    assert requested == []


def test_given_queued_job_when_worker_runs_then_job_reaches_completed() -> None:
    # Arrange
    store = InMemoryJobStore()
    service = CompileJobService(store)
    job = service.submit(
        principal=principal(),
        source=source(),
        output=output(),
        idempotency_key="worker",
        requested_token_budget=100,
    )

    # Act
    result = CompileJobWorker(store, execute=lambda current: None).run(job.job_id)

    # Assert
    assert result.state is JobState.COMPLETED


def test_given_compiler_failure_when_worker_runs_then_diagnostic_is_persisted() -> None:
    store = InMemoryJobStore()
    service = CompileJobService(store)
    job = service.submit(
        principal=principal(),
        source=source(),
        output=output(),
        idempotency_key="worker-failure",
        requested_token_budget=100,
    )

    def fail(_job: object) -> None:
        raise RuntimeError("synthetic compiler failure")

    result = CompileJobWorker(store, execute=fail).run(job.job_id)

    assert result.state is JobState.FAILED
    assert result.diagnostic == "RuntimeError: synthetic compiler failure"
