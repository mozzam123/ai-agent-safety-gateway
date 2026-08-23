from pydantic import BaseModel


class ToolRequest(BaseModel):
    tool_name: str
    arguments: dict
