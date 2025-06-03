from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ConversationMessageBase(BaseModel):
    conversation_id: str = Field(..., min_length=1, max_length=100)
    node_type: str = Field(..., pattern="^(query|answer|log)$")
    content: str = Field(..., min_length=1)
    sort: int = Field(..., ge=0)
    agent_id: Optional[str] = None


class ConversationMessageCreate(ConversationMessageBase):
    pass


class ConversationMessageUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    sort: Optional[int] = Field(None, ge=0)


class ConversationMessage(ConversationMessageBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationSummary(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int


class Conversation(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[ConversationMessage]


class SaveConversationRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    messages: List[ConversationMessageCreate] = Field(..., min_items=0) 