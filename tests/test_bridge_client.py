"""Integration tests for BridgeClient

These tests verify the BridgeClient communicates correctly with
the LLM Bridge service API.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
import httpx
import json

from sekha.unified import BridgeClient
from sekha.errors import (
    SekhaConnectionError,
    SekhaAPIError,
    SekhaError,
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


class TestBridgeClientInit:
    """Test BridgeClient initialization"""

    def test_bridge_client_basic_init(self):
        """Test basic initialization"""
        client = BridgeClient(
            base_url="http://localhost:5001",
        )
        assert client.base_url == "http://localhost:5001"
        assert client.api_key is None
        assert client.timeout == 30.0
        assert client.max_retries == 3

    def test_bridge_client_full_init(self):
        """Test initialization with all parameters"""
        client = BridgeClient(
            base_url="http://localhost:5001",
            api_key="bridge-key-123",
            timeout=60.0,
            max_retries=5,
        )
        assert client.base_url == "http://localhost:5001"
        assert client.api_key == "bridge-key-123"
        assert client.timeout == 60.0
        assert client.max_retries == 5


class TestBridgeClientComplete:
    """Test BridgeClient.complete() method"""

    @pytest.mark.asyncio
    async def test_complete_basic(self):
        """Test basic chat completion"""
        client = BridgeClient("http://localhost:5001")
        
        # Mock response
        mock_response = MockResponse(
            status_code=200,
            json_data={
                "id": "chatcmpl-abc123",
                "object": "chat.completion",
                "created": 1234567890,
                "model": "llama3.1:8b",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Hello! How can I help you?"
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 15,
                    "total_tokens": 25
                }
            }
        )
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.complete(
                messages=[
                    {"role": "user", "content": "Hello!"}
                ]
            )
            
            assert result["id"] == "chatcmpl-abc123"
            assert result["model"] == "llama3.1:8b"
            assert len(result["choices"]) == 1
            assert result["choices"][0]["message"]["content"] == "Hello! How can I help you?"

    @pytest.mark.asyncio
    async def test_complete_with_params(self):
        """Test completion with optional parameters"""
        client = BridgeClient("http://localhost:5001")
        
        mock_response = MockResponse(
            status_code=200,
            json_data={
                "id": "chatcmpl-xyz789",
                "object": "chat.completion",
                "created": 1234567890,
                "model": "gpt-4",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Response"},
                        "finish_reason": "stop"
                    }
                ],
                "usage": {"prompt_tokens": 20, "completion_tokens": 30, "total_tokens": 50}
            }
        )
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.complete(
                messages=[{"role": "user", "content": "Test"}],
                model="gpt-4",
                temperature=0.5,
                max_tokens=1000
            )
            
            assert result["model"] == "gpt-4"
            # Verify the request was made with correct params
            call_args = mock_request.call_args
            assert call_args[1]["json"]["model"] == "gpt-4"
            assert call_args[1]["json"]["temperature"] == 0.5
            assert call_args[1]["json"]["max_tokens"] == 1000

    @pytest.mark.asyncio
    async def test_complete_error_handling(self):
        """Test error handling in complete"""
        client = BridgeClient("http://localhost:5001")
        
        # Test 500 error
        mock_response = MockResponse(
            status_code=500,
            text="Internal server error"
        )
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            with pytest.raises(SekhaAPIError, match="500"):
                await client.complete(messages=[{"role": "user", "content": "Test"}])

    @pytest.mark.asyncio
    async def test_complete_connection_error(self):
        """Test connection error handling"""
        client = BridgeClient("http://localhost:5001")
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.ConnectError("Connection failed")
            
            with pytest.raises(SekhaConnectionError):
                await client.complete(messages=[{"role": "user", "content": "Test"}])


class TestBridgeClientEmbed:
    """Test BridgeClient.embed() method"""

    @pytest.mark.asyncio
    async def test_embed_basic(self):
        """Test basic embedding generation"""
        client = BridgeClient("http://localhost:5001")
        
        mock_response = MockResponse(
            status_code=200,
            json_data={
                "embedding": [0.1, 0.2, 0.3, 0.4],
                "model": "nomic-embed-text",
                "tokens_used": 10,
                "dimension": 768
            }
        )
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.embed("Hello world")
            
            assert result["embedding"] == [0.1, 0.2, 0.3, 0.4]
            assert result["model"] == "nomic-embed-text"
            assert result["dimension"] == 768
            assert result["tokens_used"] == 10

    @pytest.mark.asyncio
    async def test_embed_with_model(self):
        """Test embedding with specific model"""
        client = BridgeClient("http://localhost:5001")
        
        mock_response = MockResponse(
            status_code=200,
            json_data={
                "embedding": [0.5] * 1536,
                "model": "text-embedding-3-small",
                "tokens_used": 5,
                "dimension": 1536
            }
        )
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.embed("Test", model="text-embedding-3-small")
            
            assert result["model"] == "text-embedding-3-small"
            assert len(result["embedding"]) == 1536
            
            # Verify request params
            call_args = mock_request.call_args
            assert call_args[1]["json"]["model"] == "text-embedding-3-small"
            assert call_args[1]["json"]["text"] == "Test"

    @pytest.mark.asyncio
    async def test_embed_error_handling(self):
        """Test error handling in embed"""
        client = BridgeClient("http://localhost:5001")
        
        mock_response = MockResponse(
            status_code=400,
            text="Bad request"
        )
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            with pytest.raises(SekhaAPIError):
                await client.embed("")


class TestBridgeClientHealth:
    """Test BridgeClient.health() method"""

    @pytest.mark.asyncio
    async def test_health_success(self):
        """Test successful health check"""
        client = BridgeClient("http://localhost:5001")
        
        mock_response = MockResponse(
            status_code=200,
            json_data={
                "status": "healthy",
                "timestamp": "2026-02-13T23:00:00Z",
                "ollama_status": {
                    "status": "healthy",
                    "models_available": ["llama3.1:8b", "nomic-embed-text"]
                },
                "models_loaded": ["llama3.1:8b", "nomic-embed-text", "gpt-4o-mini"]
            }
        )
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.health()
            
            assert result["status"] == "healthy"
            assert "timestamp" in result
            assert "ollama_status" in result
            assert len(result["models_loaded"]) == 3

    @pytest.mark.asyncio
    async def test_health_degraded(self):
        """Test degraded health status"""
        client = BridgeClient("http://localhost:5001")
        
        mock_response = MockResponse(
            status_code=200,
            json_data={
                "status": "degraded",
                "timestamp": "2026-02-13T23:00:00Z",
                "ollama_status": {"status": "unhealthy"},
                "models_loaded": []
            }
        )
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.health()
            
            assert result["status"] == "degraded"

    @pytest.mark.asyncio
    async def test_health_service_unavailable(self):
        """Test health check when service unavailable"""
        client = BridgeClient("http://localhost:5001")
        
        mock_response = MockResponse(
            status_code=503,
            text="Service unavailable"
        )
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            with pytest.raises(SekhaAPIError, match="503"):
                await client.health()


class TestBridgeClientContextManager:
    """Test BridgeClient as async context manager"""

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test using BridgeClient as context manager"""
        async with BridgeClient("http://localhost:5001") as client:
            assert client is not None
            assert hasattr(client, '_client')

    @pytest.mark.asyncio
    async def test_close_method(self):
        """Test explicit close method"""
        client = BridgeClient("http://localhost:5001")
        await client.close()
        # Should not raise error


