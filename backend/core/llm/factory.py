"""
LLM Factory
Creates LLM instances based on provider configuration
"""

from langchain_cohere import ChatCohere
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from backend.config import settings


class LLMFactory:
    """Factory for creating LLM instances"""
    
    @staticmethod
    def create(provider: str = None, temperature: float = None):
        """Create an LLM instance based on provider"""
        provider = provider or settings.LLM_PROVIDER
        temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
        
        if provider == "cohere":
            return ChatCohere(
                model="command-r-plus-08-2024",
                temperature=temperature,
                cohere_api_key=settings.COHERE_API_KEY
            )
        elif provider == "groq":
            return ChatGroq(
                model_name="llama3-8b-8192",
                temperature=temperature,
                api_key=settings.GROQ_API_KEY
            )
        elif provider == "openai":
            return ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=temperature,
                api_key=settings.OPENAI_API_KEY
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
