"""Tests for MemoryController (sekha.client.SekhaClient)"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from sekha import MemoryController
from sekha.types import CreateConversationRequest, Message


@pytest.fixture
def mock_client(test_config):
    """Create a client with mocked httpx"""
    client = MemoryController(test_config)

    # Create a mock that tracks calls but allows method assignment
    mock_httpx_client = AsyncMock()

    # Set up default mock response
    default_response = Mock()
    default_response.raise_for_status = Mock()
    default_response.json = Mock(
        return_value={
            "id": "test-uuid",
            "label": "Test",
            "folder": "/",
            "status": "active",
            "messages": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
    )

    # Set default return values for all common methods
    mock_httpx_client.post = AsyncMock(return_value=default_response)
    mock_httpx_client.get = AsyncMock(return_value=default_response)
    mock_httpx_client.put = AsyncMock(return_value=default_response)
    mock_httpx_client.delete = AsyncMock(return_value=default_response)

    # Replace the actual client with mock
    client.client = mock_httpx_client

    return client


@pytest.mark.asyncio
async def test_create_conversation(mock_client):
    """Test creating a conversation"""
    msg: Message = {"role": "user", "content": "Hello"}

    conv: CreateConversationRequest = {
        "label": "Test",
        "folder": "/",
        "messages": [msg],
    }

    result = await mock_client.create_conversation(conv)

    assert result["label"] == "Test"
    assert mock_client.client.post.called


@pytest.mark.asyncio
async def test_smart_query(mock_client):
    """Test smart query (alias for query)"""
    # Mock the response with proper QueryResponse structure
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json = Mock(
        return_value={
            "results": [
                {
                    "conversation_id": "conv-123",
                    "score": 0.8,
                    "content": "test",
                    "label": "Test",
                    "folder": "/",
                    "created_at": datetime.now().isoformat(),
                }
            ],
            "total": 1,
            "query": "test query",
        }
    )

    mock_client.client.post = AsyncMock(return_value=mock_response)

    result = await mock_client.smart_query("test query")

    assert result["total"] == 1
    assert len(result["results"]) == 1
    assert result["results"][0]["content"] == "test"


@pytest.mark.asyncio
async def test_pin_conversation(mock_client):
    """Test pinning a conversation"""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()

    mock_client.client.put = AsyncMock(return_value=mock_response)

    # Use the correct method name
    await mock_client.pin_conversation("test-conv-123")

    # Verify the call
    assert mock_client.client.put.called
    call_args = mock_client.client.put.call_args
    assert "/conversations/test-conv-123/pin" in call_args[0][0]


@pytest.mark.asyncio
async def test_archive_conversation(mock_client):
    """Test archiving a conversation"""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()

    mock_client.client.put = AsyncMock(return_value=mock_response)

    # Use the correct method name
    await mock_client.archive_conversation("test-conv-123")

    # Verify the call
    assert mock_client.client.put.called
    call_args = mock_client.client.put.call_args
    assert "/conversations/test-conv-123/archive" in call_args[0][0]


@pytest.mark.asyncio
async def test_export_conversations(mock_client):
    """Test export functionality"""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json = Mock(
        return_value={
            "content": "# Test Export\n\n## Conversation 1",
            "format": "markdown",
            "conversation_count": 1,
        }
    )

    mock_client.client.get = AsyncMock(return_value=mock_response)

    # Test export
    result = await mock_client.export(label="Project:AI", format="markdown")

    assert result == "# Test Export\n\n## Conversation 1"
    assert mock_client.client.get.called
    call_args = mock_client.client.get.call_args
    assert call_args[1]["params"]["format"] == "markdown"
    assert call_args[1]["params"]["label"] == "Project:AI"


@pytest.mark.asyncio
async def test_export_conversations_json(mock_client):
    """Test export as JSON"""
    mock_response = Mock()
    mock_response.raise_for_status = Mock()
    mock_response.json = Mock(
        return_value={
            "content": '[{"id": "123", "label": "Test"}]',
            "format": "json",
            "conversation_count": 1,
        }
    )

    mock_client.client.get = AsyncMock(return_value=mock_response)

    result = await mock_client.export(format="json")

    assert '[{"id": "123"' in result
    assert mock_client.client.get.called
    call_args = mock_client.client.get.call_args
    assert call_args[1]["params"]["format"] == "json"
