"""SharePoint release sink ordering tests."""

from __future__ import annotations

from shaper.domain import SourceDocument
from shaper.infrastructure.sharepoint_sink import SharePointReleaseSink
from tests.test_publication import bundle


class GraphWriteFake:
    """Capture ordered Graph uploads."""

    def __init__(self) -> None:
        self.paths: list[str] = []

    def upload(
        self,
        path: str,
        content: bytes,
        *,
        conflict_behavior: str,
        if_match: str | None = None,
    ) -> str:
        del content, conflict_behavior, if_match
        self.paths.append(path)
        return f"etag-{len(self.paths)}"


def test_given_complete_release_when_published_then_manifest_precedes_current_pointer(
    source_document: SourceDocument,
) -> None:
    # Arrange
    transport = GraphWriteFake()
    sink = SharePointReleaseSink(transport, output_root="/knowledge")

    # Act
    etag = sink.publish(bundle(source_document, run_id="run-1"), current_etag="old")

    # Assert
    assert transport.paths[-2].endswith("manifest.json")
    assert transport.paths[-1] == "/knowledge/current.json"
    assert etag == "etag-3"
