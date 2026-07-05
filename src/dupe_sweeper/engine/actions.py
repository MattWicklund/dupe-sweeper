from pathlib import Path

from send2trash import send2trash


def delete_files(files: list[Path]) -> int:
    deleted_count = 0

    for file in files:
        file.unlink()
        deleted_count += 1

    return deleted_count


def trash_files(files: list[Path]) -> int:
    trashed_count = 0

    for file in files:
        send2trash(str(file))
        trashed_count += 1

    return trashed_count
