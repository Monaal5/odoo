from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from pydantic import BaseModel, ConfigDict, model_validator

class AdjustmentCreate(BaseModel):
    product_id: int
    location_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    counted_qty: Optional[int] = None
    counted_quantity: Optional[int] = None
    reason: Optional[str] = "Inventory Count Adjustment"

    @model_validator(mode="before")
    @classmethod
    def resolve_aliases(cls, data: dict):
        if isinstance(data, dict):
            if "location_id" not in data and "warehouse_id" in data:
                data["location_id"] = data["warehouse_id"]
            if "counted_qty" not in data and "counted_quantity" in data:
                data["counted_qty"] = data["counted_quantity"]
        return data

class AdjustmentResponse(BaseModel):
    id: int
    adjustment_number: str
    product_id: int
    location_id: int
    counted_qty: int
    system_qty: int
    delta_qty: int
    reason: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
