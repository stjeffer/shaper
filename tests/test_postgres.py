"""PostgreSQL estate persistence contract tests without a live database."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import UTC, datetime

import pytest

from shaper.application.review import ReviewService
from shaper.domain import (
    AnswerUnit,
    Applicability,
    Claim,
    CollectionRole,
    KnowledgeEstate,
    Principal,
    ReviewDecision,
    UnitState,
)
from shaper.domain.models import Derivation, ReviewOutcome
from shaper.infrastructure.postgres import (
    PostgresEstateRepository,
    PostgresRecordStore,
    PostgresReviewStore,
)
from shaper.infrastructure.sqlite import ConcurrencyError

NOW = datetime(2026, 9, 10, tzinfo=UTC)
ZERO_HASH = "0" * 64


class FakePostgresConnection:
    """Emulate the small psycopg surface used by the record store."""

    def __init__(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row

    def execute(
        self,
        statement: str,
        parameters: Sequence[object] = (),
    ) -> sqlite3.Cursor:
        if "to_regclass('public.records')" in statement:
            statement = (
                "SELECT CASE WHEN EXISTS ("
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'records'"
                ") THEN 'records' ELSE NULL END AS record_table"
            )
        translated = statement.replace("%s", "?").replace(" FOR UPDATE", "")
        return self.connection.execute(translated, parameters)

    @contextmanager
    def transaction(self) -> Iterator[None]:
        try:
            yield
        except BaseException:
            self.connection.rollback()
            raise
        else:
            self.connection.commit()

    def close(self) -> None:
        self.connection.close()


def test_given_postgres_store_when_estate_revised_then_optimistic_lock_is_enforced(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    connection = FakePostgresConnection()

    def connect(_url: str, **kwargs: object) -> FakePostgresConnection:
        assert kwargs["autocommit"] is True
        return connection

    monkeypatch.setattr("shaper.infrastructure.postgres.psycopg.connect", connect)
    store = PostgresRecordStore("postgresql://database.example/shaper")
    store.connect()
    store.migrate()
    repository = PostgresEstateRepository(store)
    estate = KnowledgeEstate(
        estate_id="estate-1",
        collection_id="collection-1",
        tenant_id="tenant-1",
        name="Policy estate",
        created_at=NOW,
        updated_at=NOW,
    )

    # Act
    created = repository.create_estate(estate)
    values = estate.model_dump()
    values["name"] = "Renamed estate"
    updated = repository.save_estate(
        KnowledgeEstate.model_validate(values),
        expected_revision=created.revision,
    )

    # Assert
    assert updated.revision == 2
    assert repository.get_estate("estate-1") == updated
    with pytest.raises(ConcurrencyError, match="Stale record revision"):
        repository.save_estate(estate, expected_revision=created.revision)
    store.close()


def test_given_disconnected_postgres_store_when_probed_then_not_ready() -> None:
    store = PostgresRecordStore("postgresql://database.example/shaper")

    assert not store.is_ready()


def test_given_json_backed_review_when_approved_then_strict_domain_types_are_restored(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    connection = FakePostgresConnection()

    def connect(_url: str, **kwargs: object) -> FakePostgresConnection:
        assert kwargs["autocommit"] is True
        return connection

    monkeypatch.setattr("shaper.infrastructure.postgres.psycopg.connect", connect)
    store = PostgresRecordStore("postgresql://database.example/shaper")
    store.connect()
    store.migrate()
    reviews = ReviewService(PostgresReviewStore(store))
    unit = AnswerUnit.create(
        source_id="document-1",
        source_version=ZERO_HASH,
        canonical_questions=("Which health plans are eligible?",),
        answer="Employees should confirm plan eligibility with HR.",
        claims=(
            Claim(
                text="Employees should confirm plan eligibility with HR.",
                span_ids=("span-1",),
                qualifiers=("Confirm with HR if uncertain.",),
            ),
        ),
        applicability=Applicability(
            audiences=("Employees (internal audience)",),
            jurisdictions=("Not specified in document",),
            effective_from=datetime(2664, 11, 11, tzinfo=UTC),
        ),
        derivation=Derivation(
            run_id="run-1",
            model="fake",
            prompt_version="1.4",
            parameters_hash=ZERO_HASH,
        ),
        confidence=0.9,
    )
    submitted = reviews.submit(unit, ())

    try:
        # Act
        approved = reviews.decide(
            ReviewDecision(
                decision_id="decision-1",
                unit_id=unit.unit_id,
                unit_version=unit.unit_version,
                outcome=ReviewOutcome.APPROVE,
                actor=Principal(
                    principal_id="reviewer-1",
                    tenant_id="tenant-1",
                    collection_roles={
                        "collection-1": frozenset({CollectionRole.REVIEW}),
                    },
                ),
                reason="Grounding verified.",
                expected_revision=submitted.revision,
                decided_at=NOW,
            ),
            expected_revision=submitted.revision,
        )

        # Assert
        assert approved.unit.state is UnitState.APPROVED
        assert approved.unit.canonical_questions == ("Which health plans are eligible?",)
        assert approved.unit.claims[0].qualifiers == ("Confirm with HR if uncertain.",)
        assert approved.unit.applicability.audiences == ("Employees (internal audience)",)
        assert approved.unit.applicability.jurisdictions == ("Not specified in document",)
        assert approved.unit.applicability.effective_from == datetime(2664, 11, 11, tzinfo=UTC)
        assert approved.unit.conflict_unit_ids == ()
    finally:
        store.close()
