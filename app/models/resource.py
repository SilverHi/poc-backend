from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    file_name = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, md, text
    file_path = Column(String, nullable=False)  # 文件存储路径
    parsed_content = Column(Text, nullable=False)  # 解析后的文本内容
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 