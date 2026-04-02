from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, model_validator
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
    influencer_id: Optional[int] = None

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def extract_influencer_id(cls, data):
        # When populated from a SQLAlchemy model that has influencer_profile loaded
        if hasattr(data, "influencer_profile") and data.influencer_profile is not None:
            # Wrap in a dict so Pydantic can populate influencer_id
            from pydantic import ConfigDict
            obj = {col.name: getattr(data, col.name) for col in data.__table__.columns}
            obj["influencer_id"] = data.influencer_profile.id
            return obj
        return data
