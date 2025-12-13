import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # LLM Provider: "cohere", "groq", "openai"
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")  # Groq is 10x faster
    
    # Self-Reflection for better answers
    ENABLE_REFLECTION = os.getenv("ENABLE_REFLECTION", "false").lower() == "true"
    
    # API Keys
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Paths
    KNOWLEDGE_BASE_PATH = "./data/knowledge_base"
    VECTOR_DB_PATH = "./data/vector_db"
    
    # OCR Settings
    TESSERACT_PATH = os.getenv("TESSERACT_PATH", None)  # Set if not in PATH
    OCR_LANGUAGE = "eng"  # Language for OCR
    
    # Chunking Settings
    CHUNK_SIZE = 500  # Smaller chunks for faster processing
    CHUNK_OVERLAP = 50  # Minimal overlap for speed
    
    # Search Settings
    TOP_K_RESULTS = 1  # Single most relevant document for fastest response
    SIMILARITY_THRESHOLD = 0.15  # Lower threshold for faster detection