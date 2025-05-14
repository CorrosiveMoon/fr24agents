from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

def say_hello(name: str):
    """
    Greets the user by name.

    Args:
      name (str): user’s name

    Returns:
      dict: {'status':'success','report': greeting string}
    """
    return {"status":"success","report":f"Hello, {name}!"}

greeting_agent = Agent(
    name="greeting_agent",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    description="Handles simple greetings by calling say_hello(name).",
    instruction="If user greets, call say_hello with their name.",
    tools=[say_hello],
)
