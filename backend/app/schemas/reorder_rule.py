from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, model_validator

class ReorderRuleCreate(BaseModel):
    product_id: int
    location_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    min_qty: int = 5
    max_qty: int = 50

    @model_validator(mode="before")
    @classmethod
    def resolve_warehouse_id(cls, data: dict):
        if isinstance(data, dict):
            if "location_id" not in data and "warehouse_id" in data:
                data["location_id"] = data["warehouse_id"]
        return data

class ReorderRuleResponse(BaseModel):
    id: int
    product_id: int
    location_id: int
    min_qty: int
    max_qty: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
