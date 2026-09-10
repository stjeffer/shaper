"""SharePoint source connector contract tests."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime

from shaper.application.ports import SourceChange
from shaper.domain import SourceRef
from shaper.domain.models import SourceKind
from shaper.infrastructure.sharepoint import SharePointSource


class GraphFake:
    """Graph transport fake with pagination and tombstones."""

    def __init__(self) -> None:
        self.requested: list[str] = []

    def get_json(self, path_or_url: str) -> dict[str, object]:
        self.requested.append(path_or_url)
        if "/drive/root:" in path_or_url:
            return {"id": "root-1", "parentReference": {"driveId": "drive-1"}}
        if path_or_url.startswith("/sites/"):
            return {"id": "site-1"}
        if path_or_url == "next":
            return {
                "value": [{"id": "deleted-1", "deleted": {}}],
                "@odata.deltaLink": "delta-final",
            }
        return {
            "value": [
                {
                    "id": "item-1",
                    "name": "Policy.txt",
                    "lastModifiedDateTime": datetime(2026, 9, 9, tzinfo=UTC).isoformat(),
                    "file": {"mimeType": "text/plain"},
                }
            ],
            "@odata.nextLink": "next",
        }

    def get_bytes(self, path_or_url: str) -> bytes:
        self.requested.append(path_or_url)
        return b"policy"


def source_changes() -> Iterator[SourceChange]:
    """Yield fake connector changes."""
    source = SourceRef(
        tenant_id="tenant-1",
        collection_id="collection-1",
        kind=SourceKind.SHAREPOINT,
        locator="https://contoso.sharepoint.com/sites/hr/Shared%20Documents",
    )
    yield from SharePointSource(GraphFake()).changes(source, checkpoint=None)


def test_given_paged_delta_when_synchronized_then_changes_and_tombstone_are_emitted() -> None:
    # Act
    changes = list(source_changes())

    # Assert
    assert [(change.kind, change.source_id) for change in changes] == [
        ("changed", "item-1"),
        ("withdrawn", "deleted-1"),
    ]


def test_given_sharepoint_url_when_resolved_then_stable_ids_are_returned() -> None:
    # Arrange
    source = SharePointSource(GraphFake())

    # Act
    root = source.resolve("https://contoso.sharepoint.com/sites/hr/Shared%20Documents")

    # Assert
    assert (root.site_id, root.drive_id, root.item_id) == ("site-1", "drive-1", "root-1")
