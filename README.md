# AI Agent Safety Gateway

A production-oriented learning project exploring **AI Guardrails and Agent Safety** through hands-on implementation.

The system places a safety gateway between the user and an AI agent, controlling what the agent can **receive, generate, and execute**.

## Architecture

```text
User
  ↓
FastAPI Gateway
  ↓
Input Guardrails
  ↓
LangGraph Agent
  ↓
LLM
  ↓
Tool Request
  ↓
Tool Guardrail Engine
  ├── Authorization
  ├── Arguments
  └── Limits
  ↓
BLOCK / REQUIRE_APPROVAL / ALLOW
  ↓
Tool Execution
  ↓
Output Guardrails
  ↓
User
```

Observability and audit logging span the system, capturing key security events without exposing sensitive data.

## Objectives

This project explores: input/output validation, tool-level authorization, prompt injection & jailbreak protection, PII detection, human-in-the-loop approval, least privilege, fail-open vs. fail-closed handling, deterministic vs. LLM-based guardrails, and observability.

## Guardrail Types

- **Input Guardrails** — detect prompt injection, jailbreaks, prohibited topics, and PII before requests reach the agent.
- **Tool Guardrails** — enforce tool authorization, argument validation, and approval requirements before execution (e.g., `calculate → ALLOW`, `delete_file → REQUIRE_APPROVAL`, `execute_shell → BLOCK`).
- **Output Guardrails** — filter/redact sensitive or unsafe content before it reaches the user.

## Decision Model

Three decisions — **ALLOW**, **BLOCK**, **REQUIRE_APPROVAL** — are combined via a "most restrictive wins" policy, ensuring a security violation from one guardrail can't be overridden by a more permissive one.

A shared `GuardrailEngine` runs multiple checks (authorization, arguments, PII, policy) and returns a single decision, keeping the agent decoupled from individual guardrail implementations.

## Failure Handling

| Failure Type | Behavior |
|---|---|
| Guardrail failure | Fail-closed → BLOCK |
| LLM failure | Safe error response |
| Tool failure | Safe error message |
| Approval rejected/expired | STOP |

Security-critical failures default to restrictive behavior; infrastructure failures degrade gracefully.

## Human-in-the-Loop

Sensitive actions (e.g., file deletion) require explicit human approval, with a 5-minute expiration window — an expired approval can never authorize execution.

## Key Principles

1. **LLMs are not security boundaries** — the model can request an action; the application decides if it's permitted.
2. **Guardrails belong at boundaries** — input, tool request, and output are each independently validated.
3. **Fail closed** on uncertainty.
4. **Least privilege** — agents get only the permissions their task requires.
5. **Deterministic checks first** — reserve LLM-based guardrails for genuinely semantic decisions (e.g., jailbreak detection).
6. **Human approval is a security boundary**, not a formality.
7. **Observability must respect privacy** — logs capture decisions and metadata, never prompts, PII, or secrets.

## Tech Stack

Python · FastAPI · LangGraph · LangChain · Ollama (Qwen 3 8B, local) · Pydantic · SQLite

Runs entirely locally with no paid APIs or cloud dependencies — ideal for experimenting with agent safety architecture at no cost.

## Project Structure

```text
ai-agent-safety-gateway/
│
├── app/
│   ├── agent/
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── tools.py
│   │   └── approval.py
│   │
│   ├── guardrails/
│   │   ├── engine.py
│   │   ├── decisions.py
│   │   └── tool/
│   │       ├── authorization.py
│   │       └── arguments.py
│   │
│   ├── core/
│   │   └── logging.py
│   │
│   ├── llm/
│   │   └── provider.py
│   │
│   └── main.py
│
├── requirements.txt
├── checkpoints.db
└── README.md
```


## Security Model

The agent can **request** actions (untrusted intent); the safety gateway **authorizes** them (trusted decision) before they reach any tool. In short: *the agent decides what it wants to do — the gateway decides what it's allowed to do.*

## Future Production Improvements

RBAC, centralized policy management, Redis-based rate limiting, persistent approval store with correlation IDs, distributed tracing, advanced PII/prompt-injection detection, tool sandboxing, and evaluation against frameworks like NVIDIA NeMo Guardrails or OpenAI Guardrails.
