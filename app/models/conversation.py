from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    
    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, nullable=False, index=True)
    node_type = Column(String, nullable=False)  # query/answer/log
    content = Column(Text, nullable=False)
    sort = Column(Integer, nullable=False)  # 排序字段
    agent_id = Column(String, nullable=True)  # 允许为空，因为query类型可能没有agent
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 