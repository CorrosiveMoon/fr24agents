import os
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLLM
from utils.fr24_api import fetch_flight_status

AGENT_MODEL = "opnenai/gpt-4o-mini"

def get_flight_status(flight_code: str) -> dict:
    try:
        data = fetch_flight_status(flight_code)
        if not data:
            return {"status": "error", "error_message": "Flight not found or no data."}

        flight_info = data[0]
        return {
            "status": "success",
            "report": f"Flight {flight_code.upper()} is {flight_info.get('status', 'unknown')} at {flight_info.get('timestamp', 'N/A')}."
        }
    except Exception as e:
        return {"status": "error", "error_message": str(e)}

root_agent = Agent(
    name="flight_status_agent",
    # model="openai/gpt-4",  
    model = LiteLLM(model=AGENT_MODEL),
    description="Provides flight status for a given flight number.",
    instruction="Given a flight code like MS981, return its current status.",
    tools=[get_flight_status],
)
