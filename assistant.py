"""
Hybrid Personal Assistant
Answers from Knowledge Base (RAG) OR General Questions
"""

import os
from typing import Dict, List, Optional, Tuple

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
from backend.utils import get_service_logger
from backend.core.cache import RedisCacheManager

logger = get_service_logger()


class LLMFactory:
    """Create LLM instances based on provider"""
    
    @staticmethod
    def create(provider: str = None, temperature: float = 0.1):
        provider = provider or Config.LLM_PROVIDER
        
        if provider == "cohere":
            return ChatCohere(
                model="command-r-plus-08-2024",
                temperature=temperature,
                cohere_api_key=Config.COHERE_API_KEY,
                max_tokens=256  # Very short responses for speed
            )
        elif provider == "groq":
            return ChatGroq(
                model_name="llama-3.1-8b-instant",  # Fastest Groq model
                temperature=temperature,
                api_key=Config.GROQ_API_KEY,
                max_tokens=256
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
        self.cache_manager = RedisCacheManager(ttl_hours=24)  # 24 hour cache
        
        # LLM (will be initialized later)
        self.llm = None
        
        # Conversation memory - disabled for maximum speed
        self.chat_history = ChatMessageHistory()
        self.max_history = 0  # No history for fastest processing
        
        # Chains
        self.rag_chain = None
        self.general_chain = None
        self.retriever = None
        
        self.is_initialized = False
    
    def initialize(self, force_rebuild: bool = False) -> bool:
        """Initialize the assistant"""
        logger.info(f" Initializing Hybrid Assistant with {self.llm_provider.upper()}")
        
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
        
        # Setup chains
        self._setup_chains()
        
        self.is_initialized = True
        logger.info(" Assistant initialized successfully!")
        
        return True
    
    def _setup_chains(self):
        """Setup RAG and General chains"""
        
        # ===== RAG Chain (for knowledge base queries) =====
        rag_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a reliable personal assistant with access to a knowledge base.

Use the provided context to answer each query and structure your response as follows:

1. A clear and direct response.
2. **KEY POINTS** – Concise, numbered bullet-point highlights.
3. **ADDITIONAL CONTEXT** – Relevant supporting information.

Maintain accuracy, clarity, and brevity in all responses.
Be accurate and concise.

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
        
        logger.info(f" Question: {question}")
        
        # Check cache first
        logger.info(f"🔍 Cache enabled: {self.cache_manager.enabled}")
        cached_response = self.cache_manager.get_cached_answer(question)
        if cached_response:
            logger.info("⚡ Returning cached response")
            cached_response['from_cache'] = True
            return cached_response
        
        logger.info("📝 Cache miss - generating new response")
        
        # Optimize: Check vector DB first with lower threshold for faster initial check
        is_relevant, relevant_docs, scores = self.vector_store.is_query_relevant(
            question, 
            threshold=0.15  # Lower threshold for faster initial detection
        )
        
        if is_relevant and self.rag_chain and len(relevant_docs) > 0:
            # Use RAG for knowledge base questions
            logger.info(f" Using knowledge base ({len(relevant_docs)} docs found)")
            response = self._answer_from_knowledge_base(question, relevant_docs, scores)
            # Cache the response
            self.cache_manager.cache_answer(question, response)
            return response
        else:
            # Use general LLM for random questions
            logger.info(" Using general knowledge")
            response = self._answer_general_question(question)
            # Cache general responses too
            self.cache_manager.cache_answer(question, response)
            return response
    
    def _reflect_on_answer(self, question: str, answer: str, context: str) -> Dict:
        """Self-reflection: Validate answer quality and relevance"""
        # Create a fresh LLM instance without chat history interference
        reflection_llm = LLMFactory.create(self.llm_provider, temperature=0.1)
        
        reflection_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a quality checker. Evaluate if the answer properly addresses the question using the given context.\n\nRespond with:\n1. QUALITY: Good/Fair/Poor\n2. REASON: Brief explanation\n3. IMPROVED: Better answer if needed (or 'N/A' if good)"),
            ("human", "Question: {question}\n\nContext: {context}\n\nAnswer: {answer}")
        ])
        
        try:
            reflection = (reflection_prompt | reflection_llm | StrOutputParser()).invoke({
                "question": question,
                "answer": answer,
                "context": context[:500]  # Limit context length
            })
            
            # Parse reflection
            if "QUALITY: Good" in reflection or "QUALITY:Good" in reflection:
                return {"quality": "good", "improved_answer": None}
            elif "IMPROVED:" in reflection:
                # Extract improved answer
                parts = reflection.split("IMPROVED:")
                if len(parts) > 1:
                    improved = parts[1].strip().replace("N/A", "").strip()
                    if improved and improved.lower() != "n/a":
                        logger.info("Self-reflection: Improved answer generated")
                        return {"quality": "improved", "improved_answer": improved}
            
            return {"quality": "fair", "improved_answer": None}
            
        except Exception as e:
            logger.warning(f"Reflection failed: {e}")
            return {"quality": "unknown", "improved_answer": None}
    
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
            
            # Self-reflection: Validate answer quality
            if Config.ENABLE_REFLECTION and len(relevant_docs) > 0:
                context = "\n".join([doc.page_content[:200] for doc in relevant_docs[:2]])
                reflection = self._reflect_on_answer(question, answer, context)
                
                if reflection.get("improved_answer"):
                    logger.info("Using improved answer from self-reflection")
                    answer = reflection["improved_answer"]
            
            # Update memory
            self.chat_history.add_user_message(question)
            self.chat_history.add_ai_message(answer)
            
            # Format sources from relevant_docs
            sources = []
            for i, doc in enumerate(relevant_docs[:1]):  # Single source for fastest response
                source_snippet = doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
                sources.append({
                    "title": f"Source: {doc.metadata.get('filename', 'Unknown')}",
                    "page": f"Page {doc.metadata.get('page', 'N/A')}",
                    "content": source_snippet,
                    "relevance_score": f"{scores[i]:.2%}" if i < len(scores) else "N/A",
                    "extraction_method": doc.metadata.get("extraction_method", "unknown").upper()
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
            
            logger.info(f" Added {pdf_path} to knowledge base")
            return True
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return False
    
    def clear_memory(self):
        """Clear conversation history"""
        self.chat_history.clear()
        logger.info("🧹 Conversation memory cleared")
    
    def get_stats(self) -> Dict:
        """Get assistant statistics"""
        return {
            "llm_provider": self.llm_provider,
            "is_initialized": self.is_initialized,
            "vector_store": self.vector_store.get_stats(),
            "memory_messages": len(self.chat_history.messages)
        }