"""Unit tests for database module."""
import pytest


@pytest.mark.asyncio
async def test_query_basic(mocker):
    """Test basic database query."""
    from app.core.database import SupabaseClient

    # Mock httpx client
    mock_response = mocker.Mock()
    mock_response.json.return_value = [{"id": "1", "name": "Test"}]
    mock_response.is_success = True

    mock_client = mocker.AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    db = SupabaseClient()
    result = await db.query("test_table")

    assert len(result) == 1
    assert result[0]["id"] == "1"


@pytest.mark.asyncio
async def test_query_with_filters(mocker):
    """Test database query with filters."""
    from app.core.database import SupabaseClient

    mock_response = mocker.Mock()
    mock_response.json.return_value = [{"id": "1", "user_id": "user-123"}]
    mock_response.is_success = True

    mock_client = mocker.AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    db = SupabaseClient()
    result = await db.query("test_table", filters={"user_id": "user-123"})

    assert len(result) == 1
    mock_client.get.assert_called_once()
    call_args = mock_client.get.call_args
    assert "user_id" in call_args.kwargs["params"]


@pytest.mark.asyncio
async def test_query_with_order_and_limit(mocker):
    """Test database query with order and limit."""
    from app.core.database import SupabaseClient

    mock_response = mocker.Mock()
    mock_response.json.return_value = [{"id": "1"}, {"id": "2"}]
    mock_response.is_success = True

    mock_client = mocker.AsyncMock()
    mock_client.get.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    db = SupabaseClient()
    result = await db.query("test_table", order="created_at.desc", limit=10)

    assert len(result) == 2
    call_args = mock_client.get.call_args
    assert call_args.kwargs["params"]["order"] == "created_at.desc"
    assert call_args.kwargs["params"]["limit"] == "10"


@pytest.mark.asyncio
async def test_insert(mocker):
    """Test database insert."""
    from app.core.database import SupabaseClient

    mock_response = mocker.Mock()
    mock_response.json.return_value = [{"id": "new-id", "name": "Test"}]
    mock_response.is_success = True

    mock_client = mocker.AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    db = SupabaseClient()
    result = await db.insert("test_table", {"name": "Test"})

    # insert() returns a list, so access first element
    assert result[0]["id"] == "new-id"
    assert result[0]["name"] == "Test"
    mock_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_upsert(mocker):
    """Test database upsert with on_conflict."""
    from app.core.database import SupabaseClient

    mock_response = mocker.Mock()
    mock_response.json.return_value = [{"id": "new-id", "name": "Test"}]
    mock_response.is_success = True

    mock_client = mocker.AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    db = SupabaseClient()
    result = await db.upsert(
        "test_table", {"name": "Test"}, on_conflict="session_id,contact_id"
    )

    assert result[0]["id"] == "new-id"
    mock_client.post.assert_called_once()
    call_args = mock_client.post.call_args
    assert "resolution=merge-duplicates" in call_args.kwargs["headers"]["Prefer"]
    assert call_args.kwargs["params"]["on_conflict"] == "session_id,contact_id"


@pytest.mark.asyncio
async def test_upsert_without_on_conflict(mocker):
    """Test database upsert without specifying on_conflict columns."""
    from app.core.database import SupabaseClient

    mock_response = mocker.Mock()
    mock_response.json.return_value = [{"id": "new-id"}]
    mock_response.is_success = True

    mock_client = mocker.AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    db = SupabaseClient()
    result = await db.upsert("test_table", {"name": "Test"})

    assert result[0]["id"] == "new-id"
    call_args = mock_client.post.call_args
    assert call_args.kwargs["params"] == {}


@pytest.mark.asyncio
async def test_update(mocker):
    """Test database update."""
    from app.core.database import SupabaseClient

    mock_response = mocker.Mock()
    mock_response.json.return_value = [{"id": "1", "name": "Updated"}]
    mock_response.is_success = True

    mock_client = mocker.AsyncMock()
    mock_client.patch.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    db = SupabaseClient()
    result = await db.update(
        "test_table",
        filters={"id": "1"},
        data={"name": "Updated"}
    )

    assert result["name"] == "Updated"
    mock_client.patch.assert_called_once()


@pytest.mark.asyncio
async def test_delete(mocker):
    """Test database delete."""
    from app.core.database import SupabaseClient

    mock_response = mocker.Mock()
    mock_response.is_success = True

    mock_client = mocker.AsyncMock()
    mock_client.delete.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    db = SupabaseClient()
    result = await db.delete("test_table", filters={"id": "1"})

    assert result is True
    mock_client.delete.assert_called_once()


@pytest.mark.asyncio
async def test_count(mocker):
    """Test database count using HEAD request with Prefer: count=exact."""
    from app.core.database import SupabaseClient

    mock_response = mocker.Mock()
    mock_response.headers = {"content-range": "*/5"}
    mock_response.is_success = True

    mock_client = mocker.AsyncMock()
    mock_client.head.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    db = SupabaseClient()
    result = await db.count("messages", filters={"user_id": "user-123", "is_read": False})

    assert result == 5
    mock_client.head.assert_called_once()
    call_args = mock_client.head.call_args
    assert "count=exact" in call_args.kwargs["headers"]["Prefer"]
    assert call_args.kwargs["params"]["user_id"] == "eq.user-123"
    assert call_args.kwargs["params"]["is_read"] == "eq.False"


@pytest.mark.asyncio
async def test_count_no_results(mocker):
    """Test database count returns 0 when no matches."""
    from app.core.database import SupabaseClient

    mock_response = mocker.Mock()
    mock_response.headers = {"content-range": "*/0"}
    mock_response.is_success = True

    mock_client = mocker.AsyncMock()
    mock_client.head.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    db = SupabaseClient()
    result = await db.count("messages")

    assert result == 0


@pytest.mark.asyncio
async def test_rpc(mocker):
    """Test database RPC call."""
    from app.core.database import SupabaseClient

    mock_response = mocker.Mock()
    mock_response.json.return_value = {"result": "success"}
    mock_response.is_success = True

    mock_client = mocker.AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None

    mocker.patch("httpx.AsyncClient", return_value=mock_client)

    db = SupabaseClient()
    result = await db.rpc("test_function", {"param": "value"})

    assert result["result"] == "success"
    mock_client.post.assert_called_once()
