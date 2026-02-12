"""
Sekha Unified Client Demo

Demonstrates the new unified client interface that combines
Controller, MCP, and Bridge services in a single interface.
"""

import asyncio
from typing import List

from sekha import SekhaClient, create_sekha_client
from sekha.types import Message, QueryResponse


async def basic_usage():
    """
    Basic unified client setup and usage
    """
    print("\n=== Basic Unified Client Usage ===")
    
    # Method 1: Direct instantiation
    sekha = SekhaClient(
        controller_url='http://localhost:8080',
        bridge_url='http://localhost:5001',
        api_key='your-api-key',
        default_label='Demo',
    )
    
    # Method 2: Factory function
    sekha = create_sekha_client(
        controller_url='http://localhost:8080',
        bridge_url='http://localhost:5001',
        api_key='your-api-key',
    )
    
    # Use with context manager
    async with sekha:
        # Access individual clients
        conversations = await sekha.controller.list_conversations(
            label='Demo',
            page_size=10
        )
        print(f"Found {len(conversations.results)} conversations")


async def individual_clients():
    """
    Using individual clients through unified interface
    """
    print("\n=== Using Individual Clients ===")
    
    async with create_sekha_client(
        controller_url='http://localhost:8080',
        bridge_url='http://localhost:5001',
        api_key='your-api-key',
    ) as sekha:
        # 1. Controller - Memory operations
        print("\n1. Controller (Memory Operations)")
        result: QueryResponse = await sekha.controller.query(
            query="TypeScript patterns",
            limit=5
        )
        print(f"Found {result.total} results")
        for r in result.results:
            print(f"  - {r.label}: {r.content[:50]}...")
        
        # 2. MCP - Model Context Protocol (future)
        print("\n2. MCP Client (Coming Soon)")
        try:
            stats = await sekha.mcp.memory_stats({})
            print(f"Memory stats: {stats}")
        except NotImplementedError:
            print("  MCP client not yet implemented")
        
        # 3. Bridge - LLM operations (future)
        print("\n3. Bridge Client (Coming Soon)")
        try:
            completion = await sekha.bridge.complete(
                messages=[
                    {"role": "user", "content": "Hello!"}
                ]
            )
            print(f"Response: {completion}")
        except NotImplementedError:
            print("  Bridge client not yet implemented")


async def convenience_methods():
    """
    Using high-level convenience methods
    """
    print("\n=== Convenience Methods ===")
    
    async with create_sekha_client(
        controller_url='http://localhost:8080',
        bridge_url='http://localhost:5001',
        api_key='your-api-key',
    ) as sekha:
        # 1. Store and Query
        print("\n1. store_and_query()")
        messages: List[Message] = [
            {
                "role": "user",
                "content": "Explain TypeScript interfaces"
            },
            {
                "role": "assistant",
                "content": "TypeScript interfaces define the shape of objects..."
            }
        ]
        
        result = await sekha.store_and_query(
            messages=messages,
            query="TypeScript interfaces",
            label="Engineering",
            folder="/docs",
        )
        print(f"Stored conversation: {result['conversation'].id}")
        print(f"Found {result['results'].total} related conversations")
        
        # 2. Complete with Context (when bridge is ready)
        print("\n2. complete_with_context() - Coming Soon")
        try:
            response = await sekha.complete_with_context(
                prompt="What are the main TypeScript patterns we use?",
                context_query="TypeScript patterns",
                context_budget=4000,
                preferred_labels=["Engineering"],
                temperature=0.7,
            )
            print(f"Response: {response['choices'][0]['message']['content']}")
            print(f"Used {len(response['context']['messages'])} context messages")
        except NotImplementedError:
            print("  Bridge not yet implemented")
        
        # 3. Complete with Memory (when bridge is ready)
        print("\n3. complete_with_memory() - Coming Soon")
        try:
            response = await sekha.complete_with_memory(
                prompt="Summarize TypeScript best practices",
                search_query="TypeScript best practices",
                limit=5,
                temperature=0.5,
            )
            print(f"Response: {response['choices'][0]['message']['content']}")
            print(f"Used {response['search_results']['total']} search results")
        except NotImplementedError:
            print("  Bridge not yet implemented")


