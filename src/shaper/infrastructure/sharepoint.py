"""Read-only SharePoint source synchronization through a narrow Graph transport."""

from __future__ import annotations

import hashlib
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from urllib.parse import quote, unquote, urlparse

from shaper.application.ports import SourceChange
from shaper.domain import PermissionSnapshot, SourceDocument, SourceRef


class GraphTransport(Protocol):
    """Minimal Graph operations required by the source connector."""

    def get_json(self, path_or_url: str) -> dict[str, object]:
        """Return one decoded Graph response."""

    def get_bytes(self, path_or_url: str) -> bytes:
        """Return downloaded file content."""


@dataclass(frozen=True)
class SharePointRoot:
    """Stable identifiers resolved from a SharePoint library URL."""

    hostname: str
    site_id: str
    drive_id: str
    item_id: str


class SharePointSource:
    """Enumerate one permission-homogeneous configured SharePoint root."""

    def __init__(self, transport: GraphTransport) -> None:
        self._transport = transport

    def resolve(self, library_url: str) -> SharePointRoot:
        """Resolve a SharePoint URL into stable Graph IDs."""
        parsed = urlparse(library_url)
        if parsed.scheme != "https" or not parsed.hostname or not parsed.path:
            raise ValueError("SharePoint source must be an absolute HTTPS library URL")
        path_parts = [unquote(part) for part in parsed.path.split("/") if part]
        if len(path_parts) < 2 or path_parts[0] not in {"sites", "teams"}:
            raise ValueError("SharePoint URL must identify a site or team library")
        site_path = "/" + "/".join(path_parts[:2])
        site = self._transport.get_json(f"/sites/{parsed.hostname}:{quote(site_path)}")
        site_id = _required_string(site, "id")
        relative = "/".join(path_parts[2:])
        item = self._transport.get_json(f"/sites/{site_id}/drive/root:/{quote(relative, safe='/')}")
        parent = _required_mapping(item, "parentReference")
        return SharePointRoot(
            hostname=parsed.hostname,
            site_id=site_id,
            drive_id=_required_string(parent, "driveId"),
            item_id=_required_string(item, "id"),
        )

    def changes(
        self,
        source: SourceRef,
        *,
        checkpoint: str | None,
    ) -> Iterator[SourceChange]:
        """Yield deterministic changes from initial enumeration or a delta checkpoint."""
        root = self.resolve(source.locator)
        next_url: str | None = checkpoint or f"/drives/{root.drive_id}/items/{root.item_id}/delta"
        while next_url:
            page = self._transport.get_json(next_url)
            values = page.get("value")
            if not isinstance(values, list):
                raise ValueError("Graph delta response does not contain a value list")
            page_checkpoint = _optional_string(page, "@odata.deltaLink") or next_url
            for raw_item in values:
                if not isinstance(raw_item, dict):
                    raise ValueError("Graph delta item is not an object")
                item_id = _required_string(raw_item, "id")
                if "deleted" in raw_item:
                    yield SourceChange(
                        kind="withdrawn",
                        document=None,
                        source_id=item_id,
                        checkpoint=page_checkpoint,
                    )
                    continue
                if "file" not in raw_item:
                    continue
                content = self._transport.get_bytes(
                    f"/drives/{root.drive_id}/items/{item_id}/content"
                )
                digest = hashlib.sha256(content).hexdigest()
                observed_at = _required_string(raw_item, "lastModifiedDateTime")
                observed_time = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
                permission_hash = hashlib.sha256(
                    f"{source.tenant_id}:{source.collection_id}:{root.site_id}:{root.item_id}".encode()
                ).hexdigest()
                document = SourceDocument.model_validate(
                    {
                        "source_id": item_id,
                        "source_version": digest,
                        "content_hash": digest,
                        "tenant_id": source.tenant_id,
                        "collection_id": source.collection_id,
                        "title": _required_string(raw_item, "name"),
                        "media_type": _required_string(
                            _required_mapping(raw_item, "file"), "mimeType"
                        ),
                        "observed_at": observed_time,
                        "permission": PermissionSnapshot.model_validate(
                            {
                                "permission_hash": permission_hash,
                                "captured_at": observed_time,
                            }
                        ),
                    }
                )
                yield SourceChange(
                    kind="changed",
                    document=document,
                    source_id=item_id,
                    checkpoint=page_checkpoint,
                )
            next_url = _optional_string(page, "@odata.nextLink")


def _required_mapping(value: dict[str, object], key: str) -> dict[str, object]:
    result = value.get(key)
    if not isinstance(result, dict):
        raise ValueError(f"Graph response field {key!r} is missing or not an object")
    return result


def _required_string(value: dict[str, object], key: str) -> str:
    result = value.get(key)
    if not isinstance(result, str) or not result:
        raise ValueError(f"Graph response field {key!r} is missing or not a string")
    return result


def _optional_string(value: dict[str, object], key: str) -> str | None:
    result = value.get(key)
    if result is None:
        return None
    if not isinstance(result, str):
        raise ValueError(f"Graph response field {key!r} is not a string")
    return result
