from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.models.sales import Lead, Appointment, SalesProposal, DealPipeline, SalesSettings
from app.schemas.sales import (
    LeadCreate, LeadResponse, AppointmentCreate, AppointmentResponse,
    SalesProposalResponse, DealPipelineResponse, LeadSummaryResponse
)
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/sales", tags=["sales"])


# ---- Public Lead Capture ----

@router.post("/leads", response_model=LeadResponse, status_code=201)
async def capture_lead(
    data: LeadCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Public endpoint for capturing leads from website forms, demo requests, etc.
    This is accessible without authentication.
    """
    # Check if lead with this email already exists
    result = await db.execute(select(Lead).where(Lead.contact_email == data.contact_email))
    existing = result.scalar_one_or_none()

    if existing:
        # Update existing lead instead of creating duplicate
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(existing, field, value)
        lead = existing
    else:
        lead = Lead(**data.model_dump())

    db.add(lead)
    await db.flush()
    await db.refresh(lead)

    # Create deal pipeline entry automatically
    result = await db.execute(select(DealPipeline).where(DealPipeline.lead_id == lead.id))
    if not result.scalar_one_or_none():
        # Get default pipeline stage from settings
        settings_result = await db.execute(select(SalesSettings).where(SalesSettings.id == 1))
        settings = settings_result.scalar_one_or_none()

        pipeline_stages = settings.pipeline_stages if settings else {}
        default_stage = next(iter(pipeline_stages.keys())) if pipeline_stages else "Lead"

        pipeline = DealPipeline(
            lead_id=lead.id,
            current_stage=default_stage,
            deal_value=lead.estimated_budget or 0,
            probability=0,
        )
        db.add(pipeline)

    await db.commit()
    await db.refresh(lead)
    return lead


# ---- Public Appointment Booking ----

@router.post("/appointments", response_model=AppointmentResponse, status_code=201)
async def book_appointment(
    data: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Public endpoint for leads to book appointments (demos, sales calls).
    Creates or updates the appointment.
    """
    # Verify lead exists
    result = await db.execute(select(Lead).where(Lead.id == data.lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Get default duration from settings
    settings_result = await db.execute(select(SalesSettings).where(SalesSettings.id == 1))
    settings = settings_result.scalar_one_or_none()

    duration = data.duration_minutes or (settings.demo_duration_minutes if settings else 30)

    appointment = Appointment(
        lead_id=data.lead_id,
        title=data.title,
        description=data.description,
        scheduled_at=data.scheduled_at,
        duration_minutes=duration,
        timezone=data.timezone or (settings.default_timezone if settings else "UTC"),
        meeting_type=data.meeting_type or "demo",
        meeting_url=data.meeting_url,
        assigned_to_id=data.assigned_to_id,
    )

    db.add(appointment)

    # Update lead status
    lead.status = "in_demo"
    lead.last_contacted_at = datetime.utcnow()

    await db.flush()
    await db.refresh(appointment)
    await db.commit()

    return appointment


@router.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get appointment details"""
    result = await db.execute(select(Appointment).where(Appointment.id == appointment_id))
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.get("/leads/{lead_id}/appointments", response_model=list[AppointmentResponse])
async def list_lead_appointments(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all appointments for a lead"""
    # Verify lead exists
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Lead not found")

    result = await db.execute(
        select(Appointment)
        .where(Appointment.lead_id == lead_id)
        .order_by(Appointment.scheduled_at)
    )
    return result.scalars().all()


# ---- Lead Self-Service ----

@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead_public(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get lead information (public access for self-service portals)"""
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.get("/leads/{lead_id}/proposals", response_model=list[SalesProposalResponse])
async def get_lead_proposals(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get all proposals sent to a lead"""
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Lead not found")

    result = await db.execute(
        select(SalesProposal)
        .where(SalesProposal.lead_id == lead_id)
        .order_by(SalesProposal.created_at.desc())
    )
    return result.scalars().all()


@router.post("/proposals/{proposal_id}/view")
async def track_proposal_view(
    proposal_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Track when a prospect views a proposal"""
    result = await db.execute(select(SalesProposal).where(SalesProposal.id == proposal_id))
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    proposal.view_count += 1
    if not proposal.viewed_at:
        proposal.viewed_at = datetime.utcnow()

    # Update lead score
    if proposal.lead:
        settings_result = await db.execute(select(SalesSettings).where(SalesSettings.id == 1))
        settings = settings_result.scalar_one_or_none()
        if settings:
            proposal.lead.lead_score += settings.lead_score_proposal_view

    await db.commit()
    return {"detail": "Proposal view tracked"}


# ---- Public Statistics (for marketing) ----

@router.get("/stats/public")
async def get_public_stats(
    db: AsyncSession = Depends(get_db),
):
    """
    Public statistics for marketing/landing pages.
    Only shows aggregated, non-sensitive data.
    """
    from sqlalchemy import func

    result = await db.execute(select(func.count(Lead.id)))
    total_prospects = result.scalar() or 0

    result = await db.execute(select(func.count(Lead.id)).where(Lead.status == "won"))
    successful_partnerships = result.scalar() or 0

    result = await db.execute(select(func.avg(Lead.lead_score)).where(Lead.qualified == True))
    avg_prospect_quality = result.scalar() or 0

    return {
        "total_prospects": total_prospects,
        "successful_partnerships": successful_partnerships,
        "avg_prospect_quality": float(avg_prospect_quality),
    }
