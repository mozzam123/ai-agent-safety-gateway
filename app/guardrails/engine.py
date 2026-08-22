from app.guardrails.base import Guardrail, GuardrailResult
from app.guardrails.decisions import GuardrailDecision


class GuardrailEngine:
    def __init__(self, guardrails: list[Guardrail]):
        self.guardrails = guardrails

    def check(self, text: str) -> GuardrailResult:

        for guardrail in self.guardrails:
            result = guardrail.check(text)

            if result.decision == GuardrailDecision.BLOCK:
                return result

        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            reason="All guardrails passed.",
        )
