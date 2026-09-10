"""Complete active-corpus release assembly and integrity verification."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import datetime

from shaper.domain import AnswerUnit, ReleaseManifest, ReleaseUnitRef, UnitState
from shaper.domain.models import canonical_hash


@dataclass(frozen=True)
class PublishableUnit:
    """Approved unit plus immutable publication provenance."""

    unit: AnswerUnit
    permission_hash: str
    approval_id: str
    origin_run_id: str


@dataclass(frozen=True)
class ReleaseBundle:
    """Manifest and deterministic artifacts committed as one release."""

    manifest: ReleaseManifest
    artifacts: dict[str, bytes]


def assemble_release(
    *,
    tenant_id: str,
    collection_id: str,
    run_id: str,
    created_at: datetime,
    newly_approved: Sequence[PublishableUnit],
    carried_forward: Sequence[PublishableUnit],
    invalidated_unit_ids: Iterable[str] = (),
    previous_release_id: str | None = None,
) -> ReleaseBundle:
    """Assemble a complete snapshot from new and still-valid approved units."""
    invalidated = set(invalidated_unit_ids)
    selected: dict[str, PublishableUnit] = {}
    for candidate in carried_forward:
        if candidate.unit.unit_id not in invalidated:
            selected[candidate.unit.unit_id] = candidate
    for candidate in newly_approved:
        selected[candidate.unit.unit_id] = candidate
    for candidate in selected.values():
        if candidate.unit.state is not UnitState.APPROVED:
            raise ValueError(f"Unit is not approved for publication: {candidate.unit.unit_id}")

    lines: list[bytes] = []
    unit_refs: list[ReleaseUnitRef] = []
    for unit_id in sorted(selected):
        item = selected[unit_id]
        line = (
            json.dumps(item.unit.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
            + "\n"
        ).encode()
        lines.append(line)
        unit_refs.append(
            ReleaseUnitRef(
                unit_id=item.unit.unit_id,
                unit_version=item.unit.unit_version,
                source_id=item.unit.source_id,
                source_version=item.unit.source_version,
                permission_hash=item.permission_hash,
                approval_id=item.approval_id,
                origin_run_id=item.origin_run_id,
                artifact_hash=hashlib.sha256(line).hexdigest(),
            )
        )
    units_artifact = b"".join(lines)
    artifact_hashes = {"units.jsonl": hashlib.sha256(units_artifact).hexdigest()}
    release_id = canonical_hash(
        {
            "tenant_id": tenant_id,
            "collection_id": collection_id,
            "run_id": run_id,
            "created_at": created_at.isoformat(),
            "units": [unit.model_dump(mode="json") for unit in unit_refs],
        }
    )
    manifest = ReleaseManifest(
        release_id=release_id,
        tenant_id=tenant_id,
        collection_id=collection_id,
        created_at=created_at,
        run_id=run_id,
        units=tuple(unit_refs),
        artifact_hashes=artifact_hashes,
        previous_release_id=previous_release_id,
    )
    return ReleaseBundle(manifest=manifest, artifacts={"units.jsonl": units_artifact})


def verify_release(bundle: ReleaseBundle) -> None:
    """Validate every manifest artifact hash and per-unit line hash."""
    for name, expected in bundle.manifest.artifact_hashes.items():
        content = bundle.artifacts.get(name)
        if content is None:
            raise ValueError(f"Release artifact is missing: {name}")
        if hashlib.sha256(content).hexdigest() != expected:
            raise ValueError(f"Release artifact hash mismatch: {name}")
    lines = bundle.artifacts["units.jsonl"].splitlines(keepends=True)
    if len(lines) != len(bundle.manifest.units):
        raise ValueError("Release unit count does not match units artifact")
    for line, unit in zip(lines, bundle.manifest.units, strict=True):
        if hashlib.sha256(line).hexdigest() != unit.artifact_hash:
            raise ValueError(f"Release unit artifact hash mismatch: {unit.unit_id}")
