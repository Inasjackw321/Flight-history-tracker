"""Fetch flight arrivals/departures from OpenSky Network API."""

import time
import requests

API_BASE = "https://opensky-network.org/api"
WINDOW_SECONDS = 7 * 86400  # OpenSky max query window is 7 days
REQUEST_DELAY = 1.5  # seconds between requests to stay under rate limits


def _fetch_window(endpoint: str, airport: str, begin: int, end: int) -> list[dict]:
    """Fetch a single 7-day window of flights."""
    url = f"{API_BASE}/flights/{endpoint}"
    params = {"airport": airport, "begin": begin, "end": end}
    try:
        resp = requests.get(url, params=params, timeout=30)
        if resp.status_code == 200:
            return resp.json() or []
        if resp.status_code == 404:
            return []
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  Warning: request failed ({e}), skipping window.")
    return []


def fetch_flights(airport_icao: str, days: int = 60, progress_cb=None) -> list[dict]:
    """Fetch all arrivals and departures for an airport over the given period.

    Splits the date range into 7-day windows as required by the API.
    Returns deduplicated list of flight dicts.
    """
    now = int(time.time())
    start = now - days * 86400
    windows = []
    t = start
    while t < now:
        window_end = min(t + WINDOW_SECONDS, now)
        windows.append((t, window_end))
        t = window_end

    total_steps = len(windows) * 2  # arrivals + departures
    step = 0
    seen = set()
    flights = []

    for direction in ("arrival", "departure"):
        for begin, end in windows:
            step += 1
            if progress_cb:
                progress_cb(step, total_steps, direction)
            batch = _fetch_window(direction, airport_icao, begin, end)
            for f in batch:
                key = (f.get("icao24"), f.get("firstSeen"), f.get("lastSeen"))
                if key not in seen:
                    seen.add(key)
                    flights.append(f)
            time.sleep(REQUEST_DELAY)

    return flights
