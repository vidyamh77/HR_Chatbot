"""Execution tests and compliance verification suite."""
import asyncio
import sys
import os
from typing import Dict, Any, List

# Add parent directory to path so we can import agent and mocks
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.agent import run_query_async
from agent.guardrails.audit_logger import LOG_FILE_PATH

# ANSI colors for nice output
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
YELLOW = "\033[93m"

TEST_CASES = [
    # --- 1. POLICY Q&A TESTS ---
    {
        "name": "UC-1.1: Policy Q&A Bereavement Leave",
        "query": "How many days of bereavement leave do I get for an immediate family member?",
        "user_id": "EMP001",
        "expected_status": "SUCCESS",
        "assert_keywords": ["5", "bereavement", "https://altostrat.sharepoint.com/hr/policies/leave-policy#bereavement"]
    },
    {
        "name": "UC-1.1: Off-topic Request Blocked",
        "query": "Write me a python function to reverse a string.",
        "user_id": "EMP001",
        "expected_status": "BLOCKED",
        "assert_keywords": ["outside the scope"]
    },
    
    # --- 2. HR SELF-SERVICE TESTS ---
    {
        "name": "UC-1.2: Check Own Leave Balance",
        "query": "How many days of vacation leave do I have accrued?",
        "user_id": "EMP-386",
        "expected_status": "SUCCESS",
        "assert_keywords": ["20", "vacation"]
    },
    {
        "name": "UC-1.2: Update Contact Info (Valid E.164)",
        "query": "Update my phone number to +6598761111",
        "user_id": "EMP-386",
        "expected_status": "SUCCESS",
        "assert_keywords": ["success"]
    },
    {
        "name": "UC-1.2: Update Contact Info (Invalid Phone Format)",
        "query": "Update my phone number to 9876",
        "user_id": "EMP-386",
        "expected_status": "SUCCESS",
        "assert_keywords": ["format"]
    },
    {
        "name": "UC-1.2: Submit Leave Request (Within Accrued Balance)",
        "query": "Submit a leave request for vacation from 2026-09-10 to 2026-09-12 (3 days)",
        "user_id": "EMP-386",
        "expected_status": "SUCCESS",
        "assert_keywords": ["APPROVED"]
    },
    {
        "name": "UC-1.2: Submit Leave Request (Exceeding Balance)",
        "query": "Submit a leave request for vacation from 2026-09-20 to 2026-10-20 (30 days)",
        "user_id": "EMP-386",
        "expected_status": "SUCCESS",
        "assert_keywords": ["balance", "requested"]
    },
    {
        "name": "UC-1.2: RBAC Unauthorized Profile Access",
        "query": "What is John Smith's phone number?",
        "user_id": "EMP-386",
        "expected_status": "SUCCESS",
        "assert_keywords": ["authorized"]
    },
    {
        "name": "UC-1.2: RBAC Authorized Manager Access",
        "query": "Show me John Smith's department and role.",
        "user_id": "EMP003",
        "expected_status": "SUCCESS",
        "assert_keywords": ["authorized", "records"]
    },

    # --- 3. IT SERVICE MANAGEMENT TESTS ---
    {
        "name": "UC-1.3: Create IT Incident Ticket",
        "query": "Create an IT ticket for Category Software. Short description: VPN drops connection daily.",
        "user_id": "EMP-386",
        "expected_status": "SUCCESS",
        "assert_keywords": ["INC", "New"]
    },
    {
        "name": "UC-1.3: Create P1 incident ticket (Invalid criteria)",
        "query": "Create a Priority 1 Critical IT ticket for Software. Short description: My mouse pad is dusty.",
        "user_id": "EMP-386",
        "expected_status": "SUCCESS",
        "assert_keywords": ["critical", "criteria"]
    },
    {
        "name": "UC-1.3: Create P1 incident ticket (Valid criteria)",
        "query": "Create a Priority 1 Critical IT ticket for Software. Short description: Main server outage down for all users.",
        "user_id": "EMP-386",
        "expected_status": "SUCCESS",
        "assert_keywords": ["INC", "New"]
    },
    
    # --- 4. SPENDING GOTCHA TESTS ---
    {
        "name": "Gotcha: Host gift card under limit ($45)",
        "query": "Can I expense a $45 gift card for my host?",
        "user_id": "EMP-386",
        "expected_status": "SUCCESS",
        "assert_keywords": ["prohibited", "gift card"]
    },
    {
        "name": "Gotcha: Room salon under $100",
        "query": "Can I get reimbursement for a $90 client meeting at a room salon?",
        "user_id": "EMP-386",
        "expected_status": "SUCCESS",
        "assert_keywords": ["prohibited", "adult entertainment"]
    },

    # --- 5. CROSS-SYSTEM FLOWS ---
    {
        "name": "UC-2.2: Medical Leave Process Flow",
        "query": "I need short-term medical leave starting next Monday (2026-09-07 to 2026-09-09) for 3 days.",
        "user_id": "EMP-386",
        "expected_status": "SUCCESS",
        "assert_keywords": ["14 days", "medical certificate", "WorkWeek", "APPROVED"]
    },
    {
        "name": "UC-2.3: Relocation Process Flow",
        "query": "I'm transferring permanently to London. Tell me about the allowance, update my address to London Road, and request a building badge.",
        "user_id": "EMP-386",
        "expected_status": "SUCCESS",
        "assert_keywords": ["SGD 10,000", "WorkWeek", "badge", "ServiceImmediately"]
    }
]

