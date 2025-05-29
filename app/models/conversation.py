from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship to conversation messages
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan")


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"
    
    id = Column(String, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    node_type = Column(String, nullable=False)  # 'input' or 'output'
    content = Column(Text, nullable=False)
    agent_id = Column(String, nullable=True)  # Agent used for this message
    agent_name = Column(String, nullable=True)  # Agent name for display
    resources = Column(Text, nullable=True)  # JSON string of resources
    execution_logs = Column(Text, nullable=True)  # JSON string of logs
    is_current_input = Column(Boolean, default=False)
    is_editable = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship back to conversation
    conversation = relationship("Conversation", back_populates="messages") 