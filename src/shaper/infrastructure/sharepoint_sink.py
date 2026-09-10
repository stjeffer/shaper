"""SharePoint immutable release sink with eTag pointer concurrency."""

from __future__ import annotations

import json
from typing import Protocol

from shaper.application.publication import ReleaseBundle, verify_release


class GraphWriteTransport(Protocol):
    """Narrow SharePoint write operations."""

    def upload(
        self,
        path: str,
        content: bytes,
        *,
        conflict_behavior: str,
        if_match: str | None = None,
    ) -> str:
        """Upload content and return its eTag."""


class SharePointReleaseSink:
    """Write immutable release artifacts before manifest and current pointer."""

    def __init__(self, transport: GraphWriteTransport, *, output_root: str) -> None:
        self._transport = transport
        self._output_root = output_root.rstrip("/")

    def publish(
        self,
        bundle: ReleaseBundle,
        *,
        current_etag: str | None,
    ) -> str:
        """Publish a complete release and return the new current-pointer eTag."""
        verify_release(bundle)
        release_root = f"{self._output_root}/releases/{bundle.manifest.release_id}"
        for name, content in sorted(bundle.artifacts.items()):
            self._transport.upload(
                f"{release_root}/{name}",
                content,
                conflict_behavior="fail",
            )
        manifest = (
            json.dumps(
                bundle.manifest.model_dump(mode="json"),
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        ).encode()
        self._transport.upload(
            f"{release_root}/manifest.json",
            manifest,
            conflict_behavior="fail",
        )
        pointer = json.dumps({"release_id": bundle.manifest.release_id}, sort_keys=True).encode()
        return self._transport.upload(
            f"{self._output_root}/current.json",
            pointer,
            conflict_behavior="replace",
            if_match=current_etag,
        )
