from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.guardrails.decisions import GuardrailDecision


@dataclass
class GuardrailResult:
    decision: GuardrailDecision
    reason: str


class Guardrail(ABC):
    @abstractmethod
    def check(self, text: str) -> GuardrailResult:
        pass
