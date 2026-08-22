from enum import Enum


class GuardrailDecision(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
