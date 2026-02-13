"""Tests specifically targeting remaining coverage gaps using AsyncMock pattern"""

import pytest
import httpx
import asyncio
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from sekha import MemoryController
from sekha.errors import (
    SekhaNotFoundError,
    SekhaConnectionError,
    SekhaAuthError,
    SekhaValidationError,
    SekhaAPIError,
)
from sekha.utils import validate_api_key, validate_base_url, parse_iso_datetime


class TestSyncClientProperty:
    """Lines 79-88: sync_client property lazy loading"""

    def test_sync_client_lazy_creation(self, test_config):
        client = MemoryController(test_config)
        assert client._sync_client is None
        sync = client.sync_client
        assert sync is not None
        assert isinstance(sync, httpx.Client)
        sync2 = client.sync_client
        assert sync2 is sync
        sync.close()


class TestErrorHandling404:
    """Lines 135-136, 208, 230, 247, 264, 283: 404 error handling"""

    @pytest.mark.asyncio
    async def test_get_conversation_404(self, test_config):
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        error = httpx.HTTPStatusError("404", request=Mock(), response=mock_response)
        client.client.get = AsyncMock(side_effect=error)

        with pytest.raises(SekhaNotFoundError):
            await client.get_conversation("nonexistent")

    @pytest.mark.asyncio
    async def test_update_label_404(self, test_config):
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        error = httpx.HTTPStatusError("404", request=Mock(), response=mock_response)
        client.client.put = AsyncMock(side_effect=error)

        with pytest.raises(SekhaNotFoundError):
            await client.update_label("nonexistent", "label", "/")

    @pytest.mark.asyncio
    async def test_update_folder_404(self, test_config):
        """Line 230 - 404 path"""
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        error = httpx.HTTPStatusError("404", request=Mock(), response=mock_response)
        client.client.put = AsyncMock(side_effect=error)

        with pytest.raises(SekhaNotFoundError):
            await client.update_folder("nonexistent", "/new")

    @pytest.mark.asyncio
    async def test_update_folder_500(self, test_config):
        """Lines 227-230 - non-404 error path"""
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        error = httpx.HTTPStatusError("500", request=Mock(), response=mock_response)
        client.client.put = AsyncMock(side_effect=error)

        with pytest.raises(SekhaAPIError):
            await client.update_folder("123", "/new")

    @pytest.mark.asyncio
    async def test_pin_404(self, test_config):
        """Line 247 - 404 path"""
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        error = httpx.HTTPStatusError("404", request=Mock(), response=mock_response)
        client.client.put = AsyncMock(side_effect=error)

        with pytest.raises(SekhaNotFoundError):
            await client.pin_conversation("nonexistent")

    @pytest.mark.asyncio
    async def test_pin_500(self, test_config):
        """Lines 244-247 - non-404 error path"""
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        error = httpx.HTTPStatusError("500", request=Mock(), response=mock_response)
        client.client.put = AsyncMock(side_effect=error)

        with pytest.raises(SekhaAPIError):
            await client.pin_conversation("123")

    @pytest.mark.asyncio
    async def test_archive_404(self, test_config):
        """Line 264 - 404 path"""
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        error = httpx.HTTPStatusError("404", request=Mock(), response=mock_response)
        client.client.put = AsyncMock(side_effect=error)

        with pytest.raises(SekhaNotFoundError):
            await client.archive_conversation("nonexistent")

    @pytest.mark.asyncio
    async def test_archive_500(self, test_config):
        """Lines 261-264 - non-404 error path"""
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Server error"
        error = httpx.HTTPStatusError("500", request=Mock(), response=mock_response)
        client.client.put = AsyncMock(side_effect=error)

        with pytest.raises(SekhaAPIError):
            await client.archive_conversation("123")

    @pytest.mark.asyncio
    async def test_delete_404(self, test_config):
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        error = httpx.HTTPStatusError("404", request=Mock(), response=mock_response)
        client.client.delete = AsyncMock(side_effect=error)

        with pytest.raises(SekhaNotFoundError):
            await client.delete_conversation("nonexistent")


