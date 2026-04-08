"""
Proposal generation service - create and manage sales proposals
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models.sales import (
    Lead, SalesProposal, ProposalTemplate, SalesSettings
)


async def generate_proposal_number(
    db: AsyncSession,
) -> str:
    """
    Generate a unique proposal number.
    Format: PROP-2026-XXXXX
    """
    result = await db.execute(select(SalesProposal))
    count = len(result.scalars().all())
    year = datetime.utcnow().year
    seq = count + 1

    return f"PROP-{year}-{seq:05d}"


async def render_template(
    template_html: str,
    context: Dict[str, Any],
) -> str:
    """
    Render a proposal template with context variables.
    Simple implementation using {{variable}} syntax.

    In production, consider using Jinja2 for more robust templating.
    """
    rendered = template_html

    for key, value in context.items():
        placeholder = f"{{{{{key}}}}}"
        rendered = rendered.replace(placeholder, str(value))

    return rendered


async def create_proposal_from_template(
    db: AsyncSession,
    lead: Lead,
    template: ProposalTemplate,
    title: str,
    solutions: Dict[str, Any],
    total_value: float,
    **context_kwargs,
) -> Optional[SalesProposal]:
    """
    Create a proposal from a template with custom values.
    """
    # Get settings for validity period
    result = await db.execute(select(SalesSettings).where(SalesSettings.id == 1))
    settings = result.scalar_one_or_none()

    validity_days = settings.proposal_validity_days if settings else 30
    currency = settings.proposal_currency if settings else "USD"

    # Generate proposal number
    proposal_number = await generate_proposal_number(db)

    # Build context for template rendering
    context = {
        "company_name": lead.company_name,
        "contact_name": lead.contact_name,
        "contact_email": lead.contact_email,
        "proposal_date": datetime.utcnow().strftime("%B %d, %Y"),
        "proposal_number": proposal_number,
        "total_value": f"{currency} {total_value:,.2f}",
        **context_kwargs,
    }

    # Render template
    proposal_content = await render_template(template.template_html, context)

    # Create proposal
    proposal = SalesProposal(
        lead_id=lead.id,
        proposal_number=proposal_number,
        title=title,
        solutions=solutions,
        total_value=total_value,
        currency=currency,
        template_id=template.id,
        proposal_content=proposal_content,
        valid_until=datetime.utcnow() + timedelta(days=validity_days),
        status="draft",
    )

    db.add(proposal)
    await db.flush()
    await db.refresh(proposal)

    # Update lead status
    lead.status = "proposal_sent"
    lead.last_contacted_at = datetime.utcnow()

    return proposal


async def send_proposal(
    db: AsyncSession,
    proposal: SalesProposal,
) -> bool:
    """
    Mark proposal as sent and notify lead.
    In production, this would actually send via email.
    """
    proposal.status = "sent"
    proposal.sent_at = datetime.utcnow()

    if proposal.lead:
        proposal.lead.status = "proposal_sent"

    # TODO: In production, send via SendGrid/Mailgun
    # await send_via_sendgrid(
    #     to=proposal.lead.contact_email,
    #     subject=f"Your Proposal: {proposal.title}",
    #     body=proposal.proposal_content,
    # )

    return True


async def track_proposal_view(
    db: AsyncSession,
    proposal: SalesProposal,
) -> bool:
    """
    Track when a proposal is viewed by the prospect.
    """
    proposal.view_count += 1

    if not proposal.viewed_at:
        proposal.viewed_at = datetime.utcnow()

        # Update lead score and status
        if proposal.lead:
            settings_result = await db.execute(
                select(SalesSettings).where(SalesSettings.id == 1)
            )
            settings = settings_result.scalar_one_or_none()

            if settings:
                proposal.lead.lead_score += settings.lead_score_proposal_view

            if proposal.lead.status == "proposal_sent":
                proposal.lead.status = "negotiating"

    return True


async def check_proposal_expiry(
    db: AsyncSession,
) -> list:
    """
    Check for expired proposals and update their status.
    Should be run periodically (e.g., via Celery beat).
    """
    expired_proposals = []

    result = await db.execute(
        select(SalesProposal)
        .where(SalesProposal.status.in_(["draft", "sent"]))
        .where(SalesProposal.valid_until.isnot(None))
    )
    proposals = result.scalars().all()

    for proposal in proposals:
        if proposal.valid_until < datetime.utcnow():
            proposal.status = "expired"
            expired_proposals.append(proposal)

    return expired_proposals


async def get_template_options(
    db: AsyncSession,
    lead: Optional[Lead] = None,
) -> list:
    """
    Get available proposal templates for a lead.
    Can be filtered by lead industry/size in the future.
    """
    result = await db.execute(
        select(ProposalTemplate)
        .where(ProposalTemplate.is_active == True)
        .order_by(ProposalTemplate.created_at.desc())
    )
    return result.scalars().all()


async def estimate_proposal_value(
    lead: Lead,
) -> float:
    """
    Estimate proposal value based on lead information.
    Simple heuristic; in production, could use ML/historical data.
    """
    base_value = 5000  # Base package

    # Increase based on company size
    if lead.company_size == "51-200":
        base_value += 5000
    elif lead.company_size == "201-500":
        base_value += 15000
    elif lead.company_size == "501-1000":
        base_value += 25000
    elif lead.company_size == "1000+":
        base_value += 40000

    # Adjust based on estimated budget
    if lead.estimated_budget:
        if lead.estimated_budget > base_value:
            base_value = min(lead.estimated_budget, base_value * 1.5)

    return base_value
