# main.py

from langgraph.graph import StateGraph, END
from langgraph.prebuilt.tool_executor import ToolExecutor
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

from flight_status_agent.agent import root_agent as flight_agent
from airport_status_agent.agent import root_agent as airport_agent

from dotenv import load_dotenv
import os

load_dotenv()

#wrapping agents using the toolexec
flight_tool = ToolExecutor([flight_agent])
airport_tool = ToolExecutor([airport_agent])

#state handler
def route_step(state):
    last_input = state["messages"][-1].content.lower()
    if "flight" in last_input or any(char.isdigit() for char in last_input):
        return "flight_status"
    elif "airport" in last_input or any(code in last_input for code in ["CAI", "DXB", "JFK"]):
        return "airport_status"
    else:
        return "end"

#node functions for langraph
def call_flight_agent(state):
    result = flight_tool.invoke(state["messages"])
    state["messages"].extend(result)
    return state

def call_airport_agent(state):
    result = airport_tool.invoke(state["messages"])
    state["messages"].extend(result)
    return state

#LangGraph flow and adding niodes
builder = StateGraph()
builder.add_node("flight_status", call_flight_agent)
builder.add_node("airport_status", call_airport_agent)

builder.set_entry_point(route_step)
builder.add_conditional_edges(
    route_step,
    {
        "flight_status": "flight_status",
        "airport_status": "airport_status",
        "end": END
    }
)

builder.add_edge("flight_status", END)
builder.add_edge("airport_status", END)

graph = builder.compile()

#testing
print("Ask about a flight or airport (e.g. 'Is MS981 on time?' or 'Any delays at CAI?')\n")

while True:
    query = input("You: ")
    if query.lower() in ["exit", "quit"]:
        break

    state = {
        "messages": [HumanMessage(content=query)]
    }

    result = graph.invoke(state, config=RunnableConfig())
    response = result["messages"][-1]

    print(f"\n AI: {response.content}\n")
