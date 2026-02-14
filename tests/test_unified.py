"""Tests for unified module"""

import pytest

from sekha.unified import (
    SekhaClient,
    SekhaConfig,
    MCPClient,
    BridgeClient,
    message_content_to_string,
    create_sekha_client,
)


class TestMessageContentToString:
    """Test message content conversion"""

    def test_string_content(self):
        """Test converting string content"""
        result = message_content_to_string("Hello world")
        assert result == "Hello world"

    def test_multi_modal_content(self):
        """Test converting multi-modal content"""
        content = [
            {"type": "text", "text": "Hello"},
            {"type": "text", "text": "world"},
        ]
        result = message_content_to_string(content)
        assert result == "Hello world"

    def test_mixed_content_with_images(self):
        """Test converting content with non-text parts"""
        content = [
            {"type": "text", "text": "Check"},
            {"type": "image_url", "image_url": {"url": "https://example.com/img.png"}},
            {"type": "text", "text": "this"},
        ]
        result = message_content_to_string(content)
        assert result == "Check this"

    def test_empty_content(self):
        """Test converting empty content list"""
        result = message_content_to_string([])
        assert result == ""


class TestSekhaConfig:
    """Test SekhaConfig dataclass"""

    def test_minimal_config(self):
        """Test creating config with minimal args"""
        config = SekhaConfig(
            controller_url="http://localhost:8080",
            api_key="sk-test-12345678901234567890",
            bridge_url="http://localhost:5001",
        )
        assert config.controller_url == "http://localhost:8080"
        assert config.api_key == "sk-test-12345678901234567890"
        assert config.bridge_url == "http://localhost:5001"
        assert config.timeout == 30.0
        assert config.max_retries == 3

    def test_full_config(self):
        """Test creating config with all args"""
        config = SekhaConfig(
            controller_url="http://localhost:8080",
            api_key="sk-test-12345678901234567890",
            bridge_url="http://localhost:5001",
            bridge_api_key="bridge-key",
            mcp_api_key="mcp-key",
            timeout=60.0,
            max_retries=5,
            default_label="Test",
            rate_limit_requests=500,
            rate_limit_window=30.0,
        )
        assert config.bridge_api_key == "bridge-key"
        assert config.mcp_api_key == "mcp-key"
        assert config.timeout == 60.0
        assert config.max_retries == 5
        assert config.default_label == "Test"


class TestMCPClient:
    """Test MCP client stub"""

    def test_mcp_client_init(self):
        """Test MCP client initialization"""
        client = MCPClient(
            base_url="http://localhost:8080",
            api_key="sk-test-12345678901234567890",
            timeout=60.0,
            max_retries=5,
        )
        assert client.base_url == "http://localhost:8080"
        assert client.api_key == "sk-test-12345678901234567890"
        assert client.timeout == 60.0
        assert client.max_retries == 5

    @pytest.mark.asyncio
    async def test_mcp_memory_stats_not_implemented(self):
        """Test MCP memory_stats raises NotImplementedError"""
        client = MCPClient("http://localhost:8080", "sk-test-12345678901234567890")
        with pytest.raises(NotImplementedError, match="MCP client not yet implemented"):
            await client.memory_stats({})

    @pytest.mark.asyncio
    async def test_mcp_memory_search_not_implemented(self):
        """Test MCP memory_search raises NotImplementedError"""
        client = MCPClient("http://localhost:8080", "sk-test-12345678901234567890")
        with pytest.raises(NotImplementedError, match="MCP client not yet implemented"):
            await client.memory_search("test")


