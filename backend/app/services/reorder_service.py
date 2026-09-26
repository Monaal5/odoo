from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.reorder_rule import ReorderRule
from app.schemas.reorder_rule import ReorderRuleCreate

class ReorderService:
    """Service for managing min/max reordering rules per product and location."""

    @staticmethod
    def create_or_update_rule(db: Session, data: ReorderRuleCreate) -> ReorderRule:
        rule = db.query(ReorderRule).filter(
            ReorderRule.product_id == data.product_id,
            ReorderRule.location_id == data.location_id
        ).first()

        if not rule:
            rule = ReorderRule(
                product_id=data.product_id,
                location_id=data.location_id,
                min_qty=data.min_qty,
                max_qty=data.max_qty
            )
            db.add(rule)
        else:
            rule.min_qty = data.min_qty
            rule.max_qty = data.max_qty

        db.commit()
        db.refresh(rule)
        return rule

    @staticmethod
    def get_rule(db: Session, product_id: int, location_id: int) -> Optional[ReorderRule]:
        return db.query(ReorderRule).filter(
            ReorderRule.product_id == product_id,
            ReorderRule.location_id == location_id
        ).first()

    @staticmethod
    def list_rules(db: Session, skip: int = 0, limit: int = 100) -> List[ReorderRule]:
        return db.query(ReorderRule).offset(skip).limit(limit).all()
