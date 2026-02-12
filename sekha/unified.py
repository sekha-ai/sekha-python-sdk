"""
Sekha Unified Client

Single interface combining Controller, MCP, and Bridge clients
for complete Sekha ecosystem access.
"""

from typing import Optional, List, Dict, Any, AsyncIterator
from dataclasses import dataclass

from .client import SekhaClient as MemoryController
from .types import (
    Message,
    MessageContent,
    MemoryConfig,
    QueryResponse,
    Conversation,
)

# Note: MCP and Bridge clients will be implemented separately
# For now, we create stubs to match the JS SDK structure


@dataclass
class SekhaConfig:
    """
    Unified Sekha configuration
    
    Combines configuration for Controller, MCP, and Bridge services.
    """
    # Controller configuration
    controller_url: str
    api_key: str
    
    # Bridge configuration
    bridge_url: str
    bridge_api_key: Optional[str] = None
    
    # Optional MCP API key (defaults to api_key)
    mcp_api_key: Optional[str] = None
    
    # Common configuration
    timeout: float = 30.0
    max_retries: int = 3
    default_label: Optional[str] = None
    rate_limit_requests: int = 1000
    rate_limit_window: float = 60.0


class MCPClient:
    """
    Model Context Protocol (MCP) client
    
    Provides MCP tools for memory operations.
    Currently a stub - will be fully implemented in future.
    """
    
    def __init__(self, base_url: str, api_key: str, **kwargs):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = kwargs.get('timeout', 30.0)
        self.max_retries = kwargs.get('max_retries', 3)
    
    async def memory_stats(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Get memory statistics"""
        # Stub - to be implemented
        raise NotImplementedError("MCP client not yet implemented")
    
    async def memory_search(self, query: str, **kwargs) -> Dict[str, Any]:
        """MCP-based memory search"""
        # Stub - to be implemented
        raise NotImplementedError("MCP client not yet implemented")


class BridgeClient:
    """
    LLM Bridge client
    
    Provides access to LLM operations (completion, embedding, etc).
    Currently a stub - will be fully implemented in future.
    """
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, **kwargs):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = kwargs.get('timeout', 30.0)
        self.max_retries = kwargs.get('max_retries', 3)
    
    async def complete(self, **kwargs) -> Dict[str, Any]:
        """Generate LLM completion"""
        # Stub - to be implemented
        raise NotImplementedError("Bridge client not yet implemented")
    
    async def stream_complete(self, **kwargs) -> AsyncIterator[Dict[str, Any]]:
        """Stream LLM completion"""
        # Stub - to be implemented
        raise NotImplementedError("Bridge client not yet implemented")
        yield  # Make it a generator
    
    async def embed(self, text: str, **kwargs) -> Dict[str, Any]:
        """Generate text embedding"""
        # Stub - to be implemented
        raise NotImplementedError("Bridge client not yet implemented")
    
    async def health(self) -> Dict[str, Any]:
        """Check bridge health"""
        # Stub - to be implemented
        raise NotImplementedError("Bridge client not yet implemented")


def message_content_to_string(content: MessageContent) -> str:
    """
    Convert MessageContent to string
    
    Extracts text from multi-modal content or returns string as-is.
    
    Args:
        content: Message content (string or list of content parts)
        
    Returns:
        Text content as string
    """
    if isinstance(content, str):
        return content
    
    # Extract text from content parts
    text_parts = [
        part.get("text", "") 
        for part in content 
        if isinstance(part, dict) and part.get("type") == "text"
    ]
    return " ".join(text_parts)


class SekhaClient:
    """
    Unified Sekha Client
    
    Combines MemoryController, MCPClient, and BridgeClient into a single
    interface. Provides direct access to all three clients plus high-level
    convenience methods for common workflows.
    
    Example:
        ```python
        sekha = SekhaClient(
            controller_url='http://localhost:8080',
            bridge_url='http://localhost:5001',
            api_key='your-api-key'
        )
        
        # Use individual clients
        conversations = await sekha.controller.list()
        stats = await sekha.mcp.memory_stats({})
        completion = await sekha.bridge.complete(
            messages=[{'role': 'user', 'content': 'Hello'}]
        )
        
        # Or use convenience methods
        response = await sekha.complete_with_memory(
            'Explain what we discussed about TypeScript',
            'TypeScript'
        )
        ```
    """
    
    def __init__(
        self,
        controller_url: str,
        api_key: str,
        bridge_url: str,
        bridge_api_key: Optional[str] = None,
        mcp_api_key: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        default_label: Optional[str] = None,
        rate_limit_requests: int = 1000,
        rate_limit_window: float = 60.0,
    ):
        """
        Initialize unified Sekha client
        
        Args:
            controller_url: Memory controller base URL
            api_key: API key for controller
            bridge_url: LLM bridge base URL
            bridge_api_key: Optional separate bridge API key
            mcp_api_key: Optional MCP API key (defaults to api_key)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            default_label: Default conversation label
            rate_limit_requests: Max requests per window
            rate_limit_window: Rate limit window in seconds
        """
        self.config = SekhaConfig(
            controller_url=controller_url,
            api_key=api_key,
            bridge_url=bridge_url,
            bridge_api_key=bridge_api_key,
            mcp_api_key=mcp_api_key,
            timeout=timeout,
            max_retries=max_retries,
            default_label=default_label,
            rate_limit_requests=rate_limit_requests,
            rate_limit_window=rate_limit_window,
        )
        
        # Initialize Memory Controller
        controller_config = MemoryConfig(
            base_url=controller_url,
            api_key=api_key,
            default_label=default_label,
            timeout=timeout,
            max_retries=max_retries,
            rate_limit_requests=rate_limit_requests,
            rate_limit_window=rate_limit_window,
        )
        self.controller = MemoryController(controller_config)
        
        # Initialize MCP Client
        self.mcp = MCPClient(
            base_url=controller_url,
            api_key=mcp_api_key or api_key,
            timeout=timeout,
            max_retries=max_retries,
        )
        
        # Initialize Bridge Client
        self.bridge = BridgeClient(
            base_url=bridge_url,
            api_key=bridge_api_key,
            timeout=timeout,
            max_retries=max_retries,
        )
    
    async def __aenter__(self) -> "SekhaClient":
        """Async context manager entry"""
        await self.controller.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit"""
        await self.controller.__aexit__(exc_type, exc_val, exc_tb)
    
    async def close(self) -> None:
        """Close all clients"""
        await self.controller.close()
    
    # ============================================
    # Convenience Methods
    # ============================================
    
    async def store_and_query(
        self,
        messages: List[Message],
        query: str,
        label: Optional[str] = None,
        folder: Optional[str] = None,
        importance_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Store conversation and immediately search
        
        Convenience method that stores messages then performs semantic search.
        
        Args:
            messages: Messages to store
            query: Search query
            label: Conversation label
            folder: Conversation folder
            importance_score: Importance score (1-10)
            
        Returns:
            Dictionary with 'conversation' and 'results' keys
            
        Example:
            ```python
            results = await sekha.store_and_query(
                [
                    {'role': 'user', 'content': 'Explain TypeScript interfaces'},
                    {'role': 'assistant', 'content': 'Interfaces define...'}
                ],
                'TypeScript interfaces',
                label='Engineering',
                folder='/docs'
            )
            
            print(f"Found {results['results'].total} related conversations")
            ```
        """
        from .models import NewConversation, MessageDto
        
        # Store conversation
        conv = NewConversation(
            messages=[MessageDto(**msg) for msg in messages],  # type: ignore
            label=label or self.config.default_label or 'Conversation',
            folder=folder or '/',
        )
        conversation = await self.controller.create_conversation(conv)
        
        # Search
        results = await self.controller.query(query)
        
        return {
            'conversation': conversation,
            'results': results,
        }
    
    async def complete_with_context(
        self,
        prompt: str,
        context_query: str,
        context_budget: Optional[int] = None,
        preferred_labels: Optional[List[str]] = None,
        excluded_folders: Optional[List[str]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Assemble context and generate completion
        
        Gets relevant context from memory and uses it in LLM completion.
        
        Args:
            prompt: User prompt
            context_query: Query to find relevant context
            context_budget: Token budget for context
            preferred_labels: Labels to prioritize
            excluded_folders: Folders to exclude
            model: LLM model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            LLM completion response with context
            
        Example:
            ```python
            response = await sekha.complete_with_context(
                'What were the main takeaways?',
                'meeting notes',
                context_budget=4000,
                preferred_labels=['Meetings'],
                temperature=0.7
            )
            
            print(response['choices'][0]['message']['content'])
            print(f"Used {len(response['context']['messages'])} context messages")
            ```
        """
        # Assemble context from memory
        context = await self.controller.assemble_context(
            query=context_query,
            preferred_labels=preferred_labels,
            context_budget=context_budget or 4000,
            excluded_folders=excluded_folders,
        )
        
        # Build messages with context
        messages = [
            {
                'role': 'system',
                'content': 'Use the following context from previous conversations to answer the question.',
            },
            *[
                {
                    'role': msg['role'],
                    'content': message_content_to_string(msg['content']),
                }
                for msg in context.get('messages', [])
            ],
            {
                'role': 'user',
                'content': prompt,
            },
        ]
        
        # Generate completion
        completion = await self.bridge.complete(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return {
            **completion,
            'context': context,
        }
    
    async def complete_with_memory(
        self,
        prompt: str,
        search_query: str,
        limit: Optional[int] = None,
        labels: Optional[List[str]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Search memory and use results in completion
        
        Performs semantic search and includes results in LLM prompt.
        Simpler than complete_with_context but less token-efficient.
        
        Args:
            prompt: User prompt
            search_query: Query to search memory
            limit: Max search results
            labels: Filter by labels
            model: LLM model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            LLM completion response with search results
            
        Example:
            ```python
            response = await sekha.complete_with_memory(
                'Summarize what we learned about TypeScript',
                'TypeScript',
                limit=5,
                temperature=0.5
            )
            
            print(response['choices'][0]['message']['content'])
            print(f"Used {response['search_results']['total']} search results")
            ```
        """
        # Search memory
        search_results = await self.controller.query(
            query=search_query,
            limit=limit or 5,
            filters={'labels': labels} if labels else None,
        )
        
        # Build context from search results
        context_text = "\n\n".join([
            f"[{i+1}] {r.label} (score: {r.score:.2f}):\n{r.content}"
            for i, r in enumerate(search_results.results)
        ])
        
        # Build messages
        messages = [
            {
                'role': 'system',
                'content': 'Use the following search results from memory to answer the question.',
            },
            {
                'role': 'system',
                'content': f"Search Results:\n{context_text}",
            },
            {
                'role': 'user',
                'content': prompt,
            },
        ]
        
        # Generate completion
        completion = await self.bridge.complete(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return {
            **completion,
            'search_results': search_results,
        }
    
    async def stream_with_context(
        self,
        prompt: str,
        context_query: str,
        context_budget: Optional[int] = None,
        preferred_labels: Optional[List[str]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Streaming completion with memory context
        
        Assembles context and streams LLM response.
        
        Args:
            prompt: User prompt
            context_query: Query to find relevant context
            context_budget: Token budget for context
            preferred_labels: Labels to prioritize
            model: LLM model name
            temperature: Sampling temperature
            
        Yields:
            Completion chunks
            
        Example:
            ```python
            stream = sekha.stream_with_context(
                'Explain our TypeScript architecture',
                'TypeScript architecture'
            )
            
            async for chunk in stream:
                content = chunk['choices'][0].get('delta', {}).get('content')
                if content:
                    print(content, end='', flush=True)
            ```
        """
        # Assemble context
        context = await self.controller.assemble_context(
            query=context_query,
            context_budget=context_budget or 4000,
            preferred_labels=preferred_labels,
        )
        
        # Build messages
        messages = [
            {
                'role': 'system',
                'content': 'Use the following context to answer the question.',
            },
            *[
                {
                    'role': msg['role'],
                    'content': message_content_to_string(msg['content']),
                }
                for msg in context.get('messages', [])
            ],
            {
                'role': 'user',
                'content': prompt,
            },
        ]
        
        # Stream completion
        async for chunk in self.bridge.stream_complete(
            model=model,
            messages=messages,
            temperature=temperature,
        ):
            yield chunk
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Health check for all services
        
        Checks controller and bridge health simultaneously.
        
        Returns:
            Combined health status
            
        Example:
            ```python
            health = await sekha.health_check()
            print(f"Controller: {health['controller']['status']}")
            print(f"Bridge: {health['bridge']['status']}")
            ```
        """
        import asyncio
        
        # Check controller and bridge health
        controller_result = await asyncio.gather(
            self.controller.client.get('/health'),
            return_exceptions=True
        )
        
        bridge_result = await asyncio.gather(
            self.bridge.health(),
            return_exceptions=True
        )
        
        return {
            'controller': (
                controller_result[0].json()
                if not isinstance(controller_result[0], Exception)
                else {'status': 'unhealthy', 'error': str(controller_result[0])}
            ),
            'bridge': (
                bridge_result[0]
                if not isinstance(bridge_result[0], Exception)
                else {'status': 'unhealthy', 'error': str(bridge_result[0])}
            ),
        }


def create_sekha_client(
    controller_url: str,
    api_key: str,
    bridge_url: str,
    **kwargs
) -> SekhaClient:
    """
    Create unified Sekha client
    
    Convenience factory function.
    
    Args:
        controller_url: Memory controller base URL
        api_key: API key
        bridge_url: LLM bridge base URL
        **kwargs: Additional configuration options
        
    Returns:
        Initialized SekhaClient
        
    Example:
        ```python
        sekha = create_sekha_client(
            controller_url='http://localhost:8080',
            bridge_url='http://localhost:5001',
            api_key='your-api-key'
        )
        ```
    """
    return SekhaClient(
        controller_url=controller_url,
        api_key=api_key,
        bridge_url=bridge_url,
        **kwargs
    )
