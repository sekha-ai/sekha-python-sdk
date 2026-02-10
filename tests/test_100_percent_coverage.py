"""Tests specifically targeting 100% code coverage"""

import pytest
import httpx
import asyncio
import json

from sekha import SekhaClient, ClientConfig
from sekha.errors import SekhaNotFoundError, SekhaConnectionError, SekhaAuthError, SekhaValidationError
from sekha.models import QueryRequest, ImportanceScore
from sekha.utils import validate_api_key, validate_base_url, parse_iso_datetime


def create_mock_response(status=200, json_data=None, text=None):
    """Helper to create httpx Response objects with proper content"""
    if json_data is not None:
        content = json.dumps(json_data).encode()
    elif text is not None:
        content = text.encode()
    else:
        content = b"{}"
    
    return httpx.Response(
        status_code=status,
        content=content,
        request=httpx.Request("GET", "http://test"),
    )


class MockTransport(httpx.AsyncBaseTransport):
    """Mock transport that returns predefined responses"""
    
    def __init__(self):
        self.responses = {}
        self.call_count = {}
    
    def add_response(self, method, path, response):
        key = f"{method} {path}"
        self.responses[key] = response
        self.call_count[key] = 0
    
    async def handle_async_request(self, request):
        key = f"{request.method} {request.url.path}"
        self.call_count[key] = self.call_count.get(key, 0) + 1
        
        if key in self.responses:
            return self.responses[key]
        
        # Default 404
        return create_mock_response(404, text="Not found")


# ============== Client.py Coverage ==============

class TestSyncClientProperty:
    """Lines 79-88"""
    
    def test_sync_client_property(self, test_config):
        client = SekhaClient(test_config)
        assert client._sync_client is None
        sync = client.sync_client
        assert sync is not None
        sync2 = client.sync_client
        assert sync2 is sync
        sync.close()


class TestErrorPaths:
    """Lines 135-136, 208, 230, 247, 264, 283, 295, 306-307"""
    
    @pytest.mark.asyncio
    async def test_get_conversation_404(self, test_config):
        """Line 135-136"""
        transport = MockTransport()
        transport.add_response("GET", "/api/v1/conversations/123", create_mock_response(404, text="Not found"))
        
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
            client = SekhaClient(test_config)
            client.client = http_client
            
            with pytest.raises(SekhaNotFoundError):
                await client.get_conversation("123")
    
    @pytest.mark.asyncio
    async def test_update_label_404(self, test_config):
        """Line 208"""
        transport = MockTransport()
        transport.add_response("PUT", "/api/v1/conversations/123/label", create_mock_response(404, text="Not found"))
        
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
            client = SekhaClient(test_config)
            client.client = http_client
            
            with pytest.raises(SekhaNotFoundError):
                await client.update_label("123", "test", "/")
    
    @pytest.mark.asyncio
    async def test_update_folder_404(self, test_config):
        """Line 230"""
        transport = MockTransport()
        transport.add_response("PUT", "/api/v1/conversations/123/folder", create_mock_response(404, text="Not found"))
        
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
            client = SekhaClient(test_config)
            client.client = http_client
            
            with pytest.raises(SekhaNotFoundError):
                await client.update_folder("123", "/new")
    
    @pytest.mark.asyncio
    async def test_pin_404(self, test_config):
        """Line 247"""
        transport = MockTransport()
        transport.add_response("PUT", "/api/v1/conversations/123/pin", create_mock_response(404, text="Not found"))
        
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
            client = SekhaClient(test_config)
            client.client = http_client
            
            with pytest.raises(SekhaNotFoundError):
                await client.pin_conversation("123")
    
    @pytest.mark.asyncio
    async def test_archive_404(self, test_config):
        """Line 264"""
        transport = MockTransport()
        transport.add_response("PUT", "/api/v1/conversations/123/archive", create_mock_response(404, text="Not found"))
        
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
            client = SekhaClient(test_config)
            client.client = http_client
            
            with pytest.raises(SekhaNotFoundError):
                await client.archive_conversation("123")
    
    @pytest.mark.asyncio
    async def test_delete_404(self, test_config):
        """Line 283"""
        transport = MockTransport()
        transport.add_response("DELETE", "/api/v1/conversations/123", create_mock_response(404, text="Not found"))
        
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
            client = SekhaClient(test_config)
            client.client = http_client
            
            with pytest.raises(SekhaNotFoundError):
                await client.delete_conversation("123")
    
    @pytest.mark.asyncio
    async def test_query_timeout(self, test_config):
        """Line 306"""
        class TimeoutTransport(httpx.AsyncBaseTransport):
            async def handle_async_request(self, request):
                raise httpx.TimeoutException("Timeout")
        
        async with httpx.AsyncClient(transport=TimeoutTransport(), base_url="http://test") as http_client:
            client = SekhaClient(test_config)
            client.client = http_client
            
            with pytest.raises(SekhaConnectionError, match="Query timed out"):
                await client.query("test")
    
    @pytest.mark.asyncio
    async def test_query_connect_error(self, test_config):
        """Line 307"""
        class ConnectErrorTransport(httpx.AsyncBaseTransport):
            async def handle_async_request(self, request):
                raise httpx.ConnectError("Connection failed")
        
        async with httpx.AsyncClient(transport=ConnectErrorTransport(), base_url="http://test") as http_client:
            client = SekhaClient(test_config)
            client.client = http_client
            
            with pytest.raises(SekhaConnectionError, match="Connection failed"):
                await client.query("test")


