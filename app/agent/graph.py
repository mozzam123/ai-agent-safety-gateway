from langchain_core.messages import ToolMessage
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.types import interrupt
from langgraph.checkpoint.memory import InMemorySaver

from app.agent.state import AgentState
from app.agent.tools import calculate, get_weather
from app.guardrails.decisions import GuardrailDecision
from app.guardrails.engine import GuardrailEngine
from app.guardrails.tool.arguments import ToolArgumentGuard
from app.guardrails.tool.authorization import ToolAuthorizationGuard
from app.guardrails.tool.models import ToolRequest
from app.llm.provider import get_llm


# ---------------------------------------------------------
# Tools available to the agent
# ---------------------------------------------------------

tools = [
    calculate,
    get_weather,
]

tools_by_name = {tool.name: tool for tool in tools}


# ---------------------------------------------------------
# LLM
# ---------------------------------------------------------

llm = get_llm().bind_tools(tools)


# ---------------------------------------------------------
# Tool Guardrail Engine
# ---------------------------------------------------------

tool_guardrail_engine = GuardrailEngine(
    guardrails=[
        ToolAuthorizationGuard(),
        ToolArgumentGuard(),
    ]
)


# ---------------------------------------------------------
# Agent node
# ---------------------------------------------------------


def call_model(state: AgentState):
    """Run the LLM and allow it to request tools."""

    response = llm.invoke(state["messages"])

    return {
        "messages": [response],
    }


# ---------------------------------------------------------
# Tool execution node
# ---------------------------------------------------------


def execute_tools(state: AgentState):
    """
    Execute requested tools only after passing
    tool guardrails.
    """

    last_message = state["messages"][-1]

    tool_messages = []

    for tool_call in last_message.tool_calls:

        tool_name = tool_call["name"]
        arguments = tool_call["args"]

        # ---------------------------------------------
        # Create structured tool request
        # ---------------------------------------------

        tool_request = ToolRequest(
            tool_name=tool_name,
            arguments=arguments,
        )

        # ---------------------------------------------
        # Run all tool guardrails
        # ---------------------------------------------

        guardrail_result = tool_guardrail_engine.check(tool_request)

        # ---------------------------------------------
        # BLOCK
        # ---------------------------------------------

        if guardrail_result.decision == GuardrailDecision.BLOCK:

            tool_messages.append(
                ToolMessage(
                    content=guardrail_result.reason,
                    tool_call_id=tool_call["id"],
                )
            )

            continue

        # ---------------------------------------------
        # REQUIRE APPROVAL
        # ---------------------------------------------

        if guardrail_result.decision == GuardrailDecision.REQUIRE_APPROVAL:

            approval = interrupt(
                {
                    "type": "tool_approval",
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "reason": guardrail_result.reason,
                }
            )

            if approval == "reject":

                tool_messages.append(
                    ToolMessage(
                        content="Tool execution rejected by human.",
                        tool_call_id=tool_call["id"],
                    )
                )

                continue

        # ---------------------------------------------
        # ALLOW
        # ---------------------------------------------

        tool = tools_by_name.get(tool_name)

        if tool is None:

            tool_messages.append(
                ToolMessage(
                    content=f"Tool '{tool_name}' is unavailable.",
                    tool_call_id=tool_call["id"],
                )
            )

            continue

        # ---------------------------------------------
        # Execute tool
        # ---------------------------------------------

        result = tool.invoke(arguments)

        tool_messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
            )
        )

    return {
        "messages": tool_messages,
    }


# ---------------------------------------------------------
# Build LangGraph
# ---------------------------------------------------------

builder = StateGraph(AgentState)

builder.add_node(
    "agent",
    call_model,
)

builder.add_node(
    "tools",
    execute_tools,
)

builder.add_edge(
    START,
    "agent",
)

builder.add_conditional_edges(
    "agent",
    tools_condition,
)

builder.add_edge(
    "tools",
    "agent",
)


# ---------------------------------------------------------
# SQLite Checkpointer
# ---------------------------------------------------------

checkpointer = InMemorySaver()


# ---------------------------------------------------------
# Compile graph
# ---------------------------------------------------------

graph = builder.compile(
    checkpointer=checkpointer,
)
