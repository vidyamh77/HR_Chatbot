import json
from google import genai
from pydantic import BaseModel, Field
from typing import Dict, Any, List

class TeamAttribution(BaseModel):
    team_name: str
    cost_usd: float
    trend: str

class AnalyzerOutput(BaseModel):
    attributions: List[TeamAttribution]
    forecast_30_days_usd: float
    total_waste_estimate_usd: float

def run_analyzer(client: genai.Client, sentinel_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run the Analyzer Agent for cost attribution and trends."""
    
    prompt = f"""
    You are the Analyzer Agent for Cloud FinOps.
    Given the following Sentinel data, attribute the costs to teams and identify the high-level trend.
    Sentinel Data: {json.dumps(sentinel_data)}
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=AnalyzerOutput,
            temperature=0.2,
        ),
    )
    
    return json.loads(response.text)
