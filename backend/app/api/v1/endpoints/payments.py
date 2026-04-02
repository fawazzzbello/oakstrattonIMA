from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.deps import get_db, require_manager
from app.core.exceptions import NotFoundError, PaymentError
from app.models.payment import Invoice, Payout, InvoiceStatus, PayoutStatus
from app.models.influencer import Influencer
from app.models.notification import NotificationType
from app.schemas.common import PaginatedResponse
from app.services.notifications import notify_user
from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from typing import List

router = APIRouter(prefix="/payments", tags=["payments"])


class InvoiceCreate(BaseModel):
    client_id: int
    campaign_id: Optional[int] = None
    issue_date: date
    due_date: date
    line_items: List[dict]  # [{description, quantity, unit_price}]
    tax_rate: float = 0.0
    currency: str = "USD"
    notes: Optional[str] = None


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    client_id: int
    campaign_id: Optional[int] = None
    status: InvoiceStatus
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    amount_paid: Decimal
    currency: str
    issue_date: date
    due_date: date
    line_items: list
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class PayoutCreate(BaseModel):
    influencer_id: int
    campaign_influencer_id: Optional[int] = None
    amount: Decimal
    currency: str = "USD"
    description: Optional[str] = None
    scheduled_date: Optional[date] = None


class PayoutResponse(BaseModel):
    id: int
    influencer_id: int
    status: PayoutStatus
    amount: Decimal
    currency: str
    description: Optional[str] = None
    scheduled_date: Optional[date] = None
    processed_at: Optional[str] = None
    net_amount: Optional[Decimal] = None

    model_config = {"from_attributes": True}


def _generate_invoice_number(db_count: int) -> str:
    from datetime import datetime
    prefix = f"INV-{datetime.now().year}"
    return f"{prefix}-{str(db_count + 1).zfill(5)}"


@router.get("/invoices", response_model=PaginatedResponse[InvoiceResponse])
async def list_invoices(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[InvoiceStatus] = Query(None),
    client_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_manager),
):
    query = select(Invoice)
    if status:
        query = query.where(Invoice.status == status)
    if client_id:
        query = query.where(Invoice.client_id == client_id)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit))
    return PaginatedResponse(items=list(result.scalars().all()), total=total, skip=skip, limit=limit)


@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    payload: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_manager),
):
    # Calculate totals
    subtotal = sum(
        item.get("quantity", 1) * item.get("unit_price", 0)
        for item in payload.line_items
    )
    tax_amount = subtotal * payload.tax_rate
    total_amount = subtotal + tax_amount

    count = (await db.execute(select(func.count(Invoice.id)))).scalar_one()
    invoice_number = _generate_invoice_number(count)

    invoice = Invoice(
        invoice_number=invoice_number,
        client_id=payload.client_id,
        campaign_id=payload.campaign_id,
        issue_date=payload.issue_date,
        due_date=payload.due_date,
        line_items=payload.line_items,
        subtotal=Decimal(str(subtotal)),
        tax_rate=payload.tax_rate,
        tax_amount=Decimal(str(tax_amount)),
        total_amount=Decimal(str(total_amount)),
        amount_paid=Decimal("0"),
        currency=payload.currency,
        notes=payload.notes,
    )
    db.add(invoice)
    await db.commit()
    await db.refresh(invoice)
    return invoice


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_manager),
):
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise NotFoundError("Invoice", invoice_id)
    return invoice


@router.post("/invoices/{invoice_id}/send", response_model=InvoiceResponse)
async def send_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_manager),
):
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise NotFoundError("Invoice", invoice_id)

    invoice.status = InvoiceStatus.SENT
    await db.commit()
    await db.refresh(invoice)

    # Trigger email task (async)
    from app.tasks.notifications import send_invoice_email
    send_invoice_email.delay(invoice_id)

    return invoice


# --- Payouts ---

@router.get("/payouts", response_model=PaginatedResponse[PayoutResponse])
async def list_payouts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[PayoutStatus] = Query(None),
    influencer_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_manager),
):
    query = select(Payout)
    if status:
        query = query.where(Payout.status == status)
    if influencer_id:
        query = query.where(Payout.influencer_id == influencer_id)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(query.order_by(Payout.created_at.desc()).offset(skip).limit(limit))
    return PaginatedResponse(items=list(result.scalars().all()), total=total, skip=skip, limit=limit)


@router.post("/payouts", response_model=PayoutResponse, status_code=status.HTTP_201_CREATED)
async def create_payout(
    payload: PayoutCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_manager),
):
    payout = Payout(
        influencer_id=payload.influencer_id,
        campaign_influencer_id=payload.campaign_influencer_id,
        amount=payload.amount,
        currency=payload.currency,
        description=payload.description,
        scheduled_date=payload.scheduled_date,
        net_amount=payload.amount,  # adjusted if withholding applied
    )
    db.add(payout)
    await db.commit()
    await db.refresh(payout)

    # Notify influencer about the payout
    inf_res = await db.execute(select(Influencer).where(Influencer.id == payload.influencer_id))
    inf = inf_res.scalar_one_or_none()
    if inf and inf.user_id:
        amount_str = f"{float(payload.amount):,.2f}"
        campaign_label = payload.description or "your campaign"
        await notify_user(
            db,
            user_id=inf.user_id,
            notification_type=NotificationType.PAYMENT_SENT,
            title=f"Payment of ${amount_str} Sent",
            body=f"A payment of ${amount_str} {payload.currency} has been processed for {campaign_label}.",
            action_url="/app/payments",
            send_email_alert=True,
            email_subject=f"Payment Received: ${amount_str} {payload.currency}",
            email_html=f"<p>Great news! A payment of <strong>${amount_str} {payload.currency}</strong> has been processed for <strong>{campaign_label}</strong>. Funds will be transferred to your account shortly.</p>",
        )
        await db.commit()

    return payout


@router.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle Stripe webhook events for payment confirmations."""
    from app.core.config import settings
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY

    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event["type"] == "payment_intent.succeeded":
        pi = event["data"]["object"]
        # Update invoice status
        result = await db.execute(
            select(Invoice).where(Invoice.stripe_payment_intent_id == pi["id"])
        )
        invoice = result.scalar_one_or_none()
        if invoice:
            invoice.status = InvoiceStatus.PAID
            from datetime import datetime, timezone
            invoice.paid_at = datetime.now(timezone.utc)
            invoice.amount_paid = invoice.total_amount
            await db.commit()

    return {"status": "received"}
