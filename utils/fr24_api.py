# utils/fr24_api.py

import os
import requests
from datetime import datetime, timezone

API_TOKEN = os.getenv("FR24_API_TOKEN")
BASE_URL = 'https://fr24api.flightradar24.com/api'
FLIGHT_ENDPOINT = '/historic/flight-positions/full'
HEADERS = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {API_TOKEN}',
    'Accept-Version': 'v1'
}

def fetch_flight_status(flight_code: str, bounds="32.0,22.0,24.0,36.0") -> list:
    now = datetime.now(timezone.utc)
    unix_timestamp = int(now.timestamp())
    
    params = {
        'timestamp': unix_timestamp,
        'bounds': bounds
    }

    url = f"{BASE_URL}{FLIGHT_ENDPOINT}"
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    all_data = response.json()

    return [f for f in all_data.get("data", []) if f.get("flight", "").upper() == flight_code.upper()]
