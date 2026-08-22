from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.agent.state import AgentState
from app.agent.tools import calculate, get_weather
from app.llm.provider import get_llm

tools = [calculate, get_weather]

llm = get_llm().bind_tools(tools)


def call_model(state: AgentState):
    response = llm.invoke(state["messages"])

    return {
        "messages": [response],
    }


builder = StateGraph(AgentState)

builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")

builder.add_conditional_edges(
    "agent",
    tools_condition,
)

builder.add_edge("tools", "agent")

graph = builder.compile()
