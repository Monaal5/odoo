from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AIChatRequest(BaseModel):
    query: str = Field(..., description="Natural language prompt, e.g. 'How much steel is in Rack B?'")


class AIChatResponse(BaseModel):
    answer: str = Field(..., description="Assistant answer detailing current stock or operational status")
    context: Optional[Dict[str, Any]] = Field(None, description="Optional metadata/context used")
