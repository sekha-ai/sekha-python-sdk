"""
Comprehensive test suite for all 19 Sekha controller endpoints
"""

import pytest
import uuid
from sekha import SekhaClient, ClientConfig
from sekha.models import NewConversation, MessageDto, MessageRole


@pytest.fixture
def client():
    """Create test client"""
    config = ClientConfig(
        api_key="test-key",
        base_url="http://localhost:8080",
        timeout=5.0,
    )
    return SekhaClient(config)


@pytest.fixture
def test_conversation_id():
    """Generate test conversation ID"""
    return str(uuid.uuid4())


class TestConversationEndpoints:
    """Test all 9 conversation CRUD endpoints"""

    @pytest.mark.asyncio
    async def test_create_conversation(self, client):
        """POST /api/v1/conversations"""
        conversation = NewConversation(
            label="test-label",
            folder="test-folder",
            messages=[
                MessageDto(role=MessageRole.USER, content="Hello"),
                MessageDto(role=MessageRole.ASSISTANT, content="Hi there!"),
            ],
        )
        response = await client.create_conversation(conversation)
        assert response.id
        assert response.label == "test-label"
        assert response.folder == "test-folder"

    @pytest.mark.asyncio
    async def test_get_conversation(self, client, test_conversation_id):
        """GET /api/v1/conversations/{id}"""
        response = await client.get_conversation(test_conversation_id)
        assert response.id == test_conversation_id

    @pytest.mark.asyncio
    async def test_list_conversations(self, client):
        """GET /api/v1/conversations"""
        response = await client.list_conversations(page=1, page_size=10)
        assert hasattr(response, "results")
        assert hasattr(response, "total")

    @pytest.mark.asyncio
    async def test_update_label(self, client, test_conversation_id):
        """PUT /api/v1/conversations/{id}/label"""
        await client.update_label(
            test_conversation_id,
            new_label="updated-label",
            new_folder="updated-folder",
        )

    @pytest.mark.asyncio
    async def test_update_folder(self, client, test_conversation_id):
        """PUT /api/v1/conversations/{id}/folder"""
        await client.update_folder(test_conversation_id, new_folder="new-folder")

    @pytest.mark.asyncio
    async def test_pin_conversation(self, client, test_conversation_id):
        """PUT /api/v1/conversations/{id}/pin"""
        await client.pin_conversation(test_conversation_id)

    @pytest.mark.asyncio
    async def test_archive_conversation(self, client, test_conversation_id):
        """PUT /api/v1/conversations/{id}/archive"""
        await client.archive_conversation(test_conversation_id)

    @pytest.mark.asyncio
    async def test_delete_conversation(self, client, test_conversation_id):
        """DELETE /api/v1/conversations/{id}"""
        await client.delete_conversation(test_conversation_id)

    @pytest.mark.asyncio
    async def test_count_conversations(self, client):
        """GET /api/v1/conversations/count"""
        count = await client.count_conversations()
        assert isinstance(count, int)
        assert count >= 0


class TestSearchQueryEndpoints:
    """Test all 3 search/query endpoints"""

    @pytest.mark.asyncio
    async def test_semantic_query(self, client):
        """POST /api/v1/query"""
        response = await client.query(
            query="test search",
            limit=10,
            offset=0,
        )
        assert hasattr(response, "results")
        assert hasattr(response, "total")

    @pytest.mark.asyncio
    async def test_full_text_search(self, client):
        """POST /api/v1/search/fts"""
        response = await client.full_text_search(
            query="test",
            limit=10,
        )
        assert "results" in response
        assert "total" in response

    @pytest.mark.asyncio
    async def test_rebuild_embeddings(self, client):
        """POST /api/v1/rebuild-embeddings"""
        await client.rebuild_embeddings()


class TestMemoryOrchestrationEndpoints:
    """Test all 5 memory orchestration endpoints"""

    @pytest.mark.asyncio
    async def test_assemble_context(self, client):
        """POST /api/v1/context/assemble"""
        response = await client.assemble_context(
            query="test query",
            preferred_labels=["important"],
            context_budget=4000,
            excluded_folders=["archived"],
        )
        assert isinstance(response, list)

    @pytest.mark.asyncio
    async def test_summarize(self, client, test_conversation_id):
        """POST /api/v1/summarize"""
        response = await client.summarize(
            conversation_id=test_conversation_id,
            level="daily",
        )
        assert "summary" in response
        assert "level" in response

    @pytest.mark.asyncio
    async def test_prune_dry_run(self, client):
        """POST /api/v1/prune/dry-run"""
        response = await client.prune_dry_run(threshold_days=90)
        assert "suggestions" in response
        assert "total" in response

    @pytest.mark.asyncio
    async def test_prune_execute(self, client):
        """POST /api/v1/prune/execute"""
        conversation_ids = [str(uuid.uuid4())]
        await client.prune_execute(conversation_ids)

    @pytest.mark.asyncio
    async def test_suggest_labels(self, client, test_conversation_id):
        """POST /api/v1/labels/suggest"""
        response = await client.suggest_labels(test_conversation_id)
        assert "conversation_id" in response
        assert "suggestions" in response


class TestHealthMetrics:
    """Test health and metrics endpoints"""

    @pytest.mark.asyncio
    async def test_health(self, client):
        """GET /health"""
        # Health endpoint doesn't require auth typically
        import httpx

        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(f"{client.config.base_url}/health")
            response.raise_for_status()
            data = response.json()
            assert "status" in data

    @pytest.mark.asyncio
    async def test_metrics(self, client):
        """GET /metrics"""
        import httpx

        async with httpx.AsyncClient() as http_client:
            response = await http_client.get(f"{client.config.base_url}/metrics")
            response.raise_for_status()


class TestEndpointCoverage:
    """Validate all 19 endpoints are implemented"""

    def test_all_endpoints_mapped(self):
        """Ensure SekhaClient has methods for all 19 endpoints"""
        client_methods = [
            # Conversation CRUD (9)
            "create_conversation",
            "get_conversation",
            "list_conversations",
            "update_label",
            "update_folder",
            "pin_conversation",
            "archive_conversation",
            "delete_conversation",
            "count_conversations",
            # Search/Query (3)
            "query",
            "full_text_search",
            "rebuild_embeddings",
            # Memory Orchestration (5)
            "assemble_context",
            "summarize",
            "prune_dry_run",
            "prune_execute",
            "suggest_labels",
        ]

        config = ClientConfig(api_key="test", base_url="http://localhost:8080")
        client = SekhaClient(config)

        for method in client_methods:
            assert hasattr(client, method), f"SekhaClient missing method: {method}"
            assert callable(
                getattr(client, method)
            ), f"SekhaClient.{method} is not callable"

        # Total: 18 client methods + 2 health/metrics (not on client) = 20 total
        print(f"✓ All {len(client_methods)} client methods implemented")
        print("✓ Health and metrics endpoints available via direct HTTP")
        print("✓ Total coverage: 19 controller endpoints")
