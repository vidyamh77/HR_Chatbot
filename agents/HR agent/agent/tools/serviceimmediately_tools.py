"""ServiceImmediately (ITSM) tools for the HR agent."""
from typing import Dict, Any, Optional
from mocks import serviceimmediately_mock

def query_ticket_details(ticket_id: str) -> Dict[str, Any]:
    """Retrieve details of an existing support incident ticket.

    Args:
        ticket_id: The ticket ID, e.g., 'INC000123'.

    Returns:
        A dictionary containing the ticket fields (status, category, short_desc, priority, assignee, comments, details)
        or an error message if not found.
    """
    ticket = serviceimmediately_mock.query_ticket_details(ticket_id)
    if not ticket:
        return {"error": f"Ticket with ID {ticket_id} not found."}
    return ticket


def create_incident_ticket(
    requestor_id: str, category: str, short_desc: str, priority: int, description: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new incident ticket (e.g., VPN outage, badge access issue).

    Args:
        requestor_id: The unique ID of the employee requesting the ticket, e.g., 'EMP001'.
        category: Ticket category, e.g., 'Software', 'Hardware', 'Facilities'.
        short_desc: A brief summary of the issue.
        priority: Priority level: 1 (Critical), 2 (High), 3 (Moderate), 4 (Low).
        description: A detailed description of the issue. For Priority 1 (Critical), must contain critical terms (outages, security breach, etc.).

    Returns:
        A dictionary with the creation status, including ticket_id and status, or an error.
    """
    return serviceimmediately_mock.create_incident_ticket(
        requestor_id=requestor_id,
        category=category,
        short_desc=short_desc,
        priority=priority,
        description=description
    )


def post_ticket_comment(ticket_id: str, comment_text: str) -> Dict[str, Any]:
    """Add a new comment to an existing support ticket.

    Args:
        ticket_id: The ticket ID, e.g., 'INC000123'.
        comment_text: The comment message to post.

    Returns:
        A dictionary with the success status or error message.
    """
    return serviceimmediately_mock.post_ticket_comment(ticket_id=ticket_id, comment_text=comment_text)


def update_ticket_status(
    ticket_id: str, new_status: str, resolution_notes: Optional[str] = None
) -> Dict[str, Any]:
    """Update the status of a support ticket (e.g., transition from New to In Progress, or Resolved).

    Args:
        ticket_id: The ticket ID, e.g., 'INC000123'.
        new_status: The target status to transition to: 'In Progress', 'On Hold', 'Resolved', 'Closed'.
        resolution_notes: Notes describing the resolution (required if transitioning to 'Resolved').

    Returns:
        A dictionary with the success status or error message.
    """
    return serviceimmediately_mock.update_ticket_status(
        ticket_id=ticket_id, new_status=new_status, resolution_notes=resolution_notes
    )
