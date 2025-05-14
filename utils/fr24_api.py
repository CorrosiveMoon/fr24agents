import os
import requests
from datetime import datetime, timezone, timedelta, date
import json

# API_TOKEN = os.getenv("FR24_API_TOKEN") or "<YOUR_TOKEN_HERE>"
API_TOKEN = "api key here"
BASE_URL  = "https://fr24api.flightradar24.com/api"

# Global bounding box so we see flights everywhere
# GLOBAL_BOUNDS = "-90.0,90.0,-180.0,180.0"
# EGYPT_AIRSPACE = "32.0,22.0,24.0,36.0"  # Egypt region (lat_max, lat_min, lon_min, lon_max)
NA_EM_BOUNDS = "40.0,10.0,15.0,45.0"  # North Africa + Eastern Mediterranean
LIVE_FLIGHT_POSITIONS = "/live/flight-positions/full"
FLIGHT_SUMMARY_FULL    = "/flight-summary/full"
AIRPORT_FULL_TEMPLATE  = "/static/airports/{code}/full"

HEADERS = {
    "Accept": "application/json",
    "Accept-Version": "v1",
    "Authorization": f"Bearer {API_TOKEN}",
}

def get_json(path: str, params: dict | None = None):
    if not API_TOKEN:
        raise RuntimeError("FR24_API_TOKEN not set")
    url = f"{BASE_URL}{path}"
    resp = requests.get(url, headers=HEADERS, params=params or {})
    resp.raise_for_status()
    return resp.json()

def fetch_flight_status(flight_code: str):
    """
    returns the most recent matching flight record (dict) or None.
    Supports direct list return from FR24 and handles null values.
    """
    params = {
        "bounds": NA_EM_BOUNDS
    }
    payload = get_json(LIVE_FLIGHT_POSITIONS, params)
    target = flight_code.strip().upper()

    # Handle data structure
    records = []
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        records = payload["data"]
    elif isinstance(payload, list):
        records = payload

    matches = [
        r for r in records
        if ((r.get("callsign") or "").strip().upper() == target or
            (r.get("flight") or "").strip().upper() == target)
    ]

    return max(matches, key=lambda r: r.get("timestamp", "")) if matches else None



def fetch_flight_summary(flight_code: str, window_hours: int = 24):
    """
    returns the first summary record (dict) over the last window, or None.
    """
    now = datetime.now(timezone.utc)
    dt_to   = now.strftime("%Y-%m-%dT%H:%M:%S")
    dt_from = (now - timedelta(hours=window_hours)).strftime("%Y-%m-%dT%H:%M:%S")
    params = {
        "flights": flight_code.upper(),
        "flight_datetime_from": dt_from,
        "flight_datetime_to":   dt_to
    }
    payload = get_json(FLIGHT_SUMMARY_FULL, params)
    recs = payload.get("data", [])
    return recs[0] if recs else None


def fetch_airport_info(airport_code: str):
    """
    returns the static/full airport info record (dict) or None.
    """
    code = airport_code.strip().upper()
    path = AIRPORT_FULL_TEMPLATE.format(code=code)
    data = get_json(path)
    return data.get("data", data)
