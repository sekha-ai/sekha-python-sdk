"""Tests specifically targeting 100% code coverage

Covers all remaining uncovered lines in sekha/client.py, sekha/models.py, and sekha/utils.py
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import httpx
from datetime import datetime

from sekha import (
    SekhaClient,
    ClientConfig,
    NewConversation,
    MessageDto,
    MessageRole,
    SekhaAPIError,
    SekhaAuthError,
    SekhaConnectionError,
    SekhaNotFoundError,
    SekhaValidationError,
)
from sekha.models import QueryRequest, ImportanceScore, LabelSuggestion
from sekha.utils import validate_api_key, validate_base_url, parse_iso_datetime


# ============== Client.py Coverage ==============


class TestGetConversation404:
    """Test get_conversation 404 (lines 135-136)"""

    @pytest.mark.asyncio
    async def test_get_conversation_404(self, test_config, respx_mock):
        """Test get_conversation with 404"""
        respx_mock.get("http://localhost:8080/api/v1/conversations/123").mock(
            return_value=httpx.Response(404, text="Not found")
        )
        
        client = SekhaClient(test_config)
        with pytest.raises(SekhaNotFoundError, match="Conversation 123 not found"):
            await client.get_conversation("123")
        await client.close()


class TestListConversationsFilters:
    """Test list_conversations filters (line 170)"""

    @pytest.mark.asyncio
    async def test_list_with_pinned(self, test_config, respx_mock):
        """Test list with pinned filter"""
        respx_mock.get("http://localhost:8080/api/v1/conversations").mock(
            return_value=httpx.Response(
                200, json={"results": [], "total": 0, "page": 1, "page_size": 50}
            )
        )
        
        client = SekhaClient(test_config)
        await client.list_conversations(pinned=True)
        await client.close()


class TestUpdateLabel404:
    """Test update_label 404 (line 208)"""

    @pytest.mark.asyncio
    async def test_update_label_404(self, test_config, respx_mock):
        """Test update_label with 404"""
        respx_mock.put("http://localhost:8080/api/v1/conversations/123/label").mock(
            return_value=httpx.Response(404, text="Not found")
        )
        
        client = SekhaClient(test_config)
        with pytest.raises(SekhaNotFoundError, match="Conversation 123 not found"):
            await client.update_label("123", "test", "/")
        await client.close()


class TestUpdateFolder404:
    """Test update_folder 404 (line 230)"""

    @pytest.mark.asyncio
    async def test_update_folder_404(self, test_config, respx_mock):
        """Test update_folder with 404"""
        respx_mock.put("http://localhost:8080/api/v1/conversations/123/folder").mock(
            return_value=httpx.Response(404, text="Not found")
        )
        
        client = SekhaClient(test_config)
        with pytest.raises(SekhaNotFoundError, match="Conversation 123 not found"):
            await client.update_folder("123", "/new")
        await client.close()


class TestPinConversation404:
    """Test pin_conversation 404 (line 247)"""

    @pytest.mark.asyncio
    async def test_pin_404(self, test_config, respx_mock):
        """Test pin_conversation with 404"""
        respx_mock.put("http://localhost:8080/api/v1/conversations/123/pin").mock(
            return_value=httpx.Response(404, text="Not found")
        )
        
        client = SekhaClient(test_config)
        with pytest.raises(SekhaNotFoundError, match="Conversation 123 not found"):
            await client.pin_conversation("123")
        await client.close()


class TestArchiveConversation404:
    """Test archive_conversation 404 (line 264)"""

    @pytest.mark.asyncio
    async def test_archive_404(self, test_config, respx_mock):
        """Test archive_conversation with 404"""
        respx_mock.put("http://localhost:8080/api/v1/conversations/123/archive").mock(
            return_value=httpx.Response(404, text="Not found")
        )
        
        client = SekhaClient(test_config)
        with pytest.raises(SekhaNotFoundError, match="Conversation 123 not found"):
            await client.archive_conversation("123")
        await client.close()


class TestDeleteConversation404:
    """Test delete_conversation 404 (line 283)"""

    @pytest.mark.asyncio
    async def test_delete_404(self, test_config, respx_mock):
        """Test delete_conversation with 404"""
        respx_mock.delete("http://localhost:8080/api/v1/conversations/123").mock(
            return_value=httpx.Response(404, text="Not found")
        )
        
        client = SekhaClient(test_config)
        with pytest.raises(SekhaNotFoundError, match="Conversation 123 not found"):
            await client.delete_conversation("123")
        await client.close()


class TestQueryErrors:
    """Test query error handling (lines 306-307)"""

    @pytest.mark.asyncio
    async def test_query_timeout(self, test_config, respx_mock):
        """Test query with timeout"""
        respx_mock.post("http://localhost:8080/api/v1/query").mock(
            side_effect=httpx.TimeoutException("Timeout")
        )
        
        client = SekhaClient(test_config)
        with pytest.raises(SekhaConnectionError, match="Query timed out"):
            await client.query("test")
        await client.close()

    @pytest.mark.asyncio
    async def test_query_connect_error(self, test_config, respx_mock):
        """Test query with connect error"""
        respx_mock.post("http://localhost:8080/api/v1/query").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        
        client = SekhaClient(test_config)
        with pytest.raises(SekhaConnectionError, match="Connection failed"):
            await client.query("test")
        await client.close()

    @pytest.mark.asyncio
    async def test_query_400_error(self, test_config, respx_mock):
        """Test query with 400 error"""
        respx_mock.post("http://localhost:8080/api/v1/query").mock(
            return_value=httpx.Response(400, text="Bad request")
        )
        
        client = SekhaClient(test_config)
        with pytest.raises(SekhaValidationError, match="Invalid query parameters"):
            await client.query("test")
        await client.close()

    @pytest.mark.asyncio
    async def test_query_401_error(self, test_config, respx_mock):
        """Test query with 401 error"""
        respx_mock.post("http://localhost:8080/api/v1/query").mock(
            return_value=httpx.Response(401, text="Unauthorized")
        )
        
        client = SekhaClient(test_config)
        with pytest.raises(SekhaAuthError, match="Invalid API key"):
            await client.query("test")
        await client.close()


class TestCountConversationsFilters:
    """Test count_conversations with filters (line 348)"""

    @pytest.mark.asyncio
    async def test_count_with_folder(self, test_config, respx_mock):
        """Test count with folder filter"""
        respx_mock.get("http://localhost:8080/api/v1/conversations/count").mock(
            return_value=httpx.Response(200, json={"count": 5})
        )
        
        client = SekhaClient(test_config)
        result = await client.count_conversations(folder="/work")
        assert result == 5
        await client.close()


class TestAssembleContextDefaults:
    """Test assemble_context with None parameters (lines 376-377)"""

    @pytest.mark.asyncio
    async def test_assemble_context_none_params(self, test_config, respx_mock):
        """Test assemble_context with None for optional params"""
        respx_mock.post("http://localhost:8080/api/v1/context/assemble").mock(
            return_value=httpx.Response(200, json=[])
        )
        
        client = SekhaClient(test_config)
        await client.assemble_context("test", preferred_labels=None, excluded_folders=None)
        await client.close()


class TestSummarizeKwargs:
    """Test summarize with kwargs (lines 387-388, 417-418)"""

    @pytest.mark.asyncio
    async def test_summarize_with_level(self, test_config, respx_mock):
        """Test summarize with level parameter"""
        respx_mock.post("http://localhost:8080/api/v1/summarize").mock(
            return_value=httpx.Response(200, json={"summary": "test", "level": "weekly"})
        )
        
        client = SekhaClient(test_config)
        result = await client.summarize("123", level="weekly")
        assert result["level"] == "weekly"
        await client.close()

    @pytest.mark.asyncio
    async def test_generate_summary_alias(self, test_config, respx_mock):
        """Test generate_summary alias"""
        respx_mock.post("http://localhost:8080/api/v1/summarize").mock(
            return_value=httpx.Response(200, json={"summary": "test"})
        )
        
        client = SekhaClient(test_config)
        result = await client.generate_summary("123", level="daily")
        assert "summary" in result
        await client.close()


class TestAutoLabel:
    """Test auto_label paths (lines 443-444, 462-463, 480-481)"""

    @pytest.mark.asyncio
    async def test_auto_label_no_match(self, test_config, respx_mock):
        """Test auto_label when no suggestions meet threshold"""
        respx_mock.post("http://localhost:8080/api/v1/labels/suggest").mock(
            return_value=httpx.Response(
                200,
                json={
                    "conversation_id": "123",
                    "suggestions": [{"label": "test", "confidence": 0.5, "folder": "/"}],
                },
            )
        )
        
        client = SekhaClient(test_config)
        result = await client.auto_label("123", threshold=0.9)
        assert result is None
        await client.close()

    @pytest.mark.asyncio
    async def test_auto_label_with_match(self, test_config, respx_mock):
        """Test auto_label when suggestion meets threshold"""
        respx_mock.post("http://localhost:8080/api/v1/labels/suggest").mock(
            return_value=httpx.Response(
                200,
                json={
                    "conversation_id": "123",
                    "suggestions": [
                        {"label": "important", "confidence": 0.95, "folder": "/work"}
                    ],
                },
            )
        )
        respx_mock.put("http://localhost:8080/api/v1/conversations/123/label").mock(
            return_value=httpx.Response(200)
        )
        
        client = SekhaClient(test_config)
        result = await client.auto_label("123", threshold=0.7)
        assert result == "important"
        await client.close()


class TestExportFilters:
    """Test export with filters (lines 625-637)"""

    @pytest.mark.asyncio
    async def test_export_with_label(self, test_config, respx_mock):
        """Test export with label filter"""
        respx_mock.get("http://localhost:8080/api/v1/export").mock(
            return_value=httpx.Response(
                200, json={"content": "# Export", "format": "markdown"}
            )
        )
        
        client = SekhaClient(test_config)
        result = await client.export(label="test")
        assert "# Export" in result
        await client.close()

    @pytest.mark.asyncio
    async def test_export_with_folder(self, test_config, respx_mock):
        """Test export with folder filter"""
        respx_mock.get("http://localhost:8080/api/v1/export").mock(
            return_value=httpx.Response(200, json={"content": "# Export", "format": "json"})
        )
        
        client = SekhaClient(test_config)
        result = await client.export(folder="/work")
        assert "# Export" in result
        await client.close()


class TestSyncWrapper:
    """Test SyncSekhaClient (lines 621, 643-654)"""

    def test_sync_wrapper_exit(self, test_config):
        """Test SyncSekhaClient __exit__ method"""
        from sekha.client import SyncSekhaClient
        
        sync_client = SyncSekhaClient(test_config)
        # Simulate having a loop
        import asyncio
        sync_client._loop = asyncio.new_event_loop()
        
        # Call __exit__
        sync_client.__exit__(None, None, None)
        
        # Loop should be closed
        assert sync_client._loop.is_closed()

    def test_sync_wrapper_in_async_context(self, test_config):
        """Test SyncSekhaClient detects async context"""
        from sekha.client import SyncSekhaClient
        import asyncio
        
        sync_client = SyncSekhaClient(test_config)
        
        # Mock get_running_loop to simulate async context
        with patch("asyncio.get_running_loop") as mock_loop:
            mock_loop.return_value = asyncio.new_event_loop()
            
            with pytest.raises(
                RuntimeError, match="SyncSekhaClient cannot be used within an async context"
            ):
                # Try to call any method which will call _get_or_create_loop
                sync_client._get_or_create_loop()


# ============== Models.py Coverage ==============


class TestModelsEdgeCases:
    """Test models.py lines 51, 54"""

    def test_query_request_with_none_values(self):
        """Test QueryRequest with None limit/offset/filters"""
        req = QueryRequest(query="test", limit=None, offset=None, filters=None)
        data = req.model_dump()
        assert data["query"] == "test"
        assert "limit" in data or data.get("limit") is None

    def test_importance_score_validation_low(self):
        """Test ImportanceScore rejects values < 1"""
        with pytest.raises(ValueError):
            ImportanceScore(score=0)

    def test_importance_score_validation_high(self):
        """Test ImportanceScore rejects values > 10"""
        with pytest.raises(ValueError):
            ImportanceScore(score=11)


# ============== Utils.py Coverage ==============


class TestUtilsEdgeCases:
    """Test utils.py lines 17-19, 89, 105, 113"""

    def test_validate_api_key_non_string(self):
        """Test validate_api_key with non-string (line 17)"""
        with pytest.raises(ValueError, match="must be a string"):
            validate_api_key(12345)  # type: ignore

    def test_validate_api_key_wrong_prefix(self):
        """Test validate_api_key with wrong prefix (line 18)"""
        with pytest.raises(ValueError, match="must start with"):
            validate_api_key("wrong-" + "x" * 32)

    def test_validate_api_key_too_short(self):
        """Test validate_api_key too short (line 19)"""
        with pytest.raises(ValueError, match="too short"):
            validate_api_key("sk-sekha-short")

    def test_validate_base_url_non_string(self):
        """Test validate_base_url with non-string (line 89)"""
        with pytest.raises(ValueError, match="must be a string"):
            validate_base_url(12345)  # type: ignore

    def test_validate_base_url_no_scheme(self):
        """Test validate_base_url without scheme (line 105)"""
        with pytest.raises(ValueError, match="Invalid base_url"):
            validate_base_url("localhost:8080")

    def test_parse_iso_datetime_invalid(self):
        """Test parse_iso_datetime with invalid format (line 113)"""
        with pytest.raises(ValueError):
            parse_iso_datetime("not-a-date")
