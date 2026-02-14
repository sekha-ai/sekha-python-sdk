"""Tests for MCPClient

These tests verify the MCPClient communicates correctly with
the Memory Controller's MCP endpoints.
"""

import pytest
from unittest.mock import AsyncMock, patch, Mock
import httpx

from sekha.unified import MCPClient
from sekha.errors import (
    SekhaConnectionError,
    SekhaAPIError,
)


class MockResponse:
    """Mock httpx.Response object"""
    def __init__(self, status_code: int, json_data: dict = None, text: str = ""):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text
    
    def json(self):
        return self._json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}",
                request=Mock(),
                response=self
            )


class TestMCPClientInit:
    """Test MCPClient initialization"""

    def test_mcp_client_basic_init(self):
        """Test basic initialization"""
        client = MCPClient(
            base_url="http://localhost:8080",
            api_key="sk-test-key-12345678901234567890",
        )
        assert client.base_url == "http://localhost:8080"
        assert client.api_key == "sk-test-key-12345678901234567890"
        assert client.timeout == 30.0
        assert client.max_retries == 3

    def test_mcp_client_full_init(self):
        """Test initialization with all parameters"""
        client = MCPClient(
            base_url="http://localhost:8080",
            api_key="sk-test-key-12345678901234567890",
            timeout=60.0,
            max_retries=5,
        )
        assert client.base_url == "http://localhost:8080"
        assert client.api_key == "sk-test-key-12345678901234567890"
        assert client.timeout == 60.0
        assert client.max_retries == 5


class TestMCPClientMemoryStats:
    """Test MCPClient.memory_stats() method"""

    @pytest.mark.asyncio
    async def test_memory_stats_basic(self):
        """Test basic memory stats retrieval"""
        client = MCPClient("http://localhost:8080", "sk-test-key-12345678901234567890")
        
        mock_response = MockResponse(
            status_code=200,
            json_data={
                "total_conversations": 42,
                "total_messages": 156,
                "total_tokens": 125000,
                "labels": {
                    "Engineering": 15,
                    "Product": 10,
                    "Meeting": 17
                },
                "oldest_conversation": "2026-01-01T00:00:00Z",
                "newest_conversation": "2026-02-13T20:00:00Z"
            }
        )
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.memory_stats({})
            
            assert result["total_conversations"] == 42
            assert result["total_messages"] == 156
            assert result["total_tokens"] == 125000
            assert len(result["labels"]) == 3
            assert "oldest_conversation" in result

    @pytest.mark.asyncio
    async def test_memory_stats_with_filters(self):
        """Test memory stats with label filters"""
        client = MCPClient("http://localhost:8080", "sk-test-key-12345678901234567890")
        
        mock_response = MockResponse(
            status_code=200,
            json_data={
                "total_conversations": 15,
                "total_messages": 45,
                "total_tokens": 35000,
                "labels": {"Engineering": 15},
                "oldest_conversation": "2026-01-15T00:00:00Z",
                "newest_conversation": "2026-02-13T20:00:00Z"
            }
        )
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.memory_stats({"labels": ["Engineering"]})
            
            assert result["total_conversations"] == 15
            assert result["labels"] == {"Engineering": 15}
            
            # Verify filters were passed
            call_args = mock_request.call_args
            assert call_args[1]["json"]["filters"]["labels"] == ["Engineering"]

    @pytest.mark.asyncio
    async def test_memory_stats_with_date_range(self):
        """Test memory stats with date range filter"""
        client = MCPClient("http://localhost:8080", "sk-test-key-12345678901234567890")
        
        mock_response = MockResponse(
            status_code=200,
            json_data={
                "total_conversations": 10,
                "total_messages": 30,
                "total_tokens": 22000,
                "labels": {"Meeting": 10},
                "oldest_conversation": "2026-02-01T00:00:00Z",
                "newest_conversation": "2026-02-13T20:00:00Z"
            }
        )
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.memory_stats({
                "start_date": "2026-02-01T00:00:00Z",
                "end_date": "2026-02-13T23:59:59Z"
            })
            
            assert result["total_conversations"] == 10

    @pytest.mark.asyncio
    async def test_memory_stats_error_handling(self):
        """Test error handling in memory_stats"""
        client = MCPClient("http://localhost:8080", "sk-test-key-12345678901234567890")
        
        mock_response = MockResponse(
            status_code=500,
            text="Internal server error"
        )
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            with pytest.raises(SekhaAPIError) as exc_info:
                await client.memory_stats({})
            
            assert exc_info.value.status_code == 500


