"""Tests specifically targeting 100% code coverage

Covers all remaining uncovered lines in sekha/client.py, sekha/models.py, and sekha/utils.py
"""

import pytest
from unittest.mock import Mock, patch
import httpx
import asyncio

from sekha import (
    SekhaClient,
    ClientConfig,
    SekhaAuthError,
    SekhaConnectionError,
    SekhaNotFoundError,
    SekhaValidationError,
)
from sekha.models import QueryRequest, ImportanceScore
from sekha.utils import validate_api_key, validate_base_url, parse_iso_datetime


# ============== Client.py Coverage ==============


class TestSyncClientProperty:
    """Test sync_client property (lines 79-88)"""

    def test_sync_client_lazy_creation(self, test_config):
        """Test that sync_client is created on first access"""
        client = SekhaClient(test_config)
        assert client._sync_client is None

        # Access property - this creates it
        sync = client.sync_client
        assert sync is not None
        assert isinstance(sync, httpx.Client)

        # Second access returns same client
        sync2 = client.sync_client
        assert sync2 is sync
        
        # Clean up
        sync.close()


class TestGetConversation404:
    """Test get_conversation 404 (lines 135-136)"""

    @pytest.mark.asyncio
    async def test_get_conversation_404(self, test_config):
        """Test get_conversation raises SekhaNotFoundError on 404"""
        client = SekhaClient(test_config)
        
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 404
        mock_response.text = "Not found"
        
        async def mock_get(*args, **kwargs):
            raise httpx.HTTPStatusError("Not Found", request=Mock(), response=mock_response)
        
        client.client.get = mock_get
        
        with pytest.raises(SekhaNotFoundError):
            await client.get_conversation("123")
        
        await client.close()


class TestListConversationsFilters:
    """Test list_conversations filter conditions (lines 170, 174)"""

    @pytest.mark.asyncio
    async def test_list_with_pinned_true(self, test_config):
        """Test pinned=True adds to params"""
        client = SekhaClient(test_config)
        
        async def mock_get(url, **kwargs):
            # Verify pinned is in params
            assert kwargs.get('params', {}).get('pinned') is True
            mock_resp = Mock()
            mock_resp.raise_for_status = Mock()
            mock_resp.json = Mock(return_value={"results": [], "total": 0, "page": 1, "page_size": 50})
            return mock_resp
        
        client.client.get = mock_get
        await client.list_conversations(pinned=True)
        await client.close()

    @pytest.mark.asyncio
    async def test_list_with_archived_false(self, test_config):
        """Test archived=False adds to params"""
        client = SekhaClient(test_config)
        
        async def mock_get(url, **kwargs):
            # Verify archived is in params
            assert kwargs.get('params', {}).get('archived') is False
            mock_resp = Mock()
            mock_resp.raise_for_status = Mock()
            mock_resp.json = Mock(return_value={"results": [], "total": 0, "page": 1, "page_size": 50})
            return mock_resp
        
        client.client.get = mock_get
        await client.list_conversations(archived=False)
        await client.close()


class TestUpdateLabel404:
    """Test update_label 404 (line 208)"""

    @pytest.mark.asyncio
    async def test_update_label_404(self, test_config):
        """Test update_label raises SekhaNotFoundError on 404"""
        client = SekhaClient(test_config)
        
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 404
        
        async def mock_put(*args, **kwargs):
            raise httpx.HTTPStatusError("Not Found", request=Mock(), response=mock_response)
        
        client.client.put = mock_put
        
        with pytest.raises(SekhaNotFoundError):
            await client.update_label("123", "label", "/")
        
        await client.close()


class TestUpdateFolder404:
    """Test update_folder 404 (line 230)"""

    @pytest.mark.asyncio
    async def test_update_folder_404(self, test_config):
        """Test update_folder raises SekhaNotFoundError on 404"""
        client = SekhaClient(test_config)
        
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 404
        
        async def mock_put(*args, **kwargs):
            raise httpx.HTTPStatusError("Not Found", request=Mock(), response=mock_response)
        
        client.client.put = mock_put
        
        with pytest.raises(SekhaNotFoundError):
            await client.update_folder("123", "/new")
        
        await client.close()


class TestPinConversation404:
    """Test pin_conversation 404 (line 247)"""

    @pytest.mark.asyncio
    async def test_pin_404(self, test_config):
        """Test pin_conversation raises SekhaNotFoundError on 404"""
        client = SekhaClient(test_config)
        
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 404
        
        async def mock_put(*args, **kwargs):
            raise httpx.HTTPStatusError("Not Found", request=Mock(), response=mock_response)
        
        client.client.put = mock_put
        
        with pytest.raises(SekhaNotFoundError):
            await client.pin_conversation("123")
        
        await client.close()


