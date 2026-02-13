"""Tests for untested client methods"""

import pytest
from unittest.mock import Mock, AsyncMock
from sekha import MemoryController


@pytest.fixture
def mock_client(test_config):
    client = MemoryController(test_config)

    # Mock the httpx client
    mock_httpx = AsyncMock()
    default_response = Mock()
    default_response.raise_for_status = Mock()
    default_response.json = Mock(
        return_value={
            "id": "conv-123",
            "label": "Test",
            "folder": "/",
            "status": "active",
            "message_count": 1,
            "created_at": "2025-12-30T10:00:00Z",
            "updated_at": "2025-12-30T10:00:00Z",
        }
    )

    mock_httpx.get = AsyncMock(return_value=default_response)
    mock_httpx.delete = AsyncMock(return_value=default_response)
    mock_httpx.post = AsyncMock(return_value=default_response)
    mock_httpx.put = AsyncMock(return_value=default_response)

    client.client = mock_httpx
    return client


@pytest.mark.asyncio
async def test_async_context_manager_cleanup(test_config):
    """Test proper resource cleanup in async context manager"""
    client = MemoryController(test_config)
    async with client:
        assert client.client is not None

    # After exit, should be closed
    await client.close()  # Explicit close for cleanup


# ============== Untested Methods ==============


@pytest.mark.asyncio
async def test_get_conversation(mock_client):
    result = await mock_client.get_conversation("conv-123")
    assert result["id"] == "conv-123"
    assert mock_client.client.get.called


@pytest.mark.asyncio
async def test_list_conversations(mock_client):
    # Fix: Return proper QueryResponse structure
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json = Mock(
        return_value={
            "results": [
                {
                    "conversation_id": "conv-123",
                    "message_id": "msg-1",
                    "score": 1.0,
                    "content": "test",
                    "metadata": {},
                    "label": "Test",
                    "folder": "/",
                    "timestamp": "2025-12-30T10:00:00Z",
                }
            ],
            "total": 1,
            "page": 1,
            "page_size": 10,
        }
    )
    mock_client.client.get = AsyncMock(return_value=mock_response)

    result = await mock_client.list_conversations(label="Work", page=1, page_size=10)
    assert result["total"] == 1
    assert mock_client.client.get.called


@pytest.mark.asyncio
async def test_delete_conversation(mock_client):
    await mock_client.delete_conversation("conv-123")
    assert mock_client.client.delete.called


@pytest.mark.asyncio
async def test_score_message_importance(mock_client):
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json = Mock(
        return_value={
            "score": 8.5,
            "reasoning": "Critical security information",
            "model": "gpt-4",
        }
    )
    mock_client.client.post = AsyncMock(return_value=mock_response)

    result = await mock_client.score_message_importance("msg-456")
    assert result["score"] == 8.5
    assert result["model"] == "gpt-4"


@pytest.mark.asyncio
async def test_generate_summary(mock_client):
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json = Mock(
        return_value={
            "summary": "Conversation summary",
            "level": "daily",
        }
    )
    mock_client.client.post = AsyncMock(return_value=mock_response)

    result = await mock_client.generate_summary("conv-123")
    assert result["summary"] == "Conversation summary"
    assert result["level"] == "daily"


@pytest.mark.asyncio
async def test_suggest_labels(mock_client):
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json = Mock(
        return_value={
            "conversation_id": "conv-123",
            "suggestions": [
                {
                    "label": "Project:AI",
                    "confidence": 0.92,
                    "is_existing": True,
                    "reason": "Matches context",
                    "folder": "/work",
                }
            ],
        }
    )
    mock_client.client.post = AsyncMock(return_value=mock_response)

    result = await mock_client.suggest_labels("conv-123")
    suggestions = result["suggestions"]
    assert len(suggestions) == 1
    assert suggestions[0]["label"] == "Project:AI"
    assert suggestions[0]["confidence"] > 0.9


@pytest.mark.asyncio
async def test_auto_label_threshold_not_met(mock_client):
    # Setup: low confidence suggestion
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json = Mock(
        return_value={
            "conversation_id": "conv-123",
            "suggestions": [
                {
                    "label": "Uncertain",
                    "confidence": 0.5,
                    "is_existing": False,
                    "reason": "Uncertain",
                    "folder": "/",
                }
            ],
        }
    )
    mock_client.client.post = AsyncMock(return_value=mock_response)
    mock_client.client.put = AsyncMock(return_value=Mock())

    result = await mock_client.auto_label("conv-123", threshold=0.8)
    assert result is None  # No label applied


@pytest.mark.asyncio
async def test_auto_label_threshold_met(mock_client):
    # Setup: high confidence suggestion
    suggest_response = Mock()
    suggest_response.raise_for_status = Mock()
    suggest_response.json = Mock(
        return_value={
            "conversation_id": "conv-123",
            "suggestions": [
                {
                    "label": "High Confidence",
                    "confidence": 0.95,
                    "is_existing": True,
                    "reason": "Clear match",
                    "folder": "/work",
                }
            ],
        }
    )

    update_response = Mock()
    update_response.raise_for_status = Mock()

    mock_client.client.post = AsyncMock(return_value=suggest_response)
    mock_client.client.put = AsyncMock(return_value=update_response)

    result = await mock_client.auto_label("conv-123", threshold=0.8)
    assert result == "High Confidence"


@pytest.mark.asyncio
async def test_get_mcp_tools(mock_client):
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json = Mock(
        return_value=[
            {"name": "search_memory", "description": "Search conversation memory"}
        ]
    )
    mock_client.client.get = AsyncMock(return_value=mock_response)

    result = await mock_client.get_mcp_tools()
    assert len(result) == 1
    assert result[0]["name"] == "search_memory"


# ============== SyncSekhaClient Tests ==============


def test_sync_client_wrapper(test_config):
    """Test SyncSekhaClient wraps async methods"""
    from sekha.client import SyncSekhaClient

    sync_client = SyncSekhaClient(test_config)

    # Test that methods are callable
    assert callable(getattr(sync_client, "create_conversation", None))
    assert callable(getattr(sync_client, "smart_query", None))

    # Cleanup
    if sync_client._loop and not sync_client._loop.is_closed():
        sync_client._loop.close()
