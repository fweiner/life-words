"""Integration tests for Stripe subscription endpoints."""
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock


SAMPLE_USER = {
    "id": "user-123",
    "email": "test@example.com",
    "role": "authenticated",
}

SAMPLE_PROFILE_TRIAL = {
    "id": "user-123",
    "email": "test@example.com",
    "account_status": "trial",
    "trial_ends_at": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
    "stripe_customer_id": None,
    "stripe_subscription_id": None,
    "subscription_plan": None,
    "subscription_current_period_end": None,
}

SAMPLE_PROFILE_PAID = {
    "id": "user-123",
    "email": "test@example.com",
    "account_status": "paid",
    "trial_ends_at": None,
    "stripe_customer_id": "cus_test",
    "stripe_subscription_id": "sub_test",
    "subscription_plan": "monthly",
    "subscription_current_period_end": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
}


def _setup_overrides(app, mock_db, user=SAMPLE_USER):
    from app.core.auth import get_current_user
    from app.core.dependencies import get_db

    async def override_get_current_user():
        return user

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db] = override_get_db


def test_get_subscription_status(app, client, mock_db):
    """GET /api/stripe/status returns subscription info."""
    _setup_overrides(app, mock_db)
    mock_db.query.return_value = [SAMPLE_PROFILE_TRIAL]

    response = client.get(
        "/api/stripe/status",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["account_status"] == "trial"
    assert data["is_trial_active"] is True
    assert data["can_practice"] is True


def test_get_subscription_status_unauthorized(client):
    """GET /api/stripe/status requires auth."""
    response = client.get("/api/stripe/status")
    assert response.status_code == 401


def test_checkout_creates_session(app, client, mock_db, mocker):
    """POST /api/stripe/checkout creates Stripe checkout."""
    _setup_overrides(app, mock_db)
    mock_db.query.return_value = [SAMPLE_PROFILE_TRIAL]

    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_secret_key="sk_test",
                 stripe_monthly_price_id="price_monthly",
                 stripe_yearly_price_id="price_yearly",
                 cors_origins=["http://localhost:3000"])

    mock_customer = MagicMock()
    mock_customer.id = "cus_new"
    mocker.patch("app.services.stripe_service.stripe.Customer.create", return_value=mock_customer)

    mock_session = MagicMock()
    mock_session.url = "https://checkout.stripe.com/test"
    mocker.patch("app.services.stripe_service.stripe.checkout.Session.create", return_value=mock_session)

    response = client.post(
        "/api/stripe/checkout",
        json={"plan": "monthly"},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    assert response.json()["checkout_url"] == "https://checkout.stripe.com/test"


def test_checkout_invalid_plan(app, client, mock_db, mocker):
    """POST /api/stripe/checkout with invalid plan returns 400."""
    _setup_overrides(app, mock_db)

    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_secret_key="sk_test")

    response = client.post(
        "/api/stripe/checkout",
        json={"plan": "invalid"},
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 400


def test_portal_creates_session(app, client, mock_db, mocker):
    """POST /api/stripe/portal creates Stripe portal session."""
    _setup_overrides(app, mock_db)
    mock_db.query.return_value = [SAMPLE_PROFILE_PAID]

    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_secret_key="sk_test",
                 cors_origins=["http://localhost:3000"])

    mock_session = MagicMock()
    mock_session.url = "https://billing.stripe.com/test"
    mocker.patch("app.services.stripe_service.stripe.billing_portal.Session.create", return_value=mock_session)

    response = client.post(
        "/api/stripe/portal",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    assert response.json()["portal_url"] == "https://billing.stripe.com/test"


def test_portal_no_customer(app, client, mock_db, mocker):
    """POST /api/stripe/portal without Stripe customer returns 400."""
    _setup_overrides(app, mock_db)
    mock_db.query.return_value = [SAMPLE_PROFILE_TRIAL]

    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_secret_key="sk_test")

    response = client.post(
        "/api/stripe/portal",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 400


def test_webhook_no_auth_required(app, client, mock_db, mocker):
    """POST /api/stripe/webhook doesn't require auth token."""
    from app.core.dependencies import get_db

    async def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    mocker.patch("app.services.stripe_service.settings", autospec=True,
                 stripe_webhook_secret="whsec_test")

    event = {
        "type": "checkout.session.completed",
        "data": {"object": {"metadata": {}, "subscription": None}},
    }
    mocker.patch("app.services.stripe_service.stripe.Webhook.construct_event", return_value=event)

    response = client.post(
        "/api/stripe/webhook",
        content=b"raw body",
        headers={"stripe-signature": "test_sig"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
