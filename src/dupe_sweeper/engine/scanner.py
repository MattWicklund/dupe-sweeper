from collections.abc import Iterator
from pathlib import Path


def normalize_extensions(extensions: list[str] | None) -> set[str] | None:
    if not extensions:
        return None

    normalized = set()

    for ext in extensions:
        ext = ext.lower()
        normalized.add(ext if ext.startswith(".") else f".{ext}")

    return normalized


def is_hidden(path: Path, root: Path) -> bool:
    try:
        relative_parts = path.relative_to(root).parts
    except ValueError:
        relative_parts = path.parts

    return any(part.startswith(".") for part in relative_parts)


def scan_files(
    directory: Path,
    recursive: bool = False,
    extensions: list[str] | None = None,
    include_hidden: bool = False,
) -> Iterator[Path]:
    allowed_extensions = normalize_extensions(extensions)
    files = directory.rglob("*") if recursive else directory.iterdir()

    for path in files:
        if not include_hidden and is_hidden(path, directory):
            continue

        if not path.is_file():
            continue

        if allowed_extensions and path.suffix.lower() not in allowed_extensions:
            continue

        yield path
