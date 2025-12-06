"""Document processing with semantic chunking"""
import os
from typing import List, Dict
import pypdf
from docx import Document
from pptx import Presentation
import pandas as pd
import re

# Simple sentence tokenizer (no NLTK dependency)
def simple_sent_tokenize(text):
    """Simple sentence tokenizer without NLTK"""
    # Split on sentence endings
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


class DocumentProcessor:
    """Process various document types and extract text"""
    
    def __init__(self):
        self.supported_types = {
            '.pdf': self._process_pdf,
            '.docx': self._process_docx,
            '.doc': self._process_docx,
            '.txt': self._process_txt,
            '.pptx': self._process_pptx,
            '.xlsx': self._process_excel,
            '.csv': self._process_csv
        }
    
    def process_document(self, file_path: str) -> Dict[str, any]:
        """Process document and extract text with metadata"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext not in self.supported_types:
            raise ValueError(f"Unsupported file type: {ext}")
        
        text = self.supported_types[ext](file_path)
        
        return {
            'text': text,
            'filename': os.path.basename(file_path),
            'file_type': ext,
            'char_count': len(text),
            'word_count': len(text.split())
        }
    
    def _process_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        text = []
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text.strip():
                    text.append(f"[Page {page_num + 1}]\n{page_text}")
        return "\n\n".join(text)
    
    def _process_docx(self, file_path: str) -> str:
        """Extract text from DOCX"""
        doc = Document(file_path)
        text = []
        for para in doc.paragraphs:
            if para.text.strip():
                text.append(para.text)
        
        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells]
                text.append(" | ".join(row_text))
        
        return "\n\n".join(text)
    
    def _process_txt(self, file_path: str) -> str:
        """Extract text from TXT"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()
    
    def _process_pptx(self, file_path: str) -> str:
        """Extract text from PPTX"""
        prs = Presentation(file_path)
        text = []
        
        for slide_num, slide in enumerate(prs.slides):
            slide_text = [f"[Slide {slide_num + 1}]"]
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_text.append(shape.text)
            text.append("\n".join(slide_text))
        
        return "\n\n".join(text)
    
    def _process_excel(self, file_path: str) -> str:
        """Extract text from Excel"""
        df = pd.read_excel(file_path, sheet_name=None)
        text = []
        
        for sheet_name, sheet_df in df.items():
            text.append(f"[Sheet: {sheet_name}]")
            text.append(sheet_df.to_string(index=False))
        
        return "\n\n".join(text)
    
    def _process_csv(self, file_path: str) -> str:
        """Extract text from CSV"""
        df = pd.read_csv(file_path)
        return df.to_string(index=False)


class SemanticChunker:
    """Advanced semantic chunking with sentence boundary awareness"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200, min_chunk_size: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Split text into semantic chunks"""
        # Clean text
        text = self._clean_text(text)
        
        # Split into sentences using simple tokenizer
        sentences = simple_sent_tokenize(text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # If adding this sentence exceeds chunk size
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = " ".join(current_chunk)
                if len(chunk_text) >= self.min_chunk_size:
                    chunks.append(self._create_chunk(chunk_text, len(chunks), metadata))
                
                # Start new chunk with overlap
                overlap_text = " ".join(current_chunk[-3:])  # Keep last 3 sentences for context
                current_chunk = [overlap_text, sentence] if overlap_text else [sentence]
                current_length = len(overlap_text) + sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # Add final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            if len(chunk_text) >= self.min_chunk_size:
                chunks.append(self._create_chunk(chunk_text, len(chunks), metadata))
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}\'\"]+', '', text)
        return text.strip()
    
    def _create_chunk(self, text: str, index: int, metadata: Dict = None) -> Dict:
        """Create chunk with metadata"""
        chunk = {
            'text': text,
            'chunk_id': index,
            'char_count': len(text),
            'word_count': len(text.split())
        }
        
        if metadata:
            chunk.update(metadata)
        
        return chunk
