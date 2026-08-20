"""HR Agentic Solution Orchestrator and Runner."""
import asyncio
import sys
from typing import List, Dict, Any, Tuple

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from . import config
from .prompt import POLICY_AGENT_PROMPT
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from .tools.policy_rag_tool import search_policy_docs

from .guardrails.input_shield import validate_input
from .guardrails.output_shield import redact_spii, screen_toxicity, verify_grounding
from .guardrails.audit_logger import log_transaction

# Instantiate WorkWeek MCP Toolset
workweek_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=config.WORKWEEK_MCP_URL,
        headers={"X-MCP-Token": config.X_MCP_TOKEN}
    )
)

# Instantiate ServiceImmediately MCP Toolset
serviceimmediately_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=config.SERVICEIMMEDIATELY_MCP_URL,
        headers={"X-MCP-Token": config.X_MCP_TOKEN}
    )
)

# Register live toolsets and policy RAG tool
ALL_TOOLS = [
    workweek_mcp,
    serviceimmediately_mcp,
    search_policy_docs
]

# Initialize ADK LlmAgent
root_agent = LlmAgent(
    model=config.GEMINI_MODEL,
    name="hr_agentic_solution",
    description="Automated secure Tier 1 HR policy and self-service transaction assistant.",
    instruction=POLICY_AGENT_PROMPT,
    tools=ALL_TOOLS
)

_session_service = InMemorySessionService()

def _ensure_runner():
    return Runner(app_name=config.APP_NAME, agent=root_agent, session_service=_session_service)


async def _ensure_session_async(user_id: str, session_id: str):
    try:
        await _session_service.create_session(
            app_name=config.APP_NAME, user_id=user_id, session_id=session_id
        )
    except Exception:
        pass  # Already exists


async def run_query_async(query: str, user_id: str = "EMP001", session_id: str = "session-1") -> Tuple[str, str]:
    """Asynchronously runs a query through safety guardrails, execution, and output checks.

    Returns:
        (answer, status_code) where status_code is 'SUCCESS', 'BLOCKED', or 'ERROR'.
    """
    runner = _ensure_runner()
    await _ensure_session_async(user_id, session_id)

    # 1. Input Shield Validation
    input_validation = validate_input(query)
    if not input_validation["is_safe"]:
        reason = input_validation["reason"]
        # Log Blocked request
        log_transaction(
            user_id=user_id,
            session_id=session_id,
            action_type="BLOCKED",
            inputs={"query": query},
            output_summary=reason,
            success=False,
            error_code="SAFETY_BLOCKED"
        )
        return reason, "BLOCKED"

    # Assemble request message
    # Inject user context info as metadata/prompt suffix to let the model know the user ID
    user_context = f"\n\n[System Context: Active User ID is '{user_id}']"
    message = types.Content(role="user", parts=[types.Part(text=query + user_context)])
    
    final_response_text = ""
    evidence = []
    invoked_tools = []
    has_write_action = False

    try:
        # Run agent loop
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=message
        ):
            if not (event.content and event.content.parts):
                continue
            
            for part in event.content.parts:
                # Catch function calls (before execution, or intercept call request)
                fc = getattr(part, "function_call", None)
                if fc is not None:
                    tool_name = fc.name
                    invoked_tools.append(tool_name)
                    if tool_name in ["update_personal_info", "request_time_off", "cancel_leave_request", "create_ticket", "add_ticket_comment", "update_ticket_status"]:
                        has_write_action = True
                
                # Catch function responses (retrieved context)
                fr = getattr(part, "function_response", None)
                if fr is not None:
                    evidence.append({
                        "tool": getattr(fr, "name", "?"),
                        "response": fr.response
                    })
            
            if event.is_final_response() and event.content.parts:
                texts = [p.text for p in event.content.parts if getattr(p, "text", None)]
                if texts:
                    final_response_text = "\n".join(texts)
                    
    except Exception as e:
        error_msg = "An internal processing error occurred. Service temporarily unavailable."
        log_transaction(
            user_id=user_id,
            session_id=session_id,
            action_type="ERROR",
            inputs={"query": query},
            output_summary=error_msg,
            success=False,
            error_code=type(e).__name__
        )
        return error_msg, "ERROR"

    # 2. Output Shield Screening
    # Screen for Toxicity
    if screen_toxicity(final_response_text):
        refusal = "I apologize, but I cannot generate that response as it does not comply with safety guidelines."
        log_transaction(
            user_id=user_id,
            session_id=session_id,
            action_type="BLOCKED",
            inputs={"query": query},
            output_summary="Toxicity detected in response.",
            success=False,
            error_code="TOXICITY_BLOCKED"
        )
        return refusal, "BLOCKED"

    # Screen for Grounding / Hallucination
    retrieved_content_str = "\n".join([str(ev["response"]) for ev in evidence])
    if evidence and not verify_grounding(final_response_text, retrieved_content_str, user_query=query):
        # Suspect grounding failure
        warning_msg = "I couldn't find sufficient verified policy information to complete your request. Please contact HR."
        log_transaction(
            user_id=user_id,
            session_id=session_id,
            action_type="BLOCKED",
            inputs={"query": query},
            output_summary="Grounding verification failed (hallucination suspect).",
            success=False,
            error_code="GROUNDING_FAILED"
        )
        return warning_msg, "BLOCKED"

    # 3. SPII Redaction
    redacted_response = redact_spii(final_response_text)

    # 4. Audit Logging Success Transaction
    action_type = "WRITE" if has_write_action else "READ"
    log_transaction(
        user_id=user_id,
        session_id=session_id,
        action_type=action_type,
        tool_invoked=",".join(invoked_tools) if invoked_tools else None,
        inputs={"query": query},
        output_summary=redacted_response,
        success=True
    )

    return redacted_response, "SUCCESS"


def run_query(query: str, user_id: str = "EMP001", session_id: str = "session-1") -> str:
    """Synchronous entry point for runners and eval harness."""
    answer, _status = asyncio.run(run_query_async(query, user_id=user_id, session_id=session_id))
    return answer


def _interactive():
    print(f"HR Agentic Solution MVP 1 CLI Playground — type 'exit' to quit.")
    # Use default Jane Doe EMP001
    current_user = "EMP001"
    print(f"Active Session Authenticated User: {current_user}")
    while True:
        try:
            q = input("\nyou > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in {"exit", "quit"}:
            break
        if q.startswith("/user "):
            # Allow switching user in interactive CLI for testing RBAC
            parts = q.split()
            if len(parts) > 1:
                current_user = parts[1]
                print(f"Switched user context to: {current_user}")
            continue
        if q:
            ans, status = asyncio.run(run_query_async(q, user_id=current_user))
            print(f"\nagent [{status}] > {ans}")


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if argv and argv[0] == "--interactive":
        _interactive()
    elif argv:
        print(run_query(" ".join(argv)))
    else:
        print('Usage: uv run python -m agent.agent "<question>"  |  --interactive')


if __name__ == "__main__":
    main()

from google.adk.apps import App

app = App(root_agent=root_agent, name="agent")
