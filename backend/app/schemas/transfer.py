from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TransferCreate(BaseModel):
    product_id: str
    from_warehouse: Optional[str] = Field(None, alias="from_warehouse_id", description="Source warehouse/location UUID")
    to_warehouse: Optional[str] = Field(None, alias="to_warehouse_id", description="Destination warehouse/location UUID")
    quantity: float = Field(..., gt=0, description="Quantity to transfer")

    class Config:
        populate_by_name = True


class TransferResponse(BaseModel):
    id: str
    transfer_number: str
    product_id: str
    from_warehouse: Optional[str] = None
    to_warehouse: Optional[str] = None
    quantity: float
    status: str
    created_at: datetime
    updated_at: datetime
