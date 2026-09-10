"""Fail-closed expansion of untrusted ZIP bundles."""

from __future__ import annotations

import hashlib
import io
import stat
import zipfile
from dataclasses import dataclass
from pathlib import PurePosixPath

from shaper.application.ports import MalwareScanner
from shaper.infrastructure.uploads import ScannerUnavailableError, UploadRejectedError

_MEDIA_TYPES = {
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".md": "text/markdown",
    ".pdf": "application/pdf",
    ".txt": "text/plain",
}
_EXECUTABLE_SUFFIXES = frozenset({".bat", ".cmd", ".com", ".exe", ".js", ".ps1", ".sh"})


@dataclass(frozen=True)
class ArchiveEntry:
    """One validated and scanned file extracted entirely in memory."""

    path: str
    media_type: str
    content: bytes
    content_hash: str
    scan_result: str


class ZipArchiveExpander:
    """Expand bounded ZIP entries only after every entry passes validation."""

    def __init__(
        self,
        scanner: MalwareScanner,
        *,
        maximum_entries: int = 100,
        maximum_entry_bytes: int = 10 * 1024 * 1024,
        maximum_expanded_bytes: int = 50 * 1024 * 1024,
        maximum_compression_ratio: float = 100,
    ) -> None:
        self._scanner = scanner
        self._maximum_entries = maximum_entries
        self._maximum_entry_bytes = maximum_entry_bytes
        self._maximum_expanded_bytes = maximum_expanded_bytes
        self._maximum_compression_ratio = maximum_compression_ratio

    def expand(self, content: bytes) -> tuple[ArchiveEntry, ...]:
        """Return a complete safe entry set or raise without partial results."""
        try:
            archive = zipfile.ZipFile(io.BytesIO(content))
        except zipfile.BadZipFile as error:
            raise UploadRejectedError("ZIP signature is invalid") from error
        with archive:
            files = [item for item in archive.infolist() if not item.is_dir()]
            if not files:
                raise UploadRejectedError("ZIP bundle contains no files")
            if len(files) > self._maximum_entries:
                raise UploadRejectedError("ZIP bundle exceeds the configured entry limit")
            expanded = sum(item.file_size for item in files)
            if expanded > self._maximum_expanded_bytes:
                raise UploadRejectedError("ZIP bundle exceeds the aggregate expanded-size limit")
            entries = tuple(self._extract(archive, item) for item in files)
        return entries

    def _extract(self, archive: zipfile.ZipFile, item: zipfile.ZipInfo) -> ArchiveEntry:
        path = PurePosixPath(item.filename)
        if (
            path.is_absolute()
            or ".." in path.parts
            or "\\" in item.filename
            or ":" in path.parts[0]
        ):
            raise UploadRejectedError("ZIP entry path is unsafe")
        mode = item.external_attr >> 16
        if stat.S_ISLNK(mode):
            raise UploadRejectedError("ZIP symbolic links are not accepted")
        if item.flag_bits & 0x1:
            raise UploadRejectedError("Encrypted ZIP entries are not accepted")
        if item.file_size > self._maximum_entry_bytes:
            raise UploadRejectedError("ZIP entry exceeds the per-file expanded-size limit")
        ratio = item.file_size / max(item.compress_size, 1)
        if ratio > self._maximum_compression_ratio:
            raise UploadRejectedError("ZIP entry exceeds the compression-ratio limit")
        suffixes = [suffix.casefold() for suffix in path.suffixes]
        extension = path.suffix.casefold()
        if extension == ".zip":
            raise UploadRejectedError("Nested archives are not accepted")
        if extension not in _MEDIA_TYPES:
            raise UploadRejectedError(f"Unsupported ZIP entry extension: {extension or '<none>'}")
        if any(suffix in _EXECUTABLE_SUFFIXES for suffix in suffixes[:-1]):
            raise UploadRejectedError("Executable double extensions are not accepted")
        data = archive.read(item)
        self._validate_signature(extension, data)
        scan_result = self._scanner.scan(data)
        if scan_result == "infected":
            raise UploadRejectedError("Malware scanner rejected a ZIP entry")
        if scan_result != "clean":
            raise ScannerUnavailableError("Malware scanner returned no usable ZIP-entry verdict")
        return ArchiveEntry(
            path=path.as_posix(),
            media_type=_MEDIA_TYPES[extension],
            content=data,
            content_hash=hashlib.sha256(data).hexdigest(),
            scan_result=scan_result,
        )

    @staticmethod
    def _validate_signature(extension: str, content: bytes) -> None:
        if not content:
            raise UploadRejectedError("ZIP entries cannot be empty")
        if extension == ".pdf" and not content.startswith(b"%PDF-"):
            raise UploadRejectedError("PDF entry signature is invalid")
        if extension in {".md", ".txt"} and b"\x00" in content:
            raise UploadRejectedError("Text ZIP entry contains binary null bytes")
        if extension != ".docx":
            return
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as package:
                names = set(package.namelist())
                if not {"[Content_Types].xml", "word/document.xml"}.issubset(names):
                    raise UploadRejectedError("DOCX entry is missing required package files")
                if any(name.casefold().endswith("vbaproject.bin") for name in names):
                    raise UploadRejectedError("Macro-enabled DOCX entries are not accepted")
        except zipfile.BadZipFile as error:
            raise UploadRejectedError("DOCX entry signature is invalid") from error
