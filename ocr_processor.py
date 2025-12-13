"""
PDF Processing with OCR Support
Handles both regular and scanned PDFs
"""

import os
import io
from pathlib import Path
from typing import List, Tuple, Optional
import logging

# PDF Processing
from pypdf import PdfReader

# OCR
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print(" OCR not available. Install: pip install pytesseract pdf2image Pillow")

# Alternative OCR
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

from langchain_core.documents import Document
from config import Config
from backend.utils import get_core_logger

logger = get_core_logger()


class OCRProcessor:
    """Handles OCR processing for scanned documents"""
    
    def __init__(self, use_easyocr: bool = False):
        self.use_easyocr = use_easyocr and EASYOCR_AVAILABLE
        
        if self.use_easyocr:
            self.reader = easyocr.Reader(['en'])
            logger.info("Using EasyOCR")
        elif OCR_AVAILABLE:
            if Config.TESSERACT_PATH:
                pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_PATH
            logger.info("Using Tesseract OCR")
        else:
            logger.warning("No OCR engine available!")
    
    def extract_text_from_image(self, image: Image.Image) -> str:
        """Extract text from a PIL Image"""
        if self.use_easyocr:
            results = self.reader.readtext(image)
            return " ".join([text for _, text, _ in results])
        elif OCR_AVAILABLE:
            return pytesseract.image_to_string(image, lang=Config.OCR_LANGUAGE)
        return ""
    
    def process_scanned_pdf(self, pdf_path: str) -> List[Tuple[int, str]]:
        """Process scanned PDF using OCR"""
        if not OCR_AVAILABLE and not EASYOCR_AVAILABLE:
            raise RuntimeError("OCR not available. Install pytesseract or easyocr.")
        
        logger.info(f" Running OCR on: {pdf_path}")
        
        # Convert PDF pages to images
        images = convert_from_path(pdf_path, dpi=300)
        
        pages_text = []
        for i, image in enumerate(images):
            text = self.extract_text_from_image(image)
            pages_text.append((i + 1, text))
            logger.info(f"  Processed page {i + 1}/{len(images)}")
        
        return pages_text


class PDFProcessor:
    """Main PDF processing class with OCR support"""
    
    def __init__(self, use_easyocr: bool = False):
        self.ocr = OCRProcessor(use_easyocr=use_easyocr)
    
    def is_scanned_pdf(self, pdf_path: str, sample_pages: int = 3) -> bool:
        """
        Detect if PDF is scanned (image-based) or has text
        Returns True if PDF needs OCR
        """
        try:
            reader = PdfReader(pdf_path)
            total_text = ""
            
            # Check first few pages
            for i, page in enumerate(reader.pages[:sample_pages]):
                text = page.extract_text() or ""
                total_text += text
            
            # If very little text found, likely scanned
            words = total_text.split()
            avg_words_per_page = len(words) / min(len(reader.pages), sample_pages)
            
            # Threshold: if less than 50 words per page, consider it scanned
            is_scanned = avg_words_per_page < 50
            
            if is_scanned:
                logger.info(f" Detected as scanned PDF: {pdf_path}")
            else:
                logger.info(f" Detected as text PDF: {pdf_path}")
                
            return is_scanned
            
        except Exception as e:
            logger.error(f"Error checking PDF: {e}")
            return False
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Document]:
        """
        Extract text from PDF, using OCR if needed
        Returns list of LangChain Documents
        """
        logger.info(f" Processing: {pdf_path}")
        
        documents = []
        pdf_name = Path(pdf_path).name
        
        # Check if OCR is needed
        needs_ocr = self.is_scanned_pdf(pdf_path)
        
        if needs_ocr:
            # Use OCR
            pages_text = self.ocr.process_scanned_pdf(pdf_path)
            
            for page_num, text in pages_text:
                if text.strip():
                    doc = Document(
                        page_content=text,
                        metadata={
                            "source": pdf_path,
                            "filename": pdf_name,
                            "page": page_num,
                            "extraction_method": "ocr"
                        }
                    )
                    documents.append(doc)
        else:
            # Direct text extraction
            reader = PdfReader(pdf_path)
            
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                
                if text and text.strip():
                    doc = Document(
                        page_content=text,
                        metadata={
                            "source": pdf_path,
                            "filename": pdf_name,
                            "page": i + 1,
                            "extraction_method": "direct"
                        }
                    )
                    documents.append(doc)
        
        logger.info(f" Extracted {len(documents)} pages from {pdf_name}")
        return documents
    
    def process_directory(self, directory: str) -> List[Document]:
        """Process all PDFs in a directory"""
        all_documents = []
        pdf_files = list(Path(directory).glob("**/*.pdf"))
        
        logger.info(f" Found {len(pdf_files)} PDF files")
        
        for pdf_path in pdf_files:
            try:
                docs = self.extract_text_from_pdf(str(pdf_path))
                all_documents.extend(docs)
            except Exception as e:
                logger.error(f" Error processing {pdf_path}: {e}")
        
        logger.info(f" Total pages extracted: {len(all_documents)}")
        return all_documents


class TextChunker:
    """Chunk documents for embedding"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", "! ", "? ", ", ", " ", ""]
        )
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks"""
        chunks = self.splitter.split_documents(documents)
        logger.info(f" Created {len(chunks)} chunks from {len(documents)} pages")
        return chunks


# Standalone function for quick use
def process_pdfs(directory: str, chunk_size: int = 1000) -> List[Document]:
    """
    Quick function to process all PDFs in a directory
    Returns chunked documents ready for embedding
    """
    processor = PDFProcessor()
    chunker = TextChunker(chunk_size=chunk_size)
    
    documents = processor.process_directory(directory)
    chunks = chunker.chunk_documents(documents)
    
    return chunks


# Test
if __name__ == "__main__":
    # Test single PDF
    processor = PDFProcessor()
    
    test_pdf = "./knowledge_base/sample.pdf"
    if os.path.exists(test_pdf):
        docs = processor.extract_text_from_pdf(test_pdf)
        print(f"Extracted {len(docs)} pages")
        if docs:
            print(f"Sample content: {docs[0].page_content[:200]}...")