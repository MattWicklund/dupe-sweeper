import json
from pathlib import Path
from typing import Any

from dupe_sweeper.engine.cache.base import CacheStats

CACHE_PATH = Path.home() / ".dupe-sweeper-cache.json"


class JsonCache:
    def __init__(self, path: Path = CACHE_PATH) -> None:
        self.path = path
        self._cache: dict[str, Any] = self._load()

    def get(self, fingerprint: str) -> str | None:
        value = self._cache.get(fingerprint)
        return str(value) if value is not None else None

    def put(self, fingerprint: str, sha256: str) -> None:
        self._cache[fingerprint] = sha256

    def clear(self) -> None:
        self._cache.clear()

        if self.path.exists():
            self.path.unlink()

    def stats(self) -> CacheStats:
        size_bytes = self.path.stat().st_size if self.path.exists() else 0

        return CacheStats(
            path=str(self.path),
            entries=len(self._cache),
            size_bytes=size_bytes,
        )

    def save(self) -> None:
        self.path.write_text(json.dumps(self._cache, indent=2))

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}

        try:
            return json.loads(self.path.read_text())
        except json.JSONDecodeError:
            return {}
