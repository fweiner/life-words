"""Unit tests for verify_can_practice utility."""
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.services.utils import verify_can_practice


@pytest.mark.asyncio
async def test_verify_can_practice_paid(mock_db):
    """Paid users can practice."""
    mock_db.query.return_value = [
        {"account_status": "paid", "trial_ends_at": None}
    ]

    # Should not raise
    await verify_can_practice(mock_db, "user-1")


@pytest.mark.asyncio
async def test_verify_can_practice_active_trial(mock_db):
    """Active trial users can practice."""
    future_date = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    mock_db.query.return_value = [
        {"account_status": "trial", "trial_ends_at": future_date}
    ]

    # Should not raise
    await verify_can_practice(mock_db, "user-1")


@pytest.mark.asyncio
async def test_verify_can_practice_expired_trial(mock_db):
    """Expired trial users cannot practice."""
    past_date = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    mock_db.query.return_value = [
        {"account_status": "trial", "trial_ends_at": past_date}
    ]

    with pytest.raises(HTTPException) as exc_info:
        await verify_can_practice(mock_db, "user-1")
    assert exc_info.value.status_code == 403
    assert "trial has expired" in exc_info.value.detail


@pytest.mark.asyncio
async def test_verify_can_practice_cancelled(mock_db):
    """Cancelled users cannot practice."""
    mock_db.query.return_value = [
        {"account_status": "cancelled", "trial_ends_at": None}
    ]

    with pytest.raises(HTTPException) as exc_info:
        await verify_can_practice(mock_db, "user-1")
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_verify_can_practice_profile_not_found(mock_db):
    """Missing profile raises 404."""
    mock_db.query.return_value = []

    with pytest.raises(HTTPException) as exc_info:
        await verify_can_practice(mock_db, "user-1")
    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
async def test_verify_can_practice_trial_no_end_date(mock_db):
    """Trial with no end date cannot practice."""
    mock_db.query.return_value = [
        {"account_status": "trial", "trial_ends_at": None}
    ]

    with pytest.raises(HTTPException) as exc_info:
        await verify_can_practice(mock_db, "user-1")
    assert exc_info.value.status_code == 403
