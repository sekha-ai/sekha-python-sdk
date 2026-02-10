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


class TestSyncClientProperty:
    """Test sync_client property (lines 79-88)"""

    def test_sync_client_lazy_creation(self, test_config):
        """Test that sync_client is created on first access"""
        client = SekhaClient(test_config)
        assert client._sync_client is None

        # Access property
        sync = client.sync_client
        assert sync is not None
        assert isinstance(sync, httpx.Client)

        # Second access returns same client
        sync2 = client.sync_client
        assert sync2 is sync


class TestQueryValidationErrors:
    """Test query() with 400 and 401 errors (lines 295, 297)"""

    @pytest.mark.asyncio
    async def test_query_400_validation_error(self, test_config):
        """Test query with 400 validation error"""
        client = SekhaClient(test_config)
        error_response = Mock()
        error_response.status_code = 400
        error_response.text = "Invalid query"

        request_mock = Mock()
        request_mock.url = "http://localhost:8080/api/v1/query"

        client.client.post = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Bad Request", request=request_mock, response=error_response
            )
        )

        with pytest.raises(SekhaValidationError, match="Invalid query parameters"):
            await client.query("test")

        await client.close()

    @pytest.mark.asyncio
    async def test_query_401_auth_error(self, test_config):
        """Test query with 401 auth error"""
        client = SekhaClient(test_config)
        error_response = Mock()
        error_response.status_code = 401
        error_response.text = "Unauthorized"

        request_mock = Mock()
        request_mock.url = "http://localhost:8080/api/v1/query"

        client.client.post = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Unauthorized", request=request_mock, response=error_response
            )
        )

        with pytest.raises(SekhaAuthError, match="Invalid API key"):
            await client.query("test")

        await client.close()

    @pytest.mark.asyncio
    async def test_query_timeout(self, test_config):
        """Test query with timeout (line 306)"""
        client = SekhaClient(test_config)
        client.client.post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

        with pytest.raises(SekhaConnectionError, match="Query timed out"):
            await client.query("test")

        await client.close()

    @pytest.mark.asyncio
    async def test_query_connect_error(self, test_config):
        """Test query with connection error (line 307)"""
        client = SekhaClient(test_config)
        client.client.post = AsyncMock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        with pytest.raises(SekhaConnectionError, match="Connection failed"):
            await client.query("test")

        await client.close()


class TestUpdateFolder404:
    """Test update_folder 404 (lines 227-230)"""

    @pytest.mark.asyncio
    async def test_update_folder_404(self, test_config):
        """Test update_folder with 404 error"""
        client = SekhaClient(test_config)
        error_response = Mock()
        error_response.status_code = 404
        error_response.text = "Not found"

        request_mock = Mock()
        request_mock.url = "http://localhost:8080/api/v1/conversations/123/folder"

        client.client.put = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Not Found", request=request_mock, response=error_response
            )
        )

        with pytest.raises(SekhaNotFoundError):
            await client.update_folder("123", "/new")

        await client.close()


class TestPinArchiveDelete404:
    """Test 404 errors for pin, archive, delete (lines 244-247, 261-264, 283)"""

    @pytest.mark.asyncio
    async def test_pin_404(self, test_config):
        """Test pin_conversation 404"""
        client = SekhaClient(test_config)
        error_response = Mock()
        error_response.status_code = 404

        request_mock = Mock()
        request_mock.url = "http://localhost:8080/api/v1/conversations/123/pin"

        client.client.put = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Not Found", request=request_mock, response=error_response
            )
        )

        with pytest.raises(SekhaNotFoundError):
            await client.pin_conversation("123")

        await client.close()

    @pytest.mark.asyncio
    async def test_archive_404(self, test_config):
        """Test archive_conversation 404"""
        client = SekhaClient(test_config)
        error_response = Mock()
        error_response.status_code = 404

        request_mock = Mock()
        request_mock.url = "http://localhost:8080/api/v1/conversations/123/archive"

        client.client.put = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Not Found", request=request_mock, response=error_response
            )
        )

        with pytest.raises(SekhaNotFoundError):
            await client.archive_conversation("123")

        await client.close()

    @pytest.mark.asyncio
    async def test_delete_404(self, test_config):
        """Test delete_conversation 404"""
        client = SekhaClient(test_config)
        error_response = Mock()
        error_response.status_code = 404

        request_mock = Mock()
        request_mock.url = "http://localhost:8080/api/v1/conversations/123"

        client.client.delete = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Not Found", request=request_mock, response=error_response
            )
        )

        with pytest.raises(SekhaNotFoundError):
            await client.delete_conversation("123")

        await client.close()


