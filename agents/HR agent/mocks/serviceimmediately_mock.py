"""ServiceImmediately (ITSM) API Mock Service."""
import time
from typing import Dict, Any, Optional, List

# In-memory ticket store
MOCK_TICKETS: Dict[str, Dict[str, Any]] = {
    "INC000123": {
        "ticket_id": "INC000123",
        "requestor_id": "EMP001",
        "category": "Software",
        "short_desc": "VPN keeps dropping hourly",
        "description": "My Altostrat VPN drops connection every 60 minutes precisely. I need help troubleshooting.",
        "priority": 3,
        "status": "In Progress",
        "assignee": "EMP003",
        "comments": [
            {"timestamp": "2026-08-18T10:00:00Z", "comment_text": "Investigating logs."}
        ]
    }
}

# Keep track of ticket creations for duplication detection (user_id, category, timestamp)
RECENT_CREATIONS: List[Dict[str, Any]] = []

VALID_STATUSES = ["New", "In Progress", "On Hold", "Resolved", "Closed"]

# Lifecycle transition validation map
ALLOWED_TRANSITIONS = {
    "New": ["In Progress"],
    "In Progress": ["On Hold", "Resolved"],
    "On Hold": ["In Progress", "Resolved"],
    "Resolved": ["Closed", "In Progress"],
    "Closed": []  # Terminal state
}

CRITICAL_KEYWORDS = ["outage", "system down", "security breach", "all users", "compromised", "leak"]

def query_ticket_details(ticket_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve ticket details."""
    return MOCK_TICKETS.get(ticket_id)


def create_incident_ticket(
    requestor_id: str, category: str, short_desc: str, priority: int, description: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new incident ticket. Enforce duplication limits and P1 constraints."""
    now = time.time()
    
    # 1. Duplication Mitigation (same requestor and category within 5 minutes)
    for rc in RECENT_CREATIONS:
        if (rc["requestor_id"] == requestor_id and 
            rc["category"] == category and 
            (now - rc["timestamp"]) < 300):
            return {"success": False, "error": "Duplicate ticket detected. Please wait 5 minutes between tickets in the same category."}
            
    # 2. Priority check
    if priority not in (1, 2, 3, 4):
        return {"success": False, "error": "Invalid priority level. Must be 1 (Critical) to 4 (Low)."}
        
    # 3. Priority 1 Criteria Check
    full_text = f"{short_desc} {description or ''}".lower()
    if priority == 1:
        has_critical_keyword = any(kw in full_text for kw in CRITICAL_KEYWORDS)
        if not has_critical_keyword:
            return {
                "success": False, 
                "error": "Priority 1 (Critical) requires the description to match critical-incident criteria (e.g. outages, system down, security breach)."
            }
            
    # Create ticket
    ticket_id = f"INC{len(MOCK_TICKETS) + 10001:06d}"
    ticket = {
        "ticket_id": ticket_id,
        "requestor_id": requestor_id,
        "category": category,
        "short_desc": short_desc,
        "description": description or short_desc,
        "priority": priority,
        "status": "New",
        "assignee": None,
        "comments": []
    }
    
    MOCK_TICKETS[ticket_id] = ticket
    RECENT_CREATIONS.append({"requestor_id": requestor_id, "category": category, "timestamp": now})
    
    return {
        "success": True,
        "ticket_id": ticket_id,
        "status": "New",
        "requestor_id": requestor_id,
        "category": category,
        "short_desc": short_desc,
        "priority": priority
    }


def post_ticket_comment(ticket_id: str, comment_text: str) -> Dict[str, Any]:
    """Post a comment to a ticket."""
    ticket = MOCK_TICKETS.get(ticket_id)
    if not ticket:
        return {"success": False, "error": f"Ticket {ticket_id} not found."}
    
    if not comment_text.strip():
        return {"success": False, "error": "Comment text cannot be empty."}
        
    comment = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "comment_text": comment_text
    }
    ticket["comments"].append(comment)
    return {"success": True}


def update_ticket_status(ticket_id: str, new_status: str, resolution_notes: Optional[str] = None) -> Dict[str, Any]:
    """Transition ticket state conforming to lifecycle transition rules."""
    ticket = MOCK_TICKETS.get(ticket_id)
    if not ticket:
        return {"success": False, "error": f"Ticket {ticket_id} not found."}
        
    current_status = ticket["status"]
    if new_status not in VALID_STATUSES:
        return {"success": False, "error": f"Invalid status '{new_status}'."}
        
    # Validate transition
    allowed = ALLOWED_TRANSITIONS.get(current_status, [])
    if new_status not in allowed:
        return {
            "success": False, 
            "error": f"Invalid transition: Cannot move ticket from '{current_status}' to '{new_status}'. Allowed transitions: {allowed}"
        }
        
    # Enforce resolution notes for Resolved
    if new_status == "Resolved" and not resolution_notes:
        return {"success": False, "error": "Resolution notes are required to resolve a ticket."}
        
    return {
        "success": True,
        "ticket_id": ticket_id,
        "status": new_status
    }


def reset_mocks():
    """Reset mock database state and creations tracking for tests."""
    global RECENT_CREATIONS, MOCK_TICKETS
    RECENT_CREATIONS.clear()
    MOCK_TICKETS.clear()
    MOCK_TICKETS["INC000123"] = {
        "ticket_id": "INC000123",
        "requestor_id": "EMP001",
        "category": "Software",
        "short_desc": "VPN keeps dropping hourly",
        "description": "My Altostrat VPN drops connection every 60 minutes precisely. I need help troubleshooting.",
        "priority": 3,
        "status": "In Progress",
        "assignee": "EMP003",
        "comments": [
            {"timestamp": "2026-08-18T10:00:00Z", "comment_text": "Investigating logs."}
        ]
    }
