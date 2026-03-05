"""Stripe subscription service."""
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import stripe
from fastapi import HTTPException

from app.config import settings
from app.core.database import SupabaseClient
from app.core.error_logger import log_error
from app.services.utils import get_profile_or_404, FRONTEND_URL

VALID_PLANS = {"monthly", "yearly"}


def _get_price_id(plan: str) -> str:
    """Get the Stripe price ID for a plan."""
    if plan == "monthly":
        price_id = settings.stripe_monthly_price_id
    elif plan == "yearly":
        price_id = settings.stripe_yearly_price_id
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid plan. Must be one of: {', '.join(sorted(VALID_PLANS))}",
        )

    if not price_id:
        raise HTTPException(status_code=500, detail="Stripe price not configured")
    return price_id


def _configure_stripe() -> None:
    """Configure the Stripe API key."""
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=500, detail="Stripe is not configured")
    stripe.api_key = settings.stripe_secret_key


class StripeService:
    """Service for Stripe subscription operations."""

    def __init__(self, db: SupabaseClient):
        self.db = db

    async def _get_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile or raise 404."""
        return await get_profile_or_404(self.db, user_id)

    async def _get_or_create_customer(self, user_id: str, email: str) -> str:
        """Get or create a Stripe customer for a user."""
        _configure_stripe()

        profile = await self._get_profile(user_id)

        if profile.get("stripe_customer_id"):
            return profile["stripe_customer_id"]

        customer = stripe.Customer.create(
            email=email,
            metadata={"user_id": user_id},
        )

        await self.db.update(
            "profiles",
            filters={"id": user_id},
            data={"stripe_customer_id": customer.id},
        )

        return customer.id

    async def create_checkout_session(
        self, user_id: str, email: str, plan: str
    ) -> Dict[str, str]:
        """Create a Stripe Checkout session."""
        _configure_stripe()
        price_id = _get_price_id(plan)
        customer_id = await self._get_or_create_customer(user_id, email)

        session = stripe.checkout.Session.create(
            customer=customer_id,
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"{FRONTEND_URL}/dashboard?subscription=success",
            cancel_url=f"{FRONTEND_URL}/pricing",
            subscription_data={"metadata": {"user_id": user_id}},
            metadata={"user_id": user_id},
        )

        return {"checkout_url": session.url}

    async def create_portal_session(self, user_id: str) -> Dict[str, str]:
        """Create a Stripe Customer Portal session."""
        _configure_stripe()
        profile = await self._get_profile(user_id)

        customer_id = profile.get("stripe_customer_id")
        if not customer_id:
            raise HTTPException(
                status_code=400,
                detail="No billing account found. Please subscribe first.",
            )

        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"{FRONTEND_URL}/dashboard/settings",
        )

        return {"portal_url": session.url}

    async def get_subscription_status(self, user_id: str) -> Dict[str, Any]:
        """Get subscription status for a user.

        If the user has a Stripe customer but isn't marked as paid,
        checks Stripe directly and syncs the profile. This self-heals
        when webhooks are delayed or missing.
        """
        profile = await self._get_profile(user_id)

        account_status = profile.get("account_status", "trial")

        # Self-heal: if user has a Stripe customer but profile isn't paid,
        # check Stripe for an active subscription and sync if found
        if account_status != "paid" and profile.get("stripe_customer_id"):
            profile = await self._sync_subscription_from_stripe(
                user_id, profile
            )
            account_status = profile.get("account_status", "trial")

        trial_ends_at = profile.get("trial_ends_at")

        is_trial_active = False
        if account_status == "trial" and trial_ends_at:
            trial_end = (
                datetime.fromisoformat(trial_ends_at.replace("Z", "+00:00"))
                if isinstance(trial_ends_at, str)
                else trial_ends_at
            )
            is_trial_active = trial_end > datetime.now(timezone.utc)

        is_paid = account_status == "paid"
        can_practice = is_paid or is_trial_active

        return {
            "account_status": account_status,
            "trial_ends_at": trial_ends_at,
            "is_trial_active": is_trial_active,
            "is_paid": is_paid,
            "can_practice": can_practice,
            "subscription_plan": profile.get("subscription_plan"),
            "subscription_current_period_end": profile.get(
                "subscription_current_period_end"
            ),
            "has_stripe_customer": bool(profile.get("stripe_customer_id")),
            "has_subscription": bool(profile.get("stripe_subscription_id")),
        }

    async def _sync_subscription_from_stripe(
        self, user_id: str, profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check Stripe for an active subscription and update profile if found."""
        try:
            _configure_stripe()
            customer_id = profile["stripe_customer_id"]
            subscriptions = stripe.Subscription.list(
                customer=customer_id, status="active", limit=1
            )

            if not subscriptions.data:
                return profile

            sub = subscriptions.data[0]
            plan = self._determine_plan(sub)
            raw_period_end = self._get_period_end(sub)
            period_end = (
                datetime.fromtimestamp(raw_period_end, tz=timezone.utc).isoformat()
                if raw_period_end
                else None
            )

            update_data = {
                "account_status": "paid",
                "stripe_subscription_id": sub.id,
                "subscription_plan": plan,
                "subscription_current_period_end": period_end,
                "trial_ends_at": None,
            }

            await self.db.update(
                "profiles", filters={"id": user_id}, data=update_data
            )

            # Return updated profile data
            return {**profile, **update_data}
        except Exception:
            # If Stripe check fails, return original profile unchanged
            return profile

    async def handle_webhook_event(
        self, payload: bytes, sig_header: str
    ) -> Dict[str, str]:
        """Handle a Stripe webhook event."""
        if not settings.stripe_webhook_secret:
            raise HTTPException(
                status_code=500, detail="Webhook secret not configured"
            )

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.stripe_webhook_secret
            )
        except ValueError as e:
            log_error(
                error=e,
                source="swallowed",
                service_name="StripeService",
                function_name="handle_webhook_event",
                status_code=400,
            )
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.SignatureVerificationError as e:
            log_error(
                error=e,
                source="swallowed",
                service_name="StripeService",
                function_name="handle_webhook_event",
                status_code=400,
            )
            raise HTTPException(status_code=400, detail="Invalid signature")

        event_type = event["type"]

        if event_type == "checkout.session.completed":
            await self._handle_checkout_completed(event["data"]["object"])
        elif event_type == "customer.subscription.updated":
            await self._handle_subscription_updated(event["data"]["object"])
        elif event_type == "customer.subscription.deleted":
            await self._handle_subscription_deleted(event["data"]["object"])
        elif event_type == "invoice.payment_failed":
            await self._handle_payment_failed(event["data"]["object"])

        return {"status": "ok"}

    async def _handle_checkout_completed(self, session: Dict[str, Any]) -> None:
        """Handle checkout.session.completed event."""
        user_id = session.get("metadata", {}).get("user_id")
        if not user_id:
            return

        subscription_id = session.get("subscription")
        if not subscription_id:
            return

        _configure_stripe()
        subscription = stripe.Subscription.retrieve(subscription_id)

        plan = self._determine_plan(subscription)

        raw_period_end = self._get_period_end(subscription)
        period_end = (
            datetime.fromtimestamp(raw_period_end, tz=timezone.utc).isoformat()
            if raw_period_end
            else None
        )

        await self.db.update(
            "profiles",
            filters={"id": user_id},
            data={
                "account_status": "paid",
                "stripe_subscription_id": subscription_id,
                "subscription_plan": plan,
                "subscription_current_period_end": period_end,
                "trial_ends_at": None,
            },
        )

    async def _handle_subscription_updated(
        self, subscription: Dict[str, Any]
    ) -> None:
        """Handle customer.subscription.updated event."""
        user_id = subscription.get("metadata", {}).get("user_id")
        if not user_id:
            return

        status = subscription.get("status")
        plan = self._determine_plan(subscription)
        raw_period_end = self._get_period_end(subscription)
        period_end = (
            datetime.fromtimestamp(raw_period_end, tz=timezone.utc).isoformat()
            if raw_period_end
            else None
        )

        update_data: Dict[str, Any] = {
            "subscription_plan": plan,
            "subscription_current_period_end": period_end,
            "stripe_subscription_id": subscription["id"],
        }

        if status == "active":
            update_data["account_status"] = "paid"
        elif status == "past_due":
            update_data["account_status"] = "past_due"

        await self.db.update("profiles", filters={"id": user_id}, data=update_data)

    async def _handle_subscription_deleted(
        self, subscription: Dict[str, Any]
    ) -> None:
        """Handle customer.subscription.deleted event."""
        user_id = subscription.get("metadata", {}).get("user_id")
        if not user_id:
            return

        await self.db.update(
            "profiles",
            filters={"id": user_id},
            data={
                "account_status": "cancelled",
                "stripe_subscription_id": None,
                "subscription_plan": None,
                "subscription_current_period_end": None,
            },
        )

    async def _handle_payment_failed(self, invoice: Dict[str, Any]) -> None:
        """Handle invoice.payment_failed event."""
        customer_id = invoice.get("customer")
        if not customer_id:
            return

        profiles = await self.db.query(
            "profiles", select="id", filters={"stripe_customer_id": customer_id}
        )
        if not profiles:
            return

        await self.db.update(
            "profiles",
            filters={"id": profiles[0]["id"]},
            data={"account_status": "past_due"},
        )

    @staticmethod
    def _get_period_end(subscription: Any) -> Optional[int]:
        """Get current_period_end from subscription or its first item.

        Newer Stripe API versions with billing_mode=flexible put
        current_period_end on the subscription item, not the subscription.
        """
        # Try subscription-level first
        period_end = None
        if isinstance(subscription, dict):
            period_end = subscription.get("current_period_end")
        else:
            period_end = getattr(subscription, "current_period_end", None)

        if period_end:
            return period_end

        # Fall back to first item
        items_data = (
            subscription.get("items", {})
            if isinstance(subscription, dict)
            else getattr(subscription, "items", {})
        )
        items = (
            items_data.get("data", [])
            if isinstance(items_data, dict)
            else getattr(items_data, "data", [])
        )
        if items:
            item = items[0]
            if isinstance(item, dict):
                return item.get("current_period_end")
            return getattr(item, "current_period_end", None)

        return None

    def _determine_plan(self, subscription: Any) -> Optional[str]:
        """Determine the plan name from a Stripe subscription."""
        items_data = subscription.get("items", {})
        if isinstance(items_data, dict):
            items = items_data.get("data", [])
        else:
            items = getattr(items_data, "data", [])

        if not items:
            return None

        item = items[0]
        if isinstance(item, dict):
            price_id = item.get("price", {}).get("id")
        else:
            price_id = item.price.id

        if price_id == settings.stripe_monthly_price_id:
            return "monthly"
        elif price_id == settings.stripe_yearly_price_id:
            return "yearly"
        return None
