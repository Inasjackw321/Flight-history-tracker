#!/usr/bin/env python3
"""Flight History Tracker — look up flights by airport and filter by airframe.

Usage:
    python app.py

Data covers the last 60 days. Results are cached locally for fast repeat loads.
"""

import sys
import datetime as dt

from flight_tracker import airports, cache, fetcher, aircraft_db

import pandas as pd

pd.set_option("display.max_rows", 200)
pd.set_option("display.width", 160)
pd.set_option("display.max_colwidth", 24)

DAYS = 60


# ── helpers ──────────────────────────────────────────────────────────────────

def _progress(step: int, total: int, direction: str) -> None:
    pct = int(step / total * 100)
    print(f"\r  Fetching {direction}s ... {pct}%", end="", flush=True)


def _load_flights(icao: str) -> pd.DataFrame:
    """Load flights from cache or API, enrich with aircraft metadata."""
    cached = cache.get_cached(icao)
    if cached is not None:
        print(f"  Loaded {len(cached)} flights from cache (instant).")
        return aircraft_db.enrich_flights(cached)

    print(f"  Fetching last {DAYS} days from OpenSky (this may take a minute) ...")
    raw = fetcher.fetch_flights(icao, days=DAYS, progress_cb=_progress)
    print()  # newline after progress
    if raw:
        cache.save_cache(icao, raw)
        print(f"  Fetched {len(raw)} flights, cached for next time.")
    else:
        print("  No flights found for this airport/period.")
    return aircraft_db.enrich_flights(raw)


def _display_summary(df: pd.DataFrame) -> None:
    """Print a summary table of airframes seen at the airport."""
    if df.empty:
        print("\n  No data to display.\n")
        return

    summary = (
        df.groupby(["typecode", "manufacturer", "model"])
        .agg(flights=("icao24", "count"), unique_aircraft=("icao24", "nunique"))
        .reset_index()
        .sort_values("flights", ascending=False)
    )
    summary = summary[summary["typecode"].notna() & (summary["typecode"] != "")]
    print(f"\n  Airframe summary ({len(summary)} types, {len(df)} total flights):\n")
    print(summary.to_string(index=False))
    print()


def _filter_menu(df: pd.DataFrame) -> None:
    """Interactive loop to filter by airframe type."""
    while True:
        cmd = input("  Filter by typecode (e.g. B738), 'list' for types, or 'back': ").strip()
        if cmd.lower() in ("back", "b", ""):
            break
        if cmd.lower() == "list":
            _display_summary(df)
            continue

        filtered = df[df["typecode"].str.upper() == cmd.upper()]
        if filtered.empty:
            print(f"  No flights found for typecode '{cmd}'.")
            continue

        cols = ["callsign", "estDepartureAirport", "estArrivalAirport",
                "manufacturer", "model", "operator", "typecode"]
        show_cols = [c for c in cols if c in filtered.columns]

        # Add human-readable time
        view = filtered[show_cols].copy()
        if "firstSeen" in filtered.columns:
            view.insert(0, "date", pd.to_datetime(filtered["firstSeen"], unit="s").dt.strftime("%Y-%m-%d %H:%M"))

        print(f"\n  {len(view)} flights with typecode {cmd.upper()}:\n")
        print(view.to_string(index=False))
        print()


# ── main loop ────────────────────────────────────────────────────────────────

def main() -> None:
    print("\n=== Flight History Tracker ===")
    print(f"  Data window: last {DAYS} days")
    print("  Enter an airport code (IATA like JFK or ICAO like KJFK)")
    print("  Type 'quit' to exit.\n")

    # Pre-load aircraft DB in background for speed
    print("  Loading aircraft database...")
    aircraft_db.load()
    print("  Ready.\n")

    while True:
        code = input("Airport> ").strip()
        if not code:
            continue
        if code.lower() in ("quit", "exit", "q"):
            break

        icao = airports.resolve_to_icao(code)
        print(f"  Resolved to ICAO: {icao}")

        df = _load_flights(icao)
        if df.empty:
            continue

        _display_summary(df)
        _filter_menu(df)


if __name__ == "__main__":
    main()
