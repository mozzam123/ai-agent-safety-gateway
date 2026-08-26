from app.guardrails.base import Guardrail, GuardrailResult
from app.guardrails.decisions import GuardrailDecision
from app.core.logging import get_logger

logger = get_logger(__name__)


class GuardrailEngine:

    def __init__(self, guardrails: list[Guardrail]):
        self.guardrails = guardrails

    def check(self, value) -> GuardrailResult:
        results: list[GuardrailResult] = []

        for guardrail in self.guardrails:

            try:
                result = guardrail.check(value)
                logger.info(
                    "guardrail=%s decision=%s",
                    guardrail.__class__.__name__,
                    result.decision,
                )

            except Exception:
                return GuardrailResult(
                    decision=GuardrailDecision.BLOCK,
                    reason="Guardrail execution failed.",
                )

            results.append(result)

        # BLOCK has highest priority
        for result in results:
            if result.decision == GuardrailDecision.BLOCK:
                return result

        # REQUIRE_APPROVAL has second priority
        for result in results:
            if result.decision == GuardrailDecision.REQUIRE_APPROVAL:
                return result

        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            reason="All guardrails passed.",
        )
