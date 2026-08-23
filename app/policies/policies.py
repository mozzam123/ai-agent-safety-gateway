from app.guardrails.decisions import GuardrailDecision

TOOL_POLICIES = {
    "calculate": GuardrailDecision.ALLOW,
    "get_weather": GuardrailDecision.ALLOW,
    "delete_file": GuardrailDecision.REQUIRE_APPROVAL,
    "execute_shell": GuardrailDecision.BLOCK,
}
