"""Input validation and security guardrails."""
import re
from typing import Dict, Any, List

INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"bypass safety",
    r"system override",
    r"you are now a",
    r"developer mode",
    r"disregard guidelines",
    r"new instructions",
]

# Basic check to filter out completely off-topic queries (e.g. coding requests)
OFF_TOPIC_PATTERNS = [
    r"write (?:a |me a |some )?(?:python|javascript|c\+\+|java|html|css|sql|rust|go) (?:code|function|script|program)",
    r"create a website",
    r"reverse a string",
    r"solve this math",
    r"what is the meaning of life",
]

ALLOWED_GREETINGS = [
    r"hello", r"hi", r"hey", r"good morning", r"good afternoon", r"how are you", r"help"
]

def validate_input(prompt: str) -> Dict[str, Any]:
    """Inspect user input for safety, injection, and off-topic requests.

    Returns:
        {"is_safe": bool, "reason": str | None}
    """
    prompt_lower = prompt.lower().strip()

    # 1. Check for prompt injection / safety bypass
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, prompt_lower):
            return {
                "is_safe": False,
                "reason": "Prompt injection attempt detected. Request blocked by safety policy."
            }

    # 2. Check for off-topic queries
    for pattern in OFF_TOPIC_PATTERNS:
        if re.search(pattern, prompt_lower):
            return {
                "is_safe": False,
                "reason": "Request is outside the scope of HR/IT Policy and Self-Service support."
            }

    # If it is just a greeting, it is allowed
    is_greeting = any(re.match(r"^" + g + r"\b", prompt_lower) for g in ALLOWED_GREETINGS)
    if is_greeting:
        return {"is_safe": True, "reason": None}

    # For other queries, they should have some relevance to HR, PTO, Leave, Expense, IT, Tickets, VPN, Relocation, Profile
    hr_keywords = [
        "leave", "pto", "vacation", "sick", "bereavement", "medical", "mc",
        "expense", "reimbursement", "gift", "allowance", "relocation", "london",
        "ticket", "incident", "vpn", "badge", "access", "profile", "phone", "address",
        "manager", "employee", "salary", "hire", "compensation", "benefit", "role", "department", "dept"
    ]
    
    # Allow if contains any keyword, or if it is very short query (which will be rejected gracefully by agent anyway)
    has_keyword = any(kw in prompt_lower for kw in hr_keywords)
    if not has_greeting_or_kw_check(prompt_lower, hr_keywords) and len(prompt_lower.split()) > 3:
        return {
            "is_safe": False,
            "reason": "Request is outside the scope of HR/IT Policy and Self-Service support."
        }

    return {"is_safe": True, "reason": None}


def has_greeting_or_kw_check(prompt_lower: str, hr_keywords: List[str]) -> bool:
    """Helper to verify if the text is relevant or greeting."""
    if any(kw in prompt_lower for kw in hr_keywords):
        return True
    return False
