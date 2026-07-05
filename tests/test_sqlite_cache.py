from pathlib import Path

from dupe_sweeper.engine.cache.sqlite_cache import SQLiteCache


def test_sqlite_cache_get_put_stats_and_clear(tmp_path: Path) -> None:
    cache_path = tmp_path / "cache.sqlite3"
    cache = SQLiteCache(cache_path)

    assert cache.get("fingerprint-1") is None

    cache.put("fingerprint-1", "hash-1")
    cache.save()

    assert cache.get("fingerprint-1") == "hash-1"

    stats = cache.stats()

    assert stats.entries == 1
    assert stats.size_bytes > 0
    assert stats.path == str(cache_path)

    cache.clear()

    assert cache.get("fingerprint-1") is None
    assert cache.stats().entries == 0

    cache.close()
