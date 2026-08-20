"""Output validation, grounding verification, and SPII redaction."""
import re
from typing import List

TOXIC_WORDS = [
    "abuse", "harass", "idiot", "stupid", "fuck", "shit", "bastard"
]

# Patterns for SPII detection
SSN_NRIC_PATTERNS = [
    r"\b[A-Z]\d{7}[A-Z]\b",  # Singapore NRIC
    r"\b\d{3}-\d{2}-\d{4}\b",  # US SSN
]

# Match phone numbers in E.164 pattern but redact only the digits (retain format prefix if needed)
# Simple general phone regex
PHONE_PATTERN = r"\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b"
EMAIL_PATTERN = r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b"

def redact_spii(text: str) -> str:
    """Detect and redact SPII in final user responses or logs."""
    redacted = text
    
    # 1. Redact Singapore NRIC / US SSN
    for pattern in SSN_NRIC_PATTERNS:
        redacted = re.sub(pattern, "[REDACTED_NATIONAL_ID]", redacted, flags=re.IGNORECASE)
        
    # 2. Redact Emails (except corporate altostrat.com domain emails if relevant, or redact all personal emails)
    # We redact non-altostrat emails as personal, or we can redact all emails for strict safety
    redacted = re.sub(EMAIL_PATTERN, "[REDACTED_EMAIL]", redacted)
        
    # 3. Redact Phone Numbers
    redacted = re.sub(PHONE_PATTERN, "[REDACTED_PHONE]", redacted)
    
    return redacted


def screen_toxicity(text: str) -> bool:
    """Screen for toxic language. Returns True if toxic, False if clean."""
    text_lower = text.lower()
    for word in TOXIC_WORDS:
        if word in text_lower:
            return True
    return False


def verify_grounding(response_text: str, retrieved_context: str, user_query: str = "") -> bool:
    """Verifies that the generated response is grounded in the retrieved context.

    (In production, this might call a lightweight model or check fact overlap.
     Here, we implement a simple overlap check of key noun segments/numbers).
    """
    response_lower = response_text.lower()
    if (
        "i couldn't find that in the current" in response_lower
        or "not authorized" in response_lower
        or "unauthorized" in response_lower
        or "403" in response_lower
        or "permission" in response_lower
        or "restricted" in response_lower
        or "unable to" in response_lower
        or "cannot update" in response_lower
        or "does not match" in response_lower
        or "invalid" in response_lower
        or "denied" in response_lower
    ):
        return True
        
    # Extract numbers in response and verify they are present in context OR the user query
    numbers_in_response = re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", response_text)
    for num in numbers_in_response:
        # Ignore common single digit index, dates, or format numbers
        if len(num) == 1 or num.startswith("2026") or num in ["1", "2", "3", "164"]:
            continue
        # If the number is present in the user query, it is echoed/parameterized, so it is safe
        if num in user_query:
            continue
        if num not in retrieved_context:
            return False
            
    # Simple semantic overlap check (fallback: if response has specific keywords not in context)
    gotcha_keywords = ["gift card", "room salon", "cabaret", "prohibited"]
    for kw in gotcha_keywords:
        if kw in response_text.lower() and kw not in retrieved_context.lower() and kw not in user_query.lower():
            return False
            
    return True
