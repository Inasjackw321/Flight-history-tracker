"""Load and query the aircraft metadata database."""

import os
import pandas as pd
from pathlib import Path

_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "aircraftDatabase.csv"
_DOWNLOAD_URL = "https://opensky-network.org/datasets/metadata/aircraftDatabase.csv"
_df: pd.DataFrame | None = None


def _download_db() -> None:
    """Download aircraft database if not present locally."""
    import requests

    if _DB_PATH.exists():
        return
    print(f"Downloading aircraft database (~50 MB) ...")
    _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(_DOWNLOAD_URL, stream=True, timeout=120)
    resp.raise_for_status()
    with open(_DB_PATH, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1 << 20):
            f.write(chunk)
    print("Download complete.")


def load() -> pd.DataFrame:
    """Load aircraft DB into memory (cached after first call)."""
    global _df
    if _df is not None:
        return _df
    _download_db()
    _df = pd.read_csv(
        _DB_PATH,
        usecols=["icao24", "manufacturername", "model", "typecode", "operator"],
        dtype=str,
        low_memory=True,
    )
    _df.columns = ["icao24", "manufacturer", "model", "typecode", "operator"]
    _df["icao24"] = _df["icao24"].str.strip().str.lower()
    _df = _df.drop_duplicates(subset="icao24")
    _df = _df.set_index("icao24")
    return _df


def enrich_flights(flights: list[dict]) -> pd.DataFrame:
    """Join flight records with aircraft metadata and return a DataFrame."""
    db = load()
    df = pd.DataFrame(flights)
    if df.empty:
        return df
    df["icao24"] = df["icao24"].str.strip().str.lower()
    df = df.merge(db, left_on="icao24", right_index=True, how="left")
    return df
