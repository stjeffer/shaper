"""PostgreSQL estate persistence contract tests without a live database."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import UTC, datetime

import pytest

from shaper.domain import KnowledgeEstate
from shaper.infrastructure.postgres import PostgresEstateRepository, PostgresRecordStore
from shaper.infrastructure.sqlite import ConcurrencyError

NOW = datetime(2026, 9, 10, tzinfo=UTC)


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

    def connect(_url: str, **_kwargs: object) -> FakePostgresConnection:
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