class TestFilterConditions:
    """Lines 170, 174, 348"""
    
    @pytest.mark.asyncio
    async def test_list_with_pinned(self, test_config):
        """Line 170"""
        transport = MockTransport()
        transport.add_response("GET", "/api/v1/conversations", 
                             create_mock_response(200, {"results": [], "total": 0, "page": 1, "page_size": 50}))
        
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
            client = SekhaClient(test_config)
            client.client = http_client
            await client.list_conversations(pinned=True)
    
    @pytest.mark.asyncio
    async def test_list_with_archived(self, test_config):
        """Line 174"""
        transport = MockTransport()
        transport.add_response("GET", "/api/v1/conversations", 
                             create_mock_response(200, {"results": [], "total": 0, "page": 1, "page_size": 50}))
        
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
            client = SekhaClient(test_config)
            client.client = http_client
            await client.list_conversations(archived=False)
    
    @pytest.mark.asyncio
    async def test_count_with_folder(self, test_config):
        """Line 348"""
        transport = MockTransport()
        transport.add_response("GET", "/api/v1/conversations/count",
                             create_mock_response(200, {"count": 3}))
        
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
            client = SekhaClient(test_config)
            client.client = http_client
            result = await client.count_conversations(folder="/work")
            assert result == 3


class TestNoneDefaults:
    """Lines 376-377"""
    
    @pytest.mark.asyncio
    async def test_assemble_context_none_to_empty_list(self, test_config):
        transport = MockTransport()
        transport.add_response("POST", "/api/v1/context/assemble",
                             create_mock_response(200, []))
        
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
            client = SekhaClient(test_config)
            client.client = http_client
            await client.assemble_context("test", preferred_labels=None, excluded_folders=None)


class TestKwargsAndAliases:
    """Lines 387-388"""
    
    @pytest.mark.asyncio
    async def test_summarize(self, test_config):
        """Line 387-388"""
        transport = MockTransport()
        transport.add_response("POST", "/api/v1/summarize",
                             create_mock_response(200, {"summary": "test"}))
        
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
            client = SekhaClient(test_config)
            client.client = http_client
            result = await client.summarize("123", level="weekly")
            assert "summary" in result


