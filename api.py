"""
FastAPI Backend for Personal Knowledge Assistant
Serves the Next.js frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path

from assistant import HybridAssistant
from config import Config
from backend.utils import get_api_logger

logger = get_api_logger()

app = FastAPI(title="Personal Knowledge Assistant API")

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


@app.get("/api/status")
async def get_status():
    """Get backend status"""
    kb_path = Path(Config.KNOWLEDGE_BASE_PATH)
    pdf_count = len(list(kb_path.glob("*.pdf"))) if kb_path.exists() else 0
    
    stats = {
        "documents": 0,
        "pdfs": pdf_count
    }
    
    if assistant and assistant.is_initialized:
        assistant_stats = assistant.get_stats()
        stats["documents"] = assistant_stats['vector_store'].get('document_count', 0)
    
    return {
        "initialized": assistant is not None and assistant.is_initialized,
        "provider": Config.LLM_PROVIDER,
        "stats": stats
    }


@app.post("/api/initialize")
async def initialize():
    """Initialize the assistant"""
    global assistant
    
    try:
        if not Config.COHERE_API_KEY:
            raise HTTPException(status_code=400, detail="Cohere API key not configured")
        
        logger.info(" Initializing assistant...")
        assistant = HybridAssistant(llm_provider=Config.LLM_PROVIDER)
        assistant.initialize(force_rebuild=False)
        
        stats = assistant.get_stats()
        kb_path = Path(Config.KNOWLEDGE_BASE_PATH)
        pdf_count = len(list(kb_path.glob("*.pdf"))) if kb_path.exists() else 0
        
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
        response = assistant.ask(message.message)
        return ChatResponse(
            answer=response["answer"],
            source_type=response["source_type"],
            sources=response["sources"]
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/clear")
async def clear_chat():
    """Clear chat history"""
    global assistant
    
    if assistant:
        assistant.clear_memory()
        return {"status": "cleared"}
    
    return {"status": "no assistant"}


@app.get("/api/rebuild")
async def rebuild_kb():
    """Rebuild knowledge base"""
    global assistant
    
    try:
        logger.info(" Rebuilding knowledge base...")
        assistant = HybridAssistant(llm_provider=Config.LLM_PROVIDER)
        assistant.initialize(force_rebuild=True)
        
        stats = assistant.get_stats()
        return {
            "status": "rebuilt",
            "documents": stats['vector_store'].get('document_count', 0)
        }
    except Exception as e:
        logger.error(f"Rebuild failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
