from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
