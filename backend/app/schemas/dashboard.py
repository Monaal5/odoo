from typing import Any, List, Optional
from datetime import datetime
from pydantic import BaseModel


# ── KPI Card ─────────────────────────────────────────────────

class KPIsResponse(BaseModel):
    """Top-level KPI card data for the dashboard header."""
    total_products: int
    low_stock: int
    out_of_stock: int
    pending_receipts: int
    pending_deliveries: int
    pending_transfers: int


# ── Recent Activity (ledger feed) ─────────────────────────────

class ActivityEntry(BaseModel):
    """Single stock movement event shown in the dashboard activity feed."""
    id: str
    product_id: str
    product_name: Optional[str] = None
    warehouse_id: Optional[str] = None
    warehouse_name: Optional[str] = None
    qty_delta: float
    source_document_type: str
    source_document_id: Optional[str] = None
    created_at: datetime


class ActivityResponse(BaseModel):
    items: List[ActivityEntry]
    total: int


# ── Product / SKU search ───────────────────────────────────────

class ProductSearchResult(BaseModel):
    """Lightweight product hit for the search bar auto-complete."""
    id: str
    name: str
    sku: str
    unit_of_measure: str
    category_id: Optional[str] = None
    is_active: bool


class SearchResponse(BaseModel):
    items: List[ProductSearchResult]
    total: int
    query: str


# ── Filtered dashboard ────────────────────────────────────────

class FilteredMovement(BaseModel):
    """One row in the filtered movements table."""
    id: str
    document_type: str        # RECEIPT | DELIVERY | TRANSFER_IN | TRANSFER_OUT | ADJUSTMENT
    document_number: Optional[str] = None
    product_id: str
    product_name: Optional[str] = None
    warehouse_id: Optional[str] = None
    warehouse_name: Optional[str] = None
    qty_delta: float
    status: Optional[str] = None
    created_at: datetime


class FilterResponse(BaseModel):
    items: List[FilteredMovement]
    total: int


# ── Legacy schema kept for backward compat ────────────────────

class StockLevelItem(BaseModel):
    product_id: Any
    location_id: Any
    quantity: float


class DashboardKPIsResponse(BaseModel):
    total_products_in_stock: int
    total_units_in_stock: float
    low_stock_count: int
    pending_receipts: int
    pending_deliveries: int
    pending_transfers: int
    total_ledger_transactions: int
    stock_levels: List[StockLevelItem]
