"""Stripe subscription management endpoints."""
from fastapi import APIRouter, Request

from app.core.dependencies import CurrentUser, Database
from app.models.stripe import (
    CheckoutRequest,
    CheckoutResponse,
    PortalResponse,
    SubscriptionStatusResponse,
)
from app.services.stripe_service import StripeService

router = APIRouter()


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    body: CheckoutRequest,
    user: CurrentUser,
    db: Database,
):
    """Create a Stripe Checkout session for subscription."""
    service = StripeService(db)
    result = await service.create_checkout_session(
        user_id=user["id"],
        email=user["email"],
        plan=body.plan,
    )
    return CheckoutResponse(**result)


@router.post("/portal", response_model=PortalResponse)
async def create_portal(
    user: CurrentUser,
    db: Database,
):
    """Create a Stripe Customer Portal session."""
    service = StripeService(db)
    result = await service.create_portal_session(user_id=user["id"])
    return PortalResponse(**result)


@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
    user: CurrentUser,
    db: Database,
):
    """Get the current user's subscription status."""
    service = StripeService(db)
    status = await service.get_subscription_status(user["id"])
    return SubscriptionStatusResponse(**status)


@router.post("/webhook")
async def stripe_webhook(request: Request, db: Database):
    """Handle Stripe webhook events. Verified by signature, no auth required."""
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")

    service = StripeService(db)
    result = await service.handle_webhook_event(payload, signature)
    return result
