"""Tests for SekhaClient unified workflow methods

These tests verify that the convenience methods properly coordinate
between Controller, MCP, and Bridge clients.
"""

import pytest
from unittest.mock import AsyncMock, patch, Mock

from sekha.unified import SekhaClient
from sekha.errors import SekhaAPIError, SekhaConnectionError


class TestStoreAndQuery:
    """Test store_and_query workflow"""

    @pytest.mark.asyncio
    async def test_store_and_query_basic(self):
        """Test basic store and query workflow"""
        client = SekhaClient(
            controller_url="http://localhost:8080",
            api_key="sk-test-key-12345678901234567890",
            bridge_url="http://localhost:5001",
        )

        # Mock conversation object
        mock_conversation = Mock(
            id="conv-123",
            label="Engineering",
            folder="/",
            message_count=2,
        )

        # Mock query results
        mock_results = Mock(
            total=3,
            results=[
                Mock(id="conv-1", label="Engineering", score=0.92),
                Mock(id="conv-2", label="Engineering", score=0.87),
                Mock(id="conv-3", label="Product", score=0.81),
            ],
        )

        with patch.object(
            client.controller, "create_conversation", new_callable=AsyncMock
        ) as mock_create:
            with patch.object(
                client.controller, "query", new_callable=AsyncMock
            ) as mock_query:
                mock_create.return_value = mock_conversation
                mock_query.return_value = mock_results

                result = await client.store_and_query(
                    messages=[
                        {"role": "user", "content": "What is TypeScript?"},
                        {
                            "role": "assistant",
                            "content": "TypeScript is a typed superset of JavaScript.",
                        },
                    ],
                    query="TypeScript",
                    label="Engineering",
                    folder="/docs",
                )

                # Verify both operations were called
                assert mock_create.called
                assert mock_query.called

                # Verify result structure
                assert "conversation" in result
                assert "results" in result
                assert result["conversation"] == mock_conversation
                assert result["results"] == mock_results

    @pytest.mark.asyncio
    async def test_store_and_query_with_default_label(self):
        """Test store and query with default label"""
        client = SekhaClient(
            controller_url="http://localhost:8080",
            api_key="sk-test-key-12345678901234567890",
            bridge_url="http://localhost:5001",
            default_label="DefaultLabel",
        )

        mock_conversation = Mock(id="conv-123")
        mock_results = Mock(total=0, results=[])

        with patch.object(
            client.controller, "create_conversation", new_callable=AsyncMock
        ) as mock_create:
            with patch.object(
                client.controller, "query", new_callable=AsyncMock
            ) as mock_query:
                mock_create.return_value = mock_conversation
                mock_query.return_value = mock_results

                await client.store_and_query(
                    messages=[{"role": "user", "content": "Test"}],
                    query="test query",
                )

                # Verify create was called with default label
                assert mock_create.called


