"""Quarantined direct-upload storage."""

from __future__ import annotations

import hashlib
import json
import shutil
import socket
import struct
import tempfile
import uuid
import zipfile
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import BinaryIO, Protocol

from shaper.application.ports import MalwareScanner, UploadAssetMetadata
from shaper.domain import CollectionRole, Principal

_MEDIA_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".md": "text/markdown",
    ".txt": "text/plain",
    ".zip": "application/zip",
}
_EXECUTABLE_SUFFIXES = frozenset({".bat", ".cmd", ".com", ".exe", ".js", ".ps1", ".sh"})


class UploadRejectedError(ValueError):
    """Raised when untrusted upload content violates the upload policy."""


class ScannerUnavailableError(RuntimeError):
    """Raised when a required scanner cannot return a verdict."""


class ClamdScanner:
    """Scan bounded content through a private ClamAV daemon."""

    def __init__(self, host: str, port: int = 3310, *, timeout_seconds: float = 30) -> None:
        self._host = host
        self._port = port
        self._timeout_seconds = timeout_seconds

    def scan(self, content: bytes) -> str:
        """Return a clean or infected verdict from clamd INSTREAM."""
        try:
            with socket.create_connection(
                (self._host, self._port),
                timeout=self._timeout_seconds,
            ) as connection:
                connection.sendall(b"zINSTREAM\0")
                for offset in range(0, len(content), 64 * 1024):
                    chunk = content[offset : offset + 64 * 1024]
                    connection.sendall(struct.pack("!I", len(chunk)))
                    connection.sendall(chunk)
                connection.sendall(struct.pack("!I", 0))
                response = connection.recv(4096).decode("utf-8", errors="replace")
        except OSError as error:
            raise ScannerUnavailableError(
                f"Malware scanner at {self._host}:{self._port} is unavailable"
            ) from error
        if response.endswith("OK\0"):
            return "clean"
        if "FOUND" in response:
            return "infected"
        raise ScannerUnavailableError(f"Malware scanner returned an invalid response: {response!r}")

    def is_ready(self) -> bool:
        """Return whether clamd responds to a bounded ping."""
        try:
            with socket.create_connection(
                (self._host, self._port),
                timeout=self._timeout_seconds,
            ) as connection:
                connection.sendall(b"zPING\0")
                return connection.recv(16) == b"PONG\0"
        except OSError:
            return False


class BinaryWriter(Protocol):
    """Minimal writable binary stream."""

    def write(self, data: bytes) -> int:
        """Write bytes and return the number accepted."""


@dataclass(frozen=True)
class StagedAsset:
    """Opaque metadata for a scanned upload asset."""

    asset_id: str
    filename: str
    tenant_id: str
    collection_id: str
    media_type: str
    extension: str
    content_hash: str
    size: int
    scan_result: str
    created_at: str
    expires_at: str


