import re
from collections import defaultdict
from pathlib import Path

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from dupe_sweeper.engine.cache import create_cache
from dupe_sweeper.engine.hashing import file_fingerprint, quick_hash_file, sha256_file
from dupe_sweeper.models import DuplicateGroup, FileRecord, ScanResult


def finder_suffix_key(path: Path) -> tuple[bool, int, str]:
    has_finder_suffix = re.search(r" \d+$", path.stem) is not None
    return (has_finder_suffix, len(path.name), path.name.lower())


def sort_duplicate_group(records: list[FileRecord], keep: str) -> list[FileRecord]:
    if keep == "original":
        return sorted(records, key=lambda record: finder_suffix_key(record.path))

    if keep == "oldest":
        return sorted(
            records,
            key=lambda record: (
                record.path.stat().st_mtime_ns,
                record.path.name.lower(),
            ),
        )

    if keep == "newest":
        return sorted(
            records,
            key=lambda record: (
                -record.path.stat().st_mtime_ns,
                record.path.name.lower(),
            ),
        )

    if keep == "shortest-name":
        return sorted(
            records,
            key=lambda record: (
                len(record.path.name),
                record.path.name.lower(),
            ),
        )

    raise ValueError(f"Unknown keep strategy: {keep}")


def get_cached_full_hash(path: Path, cache) -> tuple[str, bool]:
    fingerprint = file_fingerprint(path)

    cached_hash = cache.get(fingerprint)

    if cached_hash is not None:
        return cached_hash, True

    file_hash = sha256_file(path)
    cache.put(fingerprint, file_hash)

    return file_hash, False


def find_duplicates(
    files: list[Path],
    keep: str = "original",
    show_progress: bool = True,
) -> ScanResult:
    cache = create_cache()

    records = [
        FileRecord(
            path=file,
            size=file.stat().st_size,
        )
        for file in files
    ]

    by_size: dict[int, list[FileRecord]] = defaultdict(list)

    for record in records:
        by_size[record.size].append(record)

    same_size_groups = [group for group in by_size.values() if len(group) > 1]
    same_size_file_count = sum(len(group) for group in same_size_groups)

    quick_hashes = 0
    full_hashes = 0
    cache_hits = 0
    cache_misses = 0
    duplicate_groups: list[DuplicateGroup] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        disable=not show_progress,
    ) as progress:
        quick_task = progress.add_task(
            "Quick hashing candidates...",
            total=same_size_file_count,
        )

        full_task = progress.add_task(
            "Full hashing/cache...",
            total=None,
        )

        for same_size_records in same_size_groups:
            by_quick_hash: dict[str, list[FileRecord]] = defaultdict(list)

            for record in same_size_records:
                quick_hashes += 1

                record.quick_hash = quick_hash_file(record.path)
                by_quick_hash[record.quick_hash].append(record)

                progress.advance(quick_task)

            quick_candidate_groups = [group for group in by_quick_hash.values() if len(group) > 1]

            for quick_group in quick_candidate_groups:
                by_full_hash: dict[str, list[FileRecord]] = defaultdict(list)

                for record in quick_group:
                    full_hashes += 1

                    file_hash, was_cached = get_cached_full_hash(record.path, cache)
                    record.sha256 = file_hash

                    if was_cached:
                        cache_hits += 1
                    else:
                        cache_misses += 1

                    by_full_hash[file_hash].append(record)

                    progress.advance(full_task)

                for same_hash_records in by_full_hash.values():
                    if len(same_hash_records) > 1:
                        sorted_records = sort_duplicate_group(
                            same_hash_records,
                            keep=keep,
                        )

                        duplicate_groups.append(
                            DuplicateGroup(
                                keep=sorted_records[0],
                                duplicates=sorted_records[1:],
                            )
                        )

    cache.save()

    return ScanResult(
        groups=duplicate_groups,
        files_scanned=len(records),
        cache_hits=cache_hits,
        cache_misses=cache_misses,
        quick_hashes=quick_hashes,
        full_hashes=full_hashes,
    )
