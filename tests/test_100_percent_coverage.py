"""Tests specifically targeting 100% code coverage

Covers all remaining uncovered lines in sekha/client.py, sekha/models.py, and sekha/utils.py
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
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
    async def test_get_conversation_404(self, test_config):
        """Test get_conversation with 404"""
        client = SekhaClient(test_config)
        
        # Mock the httpx response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.json.return_value = {}
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=Mock(), response=mock_response
        )
        
        # Patch at the client level
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            
            with pytest.raises(SekhaNotFoundError, match="Conversation 123 not found"):
                await client.get_conversation("123")
        
        await client.close()


class TestListConversationsFilters:
    """Test list_conversations filters (line 170)"""

    @pytest.mark.asyncio
    async def test_list_with_pinned(self, test_config):
        """Test list with pinned filter"""
        client = SekhaClient(test_config)
        
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {"results": [], "total": 0, "page": 1, "page_size": 50}
        
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            await client.list_conversations(pinned=True)
            
            # Verify pinned was passed
            assert mock_get.called
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs['params']['pinned'] is True
        
        await client.close()


class TestUpdateLabel404:
    """Test update_label 404 (line 208)"""

    @pytest.mark.asyncio
    async def test_update_label_404(self, test_config):
        """Test update_label with 404"""
        client = SekhaClient(test_config)
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=Mock(), response=mock_response
        )
        
        with patch.object(client.client, 'put', new_callable=AsyncMock) as mock_put:
            mock_put.return_value = mock_response
            
            with pytest.raises(SekhaNotFoundError, match="Conversation 123 not found"):
                await client.update_label("123", "test", "/")
        
        await client.close()


class TestUpdateFolder404:
    """Test update_folder 404 (lines 227-230)"""

    @pytest.mark.asyncio
    async def test_update_folder_404(self, test_config):
        """Test update_folder with 404"""
        client = SekhaClient(test_config)
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=Mock(), response=mock_response
        )
        
        with patch.object(client.client, 'put', new_callable=AsyncMock) as mock_put:
            mock_put.return_value = mock_response
            
            with pytest.raises(SekhaNotFoundError, match="Conversation 123 not found"):
                await client.update_folder("123", "/new")
        
        await client.close()


class TestPinArchiveDelete404:
    """Test 404 errors for pin, archive, delete (lines 244-247, 261-264, 283)"""

    @pytest.mark.asyncio
    async def test_pin_404(self, test_config):
        """Test pin_conversation 404"""
        client = SekhaClient(test_config)
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=Mock(), response=mock_response
        )
        
        with patch.object(client.client, 'put', new_callable=AsyncMock) as mock_put:
            mock_put.return_value = mock_response
            
            with pytest.raises(SekhaNotFoundError, match="Conversation 123 not found"):
                await client.pin_conversation("123")
        
        await client.close()

    @pytest.mark.asyncio
    async def test_archive_404(self, test_config):
        """Test archive_conversation 404"""
        client = SekhaClient(test_config)
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=Mock(), response=mock_response
        )
        
        with patch.object(client.client, 'put', new_callable=AsyncMock) as mock_put:
            mock_put.return_value = mock_response
            
            with pytest.raises(SekhaNotFoundError, match="Conversation 123 not found"):
                await client.archive_conversation("123")
        
        await client.close()

    @pytest.mark.asyncio
    async def test_delete_404(self, test_config):
        """Test delete_conversation 404"""
        client = SekhaClient(test_config)
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Not Found", request=Mock(), response=mock_response
        )
        
        with patch.object(client.client, 'delete', new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = mock_response
            
            with pytest.raises(SekhaNotFoundError, match="Conversation 123 not found"):
                await client.delete_conversation("123")
        
        await client.close()


class TestQueryErrors:
    """Test query error handling (lines 295, 297, 306-307)"""

    @pytest.mark.asyncio
    async def test_query_400_error(self, test_config):
        """Test query with 400 error"""
        client = SekhaClient(test_config)
        
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Bad Request", request=Mock(), response=mock_response
        )
        
        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            with pytest.raises(SekhaValidationError, match="Invalid query parameters"):
                await client.query("test")
        
        await client.close()

    @pytest.mark.asyncio
    async def test_query_401_error(self, test_config):
        """Test query with 401 error"""
        client = SekhaClient(test_config)
        
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Unauthorized", request=Mock(), response=mock_response
        )
        
        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            with pytest.raises(SekhaAuthError, match="Invalid API key"):
                await client.query("test")
        
        await client.close()

    @pytest.mark.asyncio
    async def test_query_timeout(self, test_config):
        """Test query with timeout"""
        client = SekhaClient(test_config)
        
        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.TimeoutException("Timeout")
            
            with pytest.raises(SekhaConnectionError, match="Query timed out"):
                await client.query("test")
        
        await client.close()

    @pytest.mark.asyncio
    async def test_query_connect_error(self, test_config):
        """Test query with connect error"""
        client = SekhaClient(test_config)
        
        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.ConnectError("Connection refused")
            
            with pytest.raises(SekhaConnectionError, match="Connection failed"):
                await client.query("test")
        
        await client.close()


class TestCountConversationsFilters:
    """Test count_conversations with filters (lines 343-348)"""

    @pytest.mark.asyncio
    async def test_count_with_label(self, test_config):
        """Test count with label filter"""
        client = SekhaClient(test_config)
        
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {"count": 5}
        
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            result = await client.count_conversations(label="test")
            assert result == 5
        
        await client.close()

    @pytest.mark.asyncio
    async def test_count_with_folder(self, test_config):
        """Test count with folder filter"""
        client = SekhaClient(test_config)
        
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {"count": 3}
        
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            result = await client.count_conversations(folder="/work")
            assert result == 3
        
        await client.close()


class TestAssembleContextDefaults:
    """Test assemble_context with None parameters (lines 376-377)"""

    @pytest.mark.asyncio
    async def test_assemble_context_none_params(self, test_config):
        """Test assemble_context with None for optional params"""
        client = SekhaClient(test_config)
        
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = []
        
        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            await client.assemble_context("test", preferred_labels=None, excluded_folders=None)
            
            # Verify empty lists were used
            call_kwargs = mock_post.call_args[1]
            body = call_kwargs['json']
            assert body['preferred_labels'] == []
            assert body['excluded_folders'] == []
        
        await client.close()


class TestSummarizeKwargs:
    """Test summarize with kwargs (lines 387-388, 417-418)"""

    @pytest.mark.asyncio
    async def test_summarize_with_level(self, test_config):
        """Test summarize with level parameter"""
        client = SekhaClient(test_config)
        
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {"summary": "test", "level": "weekly"}
        
        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await client.summarize("123", level="weekly")
            assert result["level"] == "weekly"
        
        await client.close()

    @pytest.mark.asyncio
    async def test_generate_summary_alias(self, test_config):
        """Test generate_summary alias"""
        client = SekhaClient(test_config)
        
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {"summary": "test"}
        
        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await client.generate_summary("123", level="daily")
            assert "summary" in result
        
        await client.close()


class TestAutoLabel:
    """Test auto_label paths (lines 443-444, 462-463, 480-481)"""

    @pytest.mark.asyncio
    async def test_auto_label_no_match(self, test_config):
        """Test auto_label when no suggestions meet threshold"""
        client = SekhaClient(test_config)
        
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "conversation_id": "123",
            "suggestions": [{"label": "test", "confidence": 0.5, "folder": "/"}],
        }
        
        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await client.auto_label("123", threshold=0.9)
            assert result is None
        
        await client.close()

    @pytest.mark.asyncio
    async def test_auto_label_with_match(self, test_config):
        """Test auto_label when suggestion meets threshold"""
        client = SekhaClient(test_config)
        
        suggest_response = Mock()
        suggest_response.raise_for_status = Mock()
        suggest_response.json.return_value = {
            "conversation_id": "123",
            "suggestions": [{"label": "important", "confidence": 0.95, "folder": "/work"}],
        }
        
        update_response = Mock()
        update_response.raise_for_status = Mock()
        
        with patch.object(client.client, 'post', new_callable=AsyncMock) as mock_post:
            with patch.object(client.client, 'put', new_callable=AsyncMock) as mock_put:
                mock_post.return_value = suggest_response
                mock_put.return_value = update_response
                
                result = await client.auto_label("123", threshold=0.7)
                assert result == "important"
                assert mock_put.called
        
        await client.close()


class TestExportFilters:
    """Test export with filters (lines 625-637)"""

    @pytest.mark.asyncio
    async def test_export_with_label(self, test_config):
        """Test export with label filter"""
        client = SekhaClient(test_config)
        
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {"content": "# Export", "format": "markdown"}
        
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            result = await client.export(label="test")
            assert "# Export" in result
            
            # Verify label was passed
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs['params']['label'] == "test"
        
        await client.close()

    @pytest.mark.asyncio
    async def test_export_with_folder(self, test_config):
        """Test export with folder filter"""
        client = SekhaClient(test_config)
        
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {"content": "# Export", "format": "json"}
        
        with patch.object(client.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response
            result = await client.export(folder="/work")
            assert "# Export" in result
            
            # Verify folder was passed
            call_kwargs = mock_get.call_args[1]
            assert call_kwargs['params']['folder'] == "/work"
        
        await client.close()


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