class TestBridgeClient:
    """Test Bridge client"""

    def test_bridge_client_init(self):
        """Test Bridge client initialization"""
        client = BridgeClient(
            base_url="http://localhost:5001",
            api_key="bridge-key",
            timeout=45.0,
            max_retries=4,
        )
        assert client.base_url == "http://localhost:5001"
        assert client.api_key == "bridge-key"
        assert client.timeout == 45.0
        assert client.max_retries == 4

    def test_bridge_client_init_without_api_key(self):
        """Test Bridge client init without API key"""
        client = BridgeClient(base_url="http://localhost:5001")
        assert client.base_url == "http://localhost:5001"
        assert client.api_key is None

    def test_bridge_client_has_http_client(self):
        """Test Bridge client creates HTTP client"""
        client = BridgeClient(base_url="http://localhost:5001")
        assert hasattr(client, "_client")
        assert client._client is not None

    @pytest.mark.asyncio
    async def test_bridge_client_context_manager(self):
        """Test Bridge client as async context manager"""
        async with BridgeClient("http://localhost:5001") as client:
            assert client is not None

    @pytest.mark.asyncio
    async def test_bridge_client_close(self):
        """Test Bridge client close method"""
        client = BridgeClient("http://localhost:5001")
        await client.close()
        # Verify no error raised

    # Note: Comprehensive method tests (complete, embed, health, stream_complete)
    # are in test_bridge_client.py with proper mocking


class TestSekhaClientInit:
    """Test SekhaClient initialization"""

    def test_sekha_client_init_minimal(self):
        """Test SekhaClient initialization with minimal args"""
        client = SekhaClient(
            controller_url="http://localhost:8080",
            api_key="sk-test-12345678901234567890",
            bridge_url="http://localhost:5001",
        )
        assert client.config.controller_url == "http://localhost:8080"
        assert client.config.api_key == "sk-test-12345678901234567890"
        assert client.config.bridge_url == "http://localhost:5001"
        assert client.controller is not None
        assert client.mcp is not None
        assert client.bridge is not None

    def test_sekha_client_init_full(self):
        """Test SekhaClient initialization with all args"""
        client = SekhaClient(
            controller_url="http://localhost:8080",
            api_key="sk-test-12345678901234567890",
            bridge_url="http://localhost:5001",
            bridge_api_key="bridge-key",
            mcp_api_key="sk-test-mcp-key-12345678",
            timeout=60.0,
            max_retries=5,
            default_label="Test",
            rate_limit_requests=500,
            rate_limit_window=30.0,
        )
        assert client.config.timeout == 60.0
        assert client.config.max_retries == 5
        assert client.config.default_label == "Test"
        assert client.mcp.api_key == "sk-test-mcp-key-12345678"
        assert client.bridge.api_key == "bridge-key"

    @pytest.mark.asyncio
    async def test_sekha_client_async_context_manager(self):
        """Test SekhaClient as async context manager"""
        async with SekhaClient(
            controller_url="http://localhost:8080",
            api_key="sk-test-12345678901234567890",
            bridge_url="http://localhost:5001",
        ) as client:
            assert client is not None

    @pytest.mark.asyncio
    async def test_sekha_client_close(self):
        """Test SekhaClient close method"""
        client = SekhaClient(
            controller_url="http://localhost:8080",
            api_key="sk-test-12345678901234567890",
            bridge_url="http://localhost:5001",
        )
        await client.close()
        # Just verify it doesn't raise


class TestCreateSekhaClient:
    """Test factory function"""

    def test_create_sekha_client(self):
        """Test create_sekha_client factory"""
        client = create_sekha_client(
            controller_url="http://localhost:8080",
            api_key="sk-test-12345678901234567890",
            bridge_url="http://localhost:5001",
        )
        assert isinstance(client, SekhaClient)
        assert client.config.controller_url == "http://localhost:8080"

    def test_create_sekha_client_with_kwargs(self):
        """Test create_sekha_client with additional kwargs"""
        client = create_sekha_client(
            controller_url="http://localhost:8080",
            api_key="sk-test-12345678901234567890",
            bridge_url="http://localhost:5001",
            timeout=90.0,
            default_label="Custom",
        )
        assert client.config.timeout == 90.0
        assert client.config.default_label == "Custom"
