import os
from typing import Tuple
import PyPDF2
import markdown
from io import BytesIO


class FileParser:
    """文件解析器，支持PDF、Markdown和文本文件"""
    
    @staticmethod
    def get_file_type(filename: str) -> str:
        """根据文件扩展名确定文件类型"""
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.pdf':
            return 'pdf'
        elif ext in ['.md', '.markdown']:
            return 'md'
        elif ext in ['.txt', '.text']:
            return 'text'
        else:
            return 'text'  # 默认作为文本处理
    
    @staticmethod
    def parse_pdf(file_content: bytes) -> str:
        """解析PDF文件内容"""
        try:
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
            return text_content.strip()
        except Exception as e:
            raise ValueError(f"PDF解析失败: {str(e)}")
    
    @staticmethod
    def parse_markdown(file_content: bytes) -> str:
        """解析Markdown文件内容"""
        try:
            # 将bytes转换为字符串
            text_content = file_content.decode('utf-8')
            
            # 使用markdown库解析，但我们主要需要纯文本
            # 这里可以选择返回原始markdown或转换为HTML后再提取文本
            # 为了简单起见，直接返回原始文本
            return text_content.strip()
        except Exception as e:
            raise ValueError(f"Markdown解析失败: {str(e)}")
    
    @staticmethod
    def parse_text(file_content: bytes) -> str:
        """解析文本文件内容"""
        try:
            # 尝试不同的编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
            
            for encoding in encodings:
                try:
                    text_content = file_content.decode(encoding)
                    return text_content.strip()
                except UnicodeDecodeError:
                    continue
            
            # 如果所有编码都失败，使用utf-8并忽略错误
            return file_content.decode('utf-8', errors='ignore').strip()
        except Exception as e:
            raise ValueError(f"文本解析失败: {str(e)}")
    
    @classmethod
    def parse_file(cls, filename: str, file_content: bytes) -> Tuple[str, str]:
        """
        解析文件内容
        
        Args:
            filename: 文件名
            file_content: 文件内容（bytes）
            
        Returns:
            Tuple[file_type, parsed_content]: 文件类型和解析后的内容
        """
        file_type = cls.get_file_type(filename)
        
        if file_type == 'pdf':
            parsed_content = cls.parse_pdf(file_content)
        elif file_type == 'md':
            parsed_content = cls.parse_markdown(file_content)
        else:  # text
            parsed_content = cls.parse_text(file_content)
        
        return file_type, parsed_content 