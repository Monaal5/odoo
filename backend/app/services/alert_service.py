from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.alert import Alert
from app.models.reorder_rule import ReorderRule

class AlertService:
    """Service handling low-stock detection, alert generation, and resolution."""

    DEFAULT_MIN_STOCK = 20  # Default minimum threshold if no reorder rule exists

    @staticmethod
    def check_and_trigger_alerts(db: Session, product_id: int, location_id: int, current_stock: int) -> Optional[Alert]:
        """
        Check if current stock is below minimum reorder rule threshold.
        Generates low-stock alert if current_stock < min_qty.
        Resolves alert if current_stock >= min_qty.
        """
        rule = db.query(ReorderRule).filter(
            ReorderRule.product_id == product_id,
            ReorderRule.location_id == location_id
        ).first()

        min_threshold = rule.min_qty if rule else AlertService.DEFAULT_MIN_STOCK

        active_alert = db.query(Alert).filter(
            Alert.product_id == product_id,
            Alert.location_id == location_id,
            Alert.status == "ACTIVE"
        ).first()

        if current_stock < min_threshold:
            if not active_alert:
                active_alert = Alert(
                    product_id=product_id,
                    location_id=location_id,
                    current_stock=current_stock,
                    min_stock=min_threshold,
                    status="ACTIVE",
                    message=f"Low Stock Alert: Product #{product_id} at Location #{location_id} has {current_stock} units (below min threshold {min_threshold})"
                )
                db.add(active_alert)
            else:
                active_alert.current_stock = current_stock
                active_alert.min_stock = min_threshold

            db.flush()
            return active_alert
        else:
            if active_alert:
                active_alert.status = "RESOLVED"
                db.flush()
            return None

    @staticmethod
    def get_active_alerts(db: Session, skip: int = 0, limit: int = 100) -> List[Alert]:
        """Retrieve all active low-stock alerts for dashboard display."""
        return db.query(Alert).filter(Alert.status == "ACTIVE").order_by(Alert.id.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_current_stock(conn, product_id: int, location_id: int) -> float:
        from app.db.database import dict_cursor
        with dict_cursor(conn) as cur:
            cur.execute(
                """SELECT quantity FROM stock_levels
                   WHERE product_id = %s AND location_id = %s""",
                (product_id, location_id),
            )
            row = cur.fetchone()
            return float(row["quantity"]) if row else 0.0

    @staticmethod
    def evaluate_reorder_alert(conn, product_id: int, location_id: int) -> None:
        """Re-check stock for (product_id, location_id) against its reorder rule."""
        from app.db.database import dict_cursor
        product_id = int(product_id)
        location_id = int(location_id)

        with dict_cursor(conn) as cur:
            cur.execute(
                """SELECT min_qty FROM reorder_rules
                   WHERE product_id = %s AND location_id = %s""",
                (product_id, location_id),
            )
            rule = cur.fetchone()
            if not rule:
                return

            min_qty = float(rule["min_qty"])
            current_stock = AlertService.get_current_stock(conn, product_id, location_id)

            cur.execute(
                """SELECT id FROM alerts
                   WHERE product_id = %s AND location_id = %s AND status = 'ACTIVE'""",
                (product_id, location_id),
            )
            existing_alert = cur.fetchone()

            if current_stock < min_qty:
                if existing_alert:
                    cur.execute(
                        """UPDATE alerts
                           SET current_stock = %s, min_stock = %s, updated_at = NOW()
                           WHERE id = %s""",
                        (current_stock, min_qty, existing_alert["id"]),
                    )
                else:
                    cur.execute(
                        """INSERT INTO alerts
                               (product_id, location_id, current_stock, min_stock, status)
                           VALUES (%s, %s, %s, %s, 'ACTIVE')""",
                        (product_id, location_id, current_stock, min_qty),
                    )
            else:
                if existing_alert:
                    cur.execute(
                        """UPDATE alerts
                           SET status = 'RESOLVED', current_stock = %s, updated_at = NOW()
                           WHERE id = %s""",
                        (current_stock, existing_alert["id"]),
                    )

    @staticmethod
    def dismiss_alert(db: Session, alert_id: int) -> Optional[Alert]:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            alert.status = "DISMISSED"
            db.commit()
            db.refresh(alert)
        return alert


