"""Unit tests for Stripe subscription service."""
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.services.stripe_service import StripeService


SAMPLE_PROFILE_TRIAL = {
    "id": "user-1",
    "email": "test@example.com",
    "account_status": "trial",
    "trial_ends_at": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
    "stripe_customer_id": None,
    "stripe_subscription_id": None,
    "subscription_plan": None,
    "subscription_current_period_end": None,
}

SAMPLE_PROFILE_PAID = {
    "id": "user-1",
    "email": "test@example.com",
    "account_status": "paid",
    "trial_ends_at": None,
    "stripe_customer_id": "cus_test123",
    "stripe_subscription_id": "sub_test123",
    "subscription_plan": "monthly",
    "subscription_current_period_end": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
}

SAMPLE_PROFILE_EXPIRED = {
    "id": "user-1",
    "email": "test@example.com",
    "account_status": "trial",
    "trial_ends_at": (datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
    "stripe_customer_id": None,
    "stripe_subscription_id": None,
    "subscription_plan": None,
    "subscription_current_period_end": None,
}

SAMPLE_PROFILE_TRIAL_WITH_CUSTOMER = {
    "id": "user-1",
    "email": "test@example.com",
    "account_status": "trial",
    "trial_ends_at": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
    "stripe_customer_id": "cus_test123",
    "stripe_subscription_id": None,
    "subscription_plan": None,
    "subscription_current_period_end": None,
}


@pytest.mark.asyncio
async def test_get_subscription_status_trial_active(mock_db):
    """Active trial returns can_practice=True."""
    mock_db.query.return_value = [SAMPLE_PROFILE_TRIAL]
    service = StripeService(mock_db)

    result = await service.get_subscription_status("user-1")

    assert result["account_status"] == "trial"
    assert result["is_trial_active"] is True
    assert result["is_paid"] is False
    assert result["can_practice"] is True


@pytest.mark.asyncio
async def test_get_subscription_status_trial_expired(mock_db):
    """Expired trial returns can_practice=False."""
    mock_db.query.return_value = [SAMPLE_PROFILE_EXPIRED]
    service = StripeService(mock_db)

    result = await service.get_subscription_status("user-1")

    assert result["account_status"] == "trial"
    assert result["is_trial_active"] is False
    assert result["can_practice"] is False


@pytest.mark.asyncio
async def test_get_subscription_status_paid(mock_db):
    """Paid user returns can_practice=True."""
    mock_db.query.return_value = [SAMPLE_PROFILE_PAID]
    service = StripeService(mock_db)

    result = await service.get_subscription_status("user-1")

    assert result["account_status"] == "paid"
    assert result["is_paid"] is True
    assert result["can_practice"] is True
    assert result["subscription_plan"] == "monthly"
    assert result["has_stripe_customer"] is True
    assert result["has_subscription"] is True


@pytest.mark.asyncio
async def test_get_subscription_status_profile_not_found(mock_db):
    """Missing profile raises 404."""
    mock_db.query.return_value = []
    service = StripeService(mock_db)

    with pytest.raises(HTTPException) as exc_info:
        await service.get_subscription_status("user-1")
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_create_checkout_session(mock_db, mocker):
    """Checkout session is created with correct parameters."""
    mock_db.query.return_value = [SAMPLE_PROFILE_TRIAL]

    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_secret_key="sk_test",
                 stripe_monthly_price_id="price_monthly",
                 stripe_yearly_price_id="price_yearly",
                 cors_origins=["http://localhost:3000"])

    mock_customer = mocker.MagicMock()
    mock_customer.id = "cus_new123"
    mocker.patch("app.services.stripe_service.stripe.Customer.create", return_value=mock_customer)

    mock_session = mocker.MagicMock()
    mock_session.url = "https://checkout.stripe.com/test"
    mocker.patch("app.services.stripe_service.stripe.checkout.Session.create", return_value=mock_session)

    service = StripeService(mock_db)
    result = await service.create_checkout_session("user-1", "test@example.com", "monthly")

    assert result["checkout_url"] == "https://checkout.stripe.com/test"


