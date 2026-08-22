from app.guardrails.base import Guardrail, GuardrailResult
from app.guardrails.decisions import GuardrailDecision


class BlockedTopicGuard(Guardrail):
    BLOCKED_TOPICS = [  # noqa: RUF012
        "malware",
        "ransomware",
        "credential theft",
    ]

    def check(self, text: str) -> GuardrailResult:
        normalized = text.lower()

        for topic in self.BLOCKED_TOPICS:
            if topic in normalized:
                return GuardrailResult(
                    decision=GuardrailDecision.BLOCK,
                    reason=f"Blocked topic detected: {topic}",
                )

        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            reason="No blocked topic detected.",
        )
