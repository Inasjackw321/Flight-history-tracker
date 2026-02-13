# Flight History Tracker - Data Requirements

## Overview
This application tracks flight history by airport and allows filtering by airframe (aircraft type). It uses data from the last 60 days and caches locally for fast loading.

## Data Sources

### Primary: OpenSky Network API (Free, No Auth Required)
- **API Base URL:** `https://opensky-network.org/api`
- **Endpoints Used:**
  - `/flights/arrival?airport={ICAO}&begin={unix_ts}&end={unix_ts}` — arrivals at an airport
  - `/flights/departure?airport={ICAO}&begin={unix_ts}&end={unix_ts}` — departures from an airport
- **Rate Limits:** Anonymous: 100 requests/day, 1 request every 10 seconds. The app batches requests in 7-day windows (max allowed per request) to cover 60 days.
- **Note:** OpenSky limits query windows to 7 days per request, so 60 days requires ~9 requests per direction (arrivals + departures).

### Aircraft Metadata: Local CSV Database
- **Source:** Bundled `data/aircraftDatabase.csv` (derived from OpenSky aircraft database dump)
- **Download URL:** `https://opensky-network.org/datasets/metadata/aircraftDatabase.csv`
- **Fields Used:** `icao24`, `manufacturerName`, `model`, `typecode`, `operator`

## Data Fields

### Flight Record (from API)
| Field            | Type   | Description                          |
|------------------|--------|--------------------------------------|
| `icao24`         | string | Unique ICAO 24-bit transponder address |
| `callsign`       | string | Flight callsign (e.g., "UAL123")     |
| `firstSeen`      | int    | Unix timestamp of first radar contact |
| `lastSeen`       | int    | Unix timestamp of last radar contact  |
| `estDepartureAirport` | string | ICAO code of departure airport   |
| `estArrivalAirport`   | string | ICAO code of arrival airport     |

### Aircraft Metadata (from CSV)
| Field              | Type   | Description                        |
|--------------------|--------|------------------------------------|
| `icao24`           | string | Transponder address (join key)     |
| `manufacturerName` | string | e.g., "Boeing", "Airbus"          |
| `model`            | string | e.g., "737-800", "A320-214"       |
| `typecode`         | string | ICAO type designator (e.g., "B738") |
| `operator`         | string | Airline operator name              |

## Caching Strategy (for fast loading)
- **Cache Location:** `~/.flight_tracker_cache/`
- **Format:** JSON files per airport, named `{ICAO}_flights.json`
- **TTL:** 6 hours — data is re-fetched only if cache is older than 6 hours
- **Startup:** Reading cached JSON is near-instant (<100ms for typical airports)

## Airport Codes
- The app accepts **ICAO codes** (4-letter, e.g., `KJFK`, `EGLL`, `KLAX`)
- A bundled lookup table (`data/airports.csv`) maps common IATA codes (3-letter, e.g., `JFK`) to ICAO codes for convenience
- Airport data source: OurAirports (public domain) — `https://davidmegginson.github.io/ourairports-data/airports.csv`

## System Requirements
- Python 3.8+
- Internet connection (for initial data fetch only; cached data works offline)
- ~50MB disk for aircraft database CSV
- Dependencies: `requests`, `pandas`