@pytest.mark.asyncio
async def test_create_checkout_invalid_plan(mock_db, mocker):
    """Invalid plan raises 400."""
    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_secret_key="sk_test")

    service = StripeService(mock_db)

    with pytest.raises(HTTPException) as exc_info:
        await service.create_checkout_session("user-1", "test@example.com", "invalid")
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_create_portal_session(mock_db, mocker):
    """Portal session is created for existing customer."""
    mock_db.query.return_value = [SAMPLE_PROFILE_PAID]

    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_secret_key="sk_test",
                 cors_origins=["http://localhost:3000"])

    mock_session = mocker.MagicMock()
    mock_session.url = "https://billing.stripe.com/test"
    mocker.patch("app.services.stripe_service.stripe.billing_portal.Session.create", return_value=mock_session)

    service = StripeService(mock_db)
    result = await service.create_portal_session("user-1")

    assert result["portal_url"] == "https://billing.stripe.com/test"


@pytest.mark.asyncio
async def test_create_portal_no_customer(mock_db, mocker):
    """Portal raises 400 when no Stripe customer exists."""
    mock_db.query.return_value = [SAMPLE_PROFILE_TRIAL]

    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_secret_key="sk_test")

    service = StripeService(mock_db)

    with pytest.raises(HTTPException) as exc_info:
        await service.create_portal_session("user-1")
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_handle_webhook_checkout_completed(mock_db, mocker):
    """Checkout completed webhook updates profile to paid."""
    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_secret_key="sk_test",
                 stripe_webhook_secret="whsec_test",
                 stripe_monthly_price_id="price_monthly",
                 stripe_yearly_price_id="price_yearly")

    mock_sub = mocker.MagicMock()
    mock_sub.current_period_end = 1700000000
    mock_sub.get.return_value = {"data": [{"price": {"id": "price_monthly"}}]}
    mocker.patch("app.services.stripe_service.stripe.Subscription.retrieve", return_value=mock_sub)

    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "metadata": {"user_id": "user-1"},
                "subscription": "sub_new123",
            }
        },
    }
    mocker.patch("app.services.stripe_service.stripe.Webhook.construct_event", return_value=event)

    service = StripeService(mock_db)
    result = await service.handle_webhook_event(b"payload", "sig")

    assert result["status"] == "ok"
    mock_db.update.assert_called()
    call_data = mock_db.update.call_args[1]["data"]
    assert call_data["account_status"] == "paid"
    assert call_data["stripe_subscription_id"] == "sub_new123"


@pytest.mark.asyncio
async def test_handle_webhook_subscription_deleted(mock_db, mocker):
    """Subscription deleted webhook sets account to cancelled."""
    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_webhook_secret="whsec_test")

    event = {
        "type": "customer.subscription.deleted",
        "data": {
            "object": {
                "id": "sub_123",
                "metadata": {"user_id": "user-1"},
            }
        },
    }
    mocker.patch("app.services.stripe_service.stripe.Webhook.construct_event", return_value=event)

    service = StripeService(mock_db)
    result = await service.handle_webhook_event(b"payload", "sig")

    assert result["status"] == "ok"
    mock_db.update.assert_called()
    call_data = mock_db.update.call_args[1]["data"]
    assert call_data["account_status"] == "cancelled"
    assert call_data["stripe_subscription_id"] is None


