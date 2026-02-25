"""Pydantic models for Stripe subscription endpoints."""
from typing import Optional

from pydantic import BaseModel


class CheckoutRequest(BaseModel):
    """Request to create a Stripe Checkout session."""

    plan: str  # 'monthly' or 'yearly'


class CheckoutResponse(BaseModel):
    """Response with Stripe Checkout session URL."""

    checkout_url: str


class PortalResponse(BaseModel):
    """Response with Stripe Customer Portal URL."""

    portal_url: str


class SubscriptionStatusResponse(BaseModel):
    """Response with current subscription status."""

    account_status: str
    trial_ends_at: Optional[str] = None
    is_trial_active: bool = False
    is_paid: bool = False
    can_practice: bool = False
    subscription_plan: Optional[str] = None
    subscription_current_period_end: Optional[str] = None
    has_stripe_customer: bool = False
    has_subscription: bool = False
