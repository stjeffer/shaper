"""Bounded ZIP expansion tests."""

from __future__ import annotations

import io
import stat
import zipfile

import pytest

from shaper.infrastructure.archive import ZipArchiveExpander
from shaper.infrastructure.uploads import UploadRejectedError


class Scanner:
    """Deterministic archive scanner."""

    def __init__(self, result: str = "clean") -> None:
        self.result = result

    def scan(self, content: bytes) -> str:
        return self.result


def _bundle(name: str, content: bytes, *, attributes: int = 0, flags: int = 0) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        item = zipfile.ZipInfo(name)
        item.external_attr = attributes
        item.flag_bits = flags
        archive.writestr(item, content)
    return buffer.getvalue()


def test_given_safe_archive_when_expanded_then_each_file_is_scanned_and_hashed() -> None:
    # Arrange
    content = _bundle("policies/travel.md", b"# Travel\n\nUse the approved provider.")

    # Act
    entries = ZipArchiveExpander(Scanner()).expand(content)

    # Assert
    assert (entries[0].path, entries[0].scan_result, len(entries[0].content_hash)) == (
        "policies/travel.md",
        "clean",
        64,
    )


@pytest.mark.parametrize(
    "content",
    [
        _bundle("../travel.md", b"policy"),
        _bundle("/travel.md", b"policy"),
        _bundle("travel.exe.pdf", b"%PDF-policy"),
        _bundle("nested.zip", b"PK\x03\x04"),
        _bundle(
            "link.txt",
            b"target",
            attributes=(stat.S_IFLNK | 0o777) << 16,
        ),
        _bundle("broken.pdf", b"not-a-pdf"),
        _bundle("binary.txt", b"bad\x00text"),
    ],
)
def test_given_unsafe_entry_when_expanded_then_entire_archive_is_rejected(
    content: bytes,
) -> None:
    # Act & Assert
    with pytest.raises(UploadRejectedError):
        ZipArchiveExpander(Scanner()).expand(content)


def test_given_infected_entry_when_expanded_then_no_partial_result_is_returned() -> None:
    # Arrange
    content = _bundle("travel.txt", b"policy")

    # Act & Assert
    with pytest.raises(UploadRejectedError, match="Malware"):
        ZipArchiveExpander(Scanner("infected")).expand(content)
