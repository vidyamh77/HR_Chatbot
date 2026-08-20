"""HR Agentic Solution Orchestrator and Runner (Hub-and-Spoke Architecture)."""
import asyncio
import sys
from typing import List, Dict, Any, Tuple

from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.base_tool import ToolContext
from google.genai import types

from . import config
from .prompt import (
    HUB_AGENT_PROMPT,
    WORKWEEK_AGENT_PROMPT,
    SERVICEIMMEDIATELY_AGENT_PROMPT,
    POLICY_AGENT_PROMPT
)
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from .tools.policy_rag_tool import search_policy_docs

from .guardrails.input_shield import validate_input
from .guardrails.output_shield import redact_spii, screen_toxicity, verify_grounding
from .guardrails.audit_logger import log_transaction

# 1. Instantiate Spoke MCP and RAG Toolsets
workweek_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=config.WORKWEEK_MCP_URL,
        headers={"X-MCP-Token": config.X_MCP_TOKEN}
    )
)

serviceimmediately_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=config.SERVICEIMMEDIATELY_MCP_URL,
        headers={"X-MCP-Token": config.X_MCP_TOKEN}
    )
)

# 2. Define Spoke Agents (Each has its own dedicated tools)
workweek_agent = LlmAgent(
    model=config.GEMINI_MODEL,
    name="workweek_agent",
    description="Handles employee profiles, leave balances, contact updates, and leave requests.",
    instruction=WORKWEEK_AGENT_PROMPT,
    tools=[workweek_mcp]
)

serviceimmediately_agent = LlmAgent(
    model=config.GEMINI_MODEL,
    name="serviceimmediately_agent",
    description="Handles support tickets and lifecycle operations in ServiceImmediately.",
    instruction=SERVICEIMMEDIATELY_AGENT_PROMPT,
    tools=[serviceimmediately_mcp]
)

policy_agent = LlmAgent(
    model=config.GEMINI_MODEL,
    name="policy_agent",
    description="Answers policy questions using retrieved HR guidelines.",
    instruction=POLICY_AGENT_PROMPT,
    tools=[search_policy_docs]
)

# 3. Define Hub Routing Tools (Allows Hub Agent to delegate to Spoke Agents)
async def query_workweek_agent(query: str, tool_context: ToolContext) -> str:
    """Delegates a query to the WorkWeek Agent to check balances, profiles, or requests.
    
    Args:
        query: The request/instruction for the WorkWeek agent.
    """
    return await tool_context.run_node(workweek_agent, query)

async def query_serviceimmediately_agent(query: str, tool_context: ToolContext) -> str:
    """Delegates a query to the ServiceImmediately Agent to create, comment, or check tickets.
    
    Args:
        query: The request/instruction for the ServiceImmediately agent.
    """
    return await tool_context.run_node(serviceimmediately_agent, query)

async def query_policy_agent(query: str, tool_context: ToolContext) -> str:
    """Delegates a query to the Policy Agent to search and answer company policy rules.
    
    Args:
        query: The policy question.
    """
    return await tool_context.run_node(policy_agent, query)

# 4. Initialize Hub Agent (Root Agent)
root_agent = LlmAgent(
    model=config.GEMINI_MODEL,
    name="hr_agent_hub",
    description="Automated secure Tier 1 HR assistant hub.",
    instruction=HUB_AGENT_PROMPT,
    tools=[
        query_workweek_agent,
        query_serviceimmediately_agent,
        query_policy_agent
    ]
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

    try:
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=message):
            if not (event.content and event.content.parts):
                continue
            
            # Extract tool invocation names and outputs
            for part in event.content.parts:
                fr = getattr(part, "function_response", None)
                if fr is not None:
                    tool_name = getattr(fr, "name", "?")
                    invoked_tools.append(tool_name)
                    evidence.append({"tool": tool_name, "payload": fr.response})

            if event.is_final_response() and event.content.parts:
                texts = [p.text for p in event.content.parts if getattr(p, "text", None)]
                if texts:
                    final_response_text = "\n".join(texts)

        # 2. Output Guardrails Check
        # Redact SPII
        cleaned_response = redact_spii(final_response_text)
        
        # Screen toxicity
        is_toxic = screen_toxicity(cleaned_response)
        if is_toxic:
            log_transaction(
                user_id=user_id,
                session_id=session_id,
                action_type="BLOCKED",
                inputs={"query": query},
                output_summary="Blocked by toxicity output filter",
                success=False,
                error_code="TOXICITY_BLOCKED"
            )
            return "Response blocked by output safety rules.", "BLOCKED"

        # Verify Grounding (using evidence from RAG/MCP calls)
        evidence_text = "\n".join([str(e.get("payload", "")) for e in evidence])
        is_grounded = verify_grounding(cleaned_response, evidence_text, query)
        if not is_grounded:
            log_transaction(
                user_id=user_id,
                session_id=session_id,
                action_type="BLOCKED",
                inputs={"query": query},
                output_summary="Blocked due to hallucination/grounding failure",
                success=False,
                error_code="UNGROUNDED_RESPONSE"
            )
            return "Response blocked due to grounding verification failure.", "BLOCKED"

        # Log successful transaction
        log_transaction(
            user_id=user_id,
            session_id=session_id,
            action_type="WRITE" if ("request" in query.lower() or "update" in query.lower() or "create" in query.lower()) else "READ",
            inputs={"query": query},
            output_summary=cleaned_response,
            success=True,
            tool_invoked=",".join(invoked_tools)
        )
        return cleaned_response, "SUCCESS"

    except Exception as e:
        import traceback
        import sys
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        logger_err = f"Agent execution crash: {e}"
        log_transaction(
            user_id=user_id,
            session_id=session_id,
            action_type="ERROR",
            inputs={"query": query},
            output_summary=logger_err,
            success=False,
            error_code="CRASH"
        )
        return "An internal server error occurred while processing your request.", "ERROR"


def run_query(query: str, user_id: str = "EMP001", session_id: str = "session-1") -> str:
    """Synchronous wrapper for run_query_async."""
    answer, _ = asyncio.run(run_query_async(query, user_id, session_id))
    return answer


if __name__ == "__main__":
    # Interactive CLI runner
    import sys
    if len(sys.argv) > 1:
        query_arg = " ".join(sys.argv[1:])
        print(run_query(query_arg))
    else:
        print("Usage: uv run python -m agent.agent <query>")
