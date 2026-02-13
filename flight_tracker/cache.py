"""Local file cache for flight data — ensures fast loading on repeat queries."""

import json
import os
import time
from pathlib import Path

CACHE_DIR = Path.home() / ".flight_tracker_cache"
CACHE_TTL_SECONDS = 6 * 3600  # 6 hours


def _cache_path(icao_code: str) -> Path:
    return CACHE_DIR / f"{icao_code.upper()}_flights.json"


def get_cached(icao_code: str) -> list[dict] | None:
    """Return cached flight list if fresh, else None."""
    path = _cache_path(icao_code)
    if not path.exists():
        return None
    age = time.time() - path.stat().st_mtime
    if age > CACHE_TTL_SECONDS:
        return None
    with open(path, "r") as f:
        return json.load(f)


def save_cache(icao_code: str, flights: list[dict]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(_cache_path(icao_code), "w") as f:
        json.dump(flights, f)
