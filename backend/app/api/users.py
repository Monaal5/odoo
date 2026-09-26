from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.db.database import get_db
from app.schemas.user import UserResponse, RoleUpdate
from app.services.user_service import UserService
from app.api.deps import get_current_user, require_manager

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=List[UserResponse])
def list_users(
    conn=Depends(get_db),
    current_user: dict = Depends(require_manager),
):
    """
    List all registered users (Inventory Manager only).
    """
    return UserService.list_users(conn)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get a single user by UUID (Requires authentication).
    """
    user = UserService.get_profile(conn, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: str,
    body: RoleUpdate,
    conn=Depends(get_db),
    current_user: dict = Depends(require_manager),
):
    """
    Change user role (Inventory Manager / Admin only).
    Supported roles: 'inventory_manager', 'warehouse_staff'.
    """
    try:
        return UserService.update_user_role(conn, user_id, body.role)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
