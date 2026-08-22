from fastapi import FastAPI
from pydantic import BaseModel

from app.agent.graph import graph

app = FastAPI(
    title="AI Agent Safety Gateway",
    version="0.1.0",
)


class ChatRequest(BaseModel):
    message: str


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/chat")
async def chat(request: ChatRequest):
    result = graph.invoke(
        {
            "messages": [
                ("user", request.message),
            ]
        }
    )

    return {
        "response": result["messages"][-1].content,
    }
