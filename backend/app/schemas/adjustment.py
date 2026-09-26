from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class AdjustmentCreate(BaseModel):
    product_id: int
    location_id: int
    counted_qty: int
    reason: Optional[str] = "Inventory Count Adjustment"

class AdjustmentResponse(BaseModel):
    id: int
    adjustment_number: str
    product_id: int
    location_id: int
    counted_qty: int
    system_qty: int
    delta_qty: int
    reason: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
