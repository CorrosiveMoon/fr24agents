from langchain_core.tools import tool
from utils.fr24_api import fetch_airport_info

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from utils.fr24_api import fetch_airport_info


MOCKED_DELAYS = {
    "ATL": "Delays up to 25 minutes due to runway congestion.",
    "PEK": "Delays up to 15 minutes due to air traffic.",
    "LAX": "Delays up to 30 minutes due to weather.",
    "DXB": "No significant delays reported.",
    "HND": "Delays up to 10 minutes due to security checks.",
    "ORD": "Delays up to 20 minutes due to staffing shortages.",
    "LHR": "Delays up to 35 minutes due to runway maintenance.",
    "PVG": "Delays up to 40 minutes due to air traffic.",
    "CDG": "Delays up to 15 minutes due to weather.",
    "DFW": "No significant delays reported.",
    "CAN": "Delays up to 20 minutes due to congestion.",
    "JFK": "Delays up to 45 minutes due to weather.",
    "SIN": "No significant delays reported.",
    "DEN": "Delays up to 10 minutes due to snow.",
    "ICN": "Delays up to 25 minutes due to air traffic.",
    "AMS": "Delays up to 30 minutes due to maintenance.",
    "FRA": "No significant delays reported.",
    "DEL": "Delays up to 50 minutes due to fog.",
    "BKK": "Delays up to 20 minutes due to runway congestion.",
    "SHA": "Delays up to 15 minutes due to air traffic.",
    "CGK": "Delays up to 40 minutes due to weather.",
    "HKG": "Delays up to 10 minutes due to security.",
    "MAD": "No significant delays reported.",
    "BCN": "Delays up to 20 minutes due to air traffic.",
    "SFO": "Delays up to 30 minutes due to runway maintenance.",
    "LAS": "No significant delays reported.",
    "PHX": "Delays up to 15 minutes due to staffing.",
    "MIA": "Delays up to 25 minutes due to weather.",
    "SEA": "Delays up to 10 minutes due to congestion.",
    "MCO": "No significant delays reported.",
    "CLT": "Delays up to 20 minutes due to security.",
    "EWR": "Delays up to 30 minutes due to air traffic.",
    "MSP": "No significant delays reported.",
    "MUC": "Delays up to 15 minutes due to weather.",
    "EZE": "Delays up to 25 minutes due to staffing.",
    "GRU": "Delays up to 40 minutes due to runway maintenance.",
    "GIG": "No significant delays reported.",
    "YVR": "Delays up to 20 minutes due to weather.",
    "YYZ": "Delays up to 30 minutes due to air traffic.",
    "CPH": "No significant delays reported.",
    "ZRH": "Delays up to 10 minutes due to security.",
    "IST": "Delays up to 25 minutes due to congestion.",
    "DOH": "No significant delays reported.",
    "KUL": "Delays up to 20 minutes due to weather.",
    "MEL": "Delays up to 15 minutes due to runway maintenance.",
    "SYD": "No significant delays reported.",
    "AKL": "Delays up to 30 minutes due to air traffic.",
    "CPT": "Delays up to 20 minutes due to security.",
    "JNB": "No significant delays reported.",
    "TLV": "Delays up to 10 minutes due to staffing."
}


AGENT_MODEL = LiteLlm(model="openai/gpt-4o-mini")

def airport_info_tool(code: str):
    """
    Fetches full airport info from FR24.

    Args:
      code (str): IATA like 'CAI'

    Returns:
      dict: {status: 'success'/'error', report: str}
    """
    info = fetch_airport_info(code)
    if not info or not info.get("name"):
        return {"status":"error","report":f"No data for {code}"}
    tz = info.get("timezone", {})
    off = int(tz.get("offset",0)/3600)
    delay = MOCKED_DELAYS.get(code.upper(), "No delay info.")
    rpt = (
      f"{info['iata']}/{info['icao']}: {info['name']}\n"
      f"Loc {info['lat']},{info['lon']} @ {info['elevation']}ft\n"
      f"{info['city']}, {info['country']['name']} ({info['country']['code']})\n"
      f"TZ: {tz['name']} (UTC{off:+d})\n"
      f"Delay: {delay}"
    )
    return {"status":"success","report":rpt}

airport_agent = Agent(
    name="airport_agent",
    model=AGENT_MODEL,
    description="Provides full airport info and current (mocked) delays.",
    instruction=(
      "When asked about airport delays or status, call airport_info_tool "
      "and return the report."
    ),
    tools=[airport_info_tool],
)
