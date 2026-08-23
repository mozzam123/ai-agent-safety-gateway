import re

from app.guardrails.base import Guardrail, GuardrailResult
from app.guardrails.decisions import GuardrailDecision


class OutputPIIGuard(Guardrail):

    PATTERNS = {  # noqa: RUF012
        "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "phone": re.compile(r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b"),
        "credit_card": re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    }

    def check(self, text: str) -> GuardrailResult:
        transformed_text = text
        detected = False

        for pattern in self.PATTERNS.values():
            if pattern.search(transformed_text):
                detected = True
                transformed_text = pattern.sub(
                    "[REDACTED]",
                    transformed_text,
                )

        if detected:
            return GuardrailResult(
                decision=GuardrailDecision.ALLOW,
                reason="PII detected and redacted.",
                transformed_text=transformed_text,
            )

        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            reason="No supported PII detected.",
        )