class TestAutoLabelPaths:
    """Lines 462-463, 480-481"""
    
    @pytest.mark.asyncio
    async def test_auto_label_no_match(self, test_config):
        """Lines 462-463"""
        transport = MockTransport()
        transport.add_response("POST", "/api/v1/labels/suggest",
                             create_mock_response(200, {
                                 "conversation_id": "123",
                                 "suggestions": [{"label": "test", "confidence": 0.5, "folder": "/"}]
                             }))
        
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
            client = SekhaClient(test_config)
            client.client = http_client
            result = await client.auto_label("123", threshold=0.9)
            assert result is None
    
    @pytest.mark.asyncio
    async def test_auto_label_with_match(self, test_config):
        """Lines 480-481"""
        transport = MockTransport()
        transport.add_response("POST", "/api/v1/labels/suggest",
                             create_mock_response(200, {
                                 "conversation_id": "123",
                                 "suggestions": [{"label": "important", "confidence": 0.95, "folder": "/work"}]
                             }))
        transport.add_response("PUT", "/api/v1/conversations/123/label",
                             create_mock_response(200, {}))
        
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as http_client:
            client = SekhaClient(test_config)
            client.client = http_client
            result = await client.auto_label("123", threshold=0.7)
            assert result == "important"


class TestSyncWrapper:
    """Lines 628, 643-654"""
    
    def test_sync_wrapper_enter(self, test_config):
        """Line 628"""
        from sekha.client import SyncSekhaClient
        sync_client = SyncSekhaClient(test_config)
        result = sync_client.__enter__()
        assert result is sync_client
    
    def test_sync_wrapper_exit(self, test_config):
        """Lines 643-654"""
        from sekha.client import SyncSekhaClient
        sync_client = SyncSekhaClient(test_config)
        sync_client._loop = asyncio.new_event_loop()
        sync_client.__exit__(None, None, None)
        assert sync_client._loop.is_closed()
    
    def test_sync_wrapper_exit_no_loop(self, test_config):
        """Test __exit__ when loop is None"""
        from sekha.client import SyncSekhaClient
        sync_client = SyncSekhaClient(test_config)
        sync_client._loop = None
        sync_client.__exit__(None, None, None)  # Should not error
    
    def test_get_or_create_loop_new(self, test_config):
        """Test _get_or_create_loop creates new loop"""
        from sekha.client import SyncSekhaClient
        sync_client = SyncSekhaClient(test_config)
        loop = sync_client._get_or_create_loop()
        assert loop is not None
        assert sync_client._loop is loop
        loop.close()


# ============== Models.py Coverage ==============

class TestModels:
    """Lines 51, 54"""
    
    def test_query_request_none_values(self):
        """Line 51"""
        req = QueryRequest(query="test", limit=None, offset=None, filters=None)
        data = req.model_dump()
        assert data["query"] == "test"
    
    def test_importance_score_too_low(self):
        """Line 54"""
        with pytest.raises(ValueError):
            ImportanceScore(score=0)
    
    def test_importance_score_too_high(self):
        with pytest.raises(ValueError):
            ImportanceScore(score=11)


# ============== Utils.py Coverage ==============

class TestUtils:
    """Lines 17-19, 89, 105, 113"""
    
    def test_validate_api_key_not_string(self):
        """Line 17"""
        with pytest.raises(ValueError, match="must be a string"):
            validate_api_key(123)
    
    def test_validate_api_key_too_short(self):
        """Line 19"""
        with pytest.raises(ValueError, match="too short"):
            validate_api_key("sk-sekha-short")
    
    def test_validate_base_url_not_string(self):
        """Line 89"""
        with pytest.raises(ValueError, match="must be a string"):
            validate_base_url(123)
    
    def test_validate_base_url_no_scheme(self):
        """Line 105"""
        with pytest.raises(ValueError, match="Invalid base_url"):
            validate_base_url("localhost:8080")
    
    def test_parse_iso_datetime_invalid(self):
        """Line 113"""
        with pytest.raises(ValueError):
            parse_iso_datetime("not-a-date")
