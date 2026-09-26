from fastapi import APIRouter, Depends, HTTPException
from app.db.database import get_db, dict_cursor
from app.schemas.user import UserResponse
from app.api.deps import get_current_user, require_manager

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=list[UserResponse])
def list_users(conn=Depends(get_db), current_user: dict = Depends(require_manager)):
    """List all users (Inventory Manager only)."""
    with dict_cursor(conn) as cur:
        cur.execute(
            "SELECT id, name, email, role, is_active, created_at, updated_at FROM users ORDER BY created_at DESC"
        )
        return [dict(r) for r in cur.fetchall()]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, conn=Depends(get_db), current_user: dict = Depends(get_current_user)):
    """Get a single user by UUID (Requires login)."""
    with dict_cursor(conn) as cur:
        cur.execute(
            "SELECT id, name, email, role, is_active, created_at, updated_at FROM users WHERE id = %s",
            (user_id,),
        )
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(row)
