from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class FileRecord:
    path: Path
    size: int
    quick_hash: str | None = None
    sha256: str | None = None


@dataclass(slots=True)
class DuplicateGroup:
    keep: FileRecord
    duplicates: list[FileRecord]

    @property
    def files(self) -> list[FileRecord]:
        return [self.keep, *self.duplicates]

    @property
    def recoverable_bytes(self) -> int:
        return sum(file.size for file in self.duplicates)


@dataclass(slots=True)
class ScanResult:
    groups: list[DuplicateGroup] = field(default_factory=list)
    files_scanned: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    quick_hashes: int = 0
    full_hashes: int = 0

    @property
    def duplicate_files(self) -> list[FileRecord]:
        return [duplicate for group in self.groups for duplicate in group.duplicates]

    @property
    def duplicate_file_count(self) -> int:
        return len(self.duplicate_files)

    @property
    def recoverable_bytes(self) -> int:
        return sum(group.recoverable_bytes for group in self.groups)
