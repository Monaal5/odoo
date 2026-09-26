from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ── Request Schemas ──────────────────────────────────────────

class ProductCreate(BaseModel):
    name: str
    sku: str
    category_id: Optional[str] = None
    unit_of_measure: str = "units"
    reorder_min: float = 0
    reorder_max: float = 0
    description: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    category_id: Optional[str] = None
    unit_of_measure: Optional[str] = None
    reorder_min: Optional[float] = None
    reorder_max: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# ── Response Schema ──────────────────────────────────────────

class ProductResponse(BaseModel):
    id: str
    name: str
    sku: str
    category_id: Optional[str]
    unit_of_measure: str
    reorder_min: float
    reorder_max: float
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