@pytest.mark.asyncio
async def test_handle_webhook_invalid_signature(mock_db, mocker):
    """Invalid webhook signature raises 400."""
    import stripe as stripe_lib

    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_webhook_secret="whsec_test")
    mocker.patch(
        "app.services.stripe_service.stripe.Webhook.construct_event",
        side_effect=stripe_lib.SignatureVerificationError("bad sig", "sig"),
    )

    service = StripeService(mock_db)

    with pytest.raises(HTTPException) as exc_info:
        await service.handle_webhook_event(b"payload", "bad_sig")
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_handle_webhook_invalid_payload(mock_db, mocker):
    """Invalid webhook payload raises 400."""
    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_webhook_secret="whsec_test")
    mocker.patch(
        "app.services.stripe_service.stripe.Webhook.construct_event",
        side_effect=ValueError("bad payload"),
    )

    service = StripeService(mock_db)

    with pytest.raises(HTTPException) as exc_info:
        await service.handle_webhook_event(b"bad", "sig")
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_handle_webhook_no_secret(mock_db, mocker):
    """Missing webhook secret raises 500."""
    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_webhook_secret=None)

    service = StripeService(mock_db)

    with pytest.raises(HTTPException) as exc_info:
        await service.handle_webhook_event(b"payload", "sig")
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_handle_webhook_subscription_updated_active(mock_db, mocker):
    """Subscription updated to active sets account to paid."""
    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_webhook_secret="whsec_test",
                 stripe_monthly_price_id="price_monthly",
                 stripe_yearly_price_id="price_yearly")

    event = {
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_123",
                "metadata": {"user_id": "user-1"},
                "status": "active",
                "current_period_end": 1700000000,
                "items": {"data": [{"price": {"id": "price_monthly"}}]},
            }
        },
    }
    mocker.patch("app.services.stripe_service.stripe.Webhook.construct_event", return_value=event)

    service = StripeService(mock_db)
    result = await service.handle_webhook_event(b"payload", "sig")

    assert result["status"] == "ok"
    mock_db.update.assert_called_once()
    call_data = mock_db.update.call_args[1]["data"]
    assert call_data["account_status"] == "paid"
    assert call_data["subscription_plan"] == "monthly"
    assert call_data["stripe_subscription_id"] == "sub_123"


@pytest.mark.asyncio
async def test_handle_webhook_subscription_updated_past_due(mock_db, mocker):
    """Subscription updated to past_due sets account_status."""
    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_webhook_secret="whsec_test",
                 stripe_monthly_price_id="price_monthly",
                 stripe_yearly_price_id="price_yearly")

    event = {
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_123",
                "metadata": {"user_id": "user-1"},
                "status": "past_due",
                "current_period_end": 1700000000,
                "items": {"data": [{"price": {"id": "price_monthly"}}]},
            }
        },
    }
    mocker.patch("app.services.stripe_service.stripe.Webhook.construct_event", return_value=event)

    service = StripeService(mock_db)
    result = await service.handle_webhook_event(b"payload", "sig")

    assert result["status"] == "ok"
    call_data = mock_db.update.call_args[1]["data"]
    assert call_data["account_status"] == "past_due"


@pytest.mark.asyncio
async def test_handle_webhook_subscription_updated_no_user(mock_db, mocker):
    """Subscription updated without user_id is ignored."""
    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_webhook_secret="whsec_test")

    event = {
        "type": "customer.subscription.updated",
        "data": {
            "object": {
                "id": "sub_123",
                "metadata": {},
                "status": "active",
                "current_period_end": 1700000000,
                "items": {"data": []},
            }
        },
    }
    mocker.patch("app.services.stripe_service.stripe.Webhook.construct_event", return_value=event)

    service = StripeService(mock_db)
    result = await service.handle_webhook_event(b"payload", "sig")

    assert result["status"] == "ok"
    mock_db.update.assert_not_called()


@pytest.mark.asyncio
async def test_handle_webhook_payment_failed(mock_db, mocker):
    """Payment failed webhook sets account to past_due."""
    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_webhook_secret="whsec_test")

    event = {
        "type": "invoice.payment_failed",
        "data": {
            "object": {
                "customer": "cus_test123",
            }
        },
    }
    mocker.patch("app.services.stripe_service.stripe.Webhook.construct_event", return_value=event)

    mock_db.query.return_value = [{"id": "user-1"}]

    service = StripeService(mock_db)
    result = await service.handle_webhook_event(b"payload", "sig")

    assert result["status"] == "ok"
    mock_db.update.assert_called_once()
    call_data = mock_db.update.call_args[1]["data"]
    assert call_data["account_status"] == "past_due"


