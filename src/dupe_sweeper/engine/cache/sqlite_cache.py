import sqlite3
from pathlib import Path

from dupe_sweeper.engine.cache.base import CacheStats

CACHE_PATH = Path.home() / ".dupe-sweeper-cache.sqlite3"


class SQLiteCache:
    def __init__(self, path: Path = CACHE_PATH) -> None:
        self.path = path
        self.connection = sqlite3.connect(self.path)
        self._initialize()

    def get(self, fingerprint: str) -> str | None:
        cursor = self.connection.execute(
            "SELECT sha256 FROM file_hashes WHERE fingerprint = ?",
            (fingerprint,),
        )
        row = cursor.fetchone()

        if row is None:
            return None

        return str(row[0])

    def put(self, fingerprint: str, sha256: str) -> None:
        self.connection.execute(
            """
            INSERT INTO file_hashes (fingerprint, sha256)
            VALUES (?, ?)
            ON CONFLICT(fingerprint)
            DO UPDATE SET sha256 = excluded.sha256
            """,
            (fingerprint, sha256),
        )

    def clear(self) -> None:
        self.connection.execute("DELETE FROM file_hashes")
        self.connection.commit()

    def stats(self) -> CacheStats:
        cursor = self.connection.execute("SELECT COUNT(*) FROM file_hashes")
        entries = int(cursor.fetchone()[0])

        size_bytes = self.path.stat().st_size if self.path.exists() else 0

        return CacheStats(
            path=str(self.path),
            entries=entries,
            size_bytes=size_bytes,
        )

    def save(self) -> None:
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def _initialize(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS file_hashes (
                fingerprint TEXT PRIMARY KEY,
                sha256 TEXT NOT NULL
            )
            """
        )
        self.connection.commit()
