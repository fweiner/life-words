"""Unit tests for treatment service."""
import pytest
from datetime import datetime


@pytest.mark.asyncio
async def test_create_session(mock_db):
    """Test creating a treatment session."""
    from app.services.treatment_service import TreatmentService
    from app.models.schemas import TreatmentSessionCreate

    # Setup mock
    mock_db.insert.return_value = {
        "id": "session-123",
        "user_id": "user-123",
        "treatment_type": "word_finding",
        "data": {},
        "started_at": datetime.utcnow().isoformat()
    }

    service = TreatmentService(mock_db)
    session_data = TreatmentSessionCreate(treatment_type="word_finding", data={})

    result = await service.create_session("user-123", session_data)

    assert result["id"] == "session-123"
    assert result["treatment_type"] == "word_finding"
    mock_db.insert.assert_called_once()


@pytest.mark.asyncio
async def test_get_session(mock_db):
    """Test retrieving a session."""
    from app.services.treatment_service import TreatmentService

    # Setup mock
    mock_db.query.return_value = [{
        "id": "session-123",
        "user_id": "user-123",
        "treatment_type": "speech_echo"
    }]

    service = TreatmentService(mock_db)
    result = await service.get_session("session-123", "user-123")

    assert result["id"] == "session-123"
    mock_db.query.assert_called_once_with(
        "treatment_sessions",
        filters={"id": "session-123", "user_id": "user-123"},
        limit=1
    )


@pytest.mark.asyncio
async def test_get_session_not_found(mock_db):
    """Test retrieving a session that doesn't exist raises 404."""
    from app.services.treatment_service import TreatmentService
    from fastapi import HTTPException

    # Setup mock to return empty list
    mock_db.query.return_value = []

    service = TreatmentService(mock_db)
    with pytest.raises(HTTPException) as exc_info:
        await service.get_session("nonexistent", "user-123")

    assert exc_info.value.status_code == 404
    assert "Session not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_complete_session(mock_db):
    """Test completing a session."""
    from app.services.treatment_service import TreatmentService

    # Setup mock
    mock_db.update.return_value = {
        "id": "session-123",
        "completed_at": datetime.utcnow().isoformat(),
        "data": {"result": "completed"}
    }

    service = TreatmentService(mock_db)
    result = await service.complete_session(
        "session-123",
        "user-123",
        data={"result": "completed"}
    )

    assert result["completed_at"] is not None
    assert result["data"]["result"] == "completed"
    mock_db.update.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_sessions(mock_db):
    """Test retrieving all sessions for a user."""
    from app.services.treatment_service import TreatmentService

    # Setup mock
    mock_db.query.return_value = [
        {"id": "session-1", "treatment_type": "speech_echo"},
        {"id": "session-2", "treatment_type": "speech_echo"}
    ]

    service = TreatmentService(mock_db)
    results = await service.get_user_sessions("user-123")

    assert len(results) == 2
    assert results[0]["id"] == "session-1"
    mock_db.query.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_sessions_with_filter(mock_db):
    """Test retrieving sessions with treatment type filter."""
    from app.services.treatment_service import TreatmentService

    mock_db.query.return_value = [{"id": "session-1", "treatment_type": "word_finding"}]

    service = TreatmentService(mock_db)
    results = await service.get_user_sessions("user-123", treatment_type="word_finding")

    assert len(results) == 1
    call_args = mock_db.query.call_args
    assert call_args.kwargs["filters"]["treatment_type"] == "word_finding"


@pytest.mark.asyncio
async def test_create_result(mock_db, mocker):
    """Test creating a treatment result."""
    from app.services.treatment_service import TreatmentService
    from app.models.schemas import TreatmentResultCreate

    # Mock insert and progress update
    mock_db.insert.return_value = {
        "id": "result-123",
        "session_id": "session-123",
        "user_id": "user-123",
        "score": 85
    }
    mock_db.query.return_value = [
        {"treatment_type": "speech_echo"}
    ]

    # Mock the progress update method
    service = TreatmentService(mock_db)
    mocker.patch.object(service, '_update_user_progress')

    result_data = TreatmentResultCreate(
        session_id="session-123",
        score=85,
        details={"confidence": 0.85}
    )

    result = await service.create_result("user-123", result_data)

    assert result["id"] == "result-123"
    assert result["score"] == 85
    mock_db.insert.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_results(mock_db):
    """Test retrieving user results."""
    from app.services.treatment_service import TreatmentService

    mock_db.query.return_value = [
        {"id": "result-1", "score": 85},
        {"id": "result-2", "score": 90}
    ]

    service = TreatmentService(mock_db)
    results = await service.get_user_results("user-123")

    assert len(results) == 2
    assert results[0]["score"] == 85
    assert results[1]["score"] == 90


@pytest.mark.asyncio
async def test_get_user_progress(mock_db):
    """Test retrieving user progress."""
    from app.services.treatment_service import TreatmentService

    mock_db.query.return_value = [{
        "id": "progress-1",
        "user_id": "user-123",
        "treatment_type": "word_finding",
        "total_sessions": 10,
        "average_score": 87.5
    }]

    service = TreatmentService(mock_db)
    results = await service.get_user_progress("user-123")

    assert len(results) == 1
    assert results[0]["total_sessions"] == 10
    assert results[0]["average_score"] == 87.5


@pytest.mark.asyncio
async def test_update_user_progress_creates_new(mock_db):
    """Test updating user progress creates new record."""
    from app.services.treatment_service import TreatmentService

    # Mock session query
    mock_db.query.side_effect = [
        [{"id": "session-123", "treatment_type": "speech_echo"}],  # Session lookup
        [{"score": 85}],  # Results lookup
        []  # No existing progress
    ]

    service = TreatmentService(mock_db)
    await service._update_user_progress("user-123", "session-123")

    # Should call insert for new progress record
    mock_db.insert.assert_called_once()
    call_args = mock_db.insert.call_args
    assert call_args.args[0] == "user_progress"
    assert call_args.args[1]["user_id"] == "user-123"


@pytest.mark.asyncio
async def test_update_user_progress_updates_existing(mock_db):
    """Test updating user progress updates existing record."""
    from app.services.treatment_service import TreatmentService

    # Mock queries
    mock_db.query.side_effect = [
        [{"id": "session-123", "treatment_type": "speech_echo"}],  # Session lookup
        [{"score": 85}, {"score": 90}],  # Results lookup
        [{"id": "progress-1", "user_id": "user-123"}]  # Existing progress
    ]

    service = TreatmentService(mock_db)
    await service._update_user_progress("user-123", "session-123")

    # Should call update for existing progress
    mock_db.update.assert_called_once()
    call_args = mock_db.update.call_args
    assert call_args.args[0] == "user_progress"