@pytest.mark.asyncio
async def test_handle_webhook_payment_failed_no_customer(mock_db, mocker):
    """Payment failed with no customer is ignored."""
    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_webhook_secret="whsec_test")

    event = {
        "type": "invoice.payment_failed",
        "data": {"object": {}},
    }
    mocker.patch("app.services.stripe_service.stripe.Webhook.construct_event", return_value=event)

    service = StripeService(mock_db)
    result = await service.handle_webhook_event(b"payload", "sig")

    assert result["status"] == "ok"
    mock_db.update.assert_not_called()


@pytest.mark.asyncio
async def test_handle_webhook_payment_failed_unknown_customer(mock_db, mocker):
    """Payment failed for unknown customer is ignored."""
    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_webhook_secret="whsec_test")

    event = {
        "type": "invoice.payment_failed",
        "data": {"object": {"customer": "cus_unknown"}},
    }
    mocker.patch("app.services.stripe_service.stripe.Webhook.construct_event", return_value=event)

    mock_db.query.return_value = []

    service = StripeService(mock_db)
    result = await service.handle_webhook_event(b"payload", "sig")

    assert result["status"] == "ok"
    mock_db.update.assert_not_called()


@pytest.mark.asyncio
async def test_create_checkout_existing_customer(mock_db, mocker):
    """Checkout reuses existing Stripe customer."""
    mock_db.query.return_value = [SAMPLE_PROFILE_PAID]

    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_secret_key="sk_test",
                 stripe_monthly_price_id="price_monthly",
                 stripe_yearly_price_id="price_yearly",
                 cors_origins=["http://localhost:3000"])

    mock_session = mocker.MagicMock()
    mock_session.url = "https://checkout.stripe.com/test"
    mocker.patch("app.services.stripe_service.stripe.checkout.Session.create", return_value=mock_session)

    service = StripeService(mock_db)
    result = await service.create_checkout_session("user-1", "test@example.com", "monthly")

    assert result["checkout_url"] == "https://checkout.stripe.com/test"
    # Should not create a new customer since one exists
    mocker.patch("app.services.stripe_service.stripe.Customer.create").assert_not_called()


@pytest.mark.asyncio
async def test_create_checkout_yearly(mock_db, mocker):
    """Checkout session works for yearly plan."""
    mock_db.query.return_value = [SAMPLE_PROFILE_TRIAL]

    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_secret_key="sk_test",
                 stripe_monthly_price_id="price_monthly",
                 stripe_yearly_price_id="price_yearly",
                 cors_origins=["http://localhost:3000"])

    mock_customer = mocker.MagicMock()
    mock_customer.id = "cus_new"
    mocker.patch("app.services.stripe_service.stripe.Customer.create", return_value=mock_customer)

    mock_session = mocker.MagicMock()
    mock_session.url = "https://checkout.stripe.com/yearly"
    mocker.patch("app.services.stripe_service.stripe.checkout.Session.create", return_value=mock_session)

    service = StripeService(mock_db)
    result = await service.create_checkout_session("user-1", "test@example.com", "yearly")

    assert result["checkout_url"] == "https://checkout.stripe.com/yearly"


@pytest.mark.asyncio
async def test_configure_stripe_no_key(mock_db, mocker):
    """Missing Stripe key raises 500."""
    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_secret_key=None)

    service = StripeService(mock_db)

    with pytest.raises(HTTPException) as exc_info:
        await service.create_portal_session("user-1")
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_get_price_id_not_configured(mock_db, mocker):
    """Missing price ID raises 500."""
    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_secret_key="sk_test",
                 stripe_monthly_price_id=None,
                 cors_origins=["http://localhost:3000"])

    mock_db.query.return_value = [SAMPLE_PROFILE_PAID]

    service = StripeService(mock_db)

    with pytest.raises(HTTPException) as exc_info:
        await service.create_checkout_session("user-1", "test@example.com", "monthly")
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_determine_plan_yearly(mock_db, mocker):
    """_determine_plan identifies yearly plan."""
    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_monthly_price_id="price_monthly",
                 stripe_yearly_price_id="price_yearly",
                 stripe_secret_key="sk_test",
                 stripe_webhook_secret="whsec_test")

    mock_sub = mocker.MagicMock()
    mock_sub.current_period_end = 1700000000
    mock_sub.get.return_value = {"data": [{"price": {"id": "price_yearly"}}]}
    mocker.patch("app.services.stripe_service.stripe.Subscription.retrieve", return_value=mock_sub)

    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "metadata": {"user_id": "user-1"},
                "subscription": "sub_yearly",
            }
        },
    }
    mocker.patch("app.services.stripe_service.stripe.Webhook.construct_event", return_value=event)

    service = StripeService(mock_db)
    await service.handle_webhook_event(b"payload", "sig")

    call_data = mock_db.update.call_args[1]["data"]
    assert call_data["subscription_plan"] == "yearly"


