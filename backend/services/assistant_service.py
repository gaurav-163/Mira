"""
Hybrid Personal Assistant
Answers from Knowledge Base (RAG) OR General Questions
"""

import os
from typing import Dict, List, Optional, Tuple
import logging

# LLM Providers
from langchain_cohere import ChatCohere
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

# Chains & Memory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Local imports
from config import Config
from ocr_processor import PDFProcessor, TextChunker
from vector_store import VectorStoreManager
from backend.core.vector_store.semantic_search import SemanticRAGOptimizer
from backend.core.cache import RedisCacheManager

logger = logging.getLogger(__name__)


class LLMFactory:
    """Create LLM instances based on provider"""
    
    @staticmethod
    def create(provider: str = None, temperature: float = 0.3):
        provider = provider or Config.LLM_PROVIDER
        
        if provider == "cohere":
            return ChatCohere(
                model="command-r-plus-08-2024",
                temperature=temperature,
                cohere_api_key=Config.COHERE_API_KEY
            )
        elif provider == "groq":
            return ChatGroq(
                model_name="llama3-8b-8192",
                temperature=temperature,
                api_key=Config.GROQ_API_KEY
            )
        elif provider == "openai":
            return ChatOpenAI(
                model_name="gpt-3.5-turbo",
                temperature=temperature,
                api_key=Config.OPENAI_API_KEY
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")


class HybridAssistant:
    """
    Personal Assistant that:
    1. Answers from knowledge base when relevant
    2. Answers general questions when not in KB
    """
    
    def __init__(self, llm_provider: str = None):
        self.llm_provider = llm_provider or Config.LLM_PROVIDER
        
        # Initialize components
        self.pdf_processor = PDFProcessor()
        self.chunker = TextChunker(Config.CHUNK_SIZE, Config.CHUNK_OVERLAP)
        self.vector_store = VectorStoreManager()
        self.semantic_rag = None  # Will be initialized after vector store
        self.cache_manager = RedisCacheManager(ttl_hours=24)  # 24 hour cache
        
        # LLM (will be initialized later)
        self.llm = None
        
        # Conversation memory - using ChatMessageHistory
        self.chat_history = ChatMessageHistory()
        self.max_history = 5  # Remember last 5 exchanges for faster processing
        
        # Chains
        self.rag_chain = None
        self.general_chain = None
        self.retriever = None
        
        self.is_initialized = False
    
    def initialize(self, force_rebuild: bool = False) -> bool:
        """Initialize the assistant"""
        logger.info(f" Initializing Hybrid Assistant with {self.llm_provider.upper()}")
        
        # Log cache status
        if self.cache_manager.enabled:
            logger.info("✅ Redis cache is ENABLED and connected")
        else:
            logger.warning("⚠️ Redis cache is DISABLED - responses will not be cached")
        
        # Create LLM
        self.llm = LLMFactory.create(self.llm_provider)
        
        # Load or build vector store
        if not force_rebuild and self.vector_store.load_vector_store():
            logger.info(" Using existing knowledge base")
        else:
            logger.info(" Building knowledge base from PDFs...")
            
            if not os.path.exists(Config.KNOWLEDGE_BASE_PATH):
                os.makedirs(Config.KNOWLEDGE_BASE_PATH)
                logger.warning(f"Created empty folder: {Config.KNOWLEDGE_BASE_PATH}")
                logger.warning("Add PDF files and run again with force_rebuild=True")
            
            # Process PDFs
            documents = self.pdf_processor.process_directory(Config.KNOWLEDGE_BASE_PATH)
            
            if documents:
                chunks = self.chunker.chunk_documents(documents)
                self.vector_store.create_vector_store(chunks)
            else:
                logger.warning(" No documents found in knowledge base")
        
        # Initialize semantic RAG optimizer
        self.semantic_rag = SemanticRAGOptimizer(self.vector_store)
        logger.info("🚀 Semantic RAG optimizer initialized")
        
        # Setup chains
        self._setup_chains()
        
        self.is_initialized = True
        logger.info(" Assistant initialized successfully!")
        
        return True
    
    def _setup_chains(self):
        """Setup RAG and General chains"""
        
        # ===== RAG Chain (for knowledge base queries) =====
        rag_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful personal assistant with access to a knowledge base.

Use the following context from the knowledge base to answer the question.
Be accurate and cite information from the context when possible.

Context:
{context}

Chat History:
{chat_history}"""),
            ("human", "{question}")
        ])
        
        if self.vector_store.vector_store:
            # Modern LCEL chain
            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)
            
            retriever = self.vector_store.get_retriever()
            
            self.rag_chain = (
                {
                    "context": retriever | format_docs,
                    "question": RunnablePassthrough(),
                    "chat_history": lambda _: self._format_chat_history()
                }
                | rag_prompt
                | self.llm
                | StrOutputParser()
            )
            self.retriever = retriever
        else:
            self.rag_chain = None
            self.retriever = None
        
        # ===== General Chain (for random questions) =====
        general_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful, friendly personal assistant.
            
You can answer any question the user asks - general knowledge, advice, 
coding help, explanations, creative tasks, etc.

Be conversational and helpful. If you don't know something, say so honestly.

Previous conversation:
{chat_history}"""),
            ("human", "{question}")
        ])
        
        self.general_chain = general_prompt | self.llm | StrOutputParser()
    
    def _format_chat_history(self) -> str:
        """Format chat history for prompts"""
        messages = self.chat_history.messages[-self.max_history:]  # Last N messages
        
        history = []
        for msg in messages:
            role = "Human" if msg.type == "human" else "Assistant"
            history.append(f"{role}: {msg.content}")
        
        return "\n".join(history) if history else "No previous conversation"
    
    def ask(self, question: str) -> Dict:
        """
        Main method to ask questions
        Automatically decides: RAG or General response
        """
        if not self.is_initialized:
            return {
                "answer": " Assistant not initialized. Call initialize() first.",
                "source_type": "error",
                "sources": []
            }
        
        logger.info(f"❓ Question: {question}")
        
        # Check cache first
        logger.info(f"🔍 Cache enabled: {self.cache_manager.enabled}")
        cached_response = self.cache_manager.get_cached_answer(question)
        if cached_response:
            logger.info("⚡ Returning cached response")
            cached_response['from_cache'] = True
            return cached_response
        
        logger.info("📝 Cache miss - generating new response")
        
        # Use semantic RAG optimizer for faster, more accurate search
        if self.semantic_rag and self.vector_store.vector_store:
            logger.info("🚀 Using enhanced semantic search")
            
            # Smart search with hybrid approach
            results = self.semantic_rag.smart_search(question, k=5, use_rrf=True)
            
            if results and len(results) > 0:
                # Extract documents and scores
                relevant_docs = [doc for doc, _ in results]
                scores = [score for _, score in results]
                
                # Check if best result is relevant enough
                best_score = scores[0] if scores else 0
                
                if best_score > 0.3:  # Threshold for relevance
                    logger.info(f"✅ Using knowledge base ({len(relevant_docs)} docs, score: {best_score:.3f})")
                    response = self._answer_from_knowledge_base(question, relevant_docs, scores)
                    # Cache the response
                    self.cache_manager.cache_answer(question, response)
                    return response
        
        # Fallback to original method if semantic RAG not available
        is_relevant, relevant_docs, scores = self.vector_store.is_query_relevant(
            question, 
            threshold=0.2
        )
        
        if is_relevant and self.rag_chain and len(relevant_docs) > 0:
            logger.info(f"📚 Using knowledge base (fallback, {len(relevant_docs)} docs)")
            response = self._answer_from_knowledge_base(question, relevant_docs, scores)
            # Cache the response
            self.cache_manager.cache_answer(question, response)
            return response
        else:
            # Use general LLM for random questions
            logger.info("🌐 Using general knowledge")
            response = self._answer_general_question(question)
            # Cache general responses too
            self.cache_manager.cache_answer(question, response)
            return response
    
    def _answer_from_knowledge_base(
        self, 
        question: str, 
        relevant_docs: List[Document],
        scores: List[float]
    ) -> Dict:
        """Answer using RAG from knowledge base"""
        logger.info(" Answering from Knowledge Base (RAG)")
        
        try:
            # Get answer from RAG chain
            answer = self.rag_chain.invoke(question)
            
            # Update memory
            self.chat_history.add_user_message(question)
            self.chat_history.add_ai_message(answer)
            
            # Format sources from relevant_docs
            sources = []
            for i, doc in enumerate(relevant_docs[:3]):  # Top 3 sources for faster processing
                sources.append({
                    "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                    "source": doc.metadata.get("filename", "Unknown"),
                    "page": doc.metadata.get("page", "N/A"),
                    "extraction_method": doc.metadata.get("extraction_method", "unknown"),
                    "relevance": scores[i] if i < len(scores) else None
                })
            
            return {
                "answer": answer,
                "source_type": "knowledge_base",
                "sources": sources
            }
            
        except Exception as e:
            logger.error(f"RAG error: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to general
            return self._answer_general_question(question)
    
    def _answer_general_question(self, question: str) -> Dict:
        """Answer general questions using LLM directly"""
        logger.info(" Answering as General Question")
        
        try:
            chat_history = self._format_chat_history()
            
            answer = self.general_chain.invoke({
                "question": question,
                "chat_history": chat_history
            })
            
            # Update memory manually for general chain
            self.chat_history.add_user_message(question)
            self.chat_history.add_ai_message(answer)
            
            return {
                "answer": answer,
                "source_type": "general_knowledge",
                "sources": []
            }
            
        except Exception as e:
            logger.error(f"General chain error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "answer": f"Sorry, I encountered an error: {str(e)}",
                "source_type": "error",
                "sources": []
            }
    
    def force_rag(self, question: str) -> Dict:
        """Force answer from knowledge base only"""
        if not self.rag_chain:
            return {
                "answer": "Knowledge base not available",
                "source_type": "error",
                "sources": []
            }
        
        relevant_docs = self.vector_store.similarity_search(question)
        scores = [0.5] * len(relevant_docs)  # Placeholder scores
        
        return self._answer_from_knowledge_base(question, relevant_docs, scores)
    
    def force_general(self, question: str) -> Dict:
        """Force answer as general question"""
        return self._answer_general_question(question)
    
    def search_knowledge_base(self, query: str, k: int = 5) -> List[Dict]:
        """Search knowledge base without generating answer"""
        # Use semantic RAG if available
        if self.semantic_rag:
            results = self.semantic_rag.smart_search(query, k=k)
            return [
                {
                    "content": doc.page_content,
                    "source": doc.metadata.get("filename", "Unknown"),
                    "page": doc.metadata.get("page", "N/A"),
                    "score": float(score)
                }
                for doc, score in results
            ]
        
        # Fallback to regular search
        docs = self.vector_store.similarity_search(query, k=k)
        
        return [
            {
                "content": doc.page_content,
                "source": doc.metadata.get("filename", "Unknown"),
                "page": doc.metadata.get("page", "N/A")
            }
            for doc in docs
        ]
    
    def add_document(self, pdf_path: str) -> bool:
        """Add a new PDF to knowledge base"""
        try:
            documents = self.pdf_processor.extract_text_from_pdf(pdf_path)
            chunks = self.chunker.chunk_documents(documents)
            self.vector_store.add_documents(chunks)
            
            # Reinitialize RAG chain with updated retriever
            self._setup_chains()
            
            # Clear semantic search cache
            if self.semantic_rag:
                self.semantic_rag.clear_cache()
            
            # Clear Redis cache when adding new documents
            self.cache_manager.invalidate_cache()
            
            logger.info(f" Added {pdf_path} to knowledge base")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return False
    
    def clear_memory(self):
        """Clear conversation history and Redis cache"""
        self.chat_history.clear()
        self.cache_manager.invalidate_cache()
        logger.info("🧹 Conversation memory and cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return self.cache_manager.get_cache_stats()
    
    def get_stats(self) -> Dict:
        """Get assistant statistics"""
        stats = {
            "llm_provider": self.llm_provider,
            "is_initialized": self.is_initialized,
            "vector_store": self.vector_store.get_stats(),
            "memory_messages": len(self.chat_history.messages),
            "cache": self.get_cache_stats()
        }
        return stats