import json
from google import genai
from pydantic import BaseModel, Field
from typing import Dict, Any, List

class OptimizationAction(BaseModel):
    action_type: str = Field(description="e.g., DOWNGRADE_VM, PURCHASE_CUD, DELETE_DISK")
    target_resource: str
    estimated_savings_usd: float
    gcloud_command: str = Field(description="Suggested CLI command to apply this fix")

class OptimizerOutput(BaseModel):
    recommended_actions: List[OptimizationAction]
    total_potential_savings: float

def run_optimizer(client: genai.Client, detective_data: Dict[str, Any]) -> Dict[str, Any]:
    """Run the Optimizer Agent to recommend actionable fixes."""
    
    prompt = f"""
    You are the Optimizer Agent for Cloud FinOps.
    Based on the inefficiencies found by the Detective Agent, generate actionable recommendations.
    Detective Findings: {json.dumps(detective_data)}
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=OptimizerOutput,
            temperature=0.2,
        ),
    )
    
    return json.loads(response.text)
