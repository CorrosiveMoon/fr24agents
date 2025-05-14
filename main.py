import os
import asyncio
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, AIMessage, AnyMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, MessagesState, START, END

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.genai import types

from flight_status_agent.flight_agent import flight_agent
from airport_status_agent.airport_agent import airport_agent
from greeting_agent.greeting_agent import greeting_agent
from farewell_agent.farwell_agent import farewell_agent

# environment variables
load_dotenv()  # FR24_API_TOKEN, OPENAI_API_KEY, etc.

# Define and create your ADK root agent and runner here, from google adk examples
root_agent = Agent(
    name="aviation_root",
    model=LiteLlm(model="openai/gpt-4o-mini"),
    description="Coordinator for flights, airports, greetings, farewells.",
    instruction=(
    "You are an AI assistant specialized in aviation: flights, airports, and related details like status, destination, ETA, delays, and coordinates. "
    "You also handle greetings and farewells. "
    "If the user asks something clearly unrelated to aviation, greetings, or farewells, respond with: 'I’m sorry, I can only answer aviation-related questions.' "
    "Otherwise, delegate the request to the correct sub-agent: flight_agent (for anything about flights), airport_agent (for airports), "
    "greeting_agent (for greetings), or farewell_agent (for goodbyes). Follow-up questions like 'Where is it going?' or 'What's the ETA?' should be treated as flight-related."
    ),

    sub_agents=[flight_agent, airport_agent, greeting_agent, farewell_agent],
)
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent,
    app_name="mcp_demo_app",
    session_service=session_service,
)

#initial session for CLI
session_service.create_session(
    app_name="mcp_demo_app",
    user_id="user1",
    session_id="main_session"
)

#adapter node: send last human message into ADK runner and capture the final response
def call_adk(state: MessagesState):
    last_text = state["messages"][-1].content
    content = types.Content(role="user", parts=[types.Part(text=last_text)])

    async def invoke():
        final = None
        async for event in runner.run_async(
            user_id="user1",
            session_id="main_session",
            new_message=content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final = event.content.parts[0].text
                break
        return final or ""

    response_text = asyncio.run(invoke())
    return {"messages": [AIMessage(content=response_text)]}

#LangGraph flow
builder = StateGraph(MessagesState)
builder.add_node("adk_call", call_adk)
builder.add_edge(START, "adk_call")
# Directly end after ADK call
builder.add_edge("adk_call", END)

graph = builder.compile()

def main():
    print("Ask about flights, airports, hello, or bye. Type 'exit' to quit.")
    while True:
        q = input("You: ").strip()
        if q.lower() in {"exit", "quit"}:
            break
        state = {"messages": [HumanMessage(content=q)]}
        result = graph.invoke(state)
        print("\nAI:", result["messages"][-1].content, "\n")


main()
