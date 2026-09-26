import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings
from app.db.database import dict_cursor


# ─── Password helpers ────────────────────────────────────────

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ─── JWT helpers ─────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


# ─── OTP helpers ─────────────────────────────────────────────

def generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


# ─── Auth Service ─────────────────────────────────────────────

class AuthService:

    @staticmethod
    def signup(conn, name: str, email: str, password: str, role: str) -> dict:
        """Create a new user. Raises ValueError if email already taken."""
        import uuid
        with dict_cursor(conn) as cur:
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                raise ValueError("Email already registered")

            if role not in ("inventory_manager", "warehouse_staff"):
                raise ValueError("Invalid role")

            hashed = hash_password(password)
            user_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO users (id, name, email, password_hash, role)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (user_id, name, email, hashed, role),
            )
            cur.execute(
                "SELECT id, name, email, role, is_active, created_at, updated_at FROM users WHERE id = %s",
                (user_id,),
            )
            return dict(cur.fetchone())

    @staticmethod
    def login(conn, email: str, password: str) -> dict:
        """Validate credentials and return a JWT token payload."""
        with dict_cursor(conn) as cur:
            cur.execute(
                "SELECT id, name, email, role, password_hash, is_active FROM users WHERE email = %s",
                (email,),
            )
            user = cur.fetchone()

        if not user or not verify_password(password, user["password_hash"]):
            raise ValueError("Invalid email or password")

        if not user["is_active"]:
            raise ValueError("Account is deactivated")

        token = create_access_token(
            {"sub": str(user["id"]), "role": user["role"]}
        )
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": str(user["id"]),
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
        }

    @staticmethod
    def forgot_password(conn, email: str) -> str:
        """
        Generate and store a 6-digit OTP valid for 15 minutes.
        Returns the OTP (caller decides how to deliver it — console/email/SMS).
        """
        with dict_cursor(conn) as cur:
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cur.fetchone()

        if not user:
            # Don't leak whether email exists
            return None

        otp = generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)

        with dict_cursor(conn) as cur:
            cur.execute(
                "UPDATE users SET otp_code = %s, otp_expires_at = %s WHERE email = %s",
                (otp, expires_at, email),
            )

        return otp

    @staticmethod
    def reset_password(conn, email: str, otp: str, new_password: str) -> None:
        """Validate OTP and set a new password."""
        with dict_cursor(conn) as cur:
            cur.execute(
                "SELECT otp_code, otp_expires_at FROM users WHERE email = %s",
                (email,),
            )
            user = cur.fetchone()

        if not user:
            raise ValueError("Invalid request")

        if user["otp_code"] != otp:
            raise ValueError("Invalid OTP")

        if not user["otp_expires_at"] or user["otp_expires_at"] < datetime.now(timezone.utc):
            raise ValueError("OTP has expired")

        hashed = hash_password(new_password)
        with dict_cursor(conn) as cur:
            cur.execute(
                """UPDATE users
                   SET password_hash = %s, otp_code = NULL, otp_expires_at = NULL,
                       updated_at = CURRENT_TIMESTAMP
                   WHERE email = %s""",
                (hashed, email),
            )

