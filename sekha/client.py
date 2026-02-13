"""Main client for interacting with Sekha API"""

import asyncio
import httpx
from typing import Optional, List, Dict, Any, Union
import backoff

# Explicit imports instead of wildcard
from .errors import (
    SekhaError,
    SekhaAPIError,
    SekhaAuthError,
    SekhaConnectionError,
    SekhaNotFoundError,
    SekhaValidationError,
)
from .models import (
    ClientConfig,
    ConversationResponse,
    NewConversation,
    QueryRequest as QueryRequestModel,
    QueryResponse as QueryResponseModel,
)
from .types import (
    CreateConversationRequest,
    QueryRequest,
    PruneResponse,
    LabelSuggestResponse,
    SummaryResponse,
    FtsSearchResponse,
    ContextAssembly,
)
from .utils import RateLimiter, validate_api_key, validate_base_url


class SekhaClient:
    """
    Main client for Sekha AI Memory System

    Supports both sync and async operations.
    Automatically handles auth, retries, and rate limiting.
    """

    def __init__(self, config: ClientConfig) -> None:
        """
        Initialize the client

        Args:
            config: ClientConfiguration object
        """
        validate_api_key(config.api_key)
        validate_base_url(config.base_url)

        self.config = config
        self.rate_limiter = RateLimiter(
            config.rate_limit_requests, config.rate_limit_window
        )

        # Create httpx client with connection pooling
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "User-Agent": "Sekha-Python-SDK/0.6.0",
            },
        )

        # For sync operations, we'll create clients on-demand
        self._sync_client: Optional[httpx.Client] = None

    async def __aenter__(self) -> "SekhaClient":
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        await self.close()

    async def close(self) -> None:
        """Close the async client"""
        if hasattr(self, "client") and self.client:
            await self.client.aclose()

    @property
    def sync_client(self) -> httpx.Client:
        """Lazy-load sync client"""
        if self._sync_client is None:
            self._sync_client = httpx.Client(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "User-Agent": "Sekha-Python-SDK/0.6.0",
                },
            )
        return self._sync_client

    # ============== Conversation Operations ==============

    @backoff.on_exception(
        backoff.expo, (SekhaConnectionError, httpx.TimeoutException), max_tries=3
    )
    async def create_conversation(
        self,
        conversation: Union[CreateConversationRequest, NewConversation],
    ) -> Dict[str, Any]:
        """
        Create a new conversation with messages

        Args:
            conversation: Conversation data (TypedDict or Pydantic model)

        Returns:
            Created conversation with ID

        Raises:
            SekhaValidationError: Invalid input
            SekhaAPIError: API returned error
        """
        await self.rate_limiter.acquire()

        try:
            # Handle both Pydantic models and TypedDicts
            if hasattr(conversation, 'model_dump'):
                json_data = conversation.model_dump()
            else:
                json_data = dict(conversation)  # TypedDict to dict
                
            response = await self.client.post(
                "/api/v1/conversations",
                json=json_data,
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                raise SekhaValidationError("Invalid conversation data", e.response.text)
            elif e.response.status_code == 401:
                raise SekhaAuthError("Invalid API key")
            else:
                raise SekhaAPIError(
                    f"Failed to create conversation: {e.response.text}",
                    e.response.status_code,
                    e.response.text,
                )
        except httpx.TimeoutException:
            raise SekhaConnectionError("Request timed out")
        except Exception as e:
            raise SekhaError(f"Unexpected error: {e}")

    async def get_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get conversation by ID
        
        Args:
            conversation_id: Conversation UUID
            
        Returns:
            Conversation details
        """
        await self.rate_limiter.acquire()

        try:
            response = await self.client.get(f"/api/v1/conversations/{conversation_id}")
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise SekhaNotFoundError(f"Conversation {conversation_id} not found")
            raise SekhaAPIError(
                "Failed to get conversation", e.response.status_code, e.response.text
            )

    async def list_conversations(
        self,
        label: Optional[str] = None,
        folder: Optional[str] = None,
        pinned: Optional[bool] = None,
        archived: Optional[bool] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Dict[str, Any]:
        """
        List conversations with optional filtering
        
        Args:
            label: Filter by label
            folder: Filter by folder
            pinned: Filter by pinned status
            archived: Filter by archived status
            page: Page number
            page_size: Results per page
            
        Returns:
            Query response with conversations
        """
        await self.rate_limiter.acquire()

        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if label:
            params["label"] = label
        if folder:
            params["folder"] = folder
        if pinned is not None:
            params["pinned"] = pinned
        if archived is not None:
            params["archived"] = archived

        try:
            response = await self.client.get(
                "/api/v1/conversations",
                params=params,
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            raise SekhaError(f"Failed to list conversations: {e}")

    async def update_label(
        self,
        conversation_id: str,
        new_label: str,
        new_folder: str,
    ) -> None:
        """
        Update conversation label and folder
        
        Args:
            conversation_id: Conversation UUID
            new_label: New label name
            new_folder: New folder path
        """
        await self.rate_limiter.acquire()

        body = {"label": new_label, "folder": new_folder}

        try:
            response = await self.client.put(
                f"/api/v1/conversations/{conversation_id}/label",
                json=body,
            )
            response.raise_for_status()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise SekhaNotFoundError(f"Conversation {conversation_id} not found")
            raise SekhaAPIError(
                "Failed to update label", e.response.status_code, e.response.text
            )

    async def update_folder(
        self,
        conversation_id: str,
        new_folder: str,
    ) -> None:
        """
        Update conversation folder
        
        Args:
            conversation_id: Conversation UUID
            new_folder: New folder path
        """
        await self.rate_limiter.acquire()

        try:
            response = await self.client.put(
                f"/api/v1/conversations/{conversation_id}/folder",
                json={"folder": new_folder},
            )
            response.raise_for_status()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise SekhaNotFoundError(f"Conversation {conversation_id} not found")
            raise SekhaAPIError(
                "Failed to update folder", e.response.status_code, e.response.text
            )

    async def pin_conversation(self, conversation_id: str) -> None:
        """
        Pin a conversation (sets importance=10)
        
        Args:
            conversation_id: Conversation UUID
        """
        await self.rate_limiter.acquire()

        try:
            response = await self.client.put(
                f"/api/v1/conversations/{conversation_id}/pin"
            )
            response.raise_for_status()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise SekhaNotFoundError(f"Conversation {conversation_id} not found")
            raise SekhaAPIError(
                "Failed to pin conversation", e.response.status_code, e.response.text
            )

    async def archive_conversation(self, conversation_id: str) -> None:
        """
        Archive a conversation
        
        Args:
            conversation_id: Conversation UUID
        """
        await self.rate_limiter.acquire()

        try:
            response = await self.client.put(
                f"/api/v1/conversations/{conversation_id}/archive"
            )
            response.raise_for_status()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise SekhaNotFoundError(f"Conversation {conversation_id} not found")
            raise SekhaAPIError(
                "Failed to archive conversation",
                e.response.status_code,
                e.response.text,
            )

    async def delete_conversation(self, conversation_id: str) -> None:
        """
        Delete a conversation
        
        Args:
            conversation_id: Conversation UUID
        """
        await self.rate_limiter.acquire()

        try:
            response = await self.client.delete(
                f"/api/v1/conversations/{conversation_id}"
            )
            response.raise_for_status()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise SekhaNotFoundError(f"Conversation {conversation_id} not found")
            raise SekhaAPIError(
                "Failed to delete conversation", e.response.status_code, e.response.text
            )

    async def count_conversations(
        self, label: Optional[str] = None, folder: Optional[str] = None
    ) -> int:
        """
        Count conversations with optional filtering
        
        Args:
            label: Filter by label
            folder: Filter by folder
            
        Returns:
            Number of matching conversations
        """
        await self.rate_limiter.acquire()

        params: Dict[str, str] = {}
        if label:
            params["label"] = label
        if folder:
            params["folder"] = folder

        try:
            response = await self.client.get(
                "/api/v1/conversations/count", params=params
            )
            response.raise_for_status()
            return response.json()["count"]

        except Exception as e:
            raise SekhaError(f"Failed to count conversations: {e}")

    # ============== Query & Search ==============

    async def query(
        self,
        query: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Semantic query using vector similarity search

        Args:
            query: Search query
            limit: Max results
            offset: Pagination offset
            filters: Metadata filters

        Returns:
            Query response with results
        """
        await self.rate_limiter.acquire()

        body = {"query": query}
        if limit is not None:
            body["limit"] = limit
        if offset is not None:
            body["offset"] = offset
        if filters is not None:
            body["filters"] = filters

        try:
            response = await self.client.post(
                "/api/v1/query",
                json=body,
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                raise SekhaValidationError("Invalid query parameters", e.response.text)
            elif e.response.status_code == 401:
                raise SekhaAuthError("Invalid API key")
            else:
                raise SekhaAPIError(
                    f"Query failed: {e.response.text}",
                    e.response.status_code,
                    e.response.text,
                )
        except httpx.TimeoutException:
            raise SekhaConnectionError("Query timed out")
        except httpx.ConnectError as e:
            raise SekhaConnectionError(f"Connection failed: {e}")
        except Exception as e:
            raise SekhaError(f"Query failed: {e}")

    async def smart_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Alias for query() - semantic query with smart ranking
        
        Args:
            query: Search query
            **kwargs: Additional query options
            
        Returns:
            Query response with results
        """
        return await self.query(query, **kwargs)

    async def full_text_search(
        self, query: str, limit: int = 10
    ) -> FtsSearchResponse:
        """
        Full-text search using SQLite FTS5
        
        Args:
            query: Search text
            limit: Max results
            
        Returns:
            Full-text search results
        """
        await self.rate_limiter.acquire()

        try:
            response = await self.client.post(
                "/api/v1/search/fts",
                json={"query": query, "limit": limit},
            )
            response.raise_for_status()
            return response.json()  # type: ignore

        except Exception as e:
            raise SekhaError(f"Full-text search failed: {e}")

    async def rebuild_embeddings(self) -> None:
        """
        Trigger rebuild of all embeddings
        """
        await self.rate_limiter.acquire()

        try:
            response = await self.client.post("/api/v1/rebuild-embeddings")
            response.raise_for_status()

        except Exception as e:
            raise SekhaError(f"Failed to rebuild embeddings: {e}")

    # ============== Memory Orchestration ==============

    async def assemble_context(
        self,
        query: str,
        preferred_labels: Optional[List[str]] = None,
        context_budget: int = 4000,
        excluded_folders: Optional[List[str]] = None,
    ) -> ContextAssembly:
        """
        Assemble intelligent context for a query
        
        Args:
            query: Query to build context for
            preferred_labels: Labels to prioritize
            context_budget: Token budget for context
            excluded_folders: Folders to exclude
            
        Returns:
            Context assembly with messages
        """
        await self.rate_limiter.acquire()

        body = {
            "query": query,
            "preferred_labels": preferred_labels or [],
            "context_budget": context_budget,
            "excluded_folders": excluded_folders or [],
        }

        try:
            response = await self.client.post(
                "/api/v1/context/assemble",
                json=body,
            )
            response.raise_for_status()
            return response.json()  # type: ignore

        except Exception as e:
            raise SekhaError(f"Failed to assemble context: {e}")

    async def summarize(
        self, conversation_id: str, level: str = "daily"
    ) -> SummaryResponse:
        """
        Generate hierarchical summary

        Args:
            conversation_id: Conversation UUID
            level: "daily", "weekly", or "monthly"

        Returns:
            Summary response
        """
        await self.rate_limiter.acquire()

        try:
            response = await self.client.post(
                "/api/v1/summarize",
                json={"conversation_id": conversation_id, "level": level},
            )
            response.raise_for_status()
            return response.json()  # type: ignore

        except Exception as e:
            raise SekhaError(f"Failed to generate summary: {e}")

    async def generate_summary(
        self, conversation_id: str, **kwargs
    ) -> SummaryResponse:
        """
        Alias for summarize() - generate summary for conversation
        
        Args:
            conversation_id: Conversation UUID
            **kwargs: Additional summarize options
            
        Returns:
            Summary response
        """
        return await self.summarize(conversation_id, **kwargs)

    async def prune_dry_run(self, threshold_days: int = 90) -> PruneResponse:
        """
        Get pruning suggestions without executing
        
        Args:
            threshold_days: Days since last access threshold
            
        Returns:
            Pruning suggestions
        """
        await self.rate_limiter.acquire()

        try:
            response = await self.client.post(
                "/api/v1/prune/dry-run",
                json={"threshold_days": threshold_days},
            )
            response.raise_for_status()
            return response.json()  # type: ignore

        except Exception as e:
            raise SekhaError(f"Failed to get pruning suggestions: {e}")

    async def get_pruning_suggestions(self, **kwargs) -> PruneResponse:
        """
        Alias for prune_dry_run() - get pruning suggestions
        
        Args:
            **kwargs: Prune options
            
        Returns:
            Pruning suggestions
        """
        return await self.prune_dry_run(**kwargs)

    async def prune_execute(self, conversation_ids: List[str]) -> None:
        """
        Execute pruning (archive conversations)
        
        Args:
            conversation_ids: List of conversation UUIDs to archive
        """
        await self.rate_limiter.acquire()

        try:
            response = await self.client.post(
                "/api/v1/prune/execute",
                json={"conversation_ids": conversation_ids},
            )
            response.raise_for_status()

        except Exception as e:
            raise SekhaError(f"Failed to execute pruning: {e}")

    async def suggest_labels(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get AI-powered label suggestions
        
        Args:
            conversation_id: Conversation UUID
            
        Returns:
            Label suggestions with confidence scores
        """
        await self.rate_limiter.acquire()

        try:
            response = await self.client.post(
                "/api/v1/labels/suggest",
                json={"conversation_id": conversation_id},
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            raise SekhaError(f"Failed to suggest labels: {e}")

    async def auto_label(
        self, conversation_id: str, threshold: float = 0.7
    ) -> Optional[str]:
        """
        Auto-label conversation if confidence meets threshold

        Args:
            conversation_id: Conversation UUID
            threshold: Minimum confidence score (0.0-1.0)

        Returns:
            Applied label or None if no confident match
        """
        suggestions = await self.suggest_labels(conversation_id)

        # Find first suggestion above threshold
        for suggestion in suggestions.get("suggestions", []):
            if suggestion.get("confidence", 0) >= threshold:
                label = suggestion["label"]
                # Apply the label
                await self.update_label(
                    conversation_id, label, suggestion.get("folder", "/")
                )
                return label

        return None

    # ============== Additional Features ==============

    async def export(
        self,
        label: Optional[str] = None,
        folder: Optional[str] = None,
        format: str = "markdown",
    ) -> str:
        """
        Export conversations to markdown or JSON

        Args:
            label: Optional label filter
            folder: Optional folder filter
            format: Export format ('markdown' or 'json')

        Returns:
            Exported content as string
        """
        await self.rate_limiter.acquire()

        params: Dict[str, str] = {"format": format}
        if label:
            params["label"] = label
        if folder:
            params["folder"] = folder

        try:
            response = await self.client.get("/api/v1/export", params=params)
            response.raise_for_status()
            data = response.json()
            return data["content"]

        except Exception as e:
            raise SekhaError(f"Failed to export: {e}")

    async def score_message_importance(self, message_id: str) -> Dict[str, Any]:
        """
        Score importance of a message

        Args:
            message_id: Message UUID

        Returns:
            Importance score and factors
        """
        await self.rate_limiter.acquire()

        try:
            response = await self.client.post(
                "/api/v1/messages/score",
                json={"message_id": message_id},
            )
            response.raise_for_status()
            return response.json()

        except Exception as e:
            raise SekhaError(f"Failed to score message: {e}")

    async def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """
        Get available MCP (Model Context Protocol) tools

        Returns:
            List of available tools with descriptions
        """
        await self.rate_limiter.acquire()

        try:
            response = await self.client.get("/api/v1/mcp/tools")
            response.raise_for_status()
            return response.json()

        except Exception as e:
            raise SekhaError(f"Failed to get MCP tools: {e}")


# ============== Sync Wrapper ==============


class SyncSekhaClient:
    """
    Synchronous wrapper for SekhaClient

    All async methods are available as sync methods.
    """

    def __init__(self, config: ClientConfig) -> None:
        self._config = config
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def __enter__(self) -> "SyncSekhaClient":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._loop and not self._loop.is_closed():
            self._loop.close()

    def _get_or_create_loop(self) -> asyncio.AbstractEventLoop:
        """Get existing event loop or create new one"""
        try:
            _loop = asyncio.get_running_loop()
            # We're already in an async context, can't use asyncio.run
            raise RuntimeError(
                "SyncSekhaClient cannot be used within an async context. "
                "Use SekhaClient directly instead."
            )
        except RuntimeError:
            # No running loop, create new one
            if self._loop is None or self._loop.is_closed():
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
            return self._loop

    def __getattr__(self, name: str):
        """Delegate to async client"""

        def sync_wrapper(*args, **kwargs):
            loop = self._get_or_create_loop()
            async_client = SekhaClient(self._config)

            async def run_async():
                try:
                    async with async_client:
                        method = getattr(async_client, name)
                        return await method(*args, **kwargs)
                finally:
                    await async_client.close()

            return loop.run_until_complete(run_async())

        return sync_wrapper


# Alias for backward compatibility
MemoryController = SekhaClient
MemoryConfig = ClientConfig
