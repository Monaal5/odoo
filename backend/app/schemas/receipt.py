from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field


class ReceiptItemCreate(BaseModel):
    product_id: Union[str, int]
    quantity: float = Field(..., gt=0, description="Quantity received")


class ReceiptItemResponse(BaseModel):
    id: Union[str, int]
    receipt_id: Union[str, int]
    product_id: Union[str, int]
    quantity: float


class ReceiptCreate(BaseModel):
    supplier: str = Field(..., alias="supplier_name", description="Supplier name")
    warehouse_id: Optional[Union[str, int]] = None
    items: List[ReceiptItemCreate]

    class Config:
        populate_by_name = True


class ReceiptResponse(BaseModel):
    id: Union[str, int]
    receipt_number: str
    supplier: str
    warehouse_id: Optional[Union[str, int]] = None
    status: str
    items: List[ReceiptItemResponse]
    created_at: datetime
    updated_at: datetime
