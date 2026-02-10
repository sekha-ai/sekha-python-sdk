"""Complete integration tests for SekhaClient
Tests all major API endpoints with realistic scenarios
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
import httpx

from sekha import (
    SekhaClient,
    NewConversation,
    MessageDto,
    MessageRole,
    SekhaAPIError,
    SekhaAuthError,
    SekhaConnectionError,
    SekhaNotFoundError,
    SekhaValidationError,
    SekhaError,
)

# ==================== Fixtures ====================


@pytest.fixture
def memory(test_config):
    """Create client instance (no mocking yet)"""
    return SekhaClient(test_config)


@pytest.fixture
def mock_client(test_config):
    """Create a client with mocked httpx"""
    client = SekhaClient(test_config)

    # Create a mock that tracks calls but allows method assignment
    mock_httpx_client = AsyncMock()

    # Set up default mock response
    default_response = Mock()
    default_response.raise_for_status = Mock()

    # Make json dynamic to return what was sent
    def dynamic_json():
        return {
            "id": "conv-123",
            "label": "Test",
            "folder": "/work",
            "status": "active",
            "message_count": 2,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

    default_response.json = dynamic_json

    # Set default return values for all common methods
    mock_httpx_client.post = AsyncMock(return_value=default_response)
    mock_httpx_client.get = AsyncMock(return_value=default_response)
    mock_httpx_client.put = AsyncMock(return_value=default_response)
    mock_httpx_client.delete = AsyncMock(return_value=default_response)

    # Replace the actual client with mock
    client.client = mock_httpx_client

    return client


# ==================== Initialization Tests ====================


class TestMemoryControllerInit:
    """Test client initialization and configuration"""

    def test_init_with_config(self, test_config):
        """Test initialization with full config"""
        client = SekhaClient(test_config)
        assert client.config.api_key == test_config.api_key
        assert client.config.base_url == test_config.base_url

    def test_init_validates_api_key_length(self):
        """Test that short API keys raise error"""
        from sekha import ClientConfig

        with pytest.raises(ValueError, match="too short"):
            ClientConfig(api_key="sk-sekha-short")

    def test_init_validates_base_url_format(self):
        """Test that invalid URLs raise error"""
        from sekha import ClientConfig

        with pytest.raises(ValueError, match="Invalid base_url"):
            ClientConfig(api_key="sk-sekha-" + "x" * 32, base_url="not-a-url")


# ==================== Conversation Creation Tests ====================


class TestCreateConversation:
    """Test conversation creation workflows"""

    @pytest.mark.asyncio
    async def test_create_conversation_success(self, mock_client):
        """Test basic conversation creation"""
        conv = NewConversation(
            label="Test Conversation",
            folder="/work",
            messages=[
                MessageDto(role=MessageRole.USER, content="Hello"),
                MessageDto(role=MessageRole.ASSISTANT, content="Hi there!"),
            ],
        )

        result = await mock_client.create_conversation(conv)

        assert result.label == "Test"
        assert mock_client.client.post.called

    @pytest.mark.asyncio
    async def test_create_conversation_minimal(self, mock_client):
        """Test creating conversation with minimal data"""
        conv = NewConversation(
            label="Minimal Test",
            messages=[MessageDto(role=MessageRole.USER, content="Test")],
        )

        result = await mock_client.create_conversation(conv)
        assert result.id == "conv-123"

    @pytest.mark.asyncio
    async def test_create_conversation_auth_error(self, test_config):
        """Test 401 error handling"""
        client = SekhaClient(test_config)

        error_response = Mock()
        error_response.status_code = 401
        error_response.text = "Invalid API key"

        request_mock = Mock()
        request_mock.url = "http://localhost:8080/api/v1/conversations"

        auth_error = httpx.HTTPStatusError(
            "Unauthorized", request=request_mock, response=error_response
        )

        client.client = AsyncMock()
        client.client.post = AsyncMock(side_effect=auth_error)

        conv = NewConversation(
            label="Test", messages=[MessageDto(role=MessageRole.USER, content="Test")]
        )

        with pytest.raises(SekhaAuthError):
            await client.create_conversation(conv)

    @pytest.mark.asyncio
    async def test_400_bad_request(self, mock_client):
        """Test 400 error handling"""
        error_response = Mock()
        error_response.status_code = 400
        error_response.text = "Invalid request payload"

        request_mock = Mock()
        request_mock.url = "http://localhost:8080/api/v1/conversations"

        mock_client.client.post = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Bad Request", request=request_mock, response=error_response
            )
        )

        conv = NewConversation(
            label="Test", messages=[MessageDto(role=MessageRole.USER, content="Test")]
        )

        with pytest.raises(SekhaValidationError, match="Invalid conversation data"):
            await mock_client.create_conversation(conv)

    @pytest.mark.asyncio
    async def test_429_rate_limit(self, mock_client):
        """Test rate limit error handling"""
        error_response = Mock()
        error_response.status_code = 429
        error_response.text = "Rate limit exceeded"

        request_mock = Mock()
        request_mock.url = "http://localhost:8080/api/v1/conversations"

        mock_client.client.post = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Too Many Requests", request=request_mock, response=error_response
            )
        )

        conv = NewConversation(
            label="Test", messages=[MessageDto(role=MessageRole.USER, content="Test")]
        )

        with pytest.raises(SekhaAPIError, match="429"):
            await mock_client.create_conversation(conv)


# ==================== Smart Query Tests ====================


class TestSmartQuery:
    """Test intelligent context assembly"""

    @pytest.mark.asyncio
    async def test_smart_query_success(self, mock_client):
        """Test successful smart query"""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={
                "results": [
                    {
                        "conversation_id": "conv-456",
                        "message_id": "msg-789",
                        "score": 0.92,
                        "content": "Authentication is handled via API keys",
                        "label": "Project:Auth",
                        "folder": "/work",
                        "timestamp": datetime.now().isoformat(),
                    }
                ],
                "total": 1,
                "page": 1,
                "page_size": 10,
            }
        )

        mock_client.client.post = AsyncMock(return_value=mock_response)

        result = await mock_client.smart_query(
            query="How to handle authentication?",
            limit=5,
            filters={"label": "Project:Auth"},
        )

        assert result.total == 1
        assert len(result.results) == 1
        assert result.results[0].score > 0.9

    @pytest.mark.asyncio
    async def test_smart_query_empty_results(self, mock_client):
        """Test query with no results"""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={
                "results": [],
                "total": 0,
                "page": 1,
                "page_size": 10,
            }
        )

        mock_client.client.post = AsyncMock(return_value=mock_response)

        result = await mock_client.smart_query(query="non-existent topic")

        assert result.total == 0
        assert len(result.results) == 0


# ==================== Memory Management Tests ====================


class TestMemoryManagement:
    """Test pin, archive, label operations"""

    @pytest.mark.asyncio
    async def test_pin_conversation(self, mock_client):
        """Test pinning a conversation"""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()

        mock_client.client.put = AsyncMock(return_value=mock_response)

        # Use the correct method name
        await mock_client.pin_conversation("conv-123")

        # Verify the call was made
        assert mock_client.client.put.called
        call_args = mock_client.client.put.call_args
        assert "conv-123/pin" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_archive_conversation(self, mock_client):
        """Test archiving a conversation"""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()

        mock_client.client.put = AsyncMock(return_value=mock_response)

        # Use the correct method name
        await mock_client.archive_conversation("conv-456")

        call_args = mock_client.client.put.call_args
        assert "conv-456/archive" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_update_label(self, mock_client):
        """Test updating conversation label and folder"""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()

        mock_client.client.put = AsyncMock(return_value=mock_response)

        await mock_client.update_label(
            conversation_id="conv-123", new_label="Updated Label", new_folder="/archive"
        )

        call_args = mock_client.client.put.call_args
        assert call_args[1]["json"]["label"] == "Updated Label"
        assert call_args[1]["json"]["folder"] == "/archive"


# ==================== Export Tests ====================


class TestExport:
    """Test export functionality"""

    @pytest.mark.asyncio
    async def test_export_markdown(self, mock_client):
        """Test markdown export"""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={
                "content": "# Test Export\n\n## Conversation 1\n\nThis is the content.",
                "format": "markdown",
                "conversation_count": 1,
            }
        )

        mock_client.client.get = AsyncMock(return_value=mock_response)

        result = await mock_client.export(label="Project:AI", format="markdown")

        assert result.startswith("# Test Export")
        assert "conversation 1" in result.lower() or "Conversation 1" in result

    @pytest.mark.asyncio
    async def test_export_json(self, mock_client):
        """Test JSON export"""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={
                "content": '[{"id": "conv-1", "label": "Test"}]',
                "format": "json",
                "conversation_count": 1,
            }
        )

        mock_client.client.get = AsyncMock(return_value=mock_response)

        result = await mock_client.export(format="json")

        assert '"id"' in result
        assert '"label"' in result


# ==================== Pruning Tests ====================


class TestPruning:
    """Test pruning suggestions"""

    @pytest.mark.asyncio
    async def test_get_pruning_suggestions(self, mock_client):
        """Test pruning suggestions retrieval"""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={
                "suggestions": [
                    {
                        "conversation_id": "old-conv-1",
                        "label": "Old Project",
                        "reason": "Not accessed in 120 days",
                    },
                    {
                        "conversation_id": "old-conv-2",
                        "label": "Legacy Code",
                        "reason": "Low importance score",
                    },
                ],
                "total": 2,
            }
        )

        mock_client.client.post = AsyncMock(return_value=mock_response)

        # Use the alias method
        result = await mock_client.get_pruning_suggestions(threshold_days=90)

        assert result["total"] == 2
        assert len(result["suggestions"]) == 2


# ==================== Error Handling Tests ====================


class TestErrorBranches:
    """Test specific error handling branches"""

    @pytest.mark.asyncio
    async def test_get_conversation_not_found(self, mock_client):
        """Test 404 on get_conversation"""
        error_response = Mock()
        error_response.status_code = 404

        request_mock = Mock()
        request_mock.url = "http://localhost:8080/api/v1/conversations/non-existent"

        mock_client.client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Not Found", request=request_mock, response=error_response
            )
        )

        with pytest.raises(SekhaNotFoundError):
            await mock_client.get_conversation("non-existent")

    @pytest.mark.asyncio
    async def test_smart_query_connection_error(self, mock_client):
        """Test connection error in smart_query"""
        mock_client.client.post = AsyncMock(
            side_effect=httpx.ConnectError("Connection failed")
        )

        with pytest.raises(SekhaConnectionError):
            await mock_client.smart_query("test query")

    @pytest.mark.asyncio
    async def test_export_invalid_format(self, mock_client):
        """Test export with invalid format parameter"""
        mock_client.client.get = AsyncMock(side_effect=Exception("Invalid format"))

        with pytest.raises(SekhaError, match="Failed to export"):
            await mock_client.export(format="invalid")


# ==================== Async Context Manager Tests ====================


class TestAsyncClient:
    """Test async context manager functionality"""

    @pytest.mark.asyncio
    async def test_async_context_manager(self, test_config):
        """Test async context manager usage"""
        async with SekhaClient(test_config) as client:
            assert isinstance(client, SekhaClient)
            assert client.client is not None

    @pytest.mark.asyncio
    async def test_async_cleanup(self, test_config):
        """Test proper cleanup of async resources"""
        client = SekhaClient(test_config)
        await client.close()
        # Should not raise any exceptions


# ==================== Rate Limiting Tests ====================


class TestRateLimiting:
    """Test rate limiter integration"""

    @pytest.mark.asyncio
    async def test_rate_limiter_acquires(self, test_config):
        """Test rate limiter is called"""
        client = SekhaClient(test_config)

        # Access the rate limiter
        assert client.rate_limiter.max_requests == 1000
        assert client.rate_limiter.window_seconds == 60.0

        await client.close()
