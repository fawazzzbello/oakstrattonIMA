from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


# --- Platform Settings ---

class PlatformSettingsResponse(BaseModel):
    id: int
    agency_name: str
    agency_tagline: Optional[str] = None
    agency_logo_url: Optional[str] = None
    primary_color: str
    accent_color: str
    bg_base_color: str
    surface_color: str
    font_heading: str
    font_body: str
    support_email: Optional[str] = None
    terms_url: Optional[str] = None
    privacy_url: Optional[str] = None
    custom_css: Optional[str] = None
    features_config: Optional[dict] = None
    max_ai_requests_per_day: int
    ai_provider_override: Optional[str] = None
    ai_model_override: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PlatformSettingsUpdate(BaseModel):
    agency_name: Optional[str] = None
    agency_tagline: Optional[str] = None
    agency_logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    accent_color: Optional[str] = None
    bg_base_color: Optional[str] = None
    surface_color: Optional[str] = None
    font_heading: Optional[str] = None
    font_body: Optional[str] = None
    support_email: Optional[str] = None
    terms_url: Optional[str] = None
    privacy_url: Optional[str] = None
    custom_css: Optional[str] = None
    features_config: Optional[dict] = None
    max_ai_requests_per_day: Optional[int] = None
    ai_provider_override: Optional[str] = None
    ai_model_override: Optional[str] = None


# --- Feature Flags ---

class FeatureFlagResponse(BaseModel):
    id: int
    flag_key: str
    flag_name: str
    description: Optional[str] = None
    is_enabled: bool
    enabled_for_roles: Optional[dict] = None
    created_by_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FeatureFlagCreate(BaseModel):
    flag_key: str
    flag_name: str
    description: Optional[str] = None
    is_enabled: bool = True
    enabled_for_roles: Optional[dict] = None


class FeatureFlagUpdate(BaseModel):
    flag_name: Optional[str] = None
    description: Optional[str] = None
    is_enabled: Optional[bool] = None
    enabled_for_roles: Optional[dict] = None


# --- Audit Log ---

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_email: str
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    extra_data: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Admin User Management ---

class AdminUserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    phone: Optional[str] = None
    timezone: str
    avatar_url: Optional[str] = None
    last_login_at: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AdminUserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.CLIENT
    is_active: bool = True
    is_verified: bool = False
    phone: Optional[str] = None
    timezone: str = "UTC"


class AdminUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    avatar_url: Optional[str] = None


# --- Admin Stats ---

class AdminStatsResponse(BaseModel):
    total_users: int
    total_campaigns: int
    total_influencers: int
    total_clients: int
    total_revenue: float
    active_campaigns: int
    users_by_role: dict
    campaigns_by_status: dict
