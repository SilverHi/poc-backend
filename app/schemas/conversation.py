from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime


class ConversationMessageBase(BaseModel):
    node_type: str
    content: str
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    resources: Optional[str] = None  # JSON string
    execution_logs: Optional[str] = None  # JSON string
    is_current_input: bool = False
    is_editable: bool = False


class ConversationMessageCreate(ConversationMessageBase):
    conversation_id: str


class ConversationMessage(ConversationMessageBase):
    id: str
    conversation_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    title: str


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    title: Optional[str] = None


class Conversation(ConversationBase):
    id: str
    created_at: datetime
    updated_at: datetime
    messages: List[ConversationMessage] = []
    
    class Config:
        from_attributes = True


class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int
    
    class Config:
        from_attributes = True


class SaveConversationRequest(BaseModel):
    title: str
    conversation_nodes: List[Any]  # Will contain the conversation nodes from frontend 