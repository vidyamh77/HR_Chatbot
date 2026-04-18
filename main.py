import json
from google import genai
from pydantic import BaseModel
from typing import Dict, Any

# Import our agents
from agents.sentinel import run_sentinel
from agents.analyzer import run_analyzer
from agents.detective import run_detective
from agents.optimizer import run_optimizer
from agents.narrator import run_narrator
from agents.memory import run_memory

def run_finops_workflow(client: genai.Client):
    print("🚀 Starting Cloud FinOps Multi-Agent Workflow...\n")

    # Step 1: Sentinel Agent (Cost Monitor)
    print(">> Invoking Sentinel Agent...")
    sentinel_output = run_sentinel(client)
    print(f"Sentinel Findings: {sentinel_output.get('status')}")

    if sentinel_output.get("status") == "ALL_CLEAR":
        print("✅ No anomalies detected. Terminating workflow early.")
        return

    # Step 2: Analyzer Agent (Cost Attribution)
    print(">> Invoking Analyzer Agent...")
    analyzer_output = run_analyzer(client, sentinel_output)
    
    # Step 3: Detective Agent (Root Cause Hunter)
    print(">> Invoking Detective Agent...")
    detective_output = run_detective(client, sentinel_output, analyzer_output)

    # Step 4: Optimizer Agent (Action Recommender)
    print(">> Invoking Optimizer Agent...")
    optimizer_output = run_optimizer(client, detective_output)

    # Step 5: Memory Agent (Learning & Improvement)
    print(">> Invoking Memory Agent...")
    memory_output = run_memory(client, optimizer_output)

    # Step 6: Narrator Agent (Daily Report)
    print(">> Invoking Narrator Agent...")
    narrator_report = run_narrator(client, sentinel_output, analyzer_output, detective_output, optimizer_output)
    
    print("\n📝 Final Daily Report Generated:")
    print("="*60)
    print(narrator_report.get("report_markdown", "No report generated."))
    print("="*60)


if __name__ == "__main__":
    # Initialize the genai Client (ensure GOOGLE_API_KEY is in environment)
    # Using a mocked approach for the ADK orchestration
    client = genai.Client()
    run_finops_workflow(client)
