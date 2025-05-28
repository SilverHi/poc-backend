from typing import List, Optional
from pydantic import BaseModel


class OpenAIModel(BaseModel):
    id: str
    name: str
    max_tokens: int
    description: str


class OpenAIConfig(BaseModel):
    models: List[OpenAIModel]
    default_model: str
    default_temperature: float
    default_max_tokens: int
    is_configured: bool
    has_api_key: bool


class OpenAIConfigUpdate(BaseModel):
    api_key: Optional[str] = None
    default_model: Optional[str] = None
    default_temperature: Optional[float] = None
    default_max_tokens: Optional[int] = None 