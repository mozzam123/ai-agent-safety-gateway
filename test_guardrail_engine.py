from app.guardrails.tool.authorization import ToolAuthorizationGuard
from app.guardrails.tool.arguments import ToolArgumentGuard
from app.guardrails.tool.models import ToolRequest


request = ToolRequest(tool_name="delete_file", arguments={"path": ""})

authorization_guard = ToolAuthorizationGuard()
argument_guard = ToolArgumentGuard()

authorization_result = authorization_guard.check(request)
argument_result = argument_guard.check(request)

print("Authorization:")
print(authorization_result.decision)
print(authorization_result.reason)

print("\nArguments:")
print(argument_result.decision)
print(argument_result.reason)
