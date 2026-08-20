import os
os.environ["GOOGLE_API_PREVENT_AGENT_TOKEN_SHARING_FOR_GCP_SERVICES"] = "false"

import json
from google import genai
from pydantic import BaseModel, Field
from typing import Dict, Any, List
from google.cloud import bigquery
from google.oauth2 import service_account

class Anomaly(BaseModel):
    service: str
    description: str
    estimated_impact_usd: float

class SentinelOutput(BaseModel):
    status: str = Field(description="Can be 'ANOMALY_DETECTED' or 'ALL_CLEAR'")
    anomalies: List[Anomaly] = Field(description="List of detected anomalies")
    daily_cost_usd: float = Field(description="Total cost for the day")

def fetch_daily_billing_data() -> Dict[str, Any]:
    """Fetch billing data from BigQuery export table for the last 7 days."""
    project_id = input("Enter BigQuery Project ID: ")
    table_full_path = input("Enter BigQuery Table Full Path (dataset.table): ")
    
    sa_key_path = os.environ.get("BIGQUERY_SERVICE_ACCOUNT_JSON")
    
    if sa_key_path:
        credentials = service_account.Credentials.from_service_account_file(sa_key_path)
        client = bigquery.Client(credentials=credentials, project=project_id)
    else:
        client = bigquery.Client(project=project_id)
        
    query = f"""
        SELECT
          DATE(usage_start_time) AS date,
          service.description AS name,
          SUM(cost) AS cost
        FROM
          `{project_id}.{table_full_path}`
        WHERE
          _PARTITIONDATE >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
        GROUP BY
          1, 2
        ORDER BY
          1 DESC, 3 DESC
    """
    
    query_job = client.query(query)
    results = query_job.result()
    
    daily_data = {}
    for row in results:
        date_str = str(row.date)
        if date_str not in daily_data:
            daily_data[date_str] = {"total_cost": 0.0, "services": []}
        
        daily_data[date_str]["services"].append({
            "name": row.name,
            "cost": float(row.cost)
        })
        daily_data[date_str]["total_cost"] += float(row.cost)
        
    return daily_data

def run_sentinel(client: genai.Client) -> Dict[str, Any]:
    """Run the Sentinel Agent to monitor costs and detect anomalies."""
    # Mocking the AI call and tool execution for ADK
    billing_data = fetch_daily_billing_data()
    
    prompt = f"""
    You are the Sentinel Agent for Cloud FinOps.
    Analyze this daily billing data and detect any anomalies or cost spikes.
    Data: {billing_data}
    """
    
    # We mock out what the LLM structured output would be using ADK
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SentinelOutput,
            temperature=0.2,
        ),
    )
    
    return json.loads(response.text)
