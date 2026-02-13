"""IATA <-> ICAO airport code lookup using bundled data."""

import csv
import os
import io
from pathlib import Path

_AIRPORTS_PATH = Path(__file__).resolve().parent.parent / "data" / "airports.csv"
_DOWNLOAD_URL = "https://davidmegginson.github.io/ourairports-data/airports.csv"
_iata_to_icao: dict[str, str] | None = None


def _download_airports() -> None:
    import requests

    if _AIRPORTS_PATH.exists():
        return
    print("Downloading airport database...")
    _AIRPORTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(_DOWNLOAD_URL, timeout=60)
    resp.raise_for_status()
    with open(_AIRPORTS_PATH, "wb") as f:
        f.write(resp.content)
    print("Airport database downloaded.")


def _load() -> dict[str, str]:
    global _iata_to_icao
    if _iata_to_icao is not None:
        return _iata_to_icao
    _download_airports()
    _iata_to_icao = {}
    with open(_AIRPORTS_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            iata = (row.get("iata_code") or "").strip().upper()
            icao = (row.get("ident") or "").strip().upper()
            if iata and icao and len(icao) == 4:
                _iata_to_icao[iata] = icao
    return _iata_to_icao


def resolve_to_icao(code: str) -> str:
    """Accept IATA (3-letter) or ICAO (4-letter) and return ICAO."""
    code = code.strip().upper()
    if len(code) == 4:
        return code
    if len(code) == 3:
        mapping = _load()
        icao = mapping.get(code)
        if icao:
            return icao
    return code
