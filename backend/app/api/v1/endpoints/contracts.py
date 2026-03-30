from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.deps import get_db, get_current_active_user, require_manager
from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.user import User, UserRole
from app.models.contract import Contract, ContractTemplate, ContractStatus
from app.schemas.common import PaginatedResponse
from pydantic import BaseModel
from datetime import date, datetime
from decimal import Decimal
from typing import Optional as Opt

router = APIRouter(prefix="/contracts", tags=["contracts"])


class ContractCreate(BaseModel):
    influencer_id: int
    campaign_id: int
    template_id: Opt[int] = None
    title: str
    content: Opt[str] = None
    total_fee: Opt[Decimal] = None
    currency: str = "USD"
    effective_date: Opt[date] = None
    expiration_date: Opt[date] = None
    exclusivity_clause: bool = False
    payment_schedule: Opt[list] = None


class ContractResponse(BaseModel):
    id: int
    status: ContractStatus
    influencer_id: int
    campaign_id: int
    title: str
    total_fee: Opt[Decimal] = None
    currency: str
    effective_date: Opt[date] = None
    expiration_date: Opt[date] = None
    exclusivity_clause: bool
    influencer_signed_at: Opt[datetime] = None
    agency_signed_at: Opt[datetime] = None
    document_url: Opt[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ContractTemplateCreate(BaseModel):
    name: str
    description: Opt[str] = None
    content: str
    variables: Opt[List[str]] = None
    is_default: bool = False


class ContractTemplateResponse(BaseModel):
    id: int
    name: str
    description: Opt[str] = None
    content: str
    variables: Opt[List[str]] = None
    is_default: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=PaginatedResponse[ContractResponse])
async def list_contracts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[ContractStatus] = Query(None),
    campaign_id: Optional[int] = Query(None),
    influencer_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = select(Contract)

    if current_user.role == UserRole.INFLUENCER:
        from app.models.influencer import Influencer
        result = await db.execute(
            select(Influencer).where(Influencer.user_id == current_user.id)
        )
        inf = result.scalar_one_or_none()
        if inf:
            query = query.where(Contract.influencer_id == inf.id)

    if status:
        query = query.where(Contract.status == status)
    if campaign_id:
        query = query.where(Contract.campaign_id == campaign_id)
    if influencer_id and current_user.role in (UserRole.ADMIN, UserRole.MANAGER):
        query = query.where(Contract.influencer_id == influencer_id)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(query.order_by(Contract.created_at.desc()).offset(skip).limit(limit))
    return PaginatedResponse(items=list(result.scalars().all()), total=total, skip=skip, limit=limit)


@router.post("", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
    payload: ContractCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    # If template provided, populate content from template
    content = payload.content
    if payload.template_id and not content:
        tmpl_result = await db.execute(
            select(ContractTemplate).where(ContractTemplate.id == payload.template_id)
        )
        tmpl = tmpl_result.scalar_one_or_none()
        if tmpl:
            content = tmpl.content

    contract = Contract(
        influencer_id=payload.influencer_id,
        campaign_id=payload.campaign_id,
        template_id=payload.template_id,
        title=payload.title,
        content=content,
        total_fee=payload.total_fee,
        currency=payload.currency,
        effective_date=payload.effective_date,
        expiration_date=payload.expiration_date,
        exclusivity_clause=payload.exclusivity_clause,
        payment_schedule=payload.payment_schedule,
        created_by_id=current_user.id,
    )
    db.add(contract)
    await db.commit()
    await db.refresh(contract)
    return contract


@router.post("/{contract_id}/sign", response_model=ContractResponse)
async def sign_contract(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Influencer or agency signs a contract."""
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise NotFoundError("Contract", contract_id)

    now = datetime.utcnow()

    if current_user.role == UserRole.INFLUENCER:
        contract.influencer_signed_at = now
        contract.status = ContractStatus.SIGNED_INFLUENCER
    elif current_user.role in (UserRole.ADMIN, UserRole.MANAGER):
        contract.agency_signed_at = now
        contract.agency_signed_by_id = current_user.id
        if contract.influencer_signed_at:
            contract.status = ContractStatus.FULLY_EXECUTED
        else:
            contract.status = ContractStatus.SIGNED_AGENCY
    else:
        raise ForbiddenError("Only influencers and agency staff can sign contracts")

    await db.commit()
    await db.refresh(contract)
    return contract


@router.post("/{contract_id}/void", response_model=ContractResponse)
async def void_contract(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise NotFoundError("Contract", contract_id)

    contract.status = ContractStatus.VOIDED
    await db.commit()
    await db.refresh(contract)
    return contract


# --- Templates ---

@router.get("/templates", response_model=List[ContractTemplateResponse])
async def list_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    result = await db.execute(
        select(ContractTemplate).where(ContractTemplate.is_active == True)
    )
    return result.scalars().all()


@router.post("/templates", response_model=ContractTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    payload: ContractTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    template = ContractTemplate(
        **payload.model_dump(exclude_unset=True),
        created_by_id=current_user.id,
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template