class TestCompleteWithContext:
    """Test complete_with_context workflow"""

    @pytest.mark.asyncio
    async def test_complete_with_context_basic(self):
        """Test basic completion with context"""
        client = SekhaClient(
            controller_url="http://localhost:8080",
            api_key="sk-test-key-12345678901234567890",
            bridge_url="http://localhost:5001",
        )

        # Mock assembled context
        mock_context = {
            "messages": [
                {"role": "user", "content": "Previous question about TypeScript"},
                {"role": "assistant", "content": "TypeScript is typed JavaScript"},
            ],
            "total_tokens": 150,
        }

        # Mock completion response
        mock_completion = {
            "choices": [
                {"message": {"role": "assistant", "content": "Based on context..."}}
            ],
            "usage": {"total_tokens": 250},
        }

        with patch.object(
            client.controller, "assemble_context", new_callable=AsyncMock
        ) as mock_assemble:
            with patch.object(
                client.bridge, "complete", new_callable=AsyncMock
            ) as mock_complete:
                mock_assemble.return_value = mock_context
                mock_complete.return_value = mock_completion

                result = await client.complete_with_context(
                    prompt="Explain TypeScript interfaces",
                    context_query="TypeScript",
                    context_budget=4000,
                    preferred_labels=["Engineering"],
                    model="llama3.1:8b",
                    temperature=0.7,
                )

                # Verify both services were called
                assert mock_assemble.called
                assert mock_complete.called

                # Verify result includes both completion and context
                assert "choices" in result
                assert "context" in result
                assert result["context"] == mock_context

                # Verify assemble_context was called with correct params
                call_args = mock_assemble.call_args
                assert call_args[1]["query"] == "TypeScript"
                assert call_args[1]["context_budget"] == 4000
                assert call_args[1]["preferred_labels"] == ["Engineering"]

                # Verify bridge.complete was called with messages including context
                call_args = mock_complete.call_args
                messages = call_args[1]["messages"]
                assert len(messages) > 2  # System + context + user
                assert messages[-1]["content"] == "Explain TypeScript interfaces"

    @pytest.mark.asyncio
    async def test_complete_with_context_error_handling(self):
        """Test error handling in complete_with_context"""
        client = SekhaClient(
            controller_url="http://localhost:8080",
            api_key="sk-test-key-12345678901234567890",
            bridge_url="http://localhost:5001",
        )

        with patch.object(
            client.controller, "assemble_context", new_callable=AsyncMock
        ) as mock_assemble:
            mock_assemble.side_effect = SekhaConnectionError("Connection failed")

            with pytest.raises(SekhaConnectionError):
                await client.complete_with_context(
                    prompt="Test", context_query="test"
                )


class TestCompleteWithMemory:
    """Test complete_with_memory workflow"""

    @pytest.mark.asyncio
    async def test_complete_with_memory_basic(self):
        """Test basic completion with memory search"""
        client = SekhaClient(
            controller_url="http://localhost:8080",
            api_key="sk-test-key-12345678901234567890",
            bridge_url="http://localhost:5001",
        )

        # Mock search results
        mock_search_results = Mock(
            total=2,
            results=[
                Mock(
                    label="Engineering",
                    content="TypeScript is typed JavaScript",
                    score=0.92,
                ),
                Mock(
                    label="Engineering",
                    content="Interfaces define object shapes",
                    score=0.87,
                ),
            ],
        )

        # Mock completion
        mock_completion = {
            "choices": [{"message": {"role": "assistant", "content": "Summary..."}}],
            "usage": {"total_tokens": 300},
        }

        with patch.object(
            client.controller, "query", new_callable=AsyncMock
        ) as mock_query:
            with patch.object(
                client.bridge, "complete", new_callable=AsyncMock
            ) as mock_complete:
                mock_query.return_value = mock_search_results
                mock_complete.return_value = mock_completion

                result = await client.complete_with_memory(
                    prompt="Summarize what we learned about TypeScript",
                    search_query="TypeScript",
                    limit=5,
                    labels=["Engineering"],
                    model="llama3.1:8b",
                    temperature=0.5,
                )

                # Verify both services were called
                assert mock_query.called
                assert mock_complete.called

                # Verify result includes completion and search results
                assert "choices" in result
                assert "search_results" in result
                assert result["search_results"] == mock_search_results

                # Verify query was called with correct params
                call_args = mock_query.call_args
                assert call_args[1]["query"] == "TypeScript"
                assert call_args[1]["limit"] == 5
                assert call_args[1]["filters"] == {"labels": ["Engineering"]}

    @pytest.mark.asyncio
    async def test_complete_with_memory_empty_results(self):
        """Test completion with empty search results"""
        client = SekhaClient(
            controller_url="http://localhost:8080",
            api_key="sk-test-key-12345678901234567890",
            bridge_url="http://localhost:5001",
        )

        mock_search_results = Mock(total=0, results=[])
        mock_completion = {
            "choices": [{"message": {"role": "assistant", "content": "No context"}}]
        }

        with patch.object(
            client.controller, "query", new_callable=AsyncMock
        ) as mock_query:
            with patch.object(
                client.bridge, "complete", new_callable=AsyncMock
            ) as mock_complete:
                mock_query.return_value = mock_search_results
                mock_complete.return_value = mock_completion

                result = await client.complete_with_memory(
                    prompt="Test", search_query="nonexistent"
                )

                # Should still complete even with no results
                assert "choices" in result
                assert result["search_results"].total == 0