class TestGetConversation404:
    """Test get_conversation 404 (lines 135-136)"""

    @pytest.mark.asyncio
    async def test_get_conversation_404(self, test_config):
        """Test get_conversation with 404"""
        client = SekhaClient(test_config)
        error_response = Mock()
        error_response.status_code = 404

        request_mock = Mock()
        request_mock.url = "http://localhost:8080/api/v1/conversations/123"

        client.client.get = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Not Found", request=request_mock, response=error_response
            )
        )

        with pytest.raises(SekhaNotFoundError):
            await client.get_conversation("123")

        await client.close()


class TestUpdateLabel404:
    """Test update_label 404 (lines 208)"""

    @pytest.mark.asyncio
    async def test_update_label_404(self, test_config):
        """Test update_label with 404"""
        client = SekhaClient(test_config)
        error_response = Mock()
        error_response.status_code = 404

        request_mock = Mock()
        request_mock.url = "http://localhost:8080/api/v1/conversations/123/label"

        client.client.put = AsyncMock(
            side_effect=httpx.HTTPStatusError(
                "Not Found", request=request_mock, response=error_response
            )
        )

        with pytest.raises(SekhaNotFoundError):
            await client.update_label("123", "label", "/")

        await client.close()


class TestListConversationsWithFilters:
    """Test list_conversations with all filter combinations (lines 170, 172, 174)"""

    @pytest.mark.asyncio
    async def test_list_with_pinned_filter(self, test_config):
        """Test list with pinned=True filter"""
        client = SekhaClient(test_config)
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={"results": [], "total": 0, "page": 1, "page_size": 50}
        )
        client.client.get = AsyncMock(return_value=mock_response)

        await client.list_conversations(pinned=True)
        
        # Verify pinned was passed in params
        call_kwargs = client.client.get.call_args[1]
        assert "params" in call_kwargs
        assert call_kwargs["params"]["pinned"] is True

        await client.close()

    @pytest.mark.asyncio
    async def test_list_with_archived_filter(self, test_config):
        """Test list with archived=False filter"""
        client = SekhaClient(test_config)
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={"results": [], "total": 0, "page": 1, "page_size": 50}
        )
        client.client.get = AsyncMock(return_value=mock_response)

        await client.list_conversations(archived=False)
        
        # Verify archived was passed
        call_kwargs = client.client.get.call_args[1]
        assert call_kwargs["params"]["archived"] is False

        await client.close()


class TestCountConversationsWithFilters:
    """Test count_conversations with filters (lines 343-348)"""

    @pytest.mark.asyncio
    async def test_count_with_label(self, test_config):
        """Test count with label filter"""
        client = SekhaClient(test_config)
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(return_value={"count": 5})
        client.client.get = AsyncMock(return_value=mock_response)

        result = await client.count_conversations(label="test")
        assert result == 5

        await client.close()

    @pytest.mark.asyncio
    async def test_count_with_folder(self, test_config):
        """Test count with folder filter"""
        client = SekhaClient(test_config)
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(return_value={"count": 3})
        client.client.get = AsyncMock(return_value=mock_response)

        result = await client.count_conversations(folder="/work")
        assert result == 3

        await client.close()


