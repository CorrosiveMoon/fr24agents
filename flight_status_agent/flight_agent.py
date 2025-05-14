from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from utils.fr24_api import fetch_flight_status, fetch_flight_summary

AGENT_MODEL = LiteLlm(model="openai/gpt-4o-mini")

def flight_summary_tool(flight_code: str):
    """
    Tries to fetch summary using the given flight code. If that fails,
    resolves it via live status to get correct callsign or flight.
    """
    s = fetch_flight_summary(flight_code)
    if not s:
        #resolving correct flight code from live status
        #was added to handle cases where flight code is not in summary abd debug
        resolved = fetch_flight_status(flight_code)
        if not resolved:
            return {"status": "error", "report": f"No summary or live info for {flight_code.upper()}"}
        fallback_code = (resolved.get("callsign") or resolved.get("flight") or "").upper()
        if fallback_code and fallback_code != flight_code.upper():
            s = fetch_flight_summary(fallback_code)

    if not s:
        return {"status": "error", "report": f"No summary for {flight_code.upper()}"}

    rpt = (
        f"Flight {s['flight']} ({s['callsign']})\n"
        f"Route: {s['orig_iata']} → {s['dest_iata']}\n"
        f"Takeoff: {s['datetime_takeoff']} (RWY{s.get('runway_takeoff', '?')})\n"
        f"Landed: {s.get('datetime_landed', 'In air')} (RWY{s.get('runway_landed', 'N/A')})\n"
        f"Time: {s.get('flight_time', '?')}s, Dist: {s.get('actual_distance', '?')} km"
    )
    return {"status": "success", "report": rpt}


def flight_status_tool(flight_code: str):
    """
    fetches the latest live position for a flight, including origin, destination, and ETA.
    """
    rec = fetch_flight_status(flight_code)
    if not rec:
        return {"status": "error", "report": f"No live data for {flight_code.upper()}"}

    rpt = (
        f"Live status for {rec.get('callsign', '?')}:\n"
        f"- Position: {rec.get('lat', '?'):.4f}, {rec.get('lon', '?'):.4f}\n"
        f"- Altitude: {rec.get('alt', '?')} ft\n"
        f"- From: {rec.get('orig_iata', 'N/A')} → To: {rec.get('dest_iata', 'N/A')}\n"
        f"- ETA: {rec.get('eta', 'Unknown')}\n"
        f"- Timestamp: {rec.get('timestamp', '?')}"
    )
    return {"status": "success", "report": rpt}


flight_agent = Agent(
    name="flight_agent",
    model=AGENT_MODEL,
    description="Handles flight‐summary and live‐status queries for a single flight.",
    instruction=(
    "When asked about a flight code (e.g. 'EK784'), or related questions like:"
    " status, summary, destination, origin, ETA, route, whether it's landed or live, "
    "you should call either flight_summary_tool or flight_status_tool depending on the context. "
    "Also respond to follow-up questions like 'Where is it now?' or 'Has it landed?'. "
    "Return the tool.output['report'] as your answer."
  ),

    tools=[flight_summary_tool, flight_status_tool],
)

