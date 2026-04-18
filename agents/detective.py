import json
from google import genai
from pydantic import BaseModel, Field
from typing import Dict, Any, List

class Inefficiency(BaseModel):
    resource_id: str
    issue_type: str = Field(description="e.g., Idle VM, Oversized Disk, AI Prompt Inefficiency")
    root_cause: str

class DetectiveOutput(BaseModel):
    investigated_anomalies: List[str]
    detected_inefficiencies: List[Inefficiency]

def run_detective(client: genai.Client, sentinel_data: Dict[str, Any], analyzer_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run the Detective Agent to finding root causes like idle resources."""
    
    prompt = f"""
    You are the Detective Agent for Cloud FinOps.
    Investigate the root cause of any anomalies or waste trends identified below.
    Sentinel Data: {json.dumps(sentinel_data)}
    Analyzer Data: {json.dumps(analyzer_data)}
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=DetectiveOutput,
            temperature=0.2,
        ),
    )
    
    return json.loads(response.text)
