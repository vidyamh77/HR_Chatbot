import json
from google import genai
from pydantic import BaseModel, Field
from typing import Dict, Any, List

class MemoryOutput(BaseModel):
    learned_patterns: List[str]
    historical_context_applied: bool

def run_memory(client: genai.Client, optimizer_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run the Memory Agent to track optimization effectiveness."""
    
    # In a real system, you'd store this in a Vector DB or Document DB
    prompt = f"""
    You are the Memory Agent for Cloud FinOps.
    Log these recommended actions and generate any learned recurring patterns.
    Optimizer Data: {json.dumps(optimizer_data)}
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=MemoryOutput,
            temperature=0.2,
        ),
    )
    
    return json.loads(response.text)
