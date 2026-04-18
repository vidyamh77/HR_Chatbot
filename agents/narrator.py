import json
from google import genai
from pydantic import BaseModel, Field
from typing import Dict, Any

class NarratorOutput(BaseModel):
    report_markdown: str = Field(description="The complete formatted daily report in Markdown format")
    alert_level: str = Field(description="INFO, WARNING, or CRITICAL")

def run_narrator(client: genai.Client, sentinel_data: Dict[str, Any], analyzer_data: Dict[str, Any], 
                 detective_data: Dict[str, Any], optimizer_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run the Narrator Agent to generate the daily digest."""
    
    prompt = f"""
    You are the Narrator Agent for Cloud FinOps.
    Synthesize all the findings below into a clear, actionable Daily Markdown Report for engineering teams.
    Sentinel Data (Cost / Anomalies): {json.dumps(sentinel_data)}
    Analyzer Data (Attribution / Forecast): {json.dumps(analyzer_data)}
    Detective Data (Inefficiencies): {json.dumps(detective_data)}
    Optimizer Data (Actionable Fixes): {json.dumps(optimizer_data)}
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=NarratorOutput,
            temperature=0.3,
        ),
    )
    
    return json.loads(response.text)
