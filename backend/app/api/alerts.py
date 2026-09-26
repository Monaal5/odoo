from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.database import get_sqlalchemy_db as get_db
from app.schemas.alert import AlertResponse
from app.schemas.reorder_rule import ReorderRuleCreate, ReorderRuleResponse
from app.services.alert_service import AlertService
from app.services.reorder_service import ReorderService

router = APIRouter(prefix="/alerts", tags=["Low Stock Alerts Engine"])

@router.get("", response_model=List[AlertResponse])
def list_active_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Retrieve active low-stock alerts."""
    return AlertService.get_active_alerts(db, skip=skip, limit=limit)


@router.post("/reorder-rules", response_model=ReorderRuleResponse, status_code=status.HTTP_201_CREATED)
def set_reorder_rule(data: ReorderRuleCreate, db: Session = Depends(get_db)):
    """Set or update min/max reorder rule thresholds for a product and location."""
    return ReorderService.create_or_update_rule(db, data)


@router.get("/reorder-rules", response_model=List[ReorderRuleResponse])
def list_reorder_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """List all reorder rules."""
    return ReorderService.list_rules(db, skip=skip, limit=limit)


@router.post("/{alert_id}/dismiss", response_model=AlertResponse)
def dismiss_alert(alert_id: int, db: Session = Depends(get_db)):
    """Dismiss a low-stock alert."""
    alert = AlertService.dismiss_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
