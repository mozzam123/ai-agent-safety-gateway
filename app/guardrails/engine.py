from app.guardrails.base import Guardrail, GuardrailResult
from app.guardrails.decisions import GuardrailDecision


class GuardrailEngine:

    def __init__(self, guardrails: list[Guardrail]):
        self.guardrails = guardrails

    def check(self, value) -> GuardrailResult:
        results: list[GuardrailResult] = []

        for guardrail in self.guardrails:
            result = guardrail.check(value)

            results.append(result)

        # ---------------------------------------------
        # BLOCK has highest priority
        # ---------------------------------------------

        for result in results:
            if result.decision == GuardrailDecision.BLOCK:
                return result

        # ---------------------------------------------
        # REQUIRE_APPROVAL has second priority
        # ---------------------------------------------

        for result in results:
            if result.decision == GuardrailDecision.REQUIRE_APPROVAL:
                return result

        # ---------------------------------------------
        # Everything passed
        # ---------------------------------------------

        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            reason="All guardrails passed.",
        )
