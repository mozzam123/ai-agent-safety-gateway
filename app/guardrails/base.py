from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.guardrails.decisions import GuardrailDecision


@dataclass
class GuardrailResult:
    decision: GuardrailDecision
    reason: str
    transformed_text: str | None = None


class Guardrail(ABC):

    @abstractmethod
    def check(self, value: Any) -> GuardrailResult:
        pass