@pytest.mark.asyncio
async def test_determine_plan_unknown_price(mock_db, mocker):
    """_determine_plan returns None for unknown price."""
    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_monthly_price_id="price_monthly",
                 stripe_yearly_price_id="price_yearly",
                 stripe_secret_key="sk_test",
                 stripe_webhook_secret="whsec_test")

    mock_sub = mocker.MagicMock()
    mock_sub.current_period_end = 1700000000
    mock_sub.get.return_value = {"data": [{"price": {"id": "price_unknown"}}]}
    mocker.patch("app.services.stripe_service.stripe.Subscription.retrieve", return_value=mock_sub)

    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "metadata": {"user_id": "user-1"},
                "subscription": "sub_test",
            }
        },
    }
    mocker.patch("app.services.stripe_service.stripe.Webhook.construct_event", return_value=event)

    service = StripeService(mock_db)
    await service.handle_webhook_event(b"payload", "sig")

    call_data = mock_db.update.call_args[1]["data"]
    assert call_data["subscription_plan"] is None


@pytest.mark.asyncio
async def test_determine_plan_no_items(mock_db, mocker):
    """_determine_plan returns None when no items."""
    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_monthly_price_id="price_monthly",
                 stripe_yearly_price_id="price_yearly",
                 stripe_secret_key="sk_test",
                 stripe_webhook_secret="whsec_test")

    mock_sub = mocker.MagicMock()
    mock_sub.current_period_end = 1700000000
    mock_sub.get.return_value = {"data": []}
    mocker.patch("app.services.stripe_service.stripe.Subscription.retrieve", return_value=mock_sub)

    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "metadata": {"user_id": "user-1"},
                "subscription": "sub_test",
            }
        },
    }
    mocker.patch("app.services.stripe_service.stripe.Webhook.construct_event", return_value=event)

    service = StripeService(mock_db)
    await service.handle_webhook_event(b"payload", "sig")

    call_data = mock_db.update.call_args[1]["data"]
    assert call_data["subscription_plan"] is None


@pytest.mark.asyncio
async def test_checkout_completed_no_user_id(mock_db, mocker):
    """Checkout completed without user_id is ignored."""
    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_webhook_secret="whsec_test")

    event = {
        "type": "checkout.session.completed",
        "data": {"object": {"metadata": {}, "subscription": "sub_test"}},
    }
    mocker.patch("app.services.stripe_service.stripe.Webhook.construct_event", return_value=event)

    service = StripeService(mock_db)
    result = await service.handle_webhook_event(b"payload", "sig")

    assert result["status"] == "ok"
    mock_db.update.assert_not_called()


@pytest.mark.asyncio
async def test_checkout_completed_no_subscription(mock_db, mocker):
    """Checkout completed without subscription ID is ignored."""
    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_webhook_secret="whsec_test")

    event = {
        "type": "checkout.session.completed",
        "data": {"object": {"metadata": {"user_id": "user-1"}, "subscription": None}},
    }
    mocker.patch("app.services.stripe_service.stripe.Webhook.construct_event", return_value=event)

    service = StripeService(mock_db)
    result = await service.handle_webhook_event(b"payload", "sig")

    assert result["status"] == "ok"
    mock_db.update.assert_not_called()


