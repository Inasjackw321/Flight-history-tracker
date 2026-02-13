"""Generate a text report for flights at an airport filtered by airframe type."""

import datetime as dt
from pathlib import Path

import pandas as pd

REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"


def generate(airport_icao: str, typecode: str, df: pd.DataFrame) -> Path:
    """Write a report file and return its path.

    Parameters
    ----------
    airport_icao : str
        ICAO code for the airport (e.g. "KJFK").
    typecode : str
        Aircraft ICAO type designator (e.g. "B738").
    df : pd.DataFrame
        Full enriched flight DataFrame for the airport.
    """
    filtered = df[df["typecode"].str.upper() == typecode.upper()]

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{airport_icao}_{typecode.upper()}_{stamp}.txt"
    path = REPORT_DIR / filename

    lines: list[str] = []
    w = lines.append

    w("=" * 70)
    w(f"  FLIGHT REPORT — {typecode.upper()} at {airport_icao}")
    w(f"  Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    w("=" * 70)

    # ── Overview ──
    unique = filtered["icao24"].nunique()
    w("")
    w(f"  Total flights : {len(filtered)}")
    w(f"  Unique aircraft: {unique}")

    if "manufacturer" in filtered.columns:
        mfr = filtered["manufacturer"].dropna().unique()
        w(f"  Manufacturer   : {', '.join(mfr) if len(mfr) else 'Unknown'}")
    if "model" in filtered.columns:
        models = filtered["model"].dropna().unique()
        w(f"  Model(s)       : {', '.join(models) if len(models) else 'Unknown'}")
    if "engines" in filtered.columns:
        eng = filtered["engines"].dropna().unique()
        if len(eng):
            w(f"  Engines        : {', '.join(eng)}")
    if "category" in filtered.columns:
        cats = filtered["category"].dropna().unique()
        if len(cats):
            w(f"  Category       : {', '.join(cats)}")

    # ── Operators ──
    if "operator" in filtered.columns:
        ops = filtered.groupby("operator")["icao24"].count().sort_values(ascending=False)
        ops = ops[ops.index.notna() & (ops.index != "")]
        if len(ops):
            w("")
            w("-" * 70)
            w("  OPERATORS")
            w("-" * 70)
            for op, cnt in ops.items():
                w(f"    {op:<40s} {cnt:>5d} flights")

    # ── Individual Aircraft ──
    detail_cols = [
        "icao24", "registration", "serialnumber", "linenumber",
        "owner", "operator", "built", "firstflightdate",
    ]
    present = [c for c in detail_cols if c in filtered.columns]
    aircraft = filtered.drop_duplicates(subset="icao24")[present].copy()
    aircraft = aircraft.sort_values("icao24")

    if not aircraft.empty:
        w("")
        w("-" * 70)
        w(f"  AIRCRAFT DETAILS ({len(aircraft)} unique)")
        w("-" * 70)
        for _, row in aircraft.iterrows():
            w("")
            w(f"    ICAO24          : {row.get('icao24', 'N/A')}")
            if "registration" in row and pd.notna(row["registration"]):
                w(f"    Registration    : {row['registration']}")
            if "serialnumber" in row and pd.notna(row["serialnumber"]):
                w(f"    Serial Number   : {row['serialnumber']}")
            if "linenumber" in row and pd.notna(row["linenumber"]):
                w(f"    Line Number     : {row['linenumber']}")
            if "owner" in row and pd.notna(row["owner"]):
                w(f"    Owner           : {row['owner']}")
            if "operator" in row and pd.notna(row["operator"]):
                w(f"    Operator        : {row['operator']}")
            if "built" in row and pd.notna(row["built"]):
                w(f"    Built           : {row['built']}")
            if "firstflightdate" in row and pd.notna(row["firstflightdate"]):
                w(f"    First Flight    : {row['firstflightdate']}")

            # Flight count for this aircraft
            count = len(filtered[filtered["icao24"] == row["icao24"]])
            w(f"    Flights (here)  : {count}")

    # ── Flight Log ──
    log_cols = ["callsign", "estDepartureAirport", "estArrivalAirport",
                "registration", "operator"]
    present_log = [c for c in log_cols if c in filtered.columns]
    log = filtered[present_log].copy()

    if "firstSeen" in filtered.columns:
        log.insert(0, "date", pd.to_datetime(filtered["firstSeen"], unit="s").dt.strftime("%Y-%m-%d %H:%M"))
    if "lastSeen" in filtered.columns and "firstSeen" in filtered.columns:
        dur = (filtered["lastSeen"] - filtered["firstSeen"]) / 60
        log["duration_min"] = dur.round(0).astype(int)

    log = log.sort_values("date") if "date" in log.columns else log

    w("")
    w("-" * 70)
    w(f"  FLIGHT LOG ({len(log)} flights)")
    w("-" * 70)
    w("")
    w(log.to_string(index=False))

    w("")
    w("=" * 70)
    w("  END OF REPORT")
    w("=" * 70)

    path.write_text("\n".join(lines), encoding="utf-8")
    return path
