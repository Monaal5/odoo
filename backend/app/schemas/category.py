from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ── Request Schemas ──────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# ── Response Schema ──────────────────────────────────────────

class CategoryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
