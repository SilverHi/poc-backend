import os
from typing import Tuple
import PyPDF2
import markdown
from io import BytesIO


class FileParser:
    """File parser that supports PDF, Markdown and text files"""
    
    @staticmethod
    def get_file_type(filename: str) -> str:
        """Determine file type based on file extension"""
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.pdf':
            return 'pdf'
        elif ext in ['.md', '.markdown']:
            return 'md'
        elif ext in ['.txt', '.text']:
            return 'text'
        else:
            return 'text'  # Default to text processing
    
    @staticmethod
    def parse_pdf(file_content: bytes) -> str:
        """Parse PDF file content"""
        try:
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
            return text_content.strip()
        except Exception as e:
            raise ValueError(f"PDF parsing failed: {str(e)}")
    
    @staticmethod
    def parse_markdown(file_content: bytes) -> str:
        """Parse Markdown file content"""
        try:
            # Convert bytes to string
            text_content = file_content.decode('utf-8')
            
            # Use markdown library to parse, but we mainly need plain text
            # Here we can choose to return raw markdown or convert to HTML then extract text
            # For simplicity, return raw text directly
            return text_content.strip()
        except Exception as e:
            raise ValueError(f"Markdown parsing failed: {str(e)}")
    
    @staticmethod
    def parse_text(file_content: bytes) -> str:
        """Parse text file content"""
        try:
            # Try different encodings
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            
            for encoding in encodings:
                try:
                    text_content = file_content.decode(encoding)
                    return text_content.strip()
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, use utf-8 and ignore errors
            return file_content.decode('utf-8', errors='ignore').strip()
        except Exception as e:
            raise ValueError(f"Text parsing failed: {str(e)}")
    
    @classmethod
    def parse_file(cls, filename: str, file_content: bytes) -> Tuple[str, str]:
        """
        Parse file content
        
        Args:
            filename: File name
            file_content: File content (bytes)
            
        Returns:
            Tuple[file_type, parsed_content]: File type and parsed content
        """
        file_type = cls.get_file_type(filename)
        
        if file_type == 'pdf':
            parsed_content = cls.parse_pdf(file_content)
        elif file_type == 'md':
            parsed_content = cls.parse_markdown(file_content)
        else:  # text
            parsed_content = cls.parse_text(file_content)
        
        return file_type, parsed_content 