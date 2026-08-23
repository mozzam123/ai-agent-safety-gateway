from app.guardrails.base import Guardrail, GuardrailResult
from app.guardrails.decisions import GuardrailDecision
from app.guardrails.tool.models import ToolRequest
from app.policies.policies import TOOL_POLICIES


class ToolAuthorizationGuard(Guardrail):

    def check(self, value: ToolRequest) -> GuardrailResult:
        decision = TOOL_POLICIES.get(value.tool_name)

        if decision is None:
            return GuardrailResult(
                decision=GuardrailDecision.BLOCK,
                reason=f"Tool '{value.tool_name}' is not authorized.",
            )

        return GuardrailResult(
            decision=decision,
            reason=f"Tool '{value.tool_name}' policy: {decision.value}.",
        )
