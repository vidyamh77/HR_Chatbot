"""HR Agentic Solution Orchestrator and Runner (Hub-and-Spoke Architecture)."""
import asyncio
import sys
from typing import List, Dict, Any, Tuple, Optional

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

# 1. Define dynamic header provider for tenant isolation
def mcp_header_provider(readonly_context) -> dict[str, str]:
    token = readonly_context.state.get("x_mcp_token")
    if not token:
        token = config.X_MCP_TOKEN
    return {"X-MCP-Token": token}

# Instantiate Spoke MCP and RAG Toolsets
workweek_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=config.WORKWEEK_MCP_URL,
    ),
    header_provider=mcp_header_provider
)

serviceimmediately_mcp = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=config.SERVICEIMMEDIATELY_MCP_URL,
    ),
    header_provider=mcp_header_provider
)

names_map = {
    "luke wilson": "EMP-004",
    "luke": "EMP-004",
    "john smith": "EMP-001",
    "john": "EMP-001",
    "suman banerjee": "EMP-361",
    "suman": "EMP-361",
    "vivek anurag": "EMP-474",
    "vivek": "EMP-474",
    "vidya m h": "EMP-386",
    "vidya": "EMP-386"
}

async def search_employee_by_name(name: str) -> str:
    """Queries the company directory to find an employee's ID by name.
    
    Args:
        name: The full name or first name of the employee (case-insensitive).
    """
    n_lower = name.lower()
    matches = []
    for emp_name, emp_id in names_map.items():
        if n_lower in emp_name:
            matches.append({
                "employee_id": emp_id,
                "name": emp_name
            })
            
    if not matches:
        return f"No employee found matching name '{name}'."
        
    import json
    return json.dumps(matches)