async def streaming_example():
    """
    Streaming completion with context
    """
    print("\n=== Streaming with Context (Coming Soon) ===")
    
    async with create_sekha_client(
        controller_url='http://localhost:8080',
        bridge_url='http://localhost:5001',
        api_key='your-api-key',
    ) as sekha:
        try:
            print("\nStreaming response: ", end='', flush=True)
            async for chunk in sekha.stream_with_context(
                prompt="Explain our architecture",
                context_query="architecture decisions",
                context_budget=3000,
            ):
                content = chunk.get('choices', [{}])[0].get('delta', {}).get('content')
                if content:
                    print(content, end='', flush=True)
            print()  # Newline
        except NotImplementedError:
            print("Bridge not yet implemented")


async def type_safe_usage():
    """
    Type-safe usage with type hints
    """
    print("\n=== Type-Safe Usage ===")
    
    from sekha.types import (
        SearchResult,
        is_multi_modal_content,
        extract_text,
    )
    
    async with create_sekha_client(
        controller_url='http://localhost:8080',
        bridge_url='http://localhost:5001',
        api_key='your-api-key',
    ) as sekha:
        # Type-safe query
        response: QueryResponse = await sekha.controller.query("search term")
        
        # Type-safe result access
        if response.results:
            result: SearchResult = response.results[0]
            print(f"Result: {result.label}")
            print(f"Score: {result.score}")
            print(f"Content: {result.content[:100]}...")
        
        # Multi-modal content handling
        message: Message = {
            "role": "user",
            "content": [
                {"type": "text", "text": "Check this:"},
                {"type": "image_url", "image_url": {"url": "https://example.com/img.png"}}
            ]
        }
        
        if is_multi_modal_content(message["content"]):
            text = extract_text(message["content"])
            print(f"Extracted text: {text}")


async def health_monitoring():
    """
    Health check for all services
    """
    print("\n=== Health Monitoring ===")
    
    async with create_sekha_client(
        controller_url='http://localhost:8080',
        bridge_url='http://localhost:5001',
        api_key='your-api-key',
    ) as sekha:
        health = await sekha.health_check()
        
        print(f"\nController Status: {health['controller'].get('status', 'unknown')}")
        if 'version' in health['controller']:
            print(f"  Version: {health['controller']['version']}")
        
        print(f"\nBridge Status: {health['bridge'].get('status', 'unknown')}")
        if 'error' in health['bridge']:
            print(f"  Error: {health['bridge']['error']}")


async def error_handling():
    """
    Error handling patterns
    """
    print("\n=== Error Handling ===")
    
    from sekha.errors import (
        SekhaError,
        SekhaAPIError,
        SekhaNotFoundError,
        SekhaConnectionError,
    )
    
    async with create_sekha_client(
        controller_url='http://localhost:8080',
        bridge_url='http://localhost:5001',
        api_key='your-api-key',
    ) as sekha:
        try:
            # Try to get non-existent conversation
            await sekha.controller.get_conversation(
                "non-existent-id"
            )
        except SekhaNotFoundError as e:
            print(f"Not found: {e}")
        except SekhaConnectionError as e:
            print(f"Connection error: {e}")
        except SekhaAPIError as e:
            print(f"API error: {e}")
        except SekhaError as e:
            print(f"General error: {e}")


async def main():
    """
    Run all examples
    """
    print("\n" + "="*60)
    print("Sekha Unified Client Demo")
    print("="*60)
    
    # Note: These examples assume services are running
    # Adjust URLs and API keys as needed
    
    await basic_usage()
    await individual_clients()
    await convenience_methods()
    await streaming_example()
    await type_safe_usage()
    await health_monitoring()
    await error_handling()
    
    print("\n" + "="*60)
    print("Demo Complete!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
