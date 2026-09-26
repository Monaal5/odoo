import logging
from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2 import IntegrityError

from app.db.database import get_db
from app.schemas.auth import (
    SignupRequest, LoginRequest,
    ForgotPasswordRequest, ResetPasswordRequest,
    TokenResponse, MessageResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = logging.getLogger(__name__)


@router.post("/signup", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest, conn=Depends(get_db)):
    """Register a new user account."""
    try:
        AuthService.signup(conn, body.name, body.email, body.password, body.role)
        return {"message": "Account created successfully. Please log in."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, conn=Depends(get_db)):
    """Authenticate and receive a JWT access token."""
    try:
        return AuthService.login(conn, body.email, body.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(body: ForgotPasswordRequest, conn=Depends(get_db)):
    """
    Generate a 6-digit OTP for password reset.
    OTP is logged to the console (dev mode). Wire up SendGrid/Twilio later.
    """
    otp = AuthService.forgot_password(conn, body.email)
    if otp:
        # ── DEV: log OTP to console. Replace with email/SMS send in production ──
        logger.warning(f"[DEV] OTP for {body.email}: {otp}")
        print(f"\n>>> [DEV] Password reset OTP for {body.email}: {otp}\n")
    # Always return generic message to avoid user enumeration
    return {"message": "If that email is registered, you will receive an OTP shortly."}


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(body: ResetPasswordRequest, conn=Depends(get_db)):
    """Validate OTP and set a new password."""
    try:
        AuthService.reset_password(conn, body.email, body.otp, body.new_password)
        return {"message": "Password reset successfully. Please log in."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