class TestQueryErrors:
    """Lines 295, 297, 306-307: Query error paths"""

    @pytest.mark.asyncio
    async def test_query_400(self, test_config):
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        error = httpx.HTTPStatusError("400", request=Mock(), response=mock_response)
        client.client.post = AsyncMock(side_effect=error)

        with pytest.raises(SekhaValidationError):
            await client.query("test")

    @pytest.mark.asyncio
    async def test_query_401(self, test_config):
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        error = httpx.HTTPStatusError("401", request=Mock(), response=mock_response)
        client.client.post = AsyncMock(side_effect=error)

        with pytest.raises(SekhaAuthError):
            await client.query("test")

    @pytest.mark.asyncio
    async def test_query_timeout(self, test_config):
        client = MemoryController(test_config)
        client.client.post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

        with pytest.raises(SekhaConnectionError, match="Query timed out"):
            await client.query("test")

    @pytest.mark.asyncio
    async def test_query_connect_error(self, test_config):
        client = MemoryController(test_config)
        client.client.post = AsyncMock(
            side_effect=httpx.ConnectError("Connection failed")
        )

        with pytest.raises(SekhaConnectionError, match="Connection failed"):
            await client.query("test")


class TestFilterConditions:
    """Lines 170, 172, 174, 343, 348: Optional filter parameters"""

    @pytest.mark.asyncio
    async def test_list_with_label_filter(self, test_config):
        """Line 172 - label filter"""
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={
                "results": [],
                "total": 0,
                "query": "label:important",
            }
        )
        client.client.get = AsyncMock(return_value=mock_response)

        await client.list_conversations(label="important")
        assert client.client.get.called

    @pytest.mark.asyncio
    async def test_list_with_pinned_filter(self, test_config):
        """Line 170"""
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={
                "results": [],
                "total": 0,
                "query": "pinned:true",
            }
        )
        client.client.get = AsyncMock(return_value=mock_response)

        await client.list_conversations(pinned=True)
        assert client.client.get.called

    @pytest.mark.asyncio
    async def test_list_with_archived_filter(self, test_config):
        """Line 174"""
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={
                "results": [],
                "total": 0,
                "query": "archived:false",
            }
        )
        client.client.get = AsyncMock(return_value=mock_response)

        await client.list_conversations(archived=False)
        assert client.client.get.called

    @pytest.mark.asyncio
    async def test_count_with_label(self, test_config):
        """Line 343 - count with label filter"""
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(return_value={"count": 5})
        client.client.get = AsyncMock(return_value=mock_response)

        count = await client.count_conversations(label="test")
        assert count == 5

    @pytest.mark.asyncio
    async def test_count_with_folder(self, test_config):
        """Line 348"""
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(return_value={"count": 3})
        client.client.get = AsyncMock(return_value=mock_response)

        count = await client.count_conversations(folder="/work")
        assert count == 3


class TestNoneToEmptyList:
    """Lines 376-377: None converted to empty list"""

    @pytest.mark.asyncio
    async def test_assemble_context_none_params(self, test_config):
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={
                "messages": [],
                "token_count": 0,
                "conversation_ids": [],
                "labels": [],
            }
        )
        client.client.post = AsyncMock(return_value=mock_response)

        result = await client.assemble_context(
            "test", preferred_labels=None, excluded_folders=None
        )
        assert result["messages"] == []


class TestKwargsAndAliases:
    """Lines 387-388, 417-418: Level parameter and aliases"""

    @pytest.mark.asyncio
    async def test_summarize_with_level(self, test_config):
        """Line 387-388"""
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={
                "conversation_id": "123",
                "summary": "test",
                "level": "weekly",
                "token_count": 100,
                "created_at": datetime.now().isoformat(),
            }
        )
        client.client.post = AsyncMock(return_value=mock_response)

        result = await client.summarize("123", level="weekly")
        assert result["level"] == "weekly"

    @pytest.mark.asyncio
    async def test_generate_summary_alias(self, test_config):
        """Lines 417-418 - generate_summary alias"""
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={
                "conversation_id": "123",
                "summary": "test",
                "level": "daily",
                "token_count": 50,
                "created_at": datetime.now().isoformat(),
            }
        )
        client.client.post = AsyncMock(return_value=mock_response)

        result = await client.generate_summary("123")
        assert "summary" in result


