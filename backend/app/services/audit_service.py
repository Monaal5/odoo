import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.db.database import dict_cursor

logger = logging.getLogger(__name__)


class AuditService:
    """Service to log and retrieve system audit trail events."""

    @staticmethod
    def log_action(
        db,
        action: str,
        entity: str,
        entity_id: Optional[Any] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Record a single audit trail entry into the audit_logs table.
        Example entries:
            User: Monaal | Action: CREATE   | Entity: Product
            User: Rahul  | Action: VALIDATE | Entity: Receipt
            User: Admin  | Action: ADJUST   | Entity: Stock
        """
        user_str = user_id or "System"
        entity_id_str = str(entity_id) if entity_id is not None else None

        # Handle SQLAlchemy Session
        if isinstance(db, Session):
            try:
                log_entry = AuditLog(
                    user_id=user_str,
                    action=action.upper(),
                    entity=entity,
                    entity_id=entity_id_str,
                    ip_address=ip_address,
                )
                db.add(log_entry)
                db.commit()
                db.refresh(log_entry)
                return {
                    "id": log_entry.id,
                    "user_id": log_entry.user_id,
                    "action": log_entry.action,
                    "entity": log_entry.entity,
                    "entity_id": log_entry.entity_id,
                    "timestamp": log_entry.timestamp,
                    "ip_address": log_entry.ip_address,
                }
            except Exception as e:
                logger.error(f"Failed to record audit log via SQLAlchemy: {e}")
                db.rollback()
                return None

        # Handle Raw Connection
        else:
            try:
                with dict_cursor(db) as cur:
                    cur.execute(
                        """
                        INSERT INTO audit_logs (user_id, action, entity, entity_id, ip_address)
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (user_str, action.upper(), entity, entity_id_str, ip_address),
                    )
                    # Fetch inserted log if needed
                    cur.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT 1")
                    row = cur.fetchone()
                    return dict(row) if row else None
            except Exception as e:
                logger.error(f"Failed to record audit log via raw connection: {e}")
                return None

    @staticmethod
    def get_audit_logs(
        db,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        entity: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Fetch audit log entries with optional filters."""
        if isinstance(db, Session):
            query = db.query(AuditLog)
            if user_id:
                query = query.filter(AuditLog.user_id.ilike(f"%{user_id}%"))
            if action:
                query = query.filter(AuditLog.action == action.upper())
            if entity:
                query = query.filter(AuditLog.entity.ilike(f"%{entity}%"))

            logs = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()
            return [
                {
                    "id": l.id,
                    "user_id": l.user_id,
                    "action": l.action,
                    "entity": l.entity,
                    "entity_id": l.entity_id,
                    "timestamp": l.timestamp,
                    "ip_address": l.ip_address,
                }
                for l in logs
            ]
        else:
            with dict_cursor(db) as cur:
                where_clauses = []
                params = []
                if user_id:
                    where_clauses.append("LOWER(user_id) LIKE %s")
                    params.append(f"%{user_id.lower()}%")
                if action:
                    where_clauses.append("action = %s")
                    params.append(action.upper())
                if entity:
                    where_clauses.append("LOWER(entity) LIKE %s")
                    params.append(f"%{entity.lower()}%")

                where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
                sql = f"SELECT * FROM audit_logs {where_sql} ORDER BY timestamp DESC LIMIT %s OFFSET %s"
                params.extend([limit, skip])

                cur.execute(sql, tuple(params))
                rows = cur.fetchall()
                return [dict(r) for r in rows]
