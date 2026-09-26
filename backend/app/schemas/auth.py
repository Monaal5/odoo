from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


# ── Request Schemas ──────────────────────────────────────────

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "warehouse_staff"  # inventory_manager | warehouse_staff


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


# ── Response Schemas ─────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str
    email: str
    role: str


class MessageResponse(BaseModel):
    message: str
