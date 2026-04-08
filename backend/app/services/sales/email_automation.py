"""
Email automation service - manage email sequences, send campaigns, track engagement
"""
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sales import Lead, EmailSequence, EmailInteraction, SalesSettings


async def get_sequence_by_trigger(
    db: AsyncSession,
    trigger: str,
) -> Optional[EmailSequence]:
    """Get active email sequence by trigger type"""
    result = await db.execute(
        select(EmailSequence)
        .where(EmailSequence.trigger == trigger)
        .where(EmailSequence.is_active == True)
    )
    return result.scalar_one_or_none()


async def send_sequence_email(
    db: AsyncSession,
    lead: Lead,
    sequence: EmailSequence,
    step_number: int = 1,
) -> Optional[EmailInteraction]:
    """
    Send an email from a sequence to a lead.
    In production, this would integrate with SendGrid/Mailgun.
    """
    if not sequence.emails:
        return None

    emails = sequence.emails if isinstance(sequence.emails, list) else []

    # Find the email at this step
    current_email = None
    for email in emails:
        if email.get("step") == step_number:
            current_email = email
            break

    if not current_email:
        return None

    # Create email interaction record
    interaction = EmailInteraction(
        lead_id=lead.id,
        sequence_id=sequence.id,
        subject=current_email.get("subject", ""),
        sent_at=datetime.utcnow(),
    )

    db.add(interaction)
    sequence.total_sent += 1

    # TODO: In production, send via SendGrid/Mailgun
    # await send_via_sendgrid(
    #     to=lead.contact_email,
    #     subject=current_email["subject"],
    #     body=current_email["body"],
    #     from_name=settings.from_name,
    #     from_email=settings.from_email,
    # )

    return interaction


async def trigger_lead_sequence(
    db: AsyncSession,
    lead: Lead,
    trigger: str,
) -> None:
    """
    Trigger and start an email sequence for a lead.
    """
    sequence = await get_sequence_by_trigger(db, trigger)
    if not sequence:
        return

    # Send first email (step 1)
    await send_sequence_email(db, lead, sequence, step_number=1)
    sequence.active_sequences += 1


async def send_follow_up_email(
    db: AsyncSession,
    lead: Lead,
) -> None:
    """
    Send an automated follow-up email if configured.
    """
    result = await db.execute(select(SalesSettings).where(SalesSettings.id == 1))
    settings = result.scalar_one_or_none()

    if not settings or not settings.auto_send_follow_up:
        return

    # Check if enough time has passed since last contact
    if lead.last_contacted_at:
        days_since = (datetime.utcnow() - lead.last_contacted_at).days
        if days_since < settings.follow_up_days:
            return

    # Create a simple follow-up interaction
    interaction = EmailInteraction(
        lead_id=lead.id,
        subject=f"Following Up - {lead.company_name}",
        sent_at=datetime.utcnow(),
    )
    db.add(interaction)

    # TODO: Send actual email
    # await send_via_sendgrid(
    #     to=lead.contact_email,
    #     subject=interaction.subject,
    #     body=f"Hi {lead.contact_name}, just checking in...",
    # )


async def handle_email_open(
    db: AsyncSession,
    interaction_id: int,
) -> Optional[EmailInteraction]:
    """
    Record when an email is opened (via pixel/webhook).
    """
    result = await db.execute(
        select(EmailInteraction).where(EmailInteraction.id == interaction_id)
    )
    interaction = result.scalar_one_or_none()
    if not interaction:
        return None

    if not interaction.opened:
        interaction.opened = True
        interaction.opened_at = datetime.utcnow()

    interaction.open_count += 1
    await db.commit()

    return interaction


async def handle_email_click(
    db: AsyncSession,
    interaction_id: int,
) -> Optional[EmailInteraction]:
    """
    Record when a link is clicked in an email.
    """
    result = await db.execute(
        select(EmailInteraction).where(EmailInteraction.id == interaction_id)
    )
    interaction = result.scalar_one_or_none()
    if not interaction:
        return None

    if not interaction.clicked:
        interaction.clicked = True
        interaction.clicked_at = datetime.utcnow()

    interaction.click_count += 1

    # Update lead score for click
    if interaction.lead:
        settings_result = await db.execute(
            select(SalesSettings).where(SalesSettings.id == 1)
        )
        settings = settings_result.scalar_one_or_none()
        if settings:
            interaction.lead.lead_score += settings.lead_score_link_click

    await db.commit()

    return interaction


async def handle_email_bounce(
    db: AsyncSession,
    interaction_id: int,
    reason: str = "unknown",
) -> Optional[EmailInteraction]:
    """
    Record when an email bounces.
    """
    result = await db.execute(
        select(EmailInteraction).where(EmailInteraction.id == interaction_id)
    )
    interaction = result.scalar_one_or_none()
    if not interaction:
        return None

    interaction.bounced = True
    interaction.bounce_reason = reason

    # Mark lead as having issues
    if interaction.lead:
        interaction.lead.status = "unqualified"
        interaction.lead.qualification_reason = f"Email bounce: {reason}"

    await db.commit()

    return interaction


async def get_pending_sequence_steps(
    db: AsyncSession,
    lead: Lead,
) -> List[dict]:
    """
    Get pending emails in a sequence for a lead.
    """
    # Get the lead's active sequences
    result = await db.execute(
        select(EmailInteraction)
        .where(EmailInteraction.lead_id == lead.id)
        .where(EmailInteraction.sequence_id.isnot(None))
        .order_by(EmailInteraction.sent_at.desc())
    )
    interactions = result.scalars().all()

    if not interactions:
        return []

    # Get the sequence from the most recent interaction
    last_interaction = interactions[0]
    if not last_interaction.sequence:
        return []

    sequence = last_interaction.sequence

    # Find which step was sent and return next steps
    pending_steps = []
    if sequence.emails:
        emails = sequence.emails if isinstance(sequence.emails, list) else []
        last_sent_step = max([int(i.get("step", 0)) for i in emails], default=0)

        for email in emails:
            step = email.get("step", 0)
            if step > last_sent_step:
                pending_steps.append(email)

    return pending_steps