class TestBridgeClientRetry:
    """Test BridgeClient retry logic"""

    @pytest.mark.asyncio
    async def test_retry_on_timeout(self):
        """Test retry on timeout error"""
        client = BridgeClient("http://localhost:5001", max_retries=2)
        
        call_count = 0
        
        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise httpx.TimeoutException("Timeout")
            return MockResponse(
                status_code=200,
                json_data={"embedding": [0.1], "model": "test", "tokens_used": 1, "dimension": 1}
            )
        
        with patch.object(client._client, 'request', side_effect=mock_request) as mock:
            result = await client.embed("test")
            
            assert call_count == 2  # Failed once, succeeded second time
            assert result["embedding"] == [0.1]

    @pytest.mark.asyncio
    async def test_retry_exhausted(self):
        """Test when retries are exhausted"""
        client = BridgeClient("http://localhost:5001", max_retries=2)
        
        with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.TimeoutException("Timeout")
            
            with pytest.raises(SekhaConnectionError):
                await client.embed("test")


class TestBridgeClientStreamComplete:
    """Test BridgeClient.stream_complete() method"""

    @pytest.mark.asyncio
    async def test_stream_complete_basic(self):
        """Test basic streaming completion"""
        client = BridgeClient("http://localhost:5001")
        
        # Mock streaming response
        class MockStreamResponse:
            status_code = 200
            
            def raise_for_status(self):
                pass
            
            async def aiter_lines(self):
                yield "data: {\"choices\": [{\"delta\": {\"content\": \"Hello\"}}]}"
                yield "data: {\"choices\": [{\"delta\": {\"content\": \" world\"}}]}"
                yield "data: [DONE]"
        
        class MockStreamContext:
            async def __aenter__(self):
                return MockStreamResponse()
            
            async def __aexit__(self, *args):
                pass
        
        with patch.object(client._client, 'stream') as mock_stream:
            mock_stream.return_value = MockStreamContext()
            
            chunks = []
            async for chunk in client.stream_complete(
                messages=[{"role": "user", "content": "Hi"}]
            ):
                chunks.append(chunk)
            
            assert len(chunks) == 2  # Two content chunks before [DONE]
            assert "choices" in chunks[0]

    @pytest.mark.asyncio
    async def test_stream_complete_error(self):
        """Test error handling in streaming"""
        client = BridgeClient("http://localhost:5001")
        
        with patch.object(client._client, 'stream') as mock_stream:
            mock_stream.side_effect = httpx.ConnectError("Failed")
            
            with pytest.raises(SekhaConnectionError):
                async for _ in client.stream_complete(
                    messages=[{"role": "user", "content": "Test"}]
                ):
                    pass
