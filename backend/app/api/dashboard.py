from typing import Optional
from fastapi import APIRouter, Depends, Query

from app.db.database import get_db
from app.api.deps import get_current_user
from app.schemas.dashboard import (
    KPIsResponse,
    ActivityResponse,
    FilterResponse,
    DashboardKPIsResponse,
)
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/kpis", response_model=KPIsResponse)
def get_kpis(
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    All KPI cards for the dashboard header.

    Returns counts for:
    - total active products
    - low-stock and out-of-stock products (derived from the ledger)
    - pending receipts, deliveries, and internal transfers
    """
    return DashboardService.get_kpis(conn)


@router.get("/activity", response_model=ActivityResponse)
def get_activity(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=200, description="Max entries to return"),
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Recent stock movements for the dashboard activity feed.

    Returns ledger entries in descending chronological order, enriched
    with product name and warehouse name for direct display.
    """
    return DashboardService.get_activity(conn, limit=limit, skip=skip)


@router.get("/filter", response_model=FilterResponse)
def get_filtered_movements(
    doc_type: Optional[str] = Query(
        None,
        description="Document type: RECEIPT | DELIVERY | TRANSFER_IN | TRANSFER_OUT | ADJUSTMENT",
    ),
    status: Optional[str] = Query(
        None,
        description="Document status: Draft | Waiting | Ready | Done | Cancelled",
    ),
    warehouse_id: Optional[str] = Query(None, description="Filter by warehouse UUID"),
    category_id: Optional[str] = Query(None, description="Filter by product category UUID"),
    product_id: Optional[str] = Query(None, description="Filter by product UUID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Filterable stock movement table.

    All filters are optional and combinable.  Results include the resolved
    source document number and status so the frontend can display full context
    without additional round-trips.
    """
    return DashboardService.get_filtered(
        conn,
        doc_type=doc_type,
        status=status,
        warehouse_id=warehouse_id,
        category_id=category_id,
        product_id=product_id,
        skip=skip,
        limit=limit,
    )
