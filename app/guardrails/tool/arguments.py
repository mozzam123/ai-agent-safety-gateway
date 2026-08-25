from app.guardrails.base import Guardrail, GuardrailResult
from app.guardrails.decisions import GuardrailDecision
from app.guardrails.tool.models import ToolRequest


class ToolArgumentGuard(Guardrail):

    def check(self, value: ToolRequest) -> GuardrailResult:

        # delete_file validation
        if value.tool_name == "delete_file":

            path = value.arguments.get("path")

            if not isinstance(path, str) or not path.strip():
                return GuardrailResult(
                    decision=GuardrailDecision.BLOCK,
                    reason="delete_file requires a valid file path.",
                )

        return GuardrailResult(
            decision=GuardrailDecision.ALLOW,
            reason="Tool arguments are valid.",
        )
