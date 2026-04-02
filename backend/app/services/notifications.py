"""
Notification service — creates in-app notifications and sends emails on key events.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.services.email import (
    send_email,
    send_welcome_email,
    send_login_alert,
    send_password_changed_alert,
)


async def notify_user(
    db: AsyncSession,
    user_id: int,
    notification_type: NotificationType,
    title: str,
    body: Optional[str] = None,
    action_url: Optional[str] = None,
    extra_data: Optional[dict] = None,
    send_email_alert: bool = False,
    email_subject: Optional[str] = None,
    email_html: Optional[str] = None,
) -> Notification:
    """
    Create an in-app notification and optionally send an email alert.

    Args:
        db: Database session
        user_id: User to notify
        notification_type: Type of notification
        title: Notification title
        body: Notification body (optional)
        action_url: URL for action button (optional)
        extra_data: Additional JSON data (optional)
        send_email_alert: Whether to send email (default False)
        email_subject: Subject for email (optional)
        email_html: HTML body for email (optional)

    Returns:
        The created Notification object
    """
    # Create in-app notification
    notification = Notification(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        body=body,
        action_url=action_url,
        extra_data=extra_data or {},
    )
    db.add(notification)
    await db.flush()

    # Send email if requested
    if send_email_alert:
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()

        if user and user.email:
            await send_email(
                to_email=user.email,
                subject=email_subject or title,
                html_content=email_html or f"<p>{body or title}</p>",
            )

    return notification


# ── Event notification triggers ──

async def notify_campaign_created(
    db: AsyncSession,
    campaign_id: int,
    campaign_name: str,
    client_user_ids: List[int],  # users to notify
) -> None:
    """Notify relevant users when a campaign is created."""
    for user_id in client_user_ids:
        await notify_user(
            db,
            user_id,
            NotificationType.CAMPAIGN_STARTED,
            title=f"Campaign '{campaign_name}' has been created",
            body="Your new campaign is ready. Start adding influencers now.",
            action_url=f"/app/campaigns/{campaign_id}",
        )


async def notify_contract_sent(
    db: AsyncSession,
    contract_id: int,
    influencer_user_id: int,
    influencer_name: str,
    campaign_name: str,
) -> None:
    """Notify influencer when contract is sent."""
    await notify_user(
        db,
        influencer_user_id,
        NotificationType.CONTRACT_SENT,
        title="New Contract Received",
        body=f"You've received a contract for '{campaign_name}'. Review and sign it now.",
        action_url=f"/app/contracts?contract_id={contract_id}",
        send_email_alert=True,
        email_subject=f"New Contract: {campaign_name}",
        email_html=f"<p>Hello {influencer_name},</p><p>A new contract has been sent to you for the campaign <strong>{campaign_name}</strong>. Please review and sign it when ready.</p>",
    )


async def notify_deliverable_approved(
    db: AsyncSession,
    deliverable_id: int,
    influencer_user_id: int,
    campaign_name: str,
) -> None:
    """Notify influencer when deliverable is approved."""
    await notify_user(
        db,
        influencer_user_id,
        NotificationType.DELIVERABLE_APPROVED,
        title="Deliverable Approved ✓",
        body=f"Your deliverable for '{campaign_name}' has been approved. Great work!",
        action_url=f"/app/campaigns",
        send_email_alert=True,
        email_subject=f"Deliverable Approved: {campaign_name}",
        email_html=f"<p>Your deliverable has been approved for <strong>{campaign_name}</strong>. Excellent work!</p>",
    )


async def notify_payment_sent(
    db: AsyncSession,
    influencer_user_id: int,
    amount: float,
    campaign_name: str,
) -> None:
    """Notify influencer when payment is sent."""
    await notify_user(
        db,
        influencer_user_id,
        NotificationType.PAYMENT_SENT,
        title=f"Payment of ${amount} received",
        body=f"Payment for '{campaign_name}' has been processed.",
        action_url=f"/app/payments",
        send_email_alert=True,
        email_subject=f"Payment Received: ${amount}",
        email_html=f"<p>Great news! You've received a payment of <strong>${amount}</strong> for <strong>{campaign_name}</strong>.</p>",
    )


async def notify_invoice_overdue(
    db: AsyncSession,
    client_user_id: int,
    invoice_id: int,
    amount: float,
) -> None:
    """Notify client when invoice is overdue."""
    await notify_user(
        db,
        client_user_id,
        NotificationType.INVOICE_OVERDUE,
        title="Invoice Overdue",
        body=f"An invoice for ${amount} is now overdue. Please settle it.",
        action_url=f"/app/payments",
        send_email_alert=True,
        email_subject="⚠️ Invoice Overdue",
        email_html=f"<p>An invoice for <strong>${amount}</strong> is overdue. Please process payment immediately.</p>",
    )