class TestAutoLabelPaths:
    """Lines 443-444, 462-463, 480-481: Auto-label logic"""

    @pytest.mark.asyncio
    async def test_auto_label_below_threshold(self, test_config):
        """Lines 462-463: Return None if no match"""
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={
                "conversation_id": "123",
                "suggestions": [
                    {
                        "label": "test",
                        "confidence": 0.5,
                        "folder": "/",
                        "reasoning": "low confidence",
                    }
                ],
                "top_suggestion": {
                    "label": "test",
                    "confidence": 0.5,
                    "folder": "/",
                    "reasoning": "low confidence",
                },
            }
        )
        client.client.post = AsyncMock(return_value=mock_response)

        result = await client.auto_label("123", threshold=0.9)
        assert result is None

    @pytest.mark.asyncio
    async def test_auto_label_above_threshold(self, test_config):
        """Lines 480-481: Apply label if above threshold"""
        client = MemoryController(test_config)
        suggest_response = Mock()
        suggest_response.raise_for_status = Mock()
        suggest_response.json = Mock(
            return_value={
                "conversation_id": "123",
                "suggestions": [
                    {
                        "label": "important",
                        "confidence": 0.95,
                        "folder": "/work",
                        "reasoning": "high confidence",
                    }
                ],
                "top_suggestion": {
                    "label": "important",
                    "confidence": 0.95,
                    "folder": "/work",
                    "reasoning": "high confidence",
                },
            }
        )

        update_response = Mock()
        update_response.raise_for_status = Mock()

        client.client.post = AsyncMock(return_value=suggest_response)
        client.client.put = AsyncMock(return_value=update_response)

        result = await client.auto_label("123", threshold=0.7)
        assert result == "important"
        assert client.client.put.called

    @pytest.mark.asyncio
    async def test_suggest_labels_error(self, test_config):
        """Lines 443-444 - error path in suggest_labels exception handling"""
        client = MemoryController(test_config)
        client.client.post = AsyncMock(side_effect=Exception("API failed"))

        with pytest.raises(Exception, match="Failed to suggest labels"):
            await client.suggest_labels("123")


class TestExportFilters:
    """Lines 550, 621: Export with filters"""

    @pytest.mark.asyncio
    async def test_export_with_label(self, test_config):
        """Line 621 - export with label filter"""
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={
                "content": "# Export",
                "format": "markdown",
                "conversation_count": 1,
            }
        )
        client.client.get = AsyncMock(return_value=mock_response)

        result = await client.export(label="important")
        assert result == "# Export"

    @pytest.mark.asyncio
    async def test_export_with_folder(self, test_config):
        """Line 550"""
        client = MemoryController(test_config)
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={
                "content": "# Export",
                "format": "markdown",
                "conversation_count": 1,
            }
        )
        client.client.get = AsyncMock(return_value=mock_response)

        result = await client.export(folder="/work")
        assert result == "# Export"


class TestSyncWrapper:
    """Lines 628, 643-654: SyncSekhaClient wrapper"""

    def test_sync_wrapper_enter(self, test_config):
        from sekha.client import SyncSekhaClient

        sync_client = SyncSekhaClient(test_config)
        result = sync_client.__enter__()
        assert result is sync_client

    def test_sync_wrapper_exit_with_loop(self, test_config):
        from sekha.client import SyncSekhaClient

        sync_client = SyncSekhaClient(test_config)
        sync_client._loop = asyncio.new_event_loop()
        sync_client.__exit__(None, None, None)
        assert sync_client._loop.is_closed()

    def test_sync_wrapper_exit_no_loop(self, test_config):
        from sekha.client import SyncSekhaClient

        sync_client = SyncSekhaClient(test_config)
        sync_client._loop = None
        sync_client.__exit__(None, None, None)

    def test_get_or_create_loop(self, test_config):
        from sekha.client import SyncSekhaClient

        sync_client = SyncSekhaClient(test_config)
        loop = sync_client._get_or_create_loop()
        assert loop is not None
        assert not loop.is_closed()
        loop.close()


# ============== Utils.py Coverage ==============


class TestUtils:
    """Lines 17-19, 89, 105, 113"""

    def test_validate_api_key_not_string(self):
        with pytest.raises(ValueError, match="must be a string"):
            validate_api_key(123)

    def test_validate_api_key_too_short(self):
        with pytest.raises(ValueError, match="too short"):
            validate_api_key("sk-sekha-short")

    def test_validate_base_url_not_string(self):
        with pytest.raises(ValueError, match="must be a string"):
            validate_base_url(123)

    def test_validate_base_url_no_scheme(self):
        with pytest.raises(ValueError, match="Invalid base_url"):
            validate_base_url("localhost:8080")

    def test_parse_iso_datetime_invalid(self):
        with pytest.raises(ValueError):
            parse_iso_datetime("not-a-date")
