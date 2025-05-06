# airport_status_agent/agent.py

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLLM

AGENT_MODEL = "openai/gpt-4o-mini"  

MOCKED_DELAYS = {
    "CAI": "Delays up to 30 minutes due to congestion.",
    "DXB": "No significant delays reported.",
    "JFK": "Weather-related delays averaging 45 minutes."
}

def get_airport_status(airport_code: str) -> dict:
    airport_code = airport_code.upper()
    delay = MOCKED_DELAYS.get(airport_code)
    if delay:
        return {"status": "success", "report": f"{airport_code}: {delay}"}
    return {"status": "error", "error_message": f"No delay information for {airport_code}."}

root_agent = Agent(
    name="airport_status_agent",
    # model="openai/gpt-4",
    model=LiteLLM(model=AGENT_MODEL),
    description="Provides delay status for a given airport.",
    instruction="Given an airport code like CAI or DXB, return delay or operational info.",
    tools=[get_airport_status],
)