class TestArchiveConversation404:
    """Test archive_conversation 404 (line 264)"""

    @pytest.mark.asyncio
    async def test_archive_404(self, test_config):
        """Test archive_conversation raises SekhaNotFoundError on 404"""
        client = SekhaClient(test_config)
        
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 404
        
        async def mock_put(*args, **kwargs):
            raise httpx.HTTPStatusError("Not Found", request=Mock(), response=mock_response)
        
        client.client.put = mock_put
        
        with pytest.raises(SekhaNotFoundError):
            await client.archive_conversation("123")
        
        await client.close()


class TestDeleteConversation404:
    """Test delete_conversation 404 (line 283)"""

    @pytest.mark.asyncio
    async def test_delete_404(self, test_config):
        """Test delete_conversation raises SekhaNotFoundError on 404"""
        client = SekhaClient(test_config)
        
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 404
        
        async def mock_delete(*args, **kwargs):
            raise httpx.HTTPStatusError("Not Found", request=Mock(), response=mock_response)
        
        client.client.delete = mock_delete
        
        with pytest.raises(SekhaNotFoundError):
            await client.delete_conversation("123")
        
        await client.close()


class TestQueryErrors:
    """Test query error handling (lines 306-307)"""

    @pytest.mark.asyncio
    async def test_query_timeout(self, test_config):
        """Test query raises SekhaConnectionError on timeout"""
        client = SekhaClient(test_config)
        
        async def mock_post(*args, **kwargs):
            raise httpx.TimeoutException("Timeout")
        
        client.client.post = mock_post
        
        with pytest.raises(SekhaConnectionError, match="Query timed out"):
            await client.query("test")
        
        await client.close()

    @pytest.mark.asyncio
    async def test_query_connect_error(self, test_config):
        """Test query raises SekhaConnectionError on connect error"""
        client = SekhaClient(test_config)
        
        async def mock_post(*args, **kwargs):
            raise httpx.ConnectError("Connection failed")
        
        client.client.post = mock_post
        
        with pytest.raises(SekhaConnectionError, match="Connection failed"):
            await client.query("test")
        
        await client.close()


class TestCountConversationsFilters:
    """Test count_conversations with filter (line 348)"""

    @pytest.mark.asyncio
    async def test_count_with_folder(self, test_config):
        """Test count_conversations with folder filter"""
        client = SekhaClient(test_config)
        
        async def mock_get(url, **kwargs):
            # Verify folder is in params
            assert kwargs.get('params', {}).get('folder') == "/work"
            mock_resp = Mock()
            mock_resp.raise_for_status = Mock()
            mock_resp.json = Mock(return_value={"count": 5})
            return mock_resp
        
        client.client.get = mock_get
        result = await client.count_conversations(folder="/work")
        assert result == 5
        await client.close()


class TestAssembleContextDefaults:
    """Test assemble_context default params (lines 376-377)"""

    @pytest.mark.asyncio
    async def test_assemble_context_none_params(self, test_config):
        """Test assemble_context converts None to empty lists"""
        client = SekhaClient(test_config)
        
        async def mock_post(url, **kwargs):
            # Verify None converted to empty lists
            body = kwargs.get('json', {})
            assert body['preferred_labels'] == []
            assert body['excluded_folders'] == []
            mock_resp = Mock()
            mock_resp.raise_for_status = Mock()
            mock_resp.json = Mock(return_value=[])
            return mock_resp
        
        client.client.post = mock_post
        await client.assemble_context("test", preferred_labels=None, excluded_folders=None)
        await client.close()


class TestSummarizeKwargs:
    """Test summarize and alias (lines 387-388, 417-418)"""

    @pytest.mark.asyncio
    async def test_summarize_with_level(self, test_config):
        """Test summarize passes level parameter"""
        client = SekhaClient(test_config)
        
        async def mock_post(url, **kwargs):
            mock_resp = Mock()
            mock_resp.raise_for_status = Mock()
            mock_resp.json = Mock(return_value={"summary": "test", "level": "weekly"})
            return mock_resp
        
        client.client.post = mock_post
        result = await client.summarize("123", level="weekly")
        assert result["level"] == "weekly"
        await client.close()

    @pytest.mark.asyncio
    async def test_generate_summary_alias(self, test_config):
        """Test generate_summary calls summarize"""
        client = SekhaClient(test_config)
        
        async def mock_post(url, **kwargs):
            mock_resp = Mock()
            mock_resp.raise_for_status = Mock()
            mock_resp.json = Mock(return_value={"summary": "test"})
            return mock_resp
        
        client.client.post = mock_post
        result = await client.generate_summary("123")
        assert "summary" in result
        await client.close()