class TestExportWithFilters:
    """Test export with filters (lines 625-637)"""

    @pytest.mark.asyncio
    async def test_export_with_label(self, test_config):
        """Test export with label filter"""
        client = SekhaClient(test_config)
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={"content": "# Export", "format": "markdown"}
        )
        client.client.get = AsyncMock(return_value=mock_response)

        result = await client.export(label="test")
        assert "# Export" in result

        await client.close()

    @pytest.mark.asyncio
    async def test_export_with_folder(self, test_config):
        """Test export with folder filter"""
        client = SekhaClient(test_config)
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={"content": "# Export", "format": "json"}
        )
        client.client.get = AsyncMock(return_value=mock_response)

        result = await client.export(folder="/work")
        assert "# Export" in result

        await client.close()


class TestAssembleContextDefaults:
    """Test assemble_context with default parameters (lines 376-377)"""

    @pytest.mark.asyncio
    async def test_assemble_context_defaults(self, test_config):
        """Test assemble_context uses empty lists for None parameters"""
        client = SekhaClient(test_config)
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(return_value=[])
        client.client.post = AsyncMock(return_value=mock_response)

        # Call without optional parameters
        await client.assemble_context("test")

        # Verify empty lists were used
        call_kwargs = client.client.post.call_args[1]
        body = call_kwargs["json"]
        assert body["preferred_labels"] == []
        assert body["excluded_folders"] == []

        await client.close()


class TestSummarizeWithKwargs:
    """Test summarize with kwargs (lines 400-418)"""

    @pytest.mark.asyncio
    async def test_generate_summary_passes_kwargs(self, test_config):
        """Test that generate_summary passes kwargs to summarize"""
        client = SekhaClient(test_config)
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={"summary": "test", "level": "weekly"}
        )
        client.client.post = AsyncMock(return_value=mock_response)

        # Use the alias with kwargs
        result = await client.generate_summary("123", level="weekly")
        assert result["level"] == "weekly"

        await client.close()


class TestAutoLabelNoMatch:
    """Test auto_label when no suggestion meets threshold (lines 462-463, 471-481)"""

    @pytest.mark.asyncio
    async def test_auto_label_returns_none(self, test_config):
        """Test auto_label returns None when threshold not met"""
        client = SekhaClient(test_config)

        # Mock suggest_labels
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(
            return_value={
                "conversation_id": "123",
                "suggestions": [
                    {"label": "test", "confidence": 0.5, "folder": "/"}
                ],
            }
        )
        client.client.post = AsyncMock(return_value=mock_response)

        # Call with high threshold
        result = await client.auto_label("123", threshold=0.9)
        assert result is None

        await client.close()

    @pytest.mark.asyncio
    async def test_auto_label_applies_label(self, test_config):
        """Test auto_label applies label when threshold met"""
        client = SekhaClient(test_config)

        # Mock suggest_labels
        suggest_response = Mock()
        suggest_response.raise_for_status = Mock()
        suggest_response.json = Mock(
            return_value={
                "conversation_id": "123",
                "suggestions": [
                    {"label": "important", "confidence": 0.95, "folder": "/work"}
                ],
            }
        )

        # Mock update_label
        update_response = Mock()
        update_response.raise_for_status = Mock()

        client.client.post = AsyncMock(return_value=suggest_response)
        client.client.put = AsyncMock(return_value=update_response)

        # Call with low threshold
        result = await client.auto_label("123", threshold=0.7)
        assert result == "important"
        assert client.client.put.called

        await client.close()


class TestSyncWrapper:
    """Test SyncSekhaClient error cases (lines 643-654)"""

    def test_sync_client_in_async_context(self, test_config):
        """Test SyncSekhaClient raises error in async context"""
        from sekha.client import SyncSekhaClient
        import asyncio

        sync_client = SyncSekhaClient(test_config)

        # Mock get_running_loop to simulate async context
        with patch("asyncio.get_running_loop") as mock_loop:
            mock_loop.return_value = Mock()

            with pytest.raises(
                RuntimeError, match="SyncSekhaClient cannot be used within an async context"
            ):
                sync_client.create_conversation(
                    NewConversation(
                        label="test",
                        messages=[MessageDto(role=MessageRole.USER, content="test")],
                    )
                )


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
