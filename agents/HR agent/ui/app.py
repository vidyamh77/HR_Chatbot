"""Web UI FastAPI backend server for the HR Agentic Solution."""
import os
import sys
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from agent import config

logger = logging.getLogger("uvicorn.error")

# Add parent directory to path to import agent modules and mocks
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.agent import run_query_async

app = FastAPI(title="HR Agentic Solution Chatbot API")

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str

class LoginResponse(BaseModel):
    status: str
    employee_id: str
    name: str
    email: str

LIVE_USER_MAPPING = {
    "vidyamh": {
        "employee_id": "EMP-386",
        "name": "Vidya M H",
        "email": "vidyamh@altostrat.com"
    },
    "sumanbaner": {
        "employee_id": "EMP-361",
        "name": "Suman Banerjee",
        "email": "sumanbaner@altostrat.com"
    },
    "sumnabaner": {
        "employee_id": "EMP-361",
        "name": "Suman Banerjee",
        "email": "sumanbaner@altostrat.com"
    },
    "vivek": {
        "employee_id": "EMP-474",
        "name": "Vivek Anurag",
        "email": "vivek.anurag@altostrat.com"
    },
    "viveka": {
        "employee_id": "EMP-474",
        "name": "Vivek Anurag",
        "email": "viveka@altostrat.com"
    },
    "vivek.anurag": {
        "employee_id": "EMP-474",
        "name": "Vivek Anurag",
        "email": "vivek.anurag@altostrat.com"
    },
    "jane.doe": {
        "employee_id": "EMP-001",
        "name": "Jane Doe",
        "email": "jane.doe@altostrat.com"
    },
    "john.smith": {
        "employee_id": "EMP-002",
        "name": "John Smith",
        "email": "john.smith@altostrat.com"
    },
    "bob.vance": {
        "employee_id": "EMP-003",
        "name": "Bob Vance",
        "email": "bob.vance@altostrat.com"
    }
}

async def verify_employee_live(employee_id: str) -> bool:
    headers = {
        "X-MCP-Token": config.X_MCP_TOKEN,
        "Content-Type": "application/json"
    }
    try:
        async with httpx.AsyncClient(headers=headers) as http_client:
            async with streamable_http_client(url=config.WORKWEEK_MCP_URL, http_client=http_client) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    res = await session.call_tool("get_personal_info", arguments={"employee_id": employee_id})
                    response_text = "".join([part.text for part in res.content if hasattr(part, 'text')])
                    if "not found" in response_text.lower():
                        return False
                    return True
    except Exception as e:
        logger.error(f"Error validating live employee: {e}")
        return False

@app.post("/api/login", response_model=LoginResponse)
async def login_endpoint(req: LoginRequest):
    """Validate username and return employee profile."""
    username = req.username.strip().lower()
    
    # 1. Lookup in the live mapping
    user_info = LIVE_USER_MAPPING.get(username)
    if not user_info:
        raise HTTPException(
            status_code=404, 
            detail="Invalid username. Please enter a valid Altostrat username."
        )
    
    # 2. Validate live on the WorkWeek MCP server (Soft check: logs warning if not found, but allows login)
    employee_id = user_info["employee_id"]
    is_valid = await verify_employee_live(employee_id)
    if not is_valid:
        logger.warning(
            f"Employee profile for '{username}' (ID: {employee_id}) was not found in the live WorkWeek MCP database. Allowing login using configured mapping fallback."
        )
        
    return LoginResponse(
        status="SUCCESS",
        employee_id=employee_id,
        name=user_info["name"],
        email=user_info["email"]
    )

class ChatRequest(BaseModel):
    message: str
    user_id: str = "EMP001"
    session_id: str = "web-session-1"

class ChatResponse(BaseModel):
    response: str
    status: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest, request: Request):
    """Chat endpoint to query the agent."""
    logger.info("=== INCOMING REQUEST HEADERS ===")
    for k, v in request.headers.items():
        logger.info(f"  {k}: {v}")
    logger.info("=================================")
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    try:
        response, status = await run_query_async(
            query=req.message,
            user_id=req.user_id,
            session_id=req.session_id
        )
        return ChatResponse(response=response, status=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static frontend files
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Default port for UI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
