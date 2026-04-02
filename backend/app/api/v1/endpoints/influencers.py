from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload
from app.core.deps import get_db, get_current_active_user, require_manager
from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.user import User, UserRole
from app.models.influencer import Influencer, InfluencerStatus
from app.models.social_account import SocialAccount, SocialPlatform
from app.schemas.influencer import (
    InfluencerCreate, InfluencerUpdate, InfluencerResponse,
    SocialAccountCreate, SocialAccountResponse, InfluencerSearchParams,
)
from app.schemas.common import PaginatedResponse
from fastapi import HTTPException

router = APIRouter(prefix="/influencers", tags=["influencers"])


@router.get("", response_model=PaginatedResponse[InfluencerResponse])
async def list_influencers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
    niche: Optional[str] = Query(None),
    platform: Optional[SocialPlatform] = Query(None),
    min_followers: Optional[int] = Query(None),
    max_followers: Optional[int] = Query(None),
    status: Optional[InfluencerStatus] = Query(None),
    country_code: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    query = select(Influencer)

    if status:
        query = query.where(Influencer.status == status)
    if country_code:
        query = query.where(Influencer.country_code == country_code)

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar_one()

    result = await db.execute(
        query.options(selectinload(Influencer.social_accounts))
        .order_by(Influencer.created_at.desc()).offset(skip).limit(limit)
    )
    influencers = result.scalars().all()

    return PaginatedResponse(items=list(influencers), total=total, skip=skip, limit=limit)


@router.post("", response_model=InfluencerResponse, status_code=status.HTTP_201_CREATED)
async def create_influencer(
    payload: InfluencerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create an influencer profile. Influencers self-register; managers create for a specific user_id."""
    # Determine target user_id
    if current_user.role == UserRole.INFLUENCER:
        target_user_id = current_user.id
    elif current_user.role in (UserRole.ADMIN, UserRole.MANAGER):
        data = payload.model_dump(exclude_unset=True)
        target_user_id = data.pop("user_id", None) or current_user.id
    else:
        raise ForbiddenError("Only influencers and agency staff can create influencer profiles")

    # Check for existing profile
    existing = await db.execute(select(Influencer).where(Influencer.user_id == target_user_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="An influencer profile already exists for this user")

    data = payload.model_dump(exclude_unset=True)
    data.pop("user_id", None)  # remove if present in data dict
    influencer = Influencer(user_id=target_user_id, **data)
    db.add(influencer)
    await db.commit()
    await db.refresh(influencer)

    # Reload with social_accounts
    result = await db.execute(
        select(Influencer).where(Influencer.id == influencer.id)
        .options(selectinload(Influencer.social_accounts))
    )
    return result.scalar_one()


@router.get("/{influencer_id}", response_model=InfluencerResponse)
async def get_influencer(
    influencer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Influencer).where(Influencer.id == influencer_id)
        .options(selectinload(Influencer.social_accounts))
    )
    influencer = result.scalar_one_or_none()
    if not influencer:
        raise NotFoundError("Influencer", influencer_id)

    # Influencers can only see their own profile
    if current_user.role == UserRole.INFLUENCER and influencer.user_id != current_user.id:
        raise ForbiddenError()

    return influencer


@router.patch("/{influencer_id}", response_model=InfluencerResponse)
async def update_influencer(
    influencer_id: int,
    payload: InfluencerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Influencer).where(Influencer.id == influencer_id)
        .options(selectinload(Influencer.social_accounts))
    )
    influencer = result.scalar_one_or_none()
    if not influencer:
        raise NotFoundError("Influencer", influencer_id)

    # Influencers can update their own profile but not status/trust_score/notes
    if current_user.role == UserRole.INFLUENCER:
        if influencer.user_id != current_user.id:
            raise ForbiddenError()
        # Strip agency-only fields
        payload = payload.model_copy(update={"status": None, "trust_score": None, "agency_notes": None})

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(influencer, field, value)

    await db.commit()
    await db.refresh(influencer)

    # Reload with social_accounts after update
    result = await db.execute(
        select(Influencer).where(Influencer.id == influencer_id)
        .options(selectinload(Influencer.social_accounts))
    )
    return result.scalar_one()


@router.post("/{influencer_id}/social-accounts", response_model=SocialAccountResponse)
async def add_social_account(
    influencer_id: int,
    payload: SocialAccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Influencer).where(Influencer.id == influencer_id))
    influencer = result.scalar_one_or_none()
    if not influencer:
        raise NotFoundError("Influencer", influencer_id)

    if current_user.role == UserRole.INFLUENCER and influencer.user_id != current_user.id:
        raise ForbiddenError()

    account = SocialAccount(
        influencer_id=influencer_id,
        **payload.model_dump(),
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


@router.get("/{influencer_id}/social-accounts", response_model=List[SocialAccountResponse])
async def list_social_accounts(
    influencer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(SocialAccount).where(SocialAccount.influencer_id == influencer_id)
    )
    return result.scalars().all()