class FileUploadStore:
    """Store bounded uploads outside release roots using generated names."""

    def __init__(
        self,
        root: Path,
        *,
        scanner: MalwareScanner,
        maximum_bytes: int = 50 * 1024 * 1024,
        retention: timedelta = timedelta(hours=24),
    ) -> None:
        self._root = root.resolve()
        self._scanner = scanner
        self._maximum_bytes = maximum_bytes
        self._retention = retention

    def stage(
        self,
        chunks: Iterable[bytes],
        *,
        supplied_filename: str,
        media_type: str,
        principal: Principal,
        collection_id: str,
        now: datetime | None = None,
    ) -> StagedAsset:
        """Validate, scan, and persist a direct upload."""
        principal.require(collection_id, CollectionRole.COMPILE)
        extension = self._validate_name_and_media_type(supplied_filename, media_type)
        self._root.mkdir(parents=True, exist_ok=True)
        asset_id = uuid.uuid4().hex
        timestamp = now or datetime.now(UTC)
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("Upload timestamp must include a timezone")

        with tempfile.NamedTemporaryFile(dir=self._root, delete=False) as temporary:
            temporary_path = Path(temporary.name)
            size, digest = self._write_bounded(chunks, temporary)
        try:
            content = temporary_path.read_bytes()
            self._validate_signature(extension, content)
            scan_result = self._scanner.scan(content)
            if scan_result not in {"clean", "infected"}:
                raise ScannerUnavailableError(
                    f"Scanner returned unsupported result {scan_result!r}; "
                    "upload remains quarantined"
                )
            if scan_result == "infected":
                raise UploadRejectedError("Malware scanner rejected the upload")
            asset = StagedAsset(
                asset_id=asset_id,
                filename=f"{asset_id}{extension}",
                tenant_id=principal.tenant_id,
                collection_id=collection_id,
                media_type=media_type,
                extension=extension,
                content_hash=digest,
                size=size,
                scan_result=scan_result,
                created_at=timestamp.isoformat(),
                expires_at=(timestamp + self._retention).isoformat(),
            )
            asset_root = self._root / asset_id
            asset_root.mkdir()
            shutil.move(str(temporary_path), asset_root / "content")
            (asset_root / "metadata.json").write_text(
                json.dumps(asdict(asset), sort_keys=True),
                encoding="utf-8",
            )
            return asset
        except BaseException:
            temporary_path.unlink(missing_ok=True)
            shutil.rmtree(self._root / asset_id, ignore_errors=True)
            raise

    @contextmanager
    def open_asset(
        self,
        asset_id: str,
        principal: Principal,
        *,
        now: datetime | None = None,
    ) -> Iterator[BinaryIO]:
        """Open an authorized clean asset before its expiry."""
        self._load_authorized_asset(asset_id, principal, now=now)
        with (self._root / asset_id / "content").open("rb") as stream:
            yield stream

    def describe(self, asset_id: str, principal: Principal) -> UploadAssetMetadata:
        """Return authorized metadata for one clean unexpired asset."""
        asset = self._load_authorized_asset(asset_id, principal)
        return UploadAssetMetadata(
            asset_id=asset.asset_id,
            filename=asset.filename,
            media_type=asset.media_type,
        )

    def cleanup(self, *, now: datetime | None = None) -> int:
        """Delete expired upload assets and return the number removed."""
        timestamp = now or datetime.now(UTC)
        removed = 0
        if not self._root.exists():
            return removed
        for metadata_path in self._root.glob("*/metadata.json"):
            asset = StagedAsset(**json.loads(metadata_path.read_text(encoding="utf-8")))
            if timestamp >= datetime.fromisoformat(asset.expires_at):
                shutil.rmtree(metadata_path.parent)
                removed += 1
        return removed

    def _load_authorized_asset(
        self,
        asset_id: str,
        principal: Principal,
        *,
        now: datetime | None = None,
    ) -> StagedAsset:
        if not asset_id.isalnum():
            raise UploadRejectedError("Asset ID is invalid")
        metadata_path = self._root / asset_id / "metadata.json"
        if not metadata_path.is_file():
            raise FileNotFoundError(f"Upload asset does not exist: {asset_id}")
        asset = StagedAsset(**json.loads(metadata_path.read_text(encoding="utf-8")))
        if principal.tenant_id != asset.tenant_id:
            raise PermissionError("Upload asset belongs to another tenant")
        principal.require(asset.collection_id, CollectionRole.COMPILE)
        timestamp = now or datetime.now(UTC)
        if timestamp >= datetime.fromisoformat(asset.expires_at):
            raise UploadRejectedError(f"Upload asset has expired: {asset_id}")
        if asset.scan_result != "clean":
            raise UploadRejectedError(f"Upload asset is not cleared for ingestion: {asset_id}")
        return asset

    def _write_bounded(self, chunks: Iterable[bytes], stream: BinaryWriter) -> tuple[int, str]:
        digest = hashlib.sha256()
        size = 0
        for chunk in chunks:
            size += len(chunk)
            if size > self._maximum_bytes:
                raise UploadRejectedError(
                    f"Upload exceeds configured limit of {self._maximum_bytes} bytes"
                )
            stream.write(chunk)
            digest.update(chunk)
        if size == 0:
            raise UploadRejectedError("Upload is empty")
        return size, digest.hexdigest()

    @staticmethod
    def _validate_name_and_media_type(filename: str, media_type: str) -> str:
        path = Path(filename)
        extension = path.suffix.lower()
        if extension not in _MEDIA_TYPES:
            raise UploadRejectedError(f"Unsupported upload extension: {extension or '<none>'}")
        if any(suffix.lower() in _EXECUTABLE_SUFFIXES for suffix in path.suffixes[:-1]):
            raise UploadRejectedError("Executable double extension is not allowed")
        if _MEDIA_TYPES[extension] != media_type:
            raise UploadRejectedError(
                f"Media type {media_type!r} does not match extension {extension!r}"
            )
        return extension

    @staticmethod
    def _validate_signature(extension: str, content: bytes) -> None:
        if extension == ".pdf" and not content.startswith(b"%PDF-"):
            raise UploadRejectedError("PDF signature is invalid")
        if extension in {".md", ".txt"} and b"\x00" in content:
            raise UploadRejectedError("Text upload contains binary null bytes")
        if extension == ".zip":
            with tempfile.NamedTemporaryFile() as temporary:
                temporary.write(content)
                temporary.flush()
                if not zipfile.is_zipfile(temporary.name):
                    raise UploadRejectedError("ZIP signature is invalid")
            return
        if extension != ".docx":
            return
        with tempfile.NamedTemporaryFile() as temporary:
            temporary.write(content)
            temporary.flush()
            if not zipfile.is_zipfile(temporary.name):
                raise UploadRejectedError("DOCX signature is invalid")
            with zipfile.ZipFile(temporary.name) as archive:
                names = set(archive.namelist())
                required = {"[Content_Types].xml", "word/document.xml"}
                if not required.issubset(names):
                    raise UploadRejectedError("DOCX package is missing required entries")
                if any(name.lower().endswith("vbaproject.bin") for name in names):
                    raise UploadRejectedError("Macro-enabled documents are not accepted")
                expanded = sum(item.file_size for item in archive.infolist())
                if expanded > max(len(content) * 100, 10 * 1024 * 1024):
                    raise UploadRejectedError("DOCX package expansion exceeds safety limits")
