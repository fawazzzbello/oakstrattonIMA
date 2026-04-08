"""
Lead scoring service - AI-powered lead qualification and scoring
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.models.sales import Lead, SalesSettings, EmailInteraction
from app.models.campaign import Campaign


async def calculate_lead_score(
    db: AsyncSession,
    lead: Lead,
    settings: SalesSettings = None,
) -> int:
    """
    Calculate lead score based on engagement and interactions.
    Higher score = more qualified lead.

    Scoring factors:
    - Website visits
    - Email opens
    - Link clicks
    - Demo requests
    - Proposal views
    - Company size and industry fit
    """
    if not settings:
        result = await db.execute(select(SalesSettings).where(SalesSettings.id == 1))
        settings = result.scalar_one_or_none()
        if not settings:
            return 0

    score = 0

    # Base score from email interactions
    result = await db.execute(
        select(EmailInteraction).where(EmailInteraction.lead_id == lead.id)
    )
    interactions = result.scalars().all()

    for interaction in interactions:
        if interaction.opened:
            score += settings.lead_score_email_open
        if interaction.clicked:
            score += settings.lead_score_link_click
        if interaction.bounced:
            score -= 20  # Penalty for bounces

    # Demo request bonus
    if lead.status == "in_demo":
        score += settings.lead_score_demo_request

    # Company size fit
    if lead.company_size and lead.company_size in ["51-200", "201-500", "501-1000", "1000+"]:
        score += 10

    # Engagement history
    if lead.contacted_count > 0:
        score += min(lead.contacted_count * 5, 30)

    # Recent activity bonus
    if lead.last_contacted_at:
        days_since_contact = (datetime.utcnow() - lead.last_contacted_at).days
        if days_since_contact <= 3:
            score += 15
        elif days_since_contact <= 7:
            score += 10

    # Budget indicator
    if lead.estimated_budget:
        if lead.estimated_budget >= 50000:
            score += 20
        elif lead.estimated_budget >= 10000:
            score += 10

    # Cap score at 100
    score = min(score, 100)
    score = max(score, 0)

    return score


async def auto_qualify_lead(
    db: AsyncSession,
    lead: Lead,
    settings: SalesSettings = None,
) -> bool:
    """
    Auto-qualify a lead based on score threshold.
    """
    if not settings:
        result = await db.execute(select(SalesSettings).where(SalesSettings.id == 1))
        settings = result.scalar_one_or_none()
        if not settings:
            return False

    score = await calculate_lead_score(db, lead, settings)

    if score >= settings.auto_qualify_score:
        lead.qualified = True
        lead.qualification_reason = f"Auto-qualified based on lead score ({score}/100)"
        return True

    return False


async def update_lead_score(
    db: AsyncSession,
    lead_id: int,
) -> None:
    """
    Recalculate and update a lead's score.
    """
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        return

    result = await db.execute(select(SalesSettings).where(SalesSettings.id == 1))
    settings = result.scalar_one_or_none()

    score = await calculate_lead_score(db, lead, settings)
    lead.lead_score = score

    # Check if should auto-qualify
    if not lead.qualified:
        await auto_qualify_lead(db, lead, settings)


async def score_batch_leads(
    db: AsyncSession,
) -> None:
    """
    Score all leads that haven't been scored recently.
    Useful for Celery background tasks.
    """
    result = await db.execute(select(Lead))
    leads = result.scalars().all()

    result = await db.execute(select(SalesSettings).where(SalesSettings.id == 1))
    settings = result.scalar_one_or_none()

    for lead in leads:
        score = await calculate_lead_score(db, lead, settings)
        lead.lead_score = score

        if not lead.qualified:
            await auto_qualify_lead(db, lead, settings)

    await db.commit()
