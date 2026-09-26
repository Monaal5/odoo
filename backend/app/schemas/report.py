from typing import Optional, List
from pydantic import BaseModel


class StockReportItem(BaseModel):
    sku: str
    product_name: str
    warehouse_name: str
    quantity: float
    reorder_min: Optional[float] = 0
    is_low_stock: Optional[bool] = False
