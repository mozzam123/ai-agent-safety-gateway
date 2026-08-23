from app.guardrails.base import Guardrail, GuardrailResult
from app.guardrails.decisions import GuardrailDecision
from app.guardrails.tool.models import ToolRequest


class ToolArgumentGuard(Guardrail):

    def check(self, value: ToolRequest) -> GuardrailResult:

        if value.tool_name == "get_weather":
            city = value.arguments.get("city")

            if not isinstance(city, str) or not city.strip():
                return GuardrailResult(
                    decision=GuardrailDecision.BLOCK,
                    reason="Weather tool requires a valid city.",
                )

            if len(city) > 100:
                return GuardrailResult(
                    decision=GuardrailDecision.BLOCK,
                    reason="City name is too long.",
                )

        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            reason="Tool arguments are valid.",
        )
