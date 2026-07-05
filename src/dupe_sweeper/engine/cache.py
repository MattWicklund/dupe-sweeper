import json
from pathlib import Path
from typing import Any

CACHE_PATH = Path.home() / ".dupe-sweeper-cache.json"


def load_cache() -> dict[str, Any]:
    if not CACHE_PATH.exists():
        return {}

    try:
        return json.loads(CACHE_PATH.read_text())
    except json.JSONDecodeError:
        return {}


def save_cache(cache: dict[str, Any]) -> None:
    CACHE_PATH.write_text(json.dumps(cache, indent=2))


def clear_cache() -> None:
    if CACHE_PATH.exists():
        CACHE_PATH.unlink()


def get_cache_stats() -> dict[str, int | str]:
    cache = load_cache()

    size_bytes = CACHE_PATH.stat().st_size if CACHE_PATH.exists() else 0

    return {
        "path": str(CACHE_PATH),
        "entries": len(cache),
        "size_bytes": size_bytes,
    }
