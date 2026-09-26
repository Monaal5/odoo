from typing import Optional, List
from app.db.database import dict_cursor
from app.services.product_service import clean_uuid


class UserService:
    """Service handling profile management and admin user management."""

    @staticmethod
    def get_profile(conn, user_id: str) -> Optional[dict]:
        """Fetch current authenticated user's profile."""
        u_id = clean_uuid(user_id) or user_id
        with dict_cursor(conn) as cur:
            cur.execute(
                """SELECT id, name, email, role, is_active, created_at, updated_at
                   FROM users WHERE id = %s""",
                (u_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    @staticmethod
    def update_profile(conn, user_id: str, name: Optional[str] = None, email: Optional[str] = None) -> dict:
        """Update current authenticated user's profile details."""
        u_id = clean_uuid(user_id) or user_id

        with dict_cursor(conn) as cur:
            if email:
                cur.execute(
                    "SELECT id FROM users WHERE email = %s AND id != %s",
                    (email, u_id),
                )
                if cur.fetchone():
                    raise ValueError(f"Email '{email}' is already in use by another user.")

            fields, values = [], []
            if name is not None and name.strip():
                fields.append("name = %s")
                values.append(name.strip())
            if email is not None and email.strip():
                fields.append("email = %s")
                values.append(email.strip())

            if not fields:
                return UserService.get_profile(conn, u_id)

            fields.append("updated_at = NOW()")
            values.append(u_id)

            sql = f"""UPDATE users
                      SET {', '.join(fields)}
                      WHERE id = %s
                      RETURNING id, name, email, role, is_active, created_at, updated_at"""
            cur.execute(sql, values)
            row = cur.fetchone()
            if not row:
                raise ValueError("User not found.")
            return dict(row)

    @staticmethod
    def list_users(conn) -> List[dict]:
        """List all registered users (Admin / Manager only)."""
        with dict_cursor(conn) as cur:
            cur.execute(
                """SELECT id, name, email, role, is_active, created_at, updated_at
                   FROM users
                   ORDER BY created_at DESC"""
            )
            return [dict(r) for r in cur.fetchall()]

    @staticmethod
    def update_user_role(conn, target_user_id: str, new_role: str) -> dict:
        """Change a user's role (Inventory Manager only)."""
        u_id = clean_uuid(target_user_id) or target_user_id
        valid_roles = ("inventory_manager", "warehouse_staff")
        if new_role not in valid_roles:
            raise ValueError(f"Invalid role '{new_role}'. Role must be one of: {', '.join(valid_roles)}")

        with dict_cursor(conn) as cur:
            cur.execute(
                """UPDATE users
                   SET role = %s, updated_at = NOW()
                   WHERE id = %s
                   RETURNING id, name, email, role, is_active, created_at, updated_at""",
                (new_role, u_id),
            )
            row = cur.fetchone()
            if not row:
                raise ValueError(f"User with ID '{target_user_id}' not found.")
            return dict(row)
