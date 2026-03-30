"""Celery tasks for payment automation."""
import asyncio
from app.tasks.worker import celery_app


@celery_app.task
def mark_overdue_invoices():
    """Mark past-due invoices as OVERDUE."""
    asyncio.run(_mark_overdue_invoices())


async def _mark_overdue_invoices():
    from app.db.session import AsyncSessionLocal
    from app.models.payment import Invoice, InvoiceStatus
    from sqlalchemy import select, update
    from datetime import date

    today = date.today()

    async with AsyncSessionLocal() as db:
        await db.execute(
            update(Invoice)
            .where(
                Invoice.status == InvoiceStatus.SENT,
                Invoice.due_date < today,
            )
            .values(status=InvoiceStatus.OVERDUE)
        )
        await db.commit()


@celery_app.task(bind=True, max_retries=3)
def process_payout_via_stripe(self, payout_id: int):
    """Trigger Stripe Connect transfer for an influencer payout."""
    try:
        asyncio.run(_process_stripe_payout(payout_id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300)


async def _process_stripe_payout(payout_id: int):
    from app.db.session import AsyncSessionLocal
    from app.models.payment import Payout, PayoutStatus, Transaction, TransactionType
    from app.models.influencer import Influencer
    from sqlalchemy import select
    from app.core.config import settings
    from datetime import datetime, timezone

    async with AsyncSessionLocal() as db:
        payout_result = await db.execute(select(Payout).where(Payout.id == payout_id))
        payout = payout_result.scalar_one_or_none()
        if not payout or payout.status != PayoutStatus.PENDING:
            return

        inf_result = await db.execute(
            select(Influencer).where(Influencer.id == payout.influencer_id)
        )
        influencer = inf_result.scalar_one_or_none()
        if not influencer or not influencer.stripe_account_id:
            payout.status = PayoutStatus.FAILED
            payout.failure_reason = "No Stripe Connect account linked"
            await db.commit()
            return

        if not settings.STRIPE_SECRET_KEY:
            payout.status = PayoutStatus.FAILED
            payout.failure_reason = "Stripe not configured"
            await db.commit()
            return

        try:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY

            transfer = stripe.Transfer.create(
                amount=int(payout.amount * 100),  # cents
                currency=payout.currency.lower(),
                destination=influencer.stripe_account_id,
                metadata={"payout_id": str(payout_id)},
            )

            payout.status = PayoutStatus.COMPLETED
            payout.stripe_transfer_id = transfer.id
            payout.processed_at = datetime.now(timezone.utc)
            payout.net_amount = payout.amount - (payout.tax_withheld or 0)

            transaction = Transaction(
                transaction_type=TransactionType.INFLUENCER_PAYOUT,
                amount=payout.amount,
                currency=payout.currency,
                payout_id=payout_id,
                processor="stripe",
                processor_transaction_id=transfer.id,
            )
            db.add(transaction)
            await db.commit()

        except Exception as e:
            payout.status = PayoutStatus.FAILED
            payout.failure_reason = str(e)
            payout.retry_count += 1
            await db.commit()
            raise
