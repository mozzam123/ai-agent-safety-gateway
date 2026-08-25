import time
from enum import Enum


class ApprovalDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"


APPROVAL_TIMEOUT_SECONDS = 300


def is_approval_expired(created_at: float) -> bool:
    return time.time() - created_at > APPROVAL_TIMEOUT_SECONDS
