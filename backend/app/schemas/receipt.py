from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ReceiptItemCreate(BaseModel):
    product_id: str
    quantity: float = Field(..., gt=0, description="Quantity received")


class ReceiptItemResponse(BaseModel):
    id: str
    receipt_id: str
    product_id: str
    quantity: float


class ReceiptCreate(BaseModel):
    supplier: str = Field(..., alias="supplier_name", description="Supplier name")
    warehouse_id: Optional[str] = None
    items: List[ReceiptItemCreate]

    class Config:
        populate_by_name = True


class ReceiptResponse(BaseModel):
    id: str
    receipt_number: str
    supplier: str
    warehouse_id: Optional[str] = None
    status: str
    items: List[ReceiptItemResponse]
    created_at: datetime
    updated_at: datetime