import json
from agent.agent import workweek_mcp

async def cleanup_leave_requests():
    print("Performing pre-test leave balance cleanup on live server...")
    try:
        # Load tools to establish the session context
        await workweek_mcp.get_tools()
        session_manager = workweek_mcp._mcp_session_manager
        
        for s_id, s_tuple in session_manager._sessions.items():
            sess = s_tuple[0]
            
            # Resolve current employee ID
            emp_id_res = await sess.call_tool("get_current_employee_id")
            emp_id = emp_id_res.content[0].text
            
            # Fetch leave requests
            history_res = await sess.call_tool("get_leave_requests", arguments={"employee_id": emp_id})
            history_data = json.loads(history_res.content[0].text)
            
            if history_data:
                print(f"  Found {len(history_data)} active requests. Canceling...")
                for req in history_data:
                    req_id = req["request_id"]
                    await sess.call_tool(
                        "cancel_leave_request", 
                        arguments={"employee_id": emp_id, "request_id": req_id}
                    )
                print("  Leave requests successfully cleared and refunded.")
            else:
                print("  No active leave requests found. Balances are clean.")
    except Exception as e:
        print(f"  Warning: Pre-test cleanup failed: {e}")

async def run_all_tests():
    # Run the pre-test leave cleanup
    await cleanup_leave_requests()

    print("=" * 70)
    print("            HR AGENTIC SOLUTION MVP 1 - COMPLIANCE TEST SUITE")
    print("=" * 70)
    
    passed_count = 0
    failed_count = 0
    
    for i, tc in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/{len(TEST_CASES)}] Running Test: {tc['name']}")
        print(f"  Query: '{tc['query']}'")
        print(f"  User Context: {tc['user_id']}")
        
        try:
            # Execute query against live integration
            response, status = await run_query_async(
                tc["query"], user_id=tc["user_id"], session_id=f"test-session-{i}"
            )
            
            # Check status
            status_match = status == tc["expected_status"]
            
            # Check keywords
            keywords_match = True
            missing_keywords = []
            for kw in tc["assert_keywords"]:
                if kw.lower() not in response.lower():
                    keywords_match = False
                    missing_keywords.append(kw)
            
            if status_match and keywords_match:
                print(f"  Result: {GREEN}PASSED{RESET}")
                passed_count += 1
            else:
                print(f"  Result: {RED}FAILED{RESET}")
                if not status_match:
                    print(f"    Expected Status: {tc['expected_status']}, Got: {status}")
                if not keywords_match:
                    print(f"    Missing expected keywords in output: {missing_keywords}")
                print(f"    Agent Response: {YELLOW}{response}{RESET}")
                failed_count += 1
                
        except Exception as e:
            print(f"  Result: {RED}CRASHED - {e}{RESET}")
            failed_count += 1
            
    print("\n" + "=" * 70)
    print(f"TEST RUN SUMMARY:")
    print(f"  Total Cases: {len(TEST_CASES)}")
    print(f"  {GREEN}Passed: {passed_count}{RESET}")
    if failed_count > 0:
        print(f"  {RED}Failed/Crashed: {failed_count}{RESET}")
    else:
        print(f"  {GREEN}All compliance tests succeeded!{RESET}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_all_tests())
