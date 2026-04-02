import enum
from typing import Optional, List
from sqlalchemy import String, Boolean, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    CLIENT = "client"
    INFLUENCER = "influencer"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="userrole"), nullable=False, default=UserRole.CLIENT)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    last_login_at: Mapped[Optional[str]] = mapped_column(String(50))

    # Relationships
    influencer_profile: Mapped[Optional["Influencer"]] = relationship(
        back_populates="user", uselist=False
    )
    client_profile: Mapped[Optional["Client"]] = relationship(
        back_populates="user", uselist=False, foreign_keys="[Client.user_id]"
    )
    notifications: Mapped[List["Notification"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.email} [{self.role}]>"
