"""Custom RAG retrieval metric to calculate Context Hit Rate."""
import re


def evaluate(instance):
    agent_data = instance.get("agent_data") or {}
    turns = agent_data.get("turns", [])
    
    retrieved_texts = []
    for turn in turns:
        for step in turn.get("steps", []):
            # Inspect tool calls for policy retrieval actions
            for tc in step.get("tool_calls", []):
                func_name = tc.get("function", {}).get("name", "")
                if func_name in ["search_policy_docs", "query_policy_agent"]:
                    # Capture the tool response output
                    tool_output = step.get("tool_output", "")
                    if tool_output:
                        retrieved_texts.append(str(tool_output).lower())

    prompt = instance.get("prompt", "").lower()
    is_rag_query = any(w in prompt for w in ["leave", "policy", "handbook", "expense", "reimbursement", "allowance", "tenure"])

    if not retrieved_texts:
        # If the query requires RAG but no documents were retrieved, hit rate is 0
        if is_rag_query:
            return {"score": 0.0, "explanation": "Failed: RAG query did not invoke search_policy_docs"}
        # For non-RAG queries (e.g. greetings, badging), hit rate is not applicable (passes as 1.0)
        return {"score": 1.0, "explanation": "N/A: Non-RAG query"}

    # Extract keywords from the expected reference response to check for hits in retrieved contexts
    reference = instance.get("reference") or {}
    ref_text = ""
    if isinstance(reference, dict):
        response_data = reference.get("response") or {}
        parts = response_data.get("parts", [])
        if parts:
            ref_text = " ".join([p.get("text", "") for p in parts if isinstance(p, dict)])
    
    if not ref_text:
        ref_text = str(reference).lower()

    # Extract relevant search nouns/adjectives (words with length >= 4)
    words = re.findall(r"\b\w{4,}\b", ref_text.lower())
    ignore_words = {"model", "role", "parts", "text", "response", "allowance", "leave"}
    keywords = [w for w in words if w not in ignore_words]

    if not keywords:
        return {"score": 1.0, "explanation": "N/A: No reference keywords to check"}

    hits = 0
    for kw in keywords:
        if any(kw in rt for rt in retrieved_texts):
            hits += 1

    hit_rate = hits / len(keywords)
    return {
        "score": hit_rate,
        "explanation": f"Context Hit Rate: {hit_rate:.2f} (matched {hits} of {len(keywords)} target keywords in retrieved context)"
    }