class TestStreamWithContext:
    """Test stream_with_context workflow"""

    @pytest.mark.asyncio
    async def test_stream_with_context_basic(self):
        """Test streaming completion with context"""
        client = SekhaClient(
            controller_url="http://localhost:8080",
            api_key="sk-test-key-12345678901234567890",
            bridge_url="http://localhost:5001",
        )

        # Mock context
        mock_context = {
            "messages": [
                {"role": "user", "content": "Context message"},
                {"role": "assistant", "content": "Context response"},
            ]
        }

        # Mock streaming chunks
        async def mock_stream_generator():
            chunks = [
                {"choices": [{"delta": {"content": "Hello"}}]},
                {"choices": [{"delta": {"content": " world"}}]},
                {"choices": [{"delta": {"content": "!"}}]},
            ]
            for chunk in chunks:
                yield chunk

        with patch.object(
            client.controller, "assemble_context", new_callable=AsyncMock
        ) as mock_assemble:
            with patch.object(
                client.bridge, "stream_complete", new_callable=AsyncMock
            ) as mock_stream:
                mock_assemble.return_value = mock_context
                mock_stream.return_value = mock_stream_generator()

                chunks = []
                async for chunk in client.stream_with_context(
                    prompt="Tell me a story",
                    context_query="stories",
                    context_budget=3000,
                    model="llama3.1:8b",
                ):
                    chunks.append(chunk)

                # Verify both services were called
                assert mock_assemble.called
                assert mock_stream.called

                # Verify we got streaming chunks
                assert len(chunks) == 3
                assert chunks[0]["choices"][0]["delta"]["content"] == "Hello"

    @pytest.mark.asyncio
    async def test_stream_with_context_error(self):
        """Test error handling in streaming"""
        client = SekhaClient(
            controller_url="http://localhost:8080",
            api_key="sk-test-key-12345678901234567890",
            bridge_url="http://localhost:5001",
        )

        mock_context = {"messages": []}

        with patch.object(
            client.controller, "assemble_context", new_callable=AsyncMock
        ) as mock_assemble:
            with patch.object(
                client.bridge, "stream_complete", new_callable=AsyncMock
            ) as mock_stream:
                mock_assemble.return_value = mock_context
                mock_stream.side_effect = SekhaAPIError(
                    "Stream failed", status_code=500
                )

                with pytest.raises(SekhaAPIError):
                    async for _ in client.stream_with_context(
                        prompt="Test", context_query="test"
                    ):
                        pass


