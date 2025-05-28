from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ResourceBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class ResourceCreate(ResourceBase):
    file_name: str
    file_size: int
    file_type: str = Field(..., pattern="^(pdf|md|text)$")
    file_path: str
    parsed_content: str


class ResourceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None


class Resource(ResourceBase):
    id: str
    file_name: str
    file_size: int
    file_type: str
    parsed_content: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ResourceUploadResponse(BaseModel):
    id: str
    title: str
    file_name: str
    file_size: int
    file_type: str
    message: str 