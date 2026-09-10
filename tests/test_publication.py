"""Complete release and filesystem publication tests."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from shaper.application.publication import (
    PublishableUnit,
    ReleaseBundle,
    assemble_release,
    verify_release,
)
from shaper.domain import SourceDocument, UnitState
from shaper.infrastructure.filesystem_sink import (
    CurrentPointerConflict,
    FilesystemReleaseSink,
)
from tests.test_validation_review import make_unit

ZERO_HASH = "0" * 64


def approved(document: SourceDocument, *, origin: str) -> PublishableUnit:
    """Return a publishable approved unit."""
    unit = make_unit(document)
    values = unit.model_dump()
    values["state"] = UnitState.APPROVED
    return PublishableUnit(
        unit=type(unit).model_validate(values),
        permission_hash=ZERO_HASH,
        approval_id=f"approval-{origin}",
        origin_run_id=origin,
    )


def bundle(document: SourceDocument, *, run_id: str) -> ReleaseBundle:
    """Build a one-unit complete release."""
    return assemble_release(
        tenant_id=document.tenant_id,
        collection_id=document.collection_id,
        run_id=run_id,
        created_at=datetime(2026, 9, 9, tzinfo=UTC),
        newly_approved=[approved(document, origin=run_id)],
        carried_forward=[],
    )


def test_given_changed_subset_when_release_assembled_then_valid_prior_units_carry_forward(
    source_document: SourceDocument,
) -> None:
    # Arrange
    prior = approved(source_document, origin="run-prior")

    # Act
    release = assemble_release(
        tenant_id="tenant-1",
        collection_id="collection-1",
        run_id="run-next",
        created_at=datetime(2026, 9, 9, tzinfo=UTC),
        newly_approved=[],
        carried_forward=[prior],
    )

    # Assert
    assert release.manifest.units[0].origin_run_id == "run-prior"
    verify_release(release)


def test_given_release_when_published_then_manifest_exists_before_current_pointer(
    tmp_path: Path,
    source_document: SourceDocument,
) -> None:
    # Arrange
    sink = FilesystemReleaseSink(tmp_path)
    release = bundle(source_document, run_id="run-1")

    # Act
    result = sink.publish(release, expected_current_hash=None)

    # Assert
    release_root = tmp_path / "releases" / result.release_id
    assert (release_root / "manifest.json").is_file()
    assert (tmp_path / "current.json").is_file()


def test_given_stale_pointer_hash_when_published_then_release_is_not_current(
    tmp_path: Path,
    source_document: SourceDocument,
) -> None:
    # Arrange
    sink = FilesystemReleaseSink(tmp_path)
    first = bundle(source_document, run_id="run-1")
    sink.publish(first, expected_current_hash=None)
    second = bundle(source_document, run_id="run-2")

    # Act & Assert
    with pytest.raises(CurrentPointerConflict) as captured:
        sink.publish(second, expected_current_hash="stale")
    assert captured.value.release_id == second.manifest.release_id
