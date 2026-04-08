"""
Payment processing service for sales proposals using Stripe
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sales import (
    SalesProposal, ProposalPayment, PaymentLink, SalesSettings
)


class StripePaymentProcessor:
    """
    Service for processing payments via Stripe.
    Handles payment intents, invoices, and payment links.
    """

    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key
        self.stripe = None
        # In production, initialize Stripe client:
        # import stripe
        # stripe.api_key = secret_key

    async def create_payment_intent(
        self,
        db: AsyncSession,
        proposal: SalesProposal,
        amount: Optional[Decimal] = None,
        description: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Stripe payment intent for a proposal.
        Returns payment intent details including client secret.
        """
        if not self.stripe:
            return None  # Stripe not configured

        try:
            payment_amount = amount or proposal.total_value
            # Convert to cents (Stripe expects integer amounts)
            amount_cents = int(float(payment_amount) * 100)

            # Create payment intent
            # intent = stripe.PaymentIntent.create(
            #     amount=amount_cents,
            #     currency=proposal.currency.lower(),
            #     description=description or f"Proposal {proposal.proposal_number}",
            #     metadata={
            #         "proposal_id": proposal.id,
            #         "lead_id": proposal.lead_id,
            #     },
            # )

            # For mock purposes, return a sample response
            intent = {
                "id": f"pi_{proposal.id}_{datetime.utcnow().timestamp()}",
                "client_secret": f"pi_{proposal.id}_secret_{datetime.utcnow().timestamp()}",
                "status": "requires_payment_method",
                "amount": amount_cents,
                "currency": proposal.currency.lower(),
            }

            # Save payment intent ID
            if proposal.payments:
                payment = proposal.payments[0]
            else:
                payment = ProposalPayment(
                    proposal_id=proposal.id,
                    amount=payment_amount,
                    currency=proposal.currency,
                    status="pending",
                )
                proposal.payments.append(payment)

            payment.stripe_payment_intent_id = intent["id"]
            await db.commit()

            return intent

        except Exception as e:
            print(f"Error creating payment intent: {e}")
            return None

    async def create_payment_link(
        self,
        db: AsyncSession,
        proposal: SalesProposal,
        return_url: str = "https://example.com/proposals",
    ) -> Optional[str]:
        """
        Create a Stripe payment link for a proposal.
        Returns the shareable payment URL.
        """
        if not self.stripe:
            return None

        try:
            # Create payment link
            # link = stripe.PaymentLink.create(
            #     line_items=[{
            #         "price_data": {
            #             "currency": proposal.currency.lower(),
            #             "product_data": {
            #                 "name": proposal.title,
            #                 "description": proposal.summary or "",
            #             },
            #             "unit_amount": int(float(proposal.total_value) * 100),
            #         },
            #         "quantity": 1,
            #     }],
            #     after_completion={
            #         "type": "redirect",
            #         "redirect": {
            #             "url": return_url,
            #         },
            #     },
            # )

            # For mock purposes
            link = {
                "id": f"plink_{proposal.id}_{datetime.utcnow().timestamp()}",
                "url": f"https://checkout.stripe.com/pay/plink_{proposal.id}",
            }

            # Save payment link
            payment_link = PaymentLink(
                proposal_id=proposal.id,
                stripe_link_id=link["id"],
                payment_link_url=link["url"],
                is_active=True,
                expires_at=datetime.utcnow() + timedelta(days=30),
            )
            db.add(payment_link)
            await db.commit()

            return link["url"]

        except Exception as e:
            print(f"Error creating payment link: {e}")
            return None

    async def confirm_payment(
        self,
        db: AsyncSession,
        proposal: SalesProposal,
        payment_intent_id: str,
    ) -> bool:
        """
        Confirm a payment from a webhook.
        """
        try:
            # Retrieve payment intent from Stripe
            # intent = stripe.PaymentIntent.retrieve(payment_intent_id)

            # For mock purposes
            intent_status = "succeeded"

            if intent_status == "succeeded":
                # Update payment record
                if proposal.payments:
                    payment = proposal.payments[0]
                    payment.status = "completed"
                    payment.paid_at = datetime.utcnow()

                # Update proposal status
                proposal.status = "paid"

                await db.commit()
                return True

            return False

        except Exception as e:
            print(f"Error confirming payment: {e}")
            return False

    async def refund_payment(
        self,
        db: AsyncSession,
        payment: ProposalPayment,
        amount: Optional[Decimal] = None,
    ) -> bool:
        """
        Refund a payment (full or partial).
        """
        if not payment.stripe_payment_intent_id:
            return False

        try:
            refund_amount = amount or payment.amount

            # Create refund
            # refund = stripe.Refund.create(
            #     payment_intent=payment.stripe_payment_intent_id,
            #     amount=int(float(refund_amount) * 100) if amount else None,
            # )

            # Update payment record
            payment.status = "refunded"
            payment.refunded_at = datetime.utcnow()
            payment.refund_amount = refund_amount

            await db.commit()
            return True

        except Exception as e:
            print(f"Error refunding payment: {e}")
            return False

    async def track_payment_link_click(
        self,
        db: AsyncSession,
        payment_link: PaymentLink,
    ) -> None:
        """
        Track when a payment link is clicked.
        """
        payment_link.link_clicks += 1
        payment_link.last_clicked_at = datetime.utcnow()
        await db.commit()

    async def get_payment_settings(
        self,
        db: AsyncSession,
    ) -> Optional[Dict[str, Any]]:
        """
        Get payment configuration settings.
        """
        result = await db.execute(select(SalesSettings).where(SalesSettings.id == 1))
        settings = result.scalar_one_or_none()

        if not settings:
            return None

        return {
            "enabled": settings.enable_payment_collection,
            "stripe_public_key": settings.stripe_public_key,
            "stripe_secret_key": settings.stripe_secret_key,
        }

    async def check_invoice_due(
        self,
        db: AsyncSession,
        proposal: SalesProposal,
    ) -> bool:
        """
        Check if a proposal payment is overdue.
        """
        if not proposal.payments:
            return False

        payment = proposal.payments[0]

        if payment.due_date and payment.status == "pending":
            return payment.due_date < datetime.utcnow()

        return False

    async def send_payment_reminder(
        self,
        db: AsyncSession,
        payment: ProposalPayment,
    ) -> bool:
        """
        Send payment reminder email to prospect.
        In production, integrate with SendGrid/Mailgun.
        """
        # TODO: Implement email sending
        # await send_email(
        #     to=payment.proposal.lead.contact_email,
        #     subject=f"Payment Due: {payment.proposal.title}",
        #     template="payment_reminder",
        #     variables={
        #         "proposal_title": payment.proposal.title,
        #         "amount": payment.amount,
        #         "due_date": payment.due_date,
        #         "payment_link": payment.proposal.payment_link.payment_link_url if payment.proposal.payment_link else "",
        #     }
        # )
        return True


# Singleton instance
stripe_payment_processor = StripePaymentProcessor()


async def initialize_payment_processor(
    db: AsyncSession,
    secret_key: Optional[str] = None,
) -> None:
    """
    Initialize the Stripe payment processor.
    """
    global stripe_payment_processor

    if secret_key:
        stripe_payment_processor = StripePaymentProcessor(secret_key=secret_key)
    else:
        settings = await stripe_payment_processor.get_payment_settings(db)
        if settings and settings.get("stripe_secret_key"):
            stripe_payment_processor = StripePaymentProcessor(
                secret_key=settings["stripe_secret_key"]
            )
