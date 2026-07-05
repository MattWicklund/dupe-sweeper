import hashlib
from pathlib import Path


def file_fingerprint(path: Path) -> str:
    stat = path.stat()
    return f"{path.resolve()}|{stat.st_size}|{stat.st_mtime_ns}"


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        while chunk := file.read(chunk_size):
            digest.update(chunk)

    return digest.hexdigest()


def quick_hash_file(path: Path, sample_size: int = 64 * 1024) -> str:
    """
    Hash a small sample from the start and end of the file.

    This is not used as final proof of duplication.
    It is only used to reduce how many files need full hashing.
    """
    digest = hashlib.sha256()
    file_size = path.stat().st_size

    with path.open("rb") as file:
        digest.update(file.read(sample_size))

        if file_size > sample_size:
            file.seek(max(file_size - sample_size, 0))
            digest.update(file.read(sample_size))

    return digest.hexdigest()
