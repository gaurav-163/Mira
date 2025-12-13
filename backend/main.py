"""
FastAPI Application
Main entry point for the backend API
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import logging

from backend.services.assistant_service import HybridAssistant
from backend.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global assistant instance
assistant: HybridAssistant = None


class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    source_type: str
    sources: list


@app.on_startup
async def startup_event():
    """Ensure directories exist on startup"""
    settings.ensure_directories()
    logger.info(f"{settings.APP_NAME} v{settings.VERSION} started")


@app.get("/api/status")
async def get_status():
    """Get backend status"""
    pdf_count = len(list(settings.KNOWLEDGE_BASE_PATH.glob("*.pdf"))) if settings.KNOWLEDGE_BASE_PATH.exists() else 0
    
    stats = {
        "documents": 0,
        "pdfs": pdf_count
    }
    
    if assistant and assistant.is_initialized:
        assistant_stats = assistant.get_stats()
        stats["documents"] = assistant_stats['vector_store'].get('document_count', 0)
    
    return {
        "initialized": assistant is not None and assistant.is_initialized,
        "provider": settings.LLM_PROVIDER,
        "stats": stats
    }


@app.post("/api/initialize")
async def initialize():
    """Initialize the assistant"""
    global assistant
    
    try:
        if not settings.COHERE_API_KEY:
            raise HTTPException(status_code=400, detail="Cohere API key not configured")
        
        logger.info("Initializing assistant...")
        assistant = HybridAssistant(llm_provider=settings.LLM_PROVIDER)
        assistant.initialize(force_rebuild=False)
        
        stats = assistant.get_stats()
        pdf_count = len(list(settings.KNOWLEDGE_BASE_PATH.glob("*.pdf"))) if settings.KNOWLEDGE_BASE_PATH.exists() else 0
        
        return {
            "status": "initialized",
            "stats": {
                "documents": stats['vector_store'].get('document_count', 0),
                "pdfs": pdf_count
            }
        }
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Chat with the assistant"""
    global assistant
    
    if not assistant or not assistant.is_initialized:
        raise HTTPException(status_code=400, detail="Assistant not initialized")
    
    try:
        result = assistant.ask(message.message)
        return ChatResponse(**result)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/clear")
async def clear_history():
    """Clear chat history"""
    global assistant
    
    if assistant:
        assistant.clear_history()
        return {"status": "cleared"}
    
    return {"status": "no_assistant"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
