from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict

class MobileStockResponse(BaseModel):
    sku: str
    qty: float
    location: str

    model_config = ConfigDict(from_attributes=True)

class MobileCountRequest(BaseModel):
    sku: str
    qty: float
    location: Optional[str] = "Main Warehouse"

class MobileCountResponse(BaseModel):
    sku: str
    qty: float
    location: str
    status: str = "success"
    message: str = "Stock count updated successfully"

    model_config = ConfigDict(from_attributes=True)

class MobileTask(BaseModel):
    id: str
    task_type: str  # e.g., "Pick", "Receipt", "Transfer"
    doc_number: str
    location: str
    sku: Optional[str] = None
    qty: float
    status: str

    model_config = ConfigDict(from_attributes=True)