class TestHealthCheck:
    """Test health_check workflow"""

    @pytest.mark.asyncio
    async def test_health_check_all_healthy(self):
        """Test health check when all services are healthy"""
        client = SekhaClient(
            controller_url="http://localhost:8080",
            api_key="sk-test-key-12345678901234567890",
            bridge_url="http://localhost:5001",
        )

        # Mock controller response
        mock_controller_response = Mock()
        mock_controller_response.json.return_value = {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2026-02-13T20:00:00Z",
        }

        # Mock bridge response
        mock_bridge_health = {
            "status": "healthy",
            "provider": "ollama",
            "models_loaded": ["llama3.1:8b"],
        }

        with patch.object(
            client.controller.client, "get", new_callable=AsyncMock
        ) as mock_controller_health:
            with patch.object(
                client.bridge, "health", new_callable=AsyncMock
            ) as mock_bridge:
                mock_controller_health.return_value = mock_controller_response
                mock_bridge.return_value = mock_bridge_health

                result = await client.health_check()

                # Verify both health checks were called
                assert mock_controller_health.called
                assert mock_bridge.called

                # Verify result structure
                assert "controller" in result
                assert "bridge" in result
                assert result["controller"]["status"] == "healthy"
                assert result["bridge"]["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_check_controller_unhealthy(self):
        """Test health check when controller is unhealthy"""
        client = SekhaClient(
            controller_url="http://localhost:8080",
            api_key="sk-test-key-12345678901234567890",
            bridge_url="http://localhost:5001",
        )

        mock_bridge_health = {"status": "healthy"}

        with patch.object(
            client.controller.client, "get", new_callable=AsyncMock
        ) as mock_controller_health:
            with patch.object(
                client.bridge, "health", new_callable=AsyncMock
            ) as mock_bridge:
                mock_controller_health.side_effect = Exception("Connection refused")
                mock_bridge.return_value = mock_bridge_health

                result = await client.health_check()

                # Controller should show unhealthy
                assert result["controller"]["status"] == "unhealthy"
                assert "error" in result["controller"]

                # Bridge should still be healthy
                assert result["bridge"]["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_check_bridge_unhealthy(self):
        """Test health check when bridge is unhealthy"""
        client = SekhaClient(
            controller_url="http://localhost:8080",
            api_key="sk-test-key-12345678901234567890",
            bridge_url="http://localhost:5001",
        )

        mock_controller_response = Mock()
        mock_controller_response.json.return_value = {"status": "healthy"}

        with patch.object(
            client.controller.client, "get", new_callable=AsyncMock
        ) as mock_controller_health:
            with patch.object(
                client.bridge, "health", new_callable=AsyncMock
            ) as mock_bridge:
                mock_controller_health.return_value = mock_controller_response
                mock_bridge.side_effect = SekhaConnectionError("Bridge unavailable")

                result = await client.health_check()

                # Controller should be healthy
                assert result["controller"]["status"] == "healthy"

                # Bridge should show unhealthy
                assert result["bridge"]["status"] == "unhealthy"
                assert "error" in result["bridge"]

    @pytest.mark.asyncio
    async def test_health_check_both_unhealthy(self):
        """Test health check when both services are unhealthy"""
        client = SekhaClient(
            controller_url="http://localhost:8080",
            api_key="sk-test-key-12345678901234567890",
            bridge_url="http://localhost:5001",
        )

        with patch.object(
            client.controller.client, "get", new_callable=AsyncMock
        ) as mock_controller_health:
            with patch.object(
                client.bridge, "health", new_callable=AsyncMock
            ) as mock_bridge:
                mock_controller_health.side_effect = Exception("Controller down")
                mock_bridge.side_effect = Exception("Bridge down")

                result = await client.health_check()

                # Both should show unhealthy
                assert result["controller"]["status"] == "unhealthy"
                assert result["bridge"]["status"] == "unhealthy"


class TestWorkflowIntegration:
    """Test integration scenarios"""

    @pytest.mark.asyncio
    async def test_workflow_with_custom_config(self):
        """Test workflows respect custom configuration"""
        client = SekhaClient(
            controller_url="http://localhost:8080",
            api_key="sk-test-key-12345678901234567890",
            bridge_url="http://localhost:5001",
            timeout=60.0,
            max_retries=5,
        )

        # Verify config propagated to sub-clients
        assert client.controller.config.timeout == 60.0
        assert client.controller.config.max_retries == 5
        assert client.bridge.timeout == 60.0
        assert client.bridge.max_retries == 5

    @pytest.mark.asyncio
    async def test_multiple_workflows_in_sequence(self):
        """Test running multiple workflows in sequence"""
        client = SekhaClient(
            controller_url="http://localhost:8080",
            api_key="sk-test-key-12345678901234567890",
            bridge_url="http://localhost:5001",
        )

        # Mock all dependencies
        with patch.object(
            client.controller, "create_conversation", new_callable=AsyncMock
        ) as mock_create:
            with patch.object(
                client.controller, "query", new_callable=AsyncMock
            ) as mock_query:
                with patch.object(
                    client.bridge, "complete", new_callable=AsyncMock
                ) as mock_complete:
                    mock_create.return_value = Mock(id="conv-123")
                    mock_query.return_value = Mock(total=1, results=[Mock()])
                    mock_completion = {"choices": [{"message": {"content": "test"}}]}
                    mock_complete.return_value = mock_completion

                    # Run store_and_query
                    result1 = await client.store_and_query(
                        messages=[{"role": "user", "content": "Test"}],
                        query="test",
                    )

                    # Run complete_with_memory
                    result2 = await client.complete_with_memory(
                        prompt="Test prompt", search_query="test"
                    )

                    # Both should succeed
                    assert "conversation" in result1
                    assert "choices" in result2
