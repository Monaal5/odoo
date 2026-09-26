from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ── Request Schemas ──────────────────────────────────────────

class WarehouseCreate(BaseModel):
    name: str
    code: str
    address: Optional[str] = None
    parent_id: Optional[str] = None   # UUID of parent location


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    address: Optional[str] = None
    parent_id: Optional[str] = None
    is_active: Optional[bool] = None


# ── Response Schema ──────────────────────────────────────────

class WarehouseResponse(BaseModel):
    id: str
    name: str
    code: str
    address: Optional[str]
    parent_id: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
