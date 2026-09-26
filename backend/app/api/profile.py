from fastapi import APIRouter, Depends, HTTPException, status
from app.db.database import get_db
from app.schemas.profile import ProfileResponse, ProfileUpdate
from app.services.user_service import UserService
from app.api.deps import get_current_user

router = APIRouter(prefix="/profile", tags=["User Profile"])


@router.get("", response_model=ProfileResponse)
def get_profile(
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get current logged-in user profile.
    """
    profile = UserService.get_profile(conn, current_user["id"])
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return profile


@router.put("", response_model=ProfileResponse)
def update_profile(
    body: ProfileUpdate,
    conn=Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update current logged-in user profile (name, email).
    """
    try:
        return UserService.update_profile(
            conn,
            user_id=current_user["id"],
            name=body.name,
            email=body.email,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
