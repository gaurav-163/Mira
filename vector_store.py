"""
Vector Store Management
Handles embeddings and similarity search
"""

import os
from typing import List, Dict, Optional, Tuple

from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from config import Config
from backend.utils import get_core_logger

logger = get_core_logger()


class VectorStoreManager:
    """Manages vector database operations"""
    
    def __init__(self, persist_directory: str = None):
        self.persist_directory = persist_directory or Config.VECTOR_DB_PATH
        self.embeddings = self._create_embeddings()
        self.vector_store: Optional[Chroma] = None
        
    def _create_embeddings(self):
        """Create embedding model (free HuggingFace)"""
        logger.info(" Loading embedding model...")
        
        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    
    def create_vector_store(self, documents: List[Document]) -> None:
        """Create new vector store from documents"""
        logger.info(f"📊 Creating vector store with {len(documents)} documents...")
        
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory,
            collection_metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(" Vector store created and persisted!")
    
    def load_vector_store(self) -> bool:
        """Load existing vector store"""
        if os.path.exists(self.persist_directory):
            try:
                logger.info("Loading existing vector store...")
                
                self.vector_store = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                
                # Check if it has documents
                count = self.vector_store._collection.count()
                logger.info(f" Loaded vector store with {count} documents")
                return count > 0
                
            except Exception as e:
                logger.error(f"Error loading vector store: {e}")
                return False
        return False
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add new documents to existing store"""
        if self.vector_store is None:
            self.create_vector_store(documents)
        else:
            self.vector_store.add_documents(documents)
            logger.info(f" Added {len(documents)} documents")
    
    def similarity_search_with_score(
        self, 
        query: str, 
        k: int = 5
    ) -> List[Tuple[Document, float]]:
        """
        Search for similar documents with relevance scores
        Returns: List of (document, score) tuples
        Score is distance (lower = more similar for cosine)
        """
        if self.vector_store is None:
            return []
        
        results = self.vector_store.similarity_search_with_score(query, k=k)
        return results
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Simple similarity search"""
        if self.vector_store is None:
            return []
        
        return self.vector_store.similarity_search(query, k=k)
    
    def is_query_relevant(
        self, 
        query: str, 
        threshold: float = None
    ) -> Tuple[bool, List[Document], List[float]]:
        """
        Check if query is relevant to knowledge base
        Returns: (is_relevant, documents, scores)
        """
        threshold = threshold or Config.SIMILARITY_THRESHOLD
        
        results = self.similarity_search_with_score(query, k=Config.TOP_K_RESULTS)
        
        if not results:
            return False, [], []
        
        documents = []
        scores = []
        
        for doc, score in results:
            # Convert distance to similarity (for cosine, similarity = 1 - distance)
            similarity = 1 - score
            
            if similarity >= threshold:
                documents.append(doc)
                scores.append(similarity)
        
        is_relevant = len(documents) > 0
        
        logger.info(f"Query relevance: {is_relevant}, Found {len(documents)} relevant docs")
        
        return is_relevant, documents, scores
    
    def get_retriever(self, k: int = None):
        """Get retriever for LangChain chains"""
        k = k or Config.TOP_K_RESULTS
        
        # Use similarity search instead of MMR for faster retrieval
        return self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
    
    def get_stats(self) -> Dict:
        """Get vector store statistics"""
        if self.vector_store is None:
            return {"status": "not_initialized"}
        
        count = self.vector_store._collection.count()
        
        return {
            "status": "active",
            "document_count": count,
            "persist_directory": self.persist_directory
        }
    
    def delete_collection(self) -> None:
        """Delete the entire collection"""
        if self.vector_store:
            self.vector_store.delete_collection()
            self.vector_store = None
            logger.info("🗑️ Vector store deleted")