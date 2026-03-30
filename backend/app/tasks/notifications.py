"""Celery tasks for sending notifications and emails."""
import asyncio
from app.tasks.worker import celery_app


@celery_app.task(bind=True, max_retries=3)
def send_invoice_email(self, invoice_id: int):
    """Send invoice email to client."""
    try:
        asyncio.run(_send_invoice_email(invoice_id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


async def _send_invoice_email(invoice_id: int):
    from app.db.session import AsyncSessionLocal
    from app.models.payment import Invoice
    from app.models.client import Client
    from app.models.user import User
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
        invoice = result.scalar_one_or_none()
        if not invoice:
            return

        client_result = await db.execute(select(Client).where(Client.id == invoice.client_id))
        client = client_result.scalar_one_or_none()
        if not client:
            return

        user_result = await db.execute(select(User).where(User.id == client.user_id))
        user = user_result.scalar_one_or_none()

        email_to = client.billing_email or (user.email if user else None)
        if not email_to:
            return

        await _send_email(
            to=email_to,
            subject=f"Invoice {invoice.invoice_number} from OakstrattonIMA",
            body=f"""
            <h2>Invoice {invoice.invoice_number}</h2>
            <p>Dear {client.company_name},</p>
            <p>Please find your invoice for ${invoice.total_amount} {invoice.currency} due by {invoice.due_date}.</p>
            <p>Thank you for your business.</p>
            <p>OakstrattonIMA Team</p>
            """,
        )


@celery_app.task(bind=True, max_retries=3)
def send_contract_notification(self, contract_id: int, notification_type: str):
    """Notify influencer or agency about contract events."""
    try:
        asyncio.run(_send_contract_notification(contract_id, notification_type))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


async def _send_contract_notification(contract_id: int, notification_type: str):
    from app.db.session import AsyncSessionLocal
    from app.models.contract import Contract, ContractStatus
    from app.models.influencer import Influencer
    from app.models.user import User
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Contract).where(Contract.id == contract_id))
        contract = result.scalar_one_or_none()
        if not contract:
            return

        inf_result = await db.execute(
            select(Influencer).where(Influencer.id == contract.influencer_id)
        )
        influencer = inf_result.scalar_one_or_none()
        if not influencer:
            return

        user_result = await db.execute(select(User).where(User.id == influencer.user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            return

        from app.core.config import settings
        action_url = f"{settings.FRONTEND_URL}/contracts/{contract_id}"

        if notification_type == "contract_sent":
            await _send_email(
                to=user.email,
                subject=f"Contract Ready to Sign: {contract.title}",
                body=f"""
                <h2>Contract Ready for Your Signature</h2>
                <p>Hi {user.full_name},</p>
                <p>A new contract <strong>{contract.title}</strong> is ready for your review and signature.</p>
                <p><a href="{action_url}">Review & Sign Contract</a></p>
                """,
            )


@celery_app.task
def send_deliverable_reminders():
    """Send reminders for deliverables due in the next 48 hours."""
    asyncio.run(_send_deliverable_reminders())


async def _send_deliverable_reminders():
    from app.db.session import AsyncSessionLocal
    from app.models.campaign import Deliverable, DeliverableStatus, CampaignInfluencer
    from app.models.influencer import Influencer
    from app.models.user import User
    from sqlalchemy import select, and_
    from datetime import date, timedelta

    tomorrow = date.today() + timedelta(days=2)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Deliverable).where(
                and_(
                    Deliverable.due_date <= tomorrow,
                    Deliverable.due_date >= date.today(),
                    Deliverable.status.in_([
                        DeliverableStatus.PENDING,
                        DeliverableStatus.IN_PROGRESS,
                    ]),
                )
            )
        )
        deliverables = result.scalars().all()

        for deliverable in deliverables:
            ci_result = await db.execute(
                select(CampaignInfluencer).where(
                    CampaignInfluencer.id == deliverable.campaign_influencer_id
                )
            )
            ci = ci_result.scalar_one_or_none()
            if not ci:
                continue

            inf_result = await db.execute(
                select(Influencer).where(Influencer.id == ci.influencer_id)
            )
            influencer = inf_result.scalar_one_or_none()
            if not influencer:
                continue

            user_result = await db.execute(
                select(User).where(User.id == influencer.user_id)
            )
            user = user_result.scalar_one_or_none()
            if not user:
                continue

            await _send_email(
                to=user.email,
                subject=f"Reminder: Deliverable Due {deliverable.due_date}",
                body=f"""
                <h2>Deliverable Due Soon</h2>
                <p>Hi {user.full_name},</p>
                <p>This is a reminder that your <strong>{deliverable.deliverable_type.value}</strong>
                deliverable is due on <strong>{deliverable.due_date}</strong>.</p>
                <p>Please submit your content via the OakstrattonIMA portal.</p>
                """,
            )


async def _send_email(to: str, subject: str, body: str):
    """Send email via SendGrid."""
    from app.core.config import settings

    if not settings.SENDGRID_API_KEY:
        print(f"[EMAIL] Would send to {to}: {subject}")
        return

    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail, Email, To, Content

        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        message = Mail(
            from_email=Email(settings.EMAIL_FROM, settings.EMAIL_FROM_NAME),
            to_emails=To(to),
            subject=subject,
            html_content=Content("text/html", body),
        )
        sg.client.mail.send.post(request_body=message.get())
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send to {to}: {e}")
        raise