# 2. Define Spoke Agents (Each has its own dedicated tools)
workweek_agent = LlmAgent(
    model=config.GEMINI_MODEL,
    name="workweek_agent",
    description="Handles employee profiles, leave balances, contact updates, and leave requests.",
    instruction=WORKWEEK_AGENT_PROMPT,
    tools=[workweek_mcp, search_employee_by_name]
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

class AccessDeniedException(Exception):
    """Exception raised when an employee attempts unauthorized access to another employee's records."""
    pass

def is_manager_of(manager_id: str, employee_id: str) -> bool:
    """Manager mapping validation utility."""
    m_id = manager_id.replace("-", "").upper()
    e_id = employee_id.replace("-", "").upper()
    
    # Manager mapping lookup (Bob Vance EMP003 is manager of standard reports)
    MANAGER_MAP = {
        "EMP003": ["EMP001", "EMP002", "EMP004", "EMP361", "EMP474", "EMP386", "JOHNSMITH"]
    }
    
    reports = MANAGER_MAP.get(m_id, [])
    return e_id in reports

def resolve_employee_id(query: str) -> str | None:
    """Helper to resolve common names or extract employee ID format from query."""
    import re
    # Check if there is an explicit ID in the query
    emp_match = re.search(r"EMP-?\d+", query, re.IGNORECASE)
    if emp_match:
        return emp_match.group(0)
        
    query_lower = query.lower()
    for name, emp_id in names_map.items():
        if name in query_lower:
            return emp_id
    return None

def contains_unauthorized_target(query: str, active_user_id: str) -> bool:
    """Helper to detect if a query mentions a third-person proper noun/name or ID that active user is not authorized to access."""
    # 1. Map active user ID to their allowed names
    active_names_lower = []
    for name, emp_id in names_map.items():
        if emp_id.replace("-", "").upper() == active_user_id.replace("-", "").upper():
            active_names_lower.append(name.lower())
            for word in name.lower().split():
                active_names_lower.append(word)

    # 2. Extract potential proper nouns (capitalized words not at the start of sentences)
    import re
    words = re.findall(r"\b[A-Za-z]+\b", query)
    
    for idx, word in enumerate(words):
        # Ignore first word of query if it is start of sentence, and ignore common system keywords
        if idx == 0:
            continue
        if word[0].isupper() and word.lower() not in ["i", "workweek", "serviceimmediately", "it", "hr", "utc", "gmt", "vacation", "sick", "hardware", "software", "network", "facilities"]:
            # If this proper noun is not the active user's own name
            if word.lower() not in active_names_lower:
                # Resolve the name to check if active user is their manager
                target_resolved = None
                query_lower = query.lower()
                for name, emp_id in names_map.items():
                    if name in query_lower:
                        target_resolved = emp_id
                        break
                
                # If they are a known employee and active user is their manager, allow it
                if target_resolved and is_manager_of(active_user_id, target_resolved):
                    continue
                return True

    # 3. Check for any explicit employee ID in query
    emp_match = re.search(r"EMP-?\d+", query, re.IGNORECASE)
    if emp_match:
        eid = emp_match.group(0)
        std_eid = eid.replace("-", "").upper()
        std_active = active_user_id.replace("-", "").upper()
        if std_eid != std_active and not is_manager_of(active_user_id, eid):
            return True

    return False

# 3. Define Hub Routing Tools (Allows Hub Agent to delegate to Spoke Agents)
async def query_workweek_agent(query: str, tool_context: ToolContext) -> str:
    """Delegates a query to the WorkWeek Agent after validating RBAC access rules.
    
    Args:
        query: The request/instruction for the WorkWeek agent.
    """
    # Block unsupported leave types at the routing boundary
    if any(term in query.lower() for term in ["study", "maternity", "bonding", "carer", "toil", "ramp-back"]):
        return "Error: Only 'Vacation' and 'Sick' leave types are supported."

    # Extract active user from session state
    active_user = tool_context.state.get("active_user_id") or "EMP001"
    
    # Pre-intercept proper nouns or IDs targetting someone else
    if contains_unauthorized_target(query, active_user):
        raise AccessDeniedException(
            f"Access Denied: User {active_user} is not authorized to access records of this third party."
        )

    target_emp = resolve_employee_id(query)
    if target_emp:
        target_std = target_emp.replace("-", "").upper()
        active_std = active_user.replace("-", "").upper()
        
        # If user is trying to view/modify someone else's record and is not their manager
        if target_std != active_std and not is_manager_of(active_user, target_emp):
            raise AccessDeniedException(
                f"Access Denied: User {active_user} is not authorized to access records of {target_emp}."
            )
            
    return await tool_context.run_node(workweek_agent, query)

async def query_serviceimmediately_agent(query: str, tool_context: ToolContext) -> str:
    """Delegates a query to the ServiceImmediately Agent after validating RBAC access rules.
    
    Args:
        query: The request/instruction for the ServiceImmediately agent.
    """
    # Extract active user from session state
    active_user = tool_context.state.get("active_user_id") or "EMP001"
    
    # Pre-intercept proper nouns or IDs targetting someone else
    if contains_unauthorized_target(query, active_user):
        raise AccessDeniedException(
            f"Access Denied: User {active_user} is not authorized to view or modify support tickets of this third party."
        )

    target_emp = resolve_employee_id(query)
    if target_emp:
        target_std = target_emp.replace("-", "").upper()
        active_std = active_user.replace("-", "").upper()
        
        # Enforce RBAC block on ticketing
        if target_std != active_std and not is_manager_of(active_user, target_emp):
            raise AccessDeniedException(
                f"Access Denied: User {active_user} is not authorized to view or modify support tickets of {target_emp}."
            )
            
    try:
        return await tool_context.run_node(serviceimmediately_agent, query)
    except Exception as e:
        # Gracefully intercept tracebacks if updating closed tickets
        err_str = str(e)
        if "closed" in err_str.lower() or "not modify" in err_str.lower() or "read-only" in err_str.lower():
            return "Error: This ticket is already closed and cannot be modified."
        raise e

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


async def run_query_async(
    query: str, 
    user_id: str = "EMP001", 
    session_id: str = "session-1",
    mcp_token: Optional[str] = None
) -> Tuple[str, str]:
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

    # Configure session state delta
    state_delta = {}
    if mcp_token:
        state_delta["x_mcp_token"] = mcp_token
    state_delta["active_user_id"] = user_id

    try:
        async for event in runner.run_async(
            user_id=user_id, 
            session_id=session_id, 
            new_message=message,
            state_delta=state_delta
        ):
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

    except AccessDeniedException as e:
        logger_err = f"Access Denied: {e}"
        log_transaction(
            user_id=user_id,
            session_id=session_id,
            action_type="BLOCKED",
            inputs={"query": query},
            output_summary=logger_err,
            success=False,
            error_code="ACCESS_DENIED"
        )
        return "Access Denied: You are not authorized to view or modify this record.", "BLOCKED"

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
