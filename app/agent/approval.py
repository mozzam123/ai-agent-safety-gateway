from enum import Enum


class ApprovalDecision(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