class TestMCPClientMemorySearch:
    """Test MCPClient.memory_search() method"""

    @pytest.mark.asyncio
    async def test_memory_search_basic(self):
        """Test basic memory search"""
        client = MCPClient("http://localhost:8080", "sk-test-key-12345678901234567890")
        
        mock_response = MockResponse(
            status_code=200,
            json_data={
                "results": [
                    {
                        "id": "conv-1",
                        "label": "Engineering",
                        "content": "Discussion about TypeScript interfaces",
                        "score": 0.92,
                        "timestamp": "2026-02-10T15:30:00Z"
                    },
                    {
                        "id": "conv-2",
                        "label": "Engineering",
                        "content": "Review of TypeScript best practices",
                        "score": 0.87,
                        "timestamp": "2026-02-11T10:00:00Z"
                    }
                ],
                "total": 2,
                "query": "TypeScript"
            }
        )
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.memory_search("TypeScript")
            
            assert result["total"] == 2
            assert len(result["results"]) == 2
            assert result["results"][0]["score"] == 0.92
            assert result["query"] == "TypeScript"

    @pytest.mark.asyncio
    async def test_memory_search_with_limit(self):
        """Test memory search with result limit"""
        client = MCPClient("http://localhost:8080", "sk-test-key-12345678901234567890")
        
        mock_response = MockResponse(
            status_code=200,
            json_data={
                "results": [
                    {
                        "id": "conv-1",
                        "label": "Engineering",
                        "content": "TypeScript discussion",
                        "score": 0.95,
                        "timestamp": "2026-02-10T15:30:00Z"
                    }
                ],
                "total": 5,
                "query": "TypeScript",
                "limit": 1
            }
        )
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.memory_search("TypeScript", limit=1)
            
            assert len(result["results"]) == 1
            assert result["limit"] == 1
            
            # Verify limit was passed
            call_args = mock_request.call_args
            assert call_args[1]["json"]["limit"] == 1

    @pytest.mark.asyncio
    async def test_memory_search_with_filters(self):
        """Test memory search with label filters"""
        client = MCPClient("http://localhost:8080", "sk-test-key-12345678901234567890")
        
        mock_response = MockResponse(
            status_code=200,
            json_data={
                "results": [
                    {
                        "id": "conv-1",
                        "label": "Engineering",
                        "content": "TypeScript discussion",
                        "score": 0.92,
                        "timestamp": "2026-02-10T15:30:00Z"
                    }
                ],
                "total": 1,
                "query": "TypeScript",
                "filters": {"labels": ["Engineering"]}
            }
        )
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.memory_search(
                "TypeScript",
                filters={"labels": ["Engineering"]}
            )
            
            assert result["total"] == 1
            assert result["results"][0]["label"] == "Engineering"

    @pytest.mark.asyncio
    async def test_memory_search_empty_results(self):
        """Test memory search with no results"""
        client = MCPClient("http://localhost:8080", "sk-test-key-12345678901234567890")
        
        mock_response = MockResponse(
            status_code=200,
            json_data={
                "results": [],
                "total": 0,
                "query": "nonexistent topic"
            }
        )
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.memory_search("nonexistent topic")
            
            assert result["total"] == 0
            assert len(result["results"]) == 0

    @pytest.mark.asyncio
    async def test_memory_search_error_handling(self):
        """Test error handling in memory_search"""
        client = MCPClient("http://localhost:8080", "sk-test-key-12345678901234567890")
        
        mock_response = MockResponse(
            status_code=400,
            text="Invalid query"
        )
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            with pytest.raises(SekhaAPIError) as exc_info:
                await client.memory_search("")
            
            assert exc_info.value.status_code == 400


class TestMCPClientContextManager:
    """Test MCPClient as async context manager"""

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using MCPClient as context manager"""
        async with MCPClient("http://localhost:8080", "sk-test-key-12345678901234567890") as client:
            assert client is not None
            assert hasattr(client, '_client')

    @pytest.mark.asyncio
    async def test_close_method(self):
        """Test explicit close method"""
        client = MCPClient("http://localhost:8080", "sk-test-key-12345678901234567890")
        await client.close()
        # Should not raise error


class TestMCPClientRetry:
    """Test MCPClient retry logic"""

    @pytest.mark.asyncio
    async def test_retry_on_timeout(self):
        """Test retry on timeout error"""
        client = MCPClient("http://localhost:8080", "sk-test-key-12345678901234567890", max_retries=3)
        
        call_count = 0
        
        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.TimeoutException("Timeout")
            return MockResponse(
                status_code=200,
                json_data={
                    "total_conversations": 42,
                    "total_messages": 156,
                    "total_tokens": 125000,
                    "labels": {}
                }
            )
        
        with patch.object(client._client, 'request', side_effect=mock_request):
            result = await client.memory_stats({})
            
            assert call_count == 3  # Failed twice, succeeded third time
            assert result["total_conversations"] == 42

    @pytest.mark.asyncio
    async def test_retry_exhausted(self):
        """Test when retries are exhausted"""
        client = MCPClient("http://localhost:8080", "sk-test-key-12345678901234567890", max_retries=3)
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.TimeoutException("Timeout")
            
            with pytest.raises(SekhaConnectionError):
                await client.memory_stats({})
            
            # Should have tried max_retries times
            assert mock_request.call_count == 3

    @pytest.mark.asyncio
    async def test_retry_on_5xx_error(self):
        """Test retry on server errors"""
        client = MCPClient("http://localhost:8080", "sk-test-key-12345678901234567890", max_retries=3)
        
        call_count = 0
        
        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                return MockResponse(status_code=503, text="Service unavailable")
            return MockResponse(
                status_code=200,
                json_data={"results": [], "total": 0, "query": "test"}
            )
        
        with patch.object(client._client, 'request', side_effect=mock_request):
            result = await client.memory_search("test")
            
            assert call_count == 2  # Failed once, succeeded second time
            assert result["total"] == 0


class TestMCPClientConnectionErrors:
    """Test MCPClient connection error handling"""

    @pytest.mark.asyncio
    async def test_connection_error(self):
        """Test connection error handling"""
        client = MCPClient("http://localhost:8080", "sk-test-key-12345678901234567890")
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.ConnectError("Connection refused")
            
            with pytest.raises(SekhaConnectionError):
                await client.memory_stats({})

    @pytest.mark.asyncio
    async def test_timeout_error(self):
        """Test timeout error handling"""
        client = MCPClient("http://localhost:8080", "sk-test-key-12345678901234567890")
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.TimeoutException("Request timeout")
            
            with pytest.raises(SekhaConnectionError):
                await client.memory_search("test")
