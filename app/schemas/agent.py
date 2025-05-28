from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    icon: str = "📝"
    category: str = Field(..., pattern="^(analysis|validation|generation|optimization)$")
    color: str = "#1890ff"
    system_prompt: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(1000, ge=1, le=8000)


class AgentCreate(AgentBase):
    pass


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    category: Optional[str] = Field(None, pattern="^(analysis|validation|generation|optimization)$")
    color: Optional[str] = None
    system_prompt: Optional[str] = Field(None, min_length=1)
    model: Optional[str] = Field(None, min_length=1)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, ge=1, le=8000)


class Agent(AgentBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AgentExecuteRequest(BaseModel):
    input: str = Field(..., min_length=1)


class AgentExecuteResponse(BaseModel):
    output: str
    logs: list[str] 