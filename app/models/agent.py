from sqlalchemy import Column, String, Float, Integer, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    icon = Column(String, default="📝")
    category = Column(String, nullable=False)  # analysis, validation, generation, optimization
    color = Column(String, default="#1890ff")
    system_prompt = Column(Text, nullable=False)
    model = Column(String, nullable=False)
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=1000)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 