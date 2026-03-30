from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.deps import get_db, get_current_active_user, require_manager, require_admin
from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.user import User, UserRole
from app.models.client import Client, Brand, ClientStatus
from app.schemas.common import PaginatedResponse
from pydantic import BaseModel
from typing import Optional as Opt

router = APIRouter(prefix="/clients", tags=["clients"])


class ClientCreate(BaseModel):
    user_id: int
    company_name: str
    company_website: Opt[str] = None
    industry: Opt[str] = None
    billing_email: Opt[str] = None
    monthly_budget: Opt[float] = None
    currency: str = "USD"
    notes: Opt[str] = None
    account_manager_id: Opt[int] = None


class ClientUpdate(BaseModel):
    company_name: Opt[str] = None
    company_website: Opt[str] = None
    industry: Opt[str] = None
    billing_email: Opt[str] = None
    monthly_budget: Opt[float] = None
    status: Opt[ClientStatus] = None
    notes: Opt[str] = None
    account_manager_id: Opt[int] = None


class ClientResponse(BaseModel):
    id: int
    user_id: int
    company_name: str
    company_website: Opt[str] = None
    industry: Opt[str] = None
    status: ClientStatus
    monthly_budget: Opt[float] = None
    currency: str
    billing_email: Opt[str] = None
    account_manager_id: Opt[int] = None
    notes: Opt[str] = None

    model_config = {"from_attributes": True}


class BrandCreate(BaseModel):
    name: str
    description: Opt[str] = None
    website: Opt[str] = None
    industry: Opt[str] = None
    target_audience: Opt[str] = None


class BrandResponse(BaseModel):
    id: int
    client_id: int
    name: str
    description: Opt[str] = None
    website: Opt[str] = None
    industry: Opt[str] = None
    is_active: bool
    logo_url: Opt[str] = None

    model_config = {"from_attributes": True}


@router.get("", response_model=PaginatedResponse[ClientResponse])
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[ClientStatus] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    query = select(Client)
    if status:
        query = query.where(Client.status == status)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(query.order_by(Client.company_name).offset(skip).limit(limit))
    return PaginatedResponse(items=list(result.scalars().all()), total=total, skip=skip, limit=limit)


@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    payload: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    client = Client(**payload.model_dump(exclude_unset=True))
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise NotFoundError("Client", client_id)

    if current_user.role == UserRole.CLIENT and client.user_id != current_user.id:
        raise ForbiddenError()

    return client


@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    payload: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise NotFoundError("Client", client_id)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(client, field, value)

    await db.commit()
    await db.refresh(client)
    return client


@router.post("/{client_id}/brands", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(
    client_id: int,
    payload: BrandCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    result = await db.execute(select(Client).where(Client.id == client_id))
    if not result.scalar_one_or_none():
        raise NotFoundError("Client", client_id)

    brand = Brand(client_id=client_id, **payload.model_dump(exclude_unset=True))
    db.add(brand)
    await db.commit()
    await db.refresh(brand)
    return brand


@router.get("/{client_id}/brands", response_model=list[BrandResponse])
async def list_brands(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Brand).where(Brand.client_id == client_id, Brand.is_active == True)
    )
    return result.scalars().all()
