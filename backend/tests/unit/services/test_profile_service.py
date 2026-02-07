"""Unit tests for profile service."""
import pytest
from datetime import datetime, timezone


SAMPLE_PROFILE = {
    "id": "user-123",
    "email": "test@example.com",
    "full_name": "John Doe",
    "date_of_birth": "1980-01-15",
    "created_at": datetime.now(timezone.utc).isoformat(),
    "updated_at": datetime.now(timezone.utc).isoformat(),
}


@pytest.mark.asyncio
async def test_get_or_create_profile_existing(mock_db):
    """Test getting an existing profile."""
    from app.services.profile_service import ProfileService

    mock_db.query.return_value = [SAMPLE_PROFILE]

    service = ProfileService(mock_db)
    result = await service.get_or_create_profile("user-123", "test@example.com")

    assert result["full_name"] == "John Doe"
    mock_db.query.assert_called_once_with("profiles", filters={"id": "user-123"})
    mock_db.insert.assert_not_called()


@pytest.mark.asyncio
async def test_get_or_create_profile_creates_new(mock_db):
    """Test creating a profile when none exists."""
    from app.services.profile_service import ProfileService

    mock_db.query.return_value = []
    new_profile = {**SAMPLE_PROFILE, "full_name": None}
    mock_db.insert.return_value = [new_profile]

    service = ProfileService(mock_db)
    result = await service.get_or_create_profile("user-123", "test@example.com")

    assert result["full_name"] is None
    mock_db.insert.assert_called_once_with(
        "profiles",
        {"id": "user-123", "email": "test@example.com", "full_name": None}
    )


@pytest.mark.asyncio
async def test_get_or_create_profile_handles_dict_return(mock_db):
    """Test handling when insert returns a dict instead of list."""
    from app.services.profile_service import ProfileService

    mock_db.query.return_value = []
    new_profile = {**SAMPLE_PROFILE, "full_name": None}
    mock_db.insert.return_value = new_profile  # dict, not list

    service = ProfileService(mock_db)
    result = await service.get_or_create_profile("user-123", "test@example.com")

    assert result["id"] == "user-123"


@pytest.mark.asyncio
async def test_get_profile(mock_db):
    """Test get_profile delegates to get_or_create_profile."""
    from app.services.profile_service import ProfileService

    mock_db.query.return_value = [SAMPLE_PROFILE]

    service = ProfileService(mock_db)
    result = await service.get_profile("user-123", "test@example.com")

    assert result["full_name"] == "John Doe"


@pytest.mark.asyncio
async def test_update_profile_with_fields(mock_db):
    """Test updating profile with specific fields."""
    from app.services.profile_service import ProfileService
    from app.models.profile import ProfileUpdate

    mock_db.query.return_value = [SAMPLE_PROFILE]
    updated = {**SAMPLE_PROFILE, "full_name": "Jane Doe"}
    mock_db.update.return_value = updated

    service = ProfileService(mock_db)
    result = await service.update_profile(
        "user-123",
        "test@example.com",
        ProfileUpdate(full_name="Jane Doe")
    )

    assert result["full_name"] == "Jane Doe"
    mock_db.update.assert_called_once_with(
        "profiles",
        filters={"id": "user-123"},
        data={"full_name": "Jane Doe"}
    )


@pytest.mark.asyncio
async def test_update_profile_with_date_of_birth(mock_db):
    """Test updating profile converts date to ISO string."""
    from app.services.profile_service import ProfileService
    from app.models.profile import ProfileUpdate
    from datetime import date

    mock_db.query.return_value = [SAMPLE_PROFILE]
    updated = {**SAMPLE_PROFILE, "date_of_birth": "1985-06-20"}
    mock_db.update.return_value = updated

    service = ProfileService(mock_db)
    result = await service.update_profile(
        "user-123",
        "test@example.com",
        ProfileUpdate(date_of_birth=date(1985, 6, 20))
    )

    assert result["date_of_birth"] == "1985-06-20"
    call_data = mock_db.update.call_args.kwargs["data"]
    assert call_data["date_of_birth"] == "1985-06-20"


@pytest.mark.asyncio
async def test_update_profile_no_changes(mock_db):
    """Test updating profile with no fields returns current profile."""
    from app.services.profile_service import ProfileService
    from app.models.profile import ProfileUpdate

    mock_db.query.side_effect = [
        [SAMPLE_PROFILE],  # get_or_create_profile
        [SAMPLE_PROFILE],  # return current profile
    ]

    service = ProfileService(mock_db)
    result = await service.update_profile(
        "user-123",
        "test@example.com",
        ProfileUpdate()
    )

    assert result["full_name"] == "John Doe"
    mock_db.update.assert_not_called()


@pytest.mark.asyncio
async def test_update_profile_multiple_fields(mock_db):
    """Test updating multiple profile fields at once."""
    from app.services.profile_service import ProfileService
    from app.models.profile import ProfileUpdate

    mock_db.query.return_value = [SAMPLE_PROFILE]
    updated = {
        **SAMPLE_PROFILE,
        "full_name": "Jane Doe",
        "gender": "female",
        "hair_color": "brown",
    }
    mock_db.update.return_value = updated

    service = ProfileService(mock_db)
    result = await service.update_profile(
        "user-123",
        "test@example.com",
        ProfileUpdate(full_name="Jane Doe", gender="female", hair_color="brown")
    )

    assert result["full_name"] == "Jane Doe"
    call_data = mock_db.update.call_args.kwargs["data"]
    assert call_data["full_name"] == "Jane Doe"
    assert call_data["gender"] == "female"
    assert call_data["hair_color"] == "brown"
