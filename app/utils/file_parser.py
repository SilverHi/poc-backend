import os
import logging
from typing import Tuple
import pypdf
import pdfplumber
import pytesseract
from pdf2image import convert_from_bytes
import markdown
from io import BytesIO

# Configure logging
logger = logging.getLogger(__name__)


class FileParser:
    """File parser that supports PDF, Markdown and text files with OCR capability"""
    
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
    def extract_text_with_ocr(file_content: bytes) -> str:
        """Extract text from PDF using OCR as fallback"""
        try:
            logger.info("Attempting OCR text extraction from PDF")
            
            # Convert PDF to images
            images = convert_from_bytes(file_content, dpi=300, fmt='jpeg')
            logger.info(f"Converted PDF to {len(images)} images for OCR")
            
            extracted_text = ""
            for i, image in enumerate(images):
                try:
                    # Use Tesseract to extract text from image
                    page_text = pytesseract.image_to_string(image, lang='eng')
                    if page_text and page_text.strip():
                        extracted_text += page_text + "\n"
                        logger.debug(f"OCR extracted text from page {i + 1}")
                    else:
                        logger.debug(f"No text found on page {i + 1}")
                except Exception as e:
                    logger.warning(f"OCR failed for page {i + 1}: {e}")
                    continue
            
            if extracted_text.strip():
                logger.info(f"OCR successfully extracted {len(extracted_text)} characters")
                return extracted_text.strip()
            else:
                logger.warning("OCR found no text in the PDF")
                return ""
                
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return ""
    
    @staticmethod
    def parse_pdf(file_content: bytes) -> str:
        """Parse PDF file content using multiple methods for better compatibility"""
        text_content = ""
        
        # Method 1: Try pypdf first (fastest for text-based PDFs)
        try:
            logger.info("Attempting PDF parsing with pypdf")
            pdf_file = BytesIO(file_content)
            pdf_reader = pypdf.PdfReader(pdf_file)
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text and page_text.strip():
                        text_content += page_text + "\n"
                        logger.debug(f"Successfully extracted text from page {page_num + 1}")
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num + 1} with pypdf: {e}")
                    continue
            
            # If we got meaningful content, return it
            if text_content.strip() and len(text_content.strip()) > 50:  # Require substantial content
                logger.info(f"Successfully parsed PDF with pypdf, extracted {len(text_content)} characters")
                return text_content.strip()
            else:
                logger.warning("pypdf extracted insufficient text, trying pdfplumber")
                text_content = ""  # Reset for next method
                
        except Exception as e:
            logger.warning(f"pypdf parsing failed: {e}, trying pdfplumber")
        
        # Method 2: Try pdfplumber as fallback (more robust but slower)
        try:
            logger.info("Attempting PDF parsing with pdfplumber")
            pdf_file = BytesIO(file_content)
            
            with pdfplumber.open(pdf_file) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text and page_text.strip():
                            text_content += page_text + "\n"
                            logger.debug(f"Successfully extracted text from page {page_num + 1}")
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num + 1} with pdfplumber: {e}")
                        continue
            
            if text_content.strip() and len(text_content.strip()) > 50:  # Require substantial content
                logger.info(f"Successfully parsed PDF with pdfplumber, extracted {len(text_content)} characters")
                return text_content.strip()
            else:
                logger.warning("pdfplumber extracted insufficient text, trying OCR")
                
        except Exception as e:
            logger.warning(f"pdfplumber parsing failed: {e}, trying OCR")
        
        # Method 3: Try OCR as final fallback (for scanned PDFs)
        ocr_text = FileParser.extract_text_with_ocr(file_content)
        if ocr_text and ocr_text.strip():
            logger.info(f"OCR successfully extracted {len(ocr_text)} characters")
            return ocr_text
        
        # If all methods fail, raise an error with helpful message
        raise ValueError(
            "PDF parsing failed: Unable to extract text content using any method. "
            "This may be due to: 1) Empty or corrupted PDF, 2) Heavily encrypted PDF, "
            "3) PDF with only images/graphics, or 4) OCR engine issues. "
            "Please ensure the PDF contains readable text or try converting it to a text format."
        )
    
    @staticmethod
    def parse_markdown(file_content: bytes) -> str:
        """Parse Markdown file content"""
        try:
            # Convert bytes to string with multiple encoding attempts
            text_content = None
            encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    text_content = file_content.decode(encoding)
                    logger.debug(f"Successfully decoded markdown with {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if text_content is None:
                # Last resort: decode with errors ignored
                text_content = file_content.decode('utf-8', errors='ignore')
                logger.warning("Decoded markdown with error handling")
            
            # Return raw markdown text (we could also convert to HTML and extract text)
            return text_content.strip()
            
        except Exception as e:
            logger.error(f"Markdown parsing failed: {e}")
            raise ValueError(f"Markdown parsing failed: {str(e)}")
    
    @staticmethod
    def parse_text(file_content: bytes) -> str:
        """Parse text file content with improved encoding detection"""
        try:
            # Try different encodings in order of likelihood
            encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'big5', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    text_content = file_content.decode(encoding)
                    logger.debug(f"Successfully decoded text file with {encoding}")
                    return text_content.strip()
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, use utf-8 and ignore errors
            text_content = file_content.decode('utf-8', errors='ignore')
            logger.warning("Decoded text file with error handling")
            return text_content.strip()
            
        except Exception as e:
            logger.error(f"Text parsing failed: {e}")
            raise ValueError(f"Text parsing failed: {str(e)}")
    
    @classmethod
    def parse_file(cls, filename: str, file_content: bytes) -> Tuple[str, str]:
        """
        Parse file content with improved error handling and logging
        
        Args:
            filename: File name
            file_content: File content (bytes)
            
        Returns:
            Tuple[file_type, parsed_content]: File type and parsed content
        """
        if not file_content:
            raise ValueError("File content is empty")
        
        file_type = cls.get_file_type(filename)
        logger.info(f"Parsing file '{filename}' as type '{file_type}', size: {len(file_content)} bytes")
        
        try:
            if file_type == 'pdf':
                parsed_content = cls.parse_pdf(file_content)
            elif file_type == 'md':
                parsed_content = cls.parse_markdown(file_content)
            else:  # text
                parsed_content = cls.parse_text(file_content)
            
            if not parsed_content or not parsed_content.strip():
                raise ValueError(f"No content could be extracted from the {file_type} file")
            
            logger.info(f"Successfully parsed file '{filename}', extracted {len(parsed_content)} characters")
            return file_type, parsed_content
            
        except Exception as e:
            logger.error(f"Failed to parse file '{filename}': {e}")
            raise 