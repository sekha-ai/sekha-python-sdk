"""Tests for TypedDict models"""

from datetime import datetime
from sekha.types import (
    MessageRole,
    ConversationStatus,
    Message,
    SearchResult,
    QueryRequest,
    QueryResponse,
)


class TestMessage:
    def test_valid_message(self):
        msg: Message = {"role": "user", "content": "Hello"}
        assert msg["role"] == "user"
        assert msg["content"] == "Hello"

    def test_message_with_metadata(self):
        msg: Message = {
            "role": "assistant",
            "content": "Response",
            "metadata": {"confidence": 0.9},
        }
        assert msg["metadata"]["confidence"] == 0.9

    def test_message_role_enum(self):
        assert MessageRole.USER == "user"
        assert MessageRole.ASSISTANT == "assistant"
        assert MessageRole.SYSTEM == "system"


class TestSearchResult:
    def test_result_creation(self):
        dt = datetime.now()
        result: SearchResult = {
            "conversation_id": "conv-456",
            "score": 0.85,
            "content": "Important message",
            "label": "Project:AI",
            "folder": "/work",
            "created_at": dt,
        }
        assert result["score"] == 0.85
        assert result["conversation_id"] == "conv-456"


class TestQueryRequest:
    def test_basic_query(self):
        req: QueryRequest = {"query": "token limits"}
        assert req["query"] == "token limits"

    def test_query_with_limit(self):
        req: QueryRequest = {"query": "auth patterns", "limit": 50}
        assert req["limit"] == 50

    def test_query_with_filters(self):
        req: QueryRequest = {
            "query": "test",
            "filters": {"label": "Project:AI", "folder": "/work"},
        }
        assert req["filters"]["label"] == "Project:AI"


class TestQueryResponse:
    def test_response_structure(self):
        response: QueryResponse = {
            "results": [],
            "total": 0,
            "query": "test",
        }
        assert response["total"] == 0
        assert response["query"] == "test"
        assert isinstance(response["results"], list)


class TestConversationStatus:
    def test_status_values(self):
        assert ConversationStatus.ACTIVE == "active"
        assert ConversationStatus.ARCHIVED == "archived"
        assert ConversationStatus.PINNED == "pinned"
