import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from dupe_sweeper.engine.cache import load_cache, save_cache
from dupe_sweeper.engine.hashing import file_fingerprint, quick_hash_file, sha256_file


@dataclass
class DuplicateResult:
    groups: list[list[Path]]
    cache_hits: int
    cache_misses: int
    quick_hashes: int
    full_hashes: int


def finder_suffix_key(path: Path) -> tuple[bool, int, str]:
    has_finder_suffix = re.search(r" \d+$", path.stem) is not None
    return (has_finder_suffix, len(path.name), path.name.lower())


def sort_duplicate_group(paths: list[Path], keep: str) -> list[Path]:
    if keep == "original":
        return sorted(paths, key=finder_suffix_key)

    if keep == "oldest":
        return sorted(paths, key=lambda path: (path.stat().st_mtime_ns, path.name.lower()))

    if keep == "newest":
        return sorted(paths, key=lambda path: (-path.stat().st_mtime_ns, path.name.lower()))

    if keep == "shortest-name":
        return sorted(paths, key=lambda path: (len(path.name), path.name.lower()))

    raise ValueError(f"Unknown keep strategy: {keep}")


def get_cached_full_hash(path: Path, cache: dict) -> tuple[str, bool]:
    fingerprint = file_fingerprint(path)

    if fingerprint in cache:
        return cache[fingerprint], True

    file_hash = sha256_file(path)
    cache[fingerprint] = file_hash
    return file_hash, False


def find_duplicates(
    files: list[Path], keep: str = "original", show_progress: bool = True
) -> DuplicateResult:
    cache = load_cache()

    by_size: dict[int, list[Path]] = defaultdict(list)

    for file in files:
        by_size[file.stat().st_size].append(file)

    same_size_groups = [group for group in by_size.values() if len(group) > 1]
    same_size_file_count = sum(len(group) for group in same_size_groups)

    quick_hashes = 0
    full_hashes = 0
    cache_hits = 0
    cache_misses = 0
    duplicate_groups: list[list[Path]] = []

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

        for same_size_files in same_size_groups:
            by_quick_hash: dict[str, list[Path]] = defaultdict(list)

            for file in same_size_files:
                quick_hashes += 1
                by_quick_hash[quick_hash_file(file)].append(file)
                progress.advance(quick_task)

            quick_candidate_groups = [group for group in by_quick_hash.values() if len(group) > 1]

            for quick_group in quick_candidate_groups:
                by_full_hash: dict[str, list[Path]] = defaultdict(list)

                for file in quick_group:
                    full_hashes += 1
                    progress.update(full_task, description="Full hashing/cache...")

                    file_hash, was_cached = get_cached_full_hash(file, cache)

                    if was_cached:
                        cache_hits += 1
                    else:
                        cache_misses += 1

                    by_full_hash[file_hash].append(file)
                    progress.advance(full_task)

                for same_hash_files in by_full_hash.values():
                    if len(same_hash_files) > 1:
                        duplicate_groups.append(sort_duplicate_group(same_hash_files, keep=keep))

    save_cache(cache)

    return DuplicateResult(
        groups=duplicate_groups,
        cache_hits=cache_hits,
        cache_misses=cache_misses,
        quick_hashes=quick_hashes,
        full_hashes=full_hashes,
    )
