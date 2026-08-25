from typing import TypedDict

from langchain_core.messages import BaseMessage


class PendingApproval(TypedDict):
    tool_name: str
    arguments: dict
    tool_call_id: str
    created_at: float


class AgentState(TypedDict):
    messages: list[BaseMessage]
    pending_approval: PendingApproval | None
