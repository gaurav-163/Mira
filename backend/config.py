"""
Configuration Management
Centralized configuration for the application
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application Settings"""
    
    # Application Info
    APP_NAME = "Personal Knowledge Assistant"
    VERSION = "2.0.0"
    
    # LLM Provider: "cohere", "groq", "openai"
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "cohere")
    
    # Self-Reflection for better answers
    ENABLE_REFLECTION = os.getenv("ENABLE_REFLECTION", "false").lower() == "true"
    
    # API Keys
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    KNOWLEDGE_BASE_PATH = BASE_DIR / "data" / "knowledge_base"
    VECTOR_DB_PATH = BASE_DIR / "data" / "vector_db"
    
    # OCR Settings
    TESSERACT_PATH = os.getenv("TESSERACT_PATH", None)
    OCR_LANGUAGE = "eng"
    
    # Document Processing Settings
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Vector Search Settings
    TOP_K_RESULTS = 2
    SIMILARITY_THRESHOLD = 0.2
    
    # LLM Settings
    LLM_TEMPERATURE = 0.3
    MAX_CHAT_HISTORY = 5
    
    # API Settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist"""
        cls.KNOWLEDGE_BASE_PATH.mkdir(parents=True, exist_ok=True)
        cls.VECTOR_DB_PATH.mkdir(parents=True, exist_ok=True)


settings = Settings()
