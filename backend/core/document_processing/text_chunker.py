"""
Text Chunking for Document Processing
"""

import logging
from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import settings

logger = logging.getLogger(__name__)


class TextChunker:
    """Chunk documents for embedding"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        chunk_size = chunk_size or settings.CHUNK_SIZE
        chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", ", ", " ", ""]
        )
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks"""
        chunks = self.splitter.split_documents(documents)
        logger.info(f"Created {len(chunks)} chunks from {len(documents)} pages")
        return chunks
