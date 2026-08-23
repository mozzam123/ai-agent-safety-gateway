import re

from app.guardrails.base import Guardrail, GuardrailResult
from app.guardrails.decisions import GuardrailDecision


class PIIGuard(Guardrail):
    PATTERNS = {  # noqa: RUF012
        "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "phone": re.compile(r"\b(?:\+91[-\s]?)?[6-9]\d{9}\b"),
        "credit_card": re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
        "aadhaar": re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
    }

    def check(self, text: str) -> GuardrailResult:
        for pii_type, pattern in self.PATTERNS.items():
            if pattern.search(text):
                return GuardrailResult(
                    decision=GuardrailDecision.BLOCK,
                    reason=f"Potential {pii_type} detected.",
                )

        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            reason="No supported PII detected.",
        )
