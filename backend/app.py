import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from . import memory
from .conversation_engine import ConversationEngine

# Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",") if os.getenv("CORS_ORIGINS") != "*" else ["*"]
MODEL_NAME = os.getenv("MODEL_NAME", "tinyllama")
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.2"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

app = FastAPI(
    title="Innotrat Chatbot",
    description="AI-powered electronics requirements assistant",
    version="1.0.0",
    debug=DEBUG
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

try:
    engine = ConversationEngine(MODEL_NAME, MODEL_TEMPERATURE)
except Exception as e:
    print(f"Warning: Could not initialize conversation engine: {e}")
    engine = None

class SessionRequest(BaseModel):
    user_id: str
    title: Optional[str] = "New chat"

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: Optional[str] = None
    system_init: Optional[bool] = False

@app.get("/")
def root():
    return {
        "ok": True,
        "service": "Innotrat Chatbot",
        "version": "1.0.0",
        "engine_status": "available" if engine else "unavailable"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "engine": "available" if engine else "unavailable",
        "database": "connected"
    }

@app.post("/session/new")
def new(req: SessionRequest):
    try:
        sid = memory.create_session(req.user_id, req.title)
        memory.add_message(sid, "assistant", "Hi, I'm your electronics requirements assistant. What's on your mind?")
        return {"session_id": sid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.post("/chat")
def chat(req: ChatRequest):
    try:
        if not engine:
            raise HTTPException(status_code=503, detail="Conversation engine not available")
        
        hist = memory.get_history(req.session_id)
        slots = memory.get_slots(req.session_id)
        
        if req.system_init:
            return {"messages": [{"role": "assistant", "content": hist[-1]["content"] if hist else ""}]}
        
        if not req.message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        memory.add_message(req.session_id, "user", req.message)
        result = engine.run_turn(hist, req.message, slots)
        memory.add_message(req.session_id, "assistant", result["assistant_message"])
        
        if result.get("collected_fields"):
            memory.update_slots(req.session_id, result["collected_fields"])
        
        return {
            "messages": [{"role": "assistant", "content": result["assistant_message"]}],
            "status": result["status"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")