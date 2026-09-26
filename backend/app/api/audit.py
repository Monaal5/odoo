from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db, get_sqlalchemy_db
from app.schemas.audit import AuditLogCreate, AuditLogResponse
from app.services.audit_service import AuditService
from app.api.deps import get_optional_user

router = APIRouter(prefix="/audit", tags=["Audit Logs & Trail"])


@router.get("", response_model=List[AuditLogResponse])
@router.get("/", response_model=List[AuditLogResponse])
def get_audit_logs(
    user_id: Optional[str] = Query(None, description="Filter by user name or ID"),
    action: Optional[str] = Query(None, description="Filter by action (CREATE, VALIDATE, ADJUST)"),
    entity: Optional[str] = Query(None, description="Filter by entity (Product, Receipt, Stock, Delivery)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_sqlalchemy_db),
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """
    Retrieve system audit log entries.
    Example entries logged:
      - Monaal | CREATE | Product
      - Rahul  | VALIDATE | Receipt
      - Admin  | ADJUST | Stock
    """
    return AuditService.get_audit_logs(
        db=db,
        user_id=user_id,
        action=action,
        entity=entity,
        skip=skip,
        limit=limit,
    )


@router.post("", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=AuditLogResponse, status_code=status.HTTP_201_CREATED)
def create_audit_log(
    data: AuditLogCreate,
    db: Session = Depends(get_sqlalchemy_db),
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Manually post an audit log entry."""
    user_name = (current_user.get("name") if current_user else None) or data.user_id or "System"
    result = AuditService.log_action(
        db=db,
        action=data.action,
        entity=data.entity,
        entity_id=data.entity_id,
        user_id=user_name,
        ip_address=data.ip_address,
    )
    return result