@pytest.mark.asyncio
async def test_sync_from_stripe_when_customer_has_active_sub(mock_db, mocker):
    """Status check syncs from Stripe when customer exists but profile not paid."""
    mock_db.query.return_value = [SAMPLE_PROFILE_TRIAL_WITH_CUSTOMER]

    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_secret_key="sk_test",
                 stripe_monthly_price_id="price_monthly",
                 stripe_yearly_price_id="price_yearly")

    mock_sub = mocker.MagicMock()
    mock_sub.id = "sub_active"
    mock_sub.current_period_end = 1700000000
    mock_sub.get.return_value = {"data": [{"price": {"id": "price_monthly"}}]}

    mock_list = mocker.MagicMock()
    mock_list.data = [mock_sub]
    mocker.patch("app.services.stripe_service.stripe.Subscription.list",
                 return_value=mock_list)

    service = StripeService(mock_db)
    result = await service.get_subscription_status("user-1")

    assert result["account_status"] == "paid"
    assert result["is_paid"] is True
    assert result["can_practice"] is True
    mock_db.update.assert_called_once()
    call_data = mock_db.update.call_args[1]["data"]
    assert call_data["account_status"] == "paid"
    assert call_data["stripe_subscription_id"] == "sub_active"


@pytest.mark.asyncio
async def test_sync_from_stripe_no_active_sub(mock_db, mocker):
    """Status check doesn't change profile when no active Stripe subscription."""
    mock_db.query.return_value = [SAMPLE_PROFILE_TRIAL_WITH_CUSTOMER]

    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_secret_key="sk_test")

    mock_list = mocker.MagicMock()
    mock_list.data = []
    mocker.patch("app.services.stripe_service.stripe.Subscription.list",
                 return_value=mock_list)

    service = StripeService(mock_db)
    result = await service.get_subscription_status("user-1")

    assert result["account_status"] == "trial"
    assert result["is_trial_active"] is True
    mock_db.update.assert_not_called()


@pytest.mark.asyncio
async def test_sync_from_stripe_api_error_returns_original(mock_db, mocker):
    """Status check returns original profile when Stripe API fails."""
    mock_db.query.return_value = [SAMPLE_PROFILE_TRIAL_WITH_CUSTOMER]

    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_secret_key="sk_test")

    mocker.patch("app.services.stripe_service.stripe.Subscription.list",
                 side_effect=Exception("Stripe API error"))

    service = StripeService(mock_db)
    result = await service.get_subscription_status("user-1")

    assert result["account_status"] == "trial"
    assert result["is_trial_active"] is True
    mock_db.update.assert_not_called()


@pytest.mark.asyncio
async def test_no_sync_when_no_stripe_customer(mock_db):
    """Status check skips Stripe sync when no customer ID exists."""
    mock_db.query.return_value = [SAMPLE_PROFILE_TRIAL]
    service = StripeService(mock_db)

    result = await service.get_subscription_status("user-1")

    assert result["account_status"] == "trial"
    # No update call means no Stripe sync attempted
    mock_db.update.assert_not_called()


@pytest.mark.asyncio
async def test_no_sync_when_already_paid(mock_db):
    """Status check skips Stripe sync when already paid."""
    mock_db.query.return_value = [SAMPLE_PROFILE_PAID]
    service = StripeService(mock_db)

    result = await service.get_subscription_status("user-1")

    assert result["account_status"] == "paid"
    mock_db.update.assert_not_called()


def test_get_period_end_from_subscription():
    """Gets current_period_end from subscription object."""
    sub = {"current_period_end": 1700000000, "items": {"data": []}}
    assert StripeService._get_period_end(sub) == 1700000000


def test_get_period_end_from_item():
    """Falls back to item-level current_period_end (flexible billing)."""
    sub = {
        "items": {
            "data": [{"current_period_end": 1700000000}]
        }
    }
    assert StripeService._get_period_end(sub) == 1700000000


def test_get_period_end_none():
    """Returns None when no period end found."""
    sub = {"items": {"data": []}}
    assert StripeService._get_period_end(sub) is None
