"""
Public directory endpoints — no authentication required.
Returns a curated public view of influencers and agency team members.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload, joinedload
from pydantic import BaseModel
from datetime import datetime

from app.core.deps import get_db
from app.models.user import User, UserRole
from app.models.influencer import Influencer, InfluencerStatus
from app.models.social_account import SocialAccount

router = APIRouter(prefix="/directory", tags=["directory"])


# ── Response schemas ──────────────────────────────────────────────────────────

class PublicSocialAccount(BaseModel):
    platform: str
    username: str
    follower_count: Optional[int] = None
    is_verified: bool = False

    model_config = {"from_attributes": True}


class PublicInfluencerCard(BaseModel):
    id: int
    full_name: str
    avatar_url: Optional[str] = None
    location: Optional[str] = None
    niches: Optional[List[str]] = None
    bio: Optional[str] = None
    social_accounts: List[PublicSocialAccount] = []
    joined_at: str

    model_config = {"from_attributes": True}


class PublicTeamMember(BaseModel):
    id: int
    full_name: str
    avatar_url: Optional[str] = None
    role: str
    joined_at: str

    model_config = {"from_attributes": True}


class DirectoryInfluencersResponse(BaseModel):
    items: List[PublicInfluencerCard]
    total: int


class DirectoryTeamResponse(BaseModel):
    items: List[PublicTeamMember]
    total: int


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/influencers", response_model=DirectoryInfluencersResponse)
async def list_directory_influencers(
    search: Optional[str] = Query(None, description="Filter by name or niche"),
    niche: Optional[str] = Query(None, description="Filter by specific niche"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Public influencer directory. No authentication required."""
    query = (
        select(Influencer)
        .where(Influencer.status == InfluencerStatus.ACTIVE)
        .options(
            joinedload(Influencer.user),
            selectinload(Influencer.social_accounts),
        )
        .order_by(Influencer.id.desc())
    )

    # Apply search filter (name via joined user, or niche contains search term)
    if search:
        term = f"%{search.lower()}%"
        query = query.join(Influencer.user).where(
            or_(
                User.full_name.ilike(term),
                Influencer.niches.cast(type_=None).ilike(term),
            )
        )

    # Count total before pagination
    count_result = await db.execute(
        select(Influencer)
        .where(Influencer.status == InfluencerStatus.ACTIVE)
        .options(joinedload(Influencer.user))
    )
    all_rows = count_result.scalars().all()
    total = len(all_rows)

    # Apply pagination
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    influencers = result.unique().scalars().all()

    items: List[PublicInfluencerCard] = []
    for inf in influencers:
        # Filter by niche if requested
        if niche and (not inf.niches or niche.lower() not in [n.lower() for n in inf.niches]):
            continue

        # Only return public social account fields
        public_accounts = [
            PublicSocialAccount(
                platform=acc.platform.value if hasattr(acc.platform, "value") else str(acc.platform),
                username=acc.username,
                follower_count=acc.follower_count,
                is_verified=acc.is_verified,
            )
            for acc in inf.social_accounts
        ]

        items.append(PublicInfluencerCard(
            id=inf.id,
            full_name=inf.user.full_name if inf.user else "Unknown",
            avatar_url=inf.user.avatar_url if inf.user else None,
            location=inf.location,
            niches=inf.niches,
            bio=inf.bio,
            social_accounts=public_accounts,
            joined_at=inf.created_at.isoformat() if inf.created_at else "",
        ))

    return DirectoryInfluencersResponse(items=items, total=total)


@router.get("/team", response_model=DirectoryTeamResponse)
async def list_directory_team(
    db: AsyncSession = Depends(get_db),
):
    """Public agency team directory — shows managers and admins. No authentication required."""
    result = await db.execute(
        select(User)
        .where(
            User.role.in_([UserRole.MANAGER, UserRole.ADMIN]),
            User.is_active == True,
        )
        .order_by(User.created_at.asc())
    )
    members = result.scalars().all()

    items = [
        PublicTeamMember(
            id=m.id,
            full_name=m.full_name,
            avatar_url=m.avatar_url,
            role=m.role.value if hasattr(m.role, "value") else str(m.role),
            joined_at=m.created_at.isoformat() if m.created_at else "",
        )
        for m in members
    ]

    return DirectoryTeamResponse(items=items, total=len(items))
