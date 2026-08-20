"""Governance audit logging service."""
import os
import json
import datetime
from typing import Dict, Any, Optional
from .. import config
from .output_shield import redact_spii

LOG_FILE_PATH = os.path.join(config.AGENT_ROOT, "logs", "audit.jsonl")

def log_transaction(
    user_id: str,
    session_id: str,
    action_type: str,  # 'READ' | 'WRITE' | 'BLOCKED'
    tool_invoked: Optional[str] = None,
    inputs: Optional[Dict[str, Any]] = None,
    output_summary: Optional[str] = None,
    success: bool = True,
    error_code: Optional[str] = None
) -> None:
    """Record an audit trail entry, ensuring SPII in inputs and output summaries are redacted."""
    # Ensure logs folder exists
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
    
    # Redact inputs
    redacted_inputs = {}
    if inputs:
        for k, v in inputs.items():
            if isinstance(v, str):
                redacted_inputs[k] = redact_spii(v)
            else:
                redacted_inputs[k] = v

    # Redact output summary
    redacted_output = redact_spii(output_summary or "")

    log_entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "user_id": user_id,
        "session_id": session_id,
        "agent_id": "hr_agentic_solution",
        "action_type": action_type,
        "actor_type": "AUTOMATION",
        "tool_invoked": tool_invoked,
        "inputs": redacted_inputs,
        "output_summary": redacted_output,
        "success": success,
        "error_code": error_code
    }

    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
