from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class CacheStats:
    path: str
    entries: int
    size_bytes: int


class CacheBackend(Protocol):
    def get(self, fingerprint: str) -> str | None: ...

    def put(self, fingerprint: str, sha256: str) -> None: ...

    def clear(self) -> None: ...

    def stats(self) -> CacheStats: ...

    def save(self) -> None: ...
