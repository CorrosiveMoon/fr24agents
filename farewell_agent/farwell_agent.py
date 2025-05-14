from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

def say_goodbye() -> dict:
    """Returns a friendly goodbye."""
    return {"status":"success","report":"Goodbye! Have a great day."}

farewell_agent = Agent(
    name="farewell_agent",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    description="Handles simple farewells by calling say_goodbye().",
    instruction="If user says bye/thanks, call say_goodbye.",
    tools=[say_goodbye],
)
