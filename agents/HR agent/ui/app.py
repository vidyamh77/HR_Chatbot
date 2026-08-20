"""Web UI FastAPI backend server for the HR Agentic Solution."""
import os
import sys
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

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
