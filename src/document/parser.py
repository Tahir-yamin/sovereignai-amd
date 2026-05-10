import os
import fitz  # PyMuPDF
from docx import Document
from loguru import logger
from typing import Optional

class DocumentParser:
    """
    Handles extraction of text from various document formats.
    Supported: PDF, DOCX, TXT.
    """
    
    @staticmethod
    def parse(file_path: str) -> Optional[str]:
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
            
        ext = os.path.splitext(file_path)[1].lower()
        logger.info(f"Parsing {ext} document: {file_path}")
        
        try:
            if ext == ".pdf":
                return DocumentParser._parse_pdf(file_path)
            elif ext == ".docx":
                return DocumentParser._parse_docx(file_path)
            elif ext == ".txt":
                return DocumentParser._parse_txt(file_path)
            else:
                logger.warning(f"Unsupported file format: {ext}")
                return None
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return None

    @staticmethod
    def _parse_pdf(file_path: str) -> str:
        text = ""
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
        return text

    @staticmethod
    def _parse_docx(file_path: str) -> str:
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])

    @staticmethod
    def _parse_txt(file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
