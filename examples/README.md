# Sekha Python SDK Examples

Comprehensive examples demonstrating Sekha SDK features.

## Quick Start

### 1. Unified Client (Recommended)

```python
from sekha import SekhaClient

sekha = SekhaClient(
    controller_url='http://localhost:8080',
    bridge_url='http://localhost:5001',
    api_key='your-api-key'
)

# High-level workflows
async with sekha:
    # Store and search
    result = await sekha.store_and_query(
        messages=[...],
        query='search term'
    )
    
    # Complete with memory context
    response = await sekha.complete_with_memory(
        prompt='Explain concepts',
        search_query='concepts'
    )
```

### 2. Individual Controller Client

```python
from sekha import MemoryController, MemoryConfig

config = MemoryConfig(
    api_key='your-key',
    base_url='http://localhost:8080'
)

async with MemoryController(config) as memory:
    # Direct memory operations
    results = await memory.query('search term')
    conversations = await memory.list_conversations()
```

## Examples

### Core Examples

| File | Description |
|------|-------------|
| `unified_client_demo.py` | Unified client with Controller + MCP + Bridge |
| `basic_usage.py` | Basic memory controller operations |
| `async_usage.py` | Async/await patterns |
| `sync_usage.py` | Synchronous wrapper usage |

### Advanced Examples

| File | Description |
|------|-------------|
| `semantic_search.py` | Vector-based semantic search |
| `context_assembly.py` | Intelligent context building for LLMs |
| `pruning_workflow.py` | Memory pruning and archival |
| `auto_labeling.py` | AI-powered conversation labeling |

### Type Safety Examples

| File | Description |
|------|-------------|
| `type_hints_demo.py` | Type-safe usage with hints |
| `multi_modal.py` | Multi-modal messages (text + images) |
| `type_guards.py` | Runtime type checking |

## Running Examples

### Prerequisites

1. **Start Sekha Controller**:
   ```bash
   cd sekha-controller
   cargo run --release
   ```

2. **Install SDK**:
   ```bash
   pip install -e .
   ```

3. **Set API Key**:
   ```bash
   export SEKHA_API_KEY="your-api-key"
   ```

### Run Examples

```bash
# Unified client demo
python examples/unified_client_demo.py

# Basic usage
python examples/basic_usage.py

# Type safety demo
python examples/type_hints_demo.py
```

## Example Categories

### 1. Getting Started

- **unified_client_demo.py** - Start here! Shows unified interface
- **basic_usage.py** - Basic CRUD operations
- **async_usage.py** - Async patterns and context managers

### 2. Search & Query

- **semantic_search.py** - Vector-based similarity search
- **full_text_search.py** - SQLite FTS5 full-text search
- **hybrid_search.py** - Combining semantic + full-text

### 3. Memory Management

- **context_assembly.py** - Build context for LLM prompts
- **pruning_workflow.py** - Archive old conversations
- **importance_scoring.py** - Score message importance

### 4. Organization

- **folders_labels.py** - Organize conversations
- **auto_labeling.py** - AI-powered labeling
- **bulk_operations.py** - Batch updates

### 5. Integration

- **llm_integration.py** - Use with LLMs (when Bridge is ready)
- **mcp_tools.py** - MCP tool usage (when MCP is ready)
- **export_import.py** - Export/import conversations

### 6. Type Safety

- **type_hints_demo.py** - Complete type coverage
- **multi_modal.py** - Text + image messages
- **type_guards.py** - Runtime validation

## Architecture

### Unified Client Structure

```
SekhaClient
├── controller (MemoryController)
│   ├── create_conversation()
│   ├── query()
│   ├── assemble_context()
│   └── ... (30+ methods)
├── mcp (MCPClient) - Coming Soon
│   ├── memory_stats()
│   ├── memory_search()
│   └── ...
├── bridge (BridgeClient) - Coming Soon
│   ├── complete()
│   ├── stream_complete()
│   ├── embed()
│   └── ...
└── Convenience Methods
    ├── store_and_query()
    ├── complete_with_context()
    ├── complete_with_memory()
    ├── stream_with_context()
    └── health_check()
```

## Configuration

### Unified Client Config

```python
from sekha import SekhaClient

sekha = SekhaClient(
    controller_url='http://localhost:8080',
    bridge_url='http://localhost:5001',
    api_key='your-api-key',
    bridge_api_key='optional-separate-key',
    mcp_api_key='optional-mcp-key',
    timeout=30.0,
    max_retries=3,
    default_label='MyApp',
    rate_limit_requests=1000,
    rate_limit_window=60.0,
)
```

### Controller-Only Config

```python
from sekha import MemoryController, MemoryConfig

config = MemoryConfig(
    base_url='http://localhost:8080',
    api_key='your-api-key',
    timeout=30.0,
    max_retries=3,
)
memory = MemoryController(config)
```

## Type Safety

### Type Hints

```python
from sekha.types import (
    Message,
    Conversation,
    QueryResponse,
    SearchResult,
)

# Fully typed
messages: List[Message] = [...]
response: QueryResponse = await sekha.controller.query('term')
result: SearchResult = response.results[0]
```

### Type Guards

```python
from sekha.types import (
    is_multi_modal_content,
    extract_text,
    extract_image_urls,
    has_images,
)

if has_images(message):
    urls = extract_image_urls(message['content'])
    text = extract_text(message['content'])
```

## Best Practices

### 1. Use Context Managers

```python
# Good ✅
async with SekhaClient(...) as sekha:
    await sekha.controller.query('term')

# Avoid ❌
sekha = SekhaClient(...)
await sekha.controller.query('term')
# Forgot to close!
```

### 2. Handle Errors

```python
from sekha.errors import SekhaError, SekhaNotFoundError

try:
    conversation = await sekha.controller.get_conversation(id)
except SekhaNotFoundError:
    print("Conversation not found")
except SekhaError as e:
    print(f"Error: {e}")
```

### 3. Use Type Hints

```python
from sekha.types import QueryResponse, SearchResult

# Better IDE support and error checking
response: QueryResponse = await sekha.controller.query('term')
for result in response.results:
    result: SearchResult
    print(result.label, result.score)
```

### 4. Leverage Convenience Methods

```python
# Instead of:
conv = await sekha.controller.create_conversation(...)
results = await sekha.controller.query('term')

# Use:
result = await sekha.store_and_query(
    messages=[...],
    query='term'
)
```

## Troubleshooting

### Connection Errors

```python
from sekha.errors import SekhaConnectionError

try:
    await sekha.controller.query('term')
except SekhaConnectionError:
    print("Cannot connect to controller. Is it running?")
    print("Start with: cargo run --release")
```

### Authentication Errors

```python
from sekha.errors import SekhaAuthError

try:
    await sekha.controller.query('term')
except SekhaAuthError:
    print("Invalid API key. Check your configuration.")
```

### Not Found Errors

```python
from sekha.errors import SekhaNotFoundError

try:
    conv = await sekha.controller.get_conversation("bad-id")
except SekhaNotFoundError:
    print("Conversation not found. Check the ID.")
```

## Contributing

Want to add an example? Follow these guidelines:

1. **Clear purpose**: Focus on one concept
2. **Type hints**: Use type annotations
3. **Error handling**: Show error patterns
4. **Documentation**: Add docstrings
5. **Runnable**: Include full working code

See `unified_client_demo.py` as a template.

## Resources

- **Documentation**: [Coming Soon]
- **API Reference**: [Coming Soon]
- **GitHub**: https://github.com/sekha-ai/sekha-python-sdk
- **Issues**: https://github.com/sekha-ai/sekha-python-sdk/issues
