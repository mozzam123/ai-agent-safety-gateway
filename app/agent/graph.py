from langchain_core.messages import ToolMessage
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.types import interrupt

from app.agent.state import AgentState
from app.agent.tools import calculate, get_weather
from app.guardrails.decisions import GuardrailDecision
from app.guardrails.tool.arguments import ToolArgumentGuard
from app.guardrails.tool.authorization import ToolAuthorizationGuard
from app.guardrails.tool.models import ToolRequest
from app.llm.provider import get_llm

# Tools available to the agent.
tools = [
    calculate,
    get_weather,
]

# Fast lookup from tool name -> tool implementation.
tools_by_name = {tool.name: tool for tool in tools}


# LLM with tool-calling capability.
llm = get_llm().bind_tools(tools)


# Tool guardrails.
tool_authorization_guard = ToolAuthorizationGuard()
tool_argument_guard = ToolArgumentGuard()


def call_model(state: AgentState):
    """Run the LLM and allow it to request tools."""

    response = llm.invoke(state["messages"])

    return {
        "messages": [response],
    }


def execute_tools(state: AgentState):
    """
    Execute requested tools only after passing tool guardrails.
    """

    last_message = state["messages"][-1]

    tool_messages = []

    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        arguments = tool_call["args"]

        # Represent the tool request as structured data.
        tool_request = ToolRequest(
            tool_name=tool_name,
            arguments=arguments,
        )

        # -------------------------------------------------
        # 1. Authorization check
        # -------------------------------------------------

        authorization_result = tool_authorization_guard.check(tool_request)

        if authorization_result.decision == GuardrailDecision.BLOCK:
            tool_messages.append(
                ToolMessage(
                    content=authorization_result.reason,
                    tool_call_id=tool_call["id"],
                )
            )
            continue

        if authorization_result.decision == GuardrailDecision.REQUIRE_APPROVAL:

            approval = interrupt(
                {
                    "type": "tool_approval",
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "reason": authorization_result.reason,
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

        # -------------------------------------------------
        # 2. Argument validation
        # -------------------------------------------------

        argument_result = tool_argument_guard.check(tool_request)

        if argument_result.decision == GuardrailDecision.BLOCK:
            tool_messages.append(
                ToolMessage(
                    content=argument_result.reason,
                    tool_call_id=tool_call["id"],
                )
            )
            continue

        # -------------------------------------------------
        # 3. Find the actual tool
        # -------------------------------------------------

        tool = tools_by_name.get(tool_name)

        if tool is None:
            tool_messages.append(
                ToolMessage(
                    content=f"Tool '{tool_name}' is unavailable.",
                    tool_call_id=tool_call["id"],
                )
            )
            continue

        # -------------------------------------------------
        # 4. Execute the tool
        # -------------------------------------------------

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

builder.add_node("agent", call_model)

builder.add_node("tools", execute_tools)

builder.add_edge(START, "agent")

builder.add_conditional_edges(
    "agent",
    tools_condition,
)

builder.add_edge("tools", "agent")

graph = builder.compile()
