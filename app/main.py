from fastapi import FastAPI  # noqa: I001
from pydantic import BaseModel

from app.agent.graph import graph
from app.guardrails.engine import GuardrailEngine
from app.guardrails.output.pii import OutputPIIGuard
from app.guardrails.input.blocked_topic import BlockedTopicGuard
from app.guardrails.input.prompt_injection import PromptInjectionGuard
from app.guardrails.input.pii import PIIGuard
from app.guardrails.decisions import GuardrailDecision
from langgraph.types import Command


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
        PIIGuard(),
    ]
)

output_guardrail_engine = GuardrailEngine(
    guardrails=[
        OutputPIIGuard(),
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

    config = {
        "configurable": {
            "thread_id": "demo-request-1",
        }
    }

    result = graph.invoke(
        {
            "messages": [
                ("user", request.message),
            ]
        },
        config=config,
    )

    result = graph.invoke(
        Command(resume="approve"),
        config=config,
    )

    result = graph.invoke(
        Command(resume="reject"),
        config=config,
    )

    response_text = result["messages"][-1].content

    output_result = output_guardrail_engine.check(response_text)

    if output_result.decision == GuardrailDecision.BLOCK:

        return {
            "decision": "block",
            "reason": output_result.reason,
        }

    return {
        "decision": "allow",
        "response": response_text,
    }
