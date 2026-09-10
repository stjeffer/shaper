"""Atomic immutable filesystem release sink."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

from shaper.application.publication import ReleaseBundle, verify_release


class CurrentPointerConflict(RuntimeError):
    """Raised when another release updates the current pointer first."""

    def __init__(self, release_id: str) -> None:
        super().__init__(f"Current release pointer changed before publishing {release_id}")
        self.release_id = release_id


@dataclass(frozen=True)
class PublishResult:
    """Filesystem publication result."""

    release_id: str
    pointer_hash: str
    status: str


class FilesystemReleaseSink:
    """Publish complete immutable releases and atomically advance current.json."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def current_hash(self) -> str | None:
        """Return the current pointer hash used as an eTag equivalent."""
        pointer = self._root / "current.json"
        return hashlib.sha256(pointer.read_bytes()).hexdigest() if pointer.is_file() else None

    def publish(
        self,
        bundle: ReleaseBundle,
        *,
        expected_current_hash: str | None,
    ) -> PublishResult:
        """Commit artifacts manifest-last, then atomically update current.json."""
        verify_release(bundle)
        self._root.mkdir(parents=True, exist_ok=True)
        releases = self._root / "releases"
        releases.mkdir(exist_ok=True)
        release_path = releases / bundle.manifest.release_id
        if release_path.exists():
            raise FileExistsError(f"Release already exists: {bundle.manifest.release_id}")

        stage = Path(tempfile.mkdtemp(prefix=".stage-", dir=releases))
        try:
            for name, content in sorted(bundle.artifacts.items()):
                target = stage / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            manifest_bytes = (
                json.dumps(
                    bundle.manifest.model_dump(mode="json"),
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n"
            ).encode()
            (stage / "manifest.json").write_bytes(manifest_bytes)
            stage.rename(release_path)
        except BaseException:
            shutil.rmtree(stage, ignore_errors=True)
            raise

        if self.current_hash() != expected_current_hash:
            raise CurrentPointerConflict(bundle.manifest.release_id)
        pointer = (
            json.dumps(
                {
                    "release_id": bundle.manifest.release_id,
                    "manifest_hash": hashlib.sha256(manifest_bytes).hexdigest(),
                },
                sort_keys=True,
            )
            + "\n"
        ).encode()
        with tempfile.NamedTemporaryFile(dir=self._root, delete=False) as temporary:
            temporary.write(pointer)
            temporary_path = Path(temporary.name)
        os.replace(temporary_path, self._root / "current.json")
        return PublishResult(
            release_id=bundle.manifest.release_id,
            pointer_hash=hashlib.sha256(pointer).hexdigest(),
            status="current",
        )

    def cleanup(
        self,
        *,
        now: datetime | None = None,
        retain_successful: int = 11,
        retain_days: int = 90,
        orphan_hours: int = 24,
    ) -> list[str]:
        """Remove only unpinned releases outside both retention guarantees."""
        timestamp = now or datetime.now(UTC)
        current = self._current_release_id()
        releases = self._root / "releases"
        if not releases.exists():
            return []
        entries = sorted(
            (path for path in releases.iterdir() if path.is_dir()),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        removed: list[str] = []
        for index, path in enumerate(entries):
            age = timestamp - datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
            if (
                path.name == current
                or index < retain_successful
                or age < timedelta(days=retain_days)
            ):
                continue
            if age >= timedelta(hours=orphan_hours):
                shutil.rmtree(path)
                removed.append(path.name)
        return removed

    def _current_release_id(self) -> str | None:
        pointer = self._root / "current.json"
        if not pointer.is_file():
            return None
        value = json.loads(pointer.read_text(encoding="utf-8"))
        release_id = value.get("release_id")
        return release_id if isinstance(release_id, str) else None
