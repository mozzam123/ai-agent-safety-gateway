from fastapi import FastAPI  # noqa: I001
from pydantic import BaseModel

from app.agent.graph import graph
from app.guardrails.engine import GuardrailEngine
from app.guardrails.input.blocked_topic import BlockedTopicGuard
from app.guardrails.input.prompt_injection import PromptInjectionGuard
from app.guardrails.decisions import GuardrailDecision


app = FastAPI(
    title="AI Agent Safety Gateway",
    version="0.1.0",
)


class ChatRequest(BaseModel):
    message: str


input_guardrail_engine = GuardrailEngine(
    guardrails=[
        PromptInjectionGuard(),
        BlockedTopicGuard(),
    ]
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/chat")
async def chat(request: ChatRequest):

    guardrail_result = input_guardrail_engine.check(request.message)

    if guardrail_result.decision == GuardrailDecision.BLOCK:
        return {
            "decision": "block",
            "reason": guardrail_result.reason,
        }

    result = graph.invoke(
        {
            "messages": [
                ("user", request.message),
            ]
        }
    )

    return {
        "decision": "allow",
        "response": result["messages"][-1].content,
    }
