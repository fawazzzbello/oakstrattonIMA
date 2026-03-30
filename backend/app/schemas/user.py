from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    timezone: str = "UTC"
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.CLIENT


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    avatar_url: Optional[str] = None


class UserAdminUpdate(UserUpdate):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
