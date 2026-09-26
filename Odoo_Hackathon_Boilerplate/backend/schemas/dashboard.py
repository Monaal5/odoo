from typing import Dict, Any, List
from pydantic import BaseModel

class StockLevelItem(BaseModel):
    product_id: int
    location_id: int
    quantity: int

class DashboardKPIsResponse(BaseModel):
    total_products_in_stock: int
    total_units_in_stock: int
    low_stock_count: int
    pending_receipts: int
    pending_deliveries: int
    pending_transfers: int
    total_ledger_transactions: int
    stock_levels: List[StockLevelItem]
