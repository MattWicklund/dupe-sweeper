from dupe_sweeper.engine.cache.base import CacheBackend, CacheStats
from dupe_sweeper.engine.cache.json_cache import JsonCache


def create_cache() -> CacheBackend:
    return JsonCache()


def clear_cache() -> None:
    cache = create_cache()
    cache.clear()


def get_cache_stats() -> CacheStats:
    cache = create_cache()
    return cache.stats()


__all__ = [
    "CacheBackend",
    "CacheStats",
    "JsonCache",
    "clear_cache",
    "create_cache",
    "get_cache_stats",
]
