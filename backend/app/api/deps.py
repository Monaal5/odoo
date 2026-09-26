from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.db.database import get_db, dict_cursor
from app.services.auth_service import decode_access_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    conn=Depends(get_db),
) -> dict:
    """
    FastAPI dependency validating Bearer JWT token from Authorization header.
    Returns authenticated user dict or raises 401 Unauthorized.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload["sub"]
    with dict_cursor(conn) as cur:
        cur.execute(
            "SELECT id, name, email, role, is_active FROM users WHERE id = %s",
            (user_id,),
        )
        user = cur.fetchone()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token no longer exists",
        )

    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    return dict(user)


def require_manager(current_user: dict = Depends(get_current_user)) -> dict:
    """Require user to have inventory_manager role."""
    if current_user.get("role") != "inventory_manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Action restricted to Inventory Managers",
        )
    return current_user
