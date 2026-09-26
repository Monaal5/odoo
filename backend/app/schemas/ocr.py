from typing import Optional, List
from pydantic import BaseModel, Field


class OCRLineItem(BaseModel):
    product_name: str
    sku: Optional[str] = None
    product_id: Optional[str] = None
    quantity: float
    unit_price: Optional[float] = None


class OCRScanResponse(BaseModel):
    supplier_name: Optional[str] = "Detected Supplier"
    document_number: Optional[str] = None
    items: List[OCRLineItem]
    confidence: float = 0.95
    raw_text: Optional[str] = None


class OCRReceiptCreateResponse(BaseModel):
    receipt_id: str
    receipt_number: str
    supplier: str
    status: str
    items_count: int
    detected_items: List[OCRLineItem]