class TestAutoLabel:
    """Test auto_label paths (lines 443-444, 462-463, 480-481)"""

    @pytest.mark.asyncio
    async def test_auto_label_no_match(self, test_config):
        """Test auto_label returns None when no suggestions meet threshold"""
        client = SekhaClient(test_config)
        
        async def mock_post(url, **kwargs):
            mock_resp = Mock()
            mock_resp.raise_for_status = Mock()
            mock_resp.json = Mock(return_value={
                "conversation_id": "123",
                "suggestions": [{"label": "test", "confidence": 0.5, "folder": "/"}],
            })
            return mock_resp
        
        client.client.post = mock_post
        result = await client.auto_label("123", threshold=0.9)
        assert result is None
        await client.close()

    @pytest.mark.asyncio
    async def test_auto_label_with_match(self, test_config):
        """Test auto_label applies label when threshold is met"""
        client = SekhaClient(test_config)
        
        post_called = False
        put_called = False
        
        async def mock_post(url, **kwargs):
            nonlocal post_called
            post_called = True
            mock_resp = Mock()
            mock_resp.raise_for_status = Mock()
            mock_resp.json = Mock(return_value={
                "conversation_id": "123",
                "suggestions": [{"label": "important", "confidence": 0.95, "folder": "/work"}],
            })
            return mock_resp
        
        async def mock_put(url, **kwargs):
            nonlocal put_called
            put_called = True
            mock_resp = Mock()
            mock_resp.raise_for_status = Mock()
            return mock_resp
        
        client.client.post = mock_post
        client.client.put = mock_put
        
        result = await client.auto_label("123", threshold=0.7)
        assert result == "important"
        assert post_called
        assert put_called
        await client.close()


class TestSyncWrapper:
    """Test SyncSekhaClient (lines 621, 643-654)"""

    def test_sync_wrapper_context_manager(self, test_config):
        """Test SyncSekhaClient context manager"""
        from sekha.client import SyncSekhaClient
        
        sync_client = SyncSekhaClient(test_config)
        
        # Test __enter__
        result = sync_client.__enter__()
        assert result is sync_client
        
        # Create a loop to test __exit__
        sync_client._loop = asyncio.new_event_loop()
        assert not sync_client._loop.is_closed()
        
        # Test __exit__
        sync_client.__exit__(None, None, None)
        assert sync_client._loop.is_closed()

    def test_sync_wrapper_async_context_detection(self, test_config):
        """Test SyncSekhaClient detects async context"""
        from sekha.client import SyncSekhaClient
        
        sync_client = SyncSekhaClient(test_config)
        
        # Mock get_running_loop to simulate being in async context
        with patch("asyncio.get_running_loop") as mock_get_loop:
            mock_get_loop.return_value = asyncio.new_event_loop()
            
            with pytest.raises(RuntimeError, match="SyncSekhaClient cannot be used within an async context"):
                sync_client._get_or_create_loop()


class TestExportFilters:
    """Test export with filters (lines 625-637)"""

    @pytest.mark.asyncio
    async def test_export_with_label(self, test_config):
        """Test export with label filter"""
        client = SekhaClient(test_config)
        
        async def mock_get(url, **kwargs):
            # Verify label in params
            assert kwargs.get('params', {}).get('label') == "test"
            mock_resp = Mock()
            mock_resp.raise_for_status = Mock()
            mock_resp.json = Mock(return_value={"content": "# Export"})
            return mock_resp
        
        client.client.get = mock_get
        result = await client.export(label="test")
        assert "# Export" in result
        await client.close()

    @pytest.mark.asyncio
    async def test_export_with_folder(self, test_config):
        """Test export with folder filter"""
        client = SekhaClient(test_config)
        
        async def mock_get(url, **kwargs):
            # Verify folder in params
            assert kwargs.get('params', {}).get('folder') == "/work"
            mock_resp = Mock()
            mock_resp.raise_for_status = Mock()
            mock_resp.json = Mock(return_value={"content": "# Export"})
            return mock_resp
        
        client.client.get = mock_get
        result = await client.export(folder="/work")
        assert "# Export" in result
        await client.close()


# ============== Models.py Coverage ==============


class TestModelsEdgeCases:
    """Test models.py lines 51, 54"""

    def test_query_request_with_none_values(self):
        """Test QueryRequest with None limit/offset/filters"""
        req = QueryRequest(query="test", limit=None, offset=None, filters=None)
        data = req.model_dump()
        assert data["query"] == "test"

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
        """Test validate_api_key with non-string"""
        with pytest.raises(ValueError, match="must be a string"):
            validate_api_key(12345)  # type: ignore

    def test_validate_api_key_wrong_prefix(self):
        """Test validate_api_key with wrong prefix"""
        with pytest.raises(ValueError, match="must start with"):
            validate_api_key("wrong-" + "x" * 32)

    def test_validate_api_key_too_short(self):
        """Test validate_api_key too short"""
        with pytest.raises(ValueError, match="too short"):
            validate_api_key("sk-sekha-short")

    def test_validate_base_url_non_string(self):
        """Test validate_base_url with non-string"""
        with pytest.raises(ValueError, match="must be a string"):
            validate_base_url(12345)  # type: ignore

    def test_validate_base_url_no_scheme(self):
        """Test validate_base_url without scheme"""
        with pytest.raises(ValueError, match="Invalid base_url"):
            validate_base_url("localhost:8080")

    def test_parse_iso_datetime_invalid(self):
        """Test parse_iso_datetime with invalid format"""
        with pytest.raises(ValueError):
            parse_iso_datetime("not-a-date")
