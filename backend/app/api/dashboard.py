from typing import List, Optional
from fastapi import APIRouter, Depends, Query

from app.db.database import get_db
from app.schemas.dashboard import (
    KPIsResponse,
    ActivityResponse,
    FilterResponse,
    DashboardKPIsResponse,
    ActivityItem,
    DashboardFilterResponse,
)
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/kpis")
def get_kpis(conn=Depends(get_db)):
    """All KPI cards for the dashboard header."""
    return DashboardService.get_kpis(conn)


@router.get("/activity")
def get_activity(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    conn=Depends(get_db),
):
    """Recent stock movements for the dashboard activity feed."""
    return DashboardService.get_activity(conn, limit=limit, skip=skip)


@router.get("/filter")
def get_filtered_movements(
    doc_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    warehouse_id: Optional[str] = Query(None),
    location_id: Optional[int] = Query(None),
    category_id: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    product_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    conn=Depends(get_db),
):
    """Filterable stock movement table and dashboard metrics."""
    target_wh = str(location_id) if location_id is not None else warehouse_id
    target_cat = category_id or category
    return DashboardService.get_filtered(
        conn,
        doc_type=doc_type,
        status=status,
        warehouse_id=target_wh,
        category_id=target_cat,
        product_id=product_id,
        skip=skip,
        limit=limit,
    )
