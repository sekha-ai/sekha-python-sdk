# Sekha Python SDK

> **Official Python Client for Sekha Memory System**

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org)
[![CI](https://github.com/sekha-ai/sekha-python-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/sekha-ai/sekha-python-sdk/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/sekha-ai/sekha-python-sdk/branch/main/graph/badge.svg)](https://codecov.io/gh/sekha-ai/sekha-python-sdk)
[![PyPI](https://img.shields.io/badge/pypi-coming--soon-orange.svg)](https://pypi.org)
[![Version](https://img.shields.io/badge/version-0.2.0-green.svg)](https://github.com/sekha-ai/sekha-python-sdk/blob/main/CHANGELOG.md)

---

## What is Sekha Python SDK?

Official Python client library for interacting with Sekha AI Memory System, providing unified access to Controller, MCP, and Bridge services.

**Features:**

- ✅ **Unified Client Interface** - Single client for all services (Controller, MCP, Bridge)
- ✅ **Full Type Safety** - Complete type hints with runtime validation
- ✅ **Async/Await Support** - Built on httpx with connection pooling
- ✅ **Streaming Support** - Server-sent events for LLM completions
- ✅ **Automatic Retries** - Exponential backoff with jitter
- ✅ **Rate Limiting** - Built-in token bucket rate limiter
- ✅ **90+% Test Coverage** - Comprehensive test suite (2,000+ lines)
- ✅ **Complete API Coverage** - 19 Controller + 4 Bridge + 2 MCP endpoints
- ✅ **5 Convenience Workflows** - High-level methods for common patterns

---

## 📚 Documentation

**Complete SDK docs: [docs.sekha.dev/sdks/python-sdk](https://docs.sekha.dev/sdks/python-sdk/)**

- [Python SDK Guide](https://docs.sekha.dev/sdks/python-sdk/)
- [API Reference](https://docs.sekha.dev/api-reference/rest-api/)
- [Code Examples](https://docs.sekha.dev/sdks/examples/)
- [Getting Started](https://docs.sekha.dev/getting-started/quickstart/)
- [Changelog](https://github.com/sekha-ai/sekha-python-sdk/blob/main/CHANGELOG.md)

---

## 🚀 Quick Start

### Installation

```bash
# From PyPI (coming soon)
pip install sekha-python-sdk

# From source (current)
git clone https://github.com/sekha-ai/sekha-python-sdk.git
cd sekha-python-sdk
pip install -e .
```

### Basic Usage - Unified Client (Recommended)

```python
from sekha import SekhaClient

# Initialize unified client with all services
client = SekhaClient(
    controller_url="http://localhost:8080",
    api_key="sk-your-api-key-here",
    bridge_url="http://localhost:5001",  # Optional
)

# ===== CONTROLLER: Memory Operations =====
await client.controller.create_conversation({
    "label": "My Conversation",
    "messages": [
        {"role": "user", "content": "Hello Sekha!"},
        {"role": "assistant", "content": "Hello! I'll remember this."}
    ]
})

# ===== BRIDGE: LLM Completions =====
response = await client.bridge.complete(
    messages=[
        {"role": "user", "content": "Explain quantum computing"}
    ],
    model="gpt-4",
    temperature=0.7
)
print(response["choices"][0]["message"]["content"])

# ===== BRIDGE: Streaming Completions =====
async for chunk in await client.bridge.stream_complete(
    messages=[{"role": "user", "content": "Tell me a story"}],
    model="gpt-4"
):
    print(chunk["choices"][0]["delta"].get("content", ""), end="")

# ===== MCP: Memory Statistics =====
stats = await client.mcp.memory_stats({
    "labels": ["important"],
    "start_date": "2026-01-01T00:00:00Z"
})
print(f"Total conversations: {stats['total_conversations']}")

# ===== MCP: Memory Search =====
results = await client.mcp.memory_search({
    "query": "project architecture",
    "limit": 5,
    "labels": ["technical"]
})
for result in results["results"]:
    print(f"{result['label']}: {result['content']}")
```

### Unified Workflow Methods (NEW in v0.2.0)

High-level convenience methods that coordinate multiple services:

```python
# 1. Store conversation and immediately search
results = await client.store_and_query(
    messages=[
        {"role": "user", "content": "Discussed project timeline"},
        {"role": "assistant", "content": "2 week sprint cycle"}
    ],
    query="timeline",
    label="Planning"
)

# 2. Assemble context from memory + generate LLM completion
response = await client.complete_with_context(
    prompt="Continue our architecture discussion",
    context_query="architecture decisions",
    model="gpt-4",
    context_budget=4000
)

# 3. Search memory + use results in LLM prompt
response = await client.complete_with_memory(
    prompt="Summarize our past discussions about:",
    search_query="architecture microservices",
    model="gpt-4",
    limit=5
)

# 4. Stream LLM response with assembled context
async for chunk in await client.stream_with_context(
    prompt="Explain our deployment strategy",
    context_query="deployment docker kubernetes",
    model="gpt-4"
):
    print(chunk["choices"][0]["delta"].get("content", ""), end="")

# 5. Health check all services concurrently
health = await client.health_check()
print(f"Controller: {health['controller']['status']}")
print(f"Bridge: {health['bridge']['status']}")
```

### Basic Usage - Memory Controller Only

```python
from sekha import MemoryController

# Direct controller client (no Bridge/MCP)
client = MemoryController(
    base_url="http://localhost:8080",
    api_key="sk-your-api-key-here",
    timeout=30.0,
    max_retries=3
)

# Store a conversation
conversation = await client.create_conversation({
    "label": "My First Conversation",
    "folder": "/personal",
    "messages": [
        {"role": "user", "content": "Hello Sekha!"},
        {"role": "assistant", "content": "Hello! I'll remember this."}
    ]
})

# Search semantically
results = await client.query(
    query="What did we discuss?",
    limit=5
)

# Assemble context for next LLM call
context = await client.assemble_context(
    query="Continue our conversation",
    context_budget=4000,
    preferred_labels=["important"]
)
```

### Async Context Manager

```python
from sekha import SekhaClient

async with SekhaClient(
    controller_url="http://localhost:8080",
    api_key="sk-your-api-key",
    bridge_url="http://localhost:5001"
) as client:
    # All clients automatically close on exit
    await client.controller.create_conversation({...})
    await client.bridge.complete(messages=[...])
    await client.mcp.memory_stats({})
```

### Factory Function

```python
from sekha import create_sekha_client

# Convenient factory function
client = create_sekha_client(
    controller_url="http://localhost:8080",
    api_key="sk-your-api-key",
    bridge_url="http://localhost:5001",
    timeout=60.0
)
```

---

## 📋 Complete API Coverage

### Controller (Memory Operations) - 19 Endpoints

#### Conversation Management (9 endpoints)
- ✅ `create_conversation` - Store new conversations with messages
- ✅ `get_conversation` - Retrieve conversation by ID
- ✅ `list_conversations` - List with filtering and pagination
- ✅ `update_label` - Update label and folder
- ✅ `update_folder` - Move to different folder
- ✅ `pin_conversation` - Pin important conversations
- ✅ `archive_conversation` - Archive old conversations
- ✅ `delete_conversation` - Permanently delete
- ✅ `count_conversations` - Get total count

#### Search & Query (3 endpoints)
- ✅ `query` - Semantic search using vector similarity
- ✅ `full_text_search` - SQLite FTS5 full-text search
- ✅ `rebuild_embeddings` - Trigger embedding rebuild

#### Memory Orchestration (5 endpoints)
- ✅ `assemble_context` - Intelligent context assembly for LLMs
- ✅ `summarize` - Generate hierarchical summaries
- ✅ `prune_dry_run` - Get pruning suggestions
- ✅ `prune_execute` - Execute pruning operations
- ✅ `suggest_labels` - AI-powered label suggestions

#### Health & Metrics (2 endpoints)
- ✅ `health` - Health check endpoint
- ✅ `metrics` - Prometheus metrics

### Bridge (LLM Integration) - 4 Endpoints

- ✅ `complete` - Generate chat completions (OpenAI-compatible)
- ✅ `stream_complete` - Streaming chat completions with SSE
- ✅ `embed` - Generate text embeddings
- ✅ `health` - Bridge service health check

### MCP (Model Context Protocol) - 2 Endpoints

- ✅ `memory_stats` - Get memory statistics with filtering
- ✅ `memory_search` - Semantic memory search with pagination

### Unified Workflows - 5 Convenience Methods

- ✅ `store_and_query` - Store conversation and immediately search
- ✅ `complete_with_context` - Assemble context + generate completion
- ✅ `complete_with_memory` - Search memory + use in prompt
- ✅ `stream_with_context` - Stream completion with context
- ✅ `health_check` - Check all services concurrently

**[Complete API Reference](https://docs.sekha.dev/api-reference/rest-api/)**

---

## 🎯 Type Safety

The SDK provides comprehensive type safety:

```python
from sekha.types import (
    # Core Models
    Message, MessageContent, ContentPart,
    Conversation, ConversationStatus,
    MessageRole,
    
    # Request Types
    CreateConversationRequest,
    QueryRequest,
    ContextAssembleRequest,
    PruneRequest,
    
    # Response Types
    QueryResponse,
    SearchResult,
    PruneResponse,
    SummaryResponse,
    
    # Enums
    SummaryLevel,
    PruneRecommendation,
)

from sekha.type_guards import (
    is_string_content,
    is_multi_modal_content,
    extract_text,
    extract_image_urls,
    has_images,
    has_text,
)
```

**Type Guards** provide runtime validation:

```python
from sekha.type_guards import is_valid_role, extract_text

if is_valid_role("user"):
    # TypeScript-style type narrowing
    message = {"role": "user", "content": "Hello"}

# Extract text from multi-modal content
text = extract_text(message["content"])
```

---

## 🔧 Configuration

### SekhaConfig (Unified Client)

```python
from sekha import SekhaConfig, SekhaClient

# Full configuration options
config = SekhaConfig(
    controller_url="http://localhost:8080",
    api_key="sk-controller-key",          # Required
    bridge_url="http://localhost:5001",   # Optional
    bridge_api_key="bridge-key",          # Optional
    mcp_url="http://localhost:8080",      # Optional (defaults to controller)
    mcp_api_key="sk-mcp-key",            # Optional
    timeout=30.0,
    max_retries=3,
)

client = SekhaClient(config)
```

### ClientConfig (Individual Clients)

```python
from sekha.types import ClientConfig
from sekha import MemoryController

config = ClientConfig(
    base_url="http://localhost:8080",
    api_key="sk-your-api-key-here",         # Required, min 32 chars
    timeout=30.0,                           # Request timeout in seconds
    max_retries=3,                          # Max retry attempts
    default_label="MyApp",                  # Default conversation label
    rate_limit_requests=1000,               # Max requests per window
    rate_limit_window=60.0,                 # Rate limit window in seconds
)

client = MemoryController(config)
```

---

## 🛡️ Error Handling

The SDK provides specific error types:

```python
from sekha import (
    SekhaError,              # Base error
    SekhaAPIError,           # API errors (4xx, 5xx)
    SekhaAuthError,          # Authentication failures (401)
    SekhaConnectionError,    # Connection/timeout errors
    SekhaNotFoundError,      # Resource not found (404)
    SekhaValidationError,    # Invalid input (400)
)

try:
    await client.controller.get_conversation(conversation_id)
except SekhaNotFoundError:
    print("Conversation not found")
except SekhaAuthError:
    print("Invalid API key")
except SekhaConnectionError:
    print("Controller unreachable")
except SekhaError as e:
    print(f"Unexpected error: {e}")
```

---

## 🧪 Development

```bash
# Clone repository
git clone https://github.com/sekha-ai/sekha-python-sdk.git
cd sekha-python-sdk

# Install dev dependencies
pip install -e ".[dev]"

# Run tests (unit + integration)
pytest

# Run only unit tests
pytest tests/ -m "not integration"

# Run with coverage
pytest --cov=sekha --cov-report=html --cov-report=term

# Type checking
mypy sekha/

# Linting
ruff check .
black --check .

# Format code
black .
ruff check --fix .
```

### Running Integration Tests

Integration tests run against a real Sekha controller:

```bash
# Start controller locally (see sekha-controller docs)
docker compose up -d

# Set environment variables
export SEKHA_INTEGRATION_TESTS=1
export SEKHA_BASE_URL=http://localhost:8080
export SEKHA_API_KEY=your-test-key

# Run integration tests
pytest tests/test_all_endpoints.py
```

---

## 📁 Project Structure

```
sekha-python-sdk/
├── sekha/
│   ├── __init__.py           # Public API exports
│   ├── client.py             # MemoryController (main client)
│   ├── unified.py            # SekhaClient (unified interface)
│   ├── types.py              # Type definitions (dataclasses)
│   ├── models.py             # Legacy Pydantic models
│   ├── type_guards.py        # Runtime type validation
│   ├── errors.py             # Exception hierarchy
│   └── utils.py              # Utilities (rate limiter, validators)
├── tests/
│   ├── conftest.py                  # Pytest fixtures
│   ├── test_client_complete.py      # Controller tests
│   ├── test_bridge_client.py        # Bridge tests (528 lines)
│   ├── test_mcp_client.py           # MCP tests (442 lines)
│   ├── test_unified_workflows.py    # Workflow tests (616 lines)
│   ├── test_type_guards.py          # Type guard tests
│   ├── test_unified.py              # Unified client tests
│   ├── test_utils_coverage.py       # Utils tests
│   └── test_all_endpoints.py        # Integration tests
├── pyproject.toml            # Project config
├── CHANGELOG.md              # Version history
└── README.md                 # This file
```

---

## 🗺️ Roadmap

- [ ] Batch operations for bulk creates/updates
- [ ] Connection pooling optimizations
- [ ] WebSocket support for real-time updates
- [ ] Enhanced caching layer

---

## 🔗 Links

- **Main Repo:** [sekha-controller](https://github.com/sekha-ai/sekha-controller)
- **Docs:** [docs.sekha.dev](https://docs.sekha.dev)
- **Website:** [sekha.dev](https://sekha.dev)
- **Discord:** [discord.gg/sekha](https://discord.gg/gZb7U9deKH)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

---

## 📄 License

AGPL-3.0 - **[License Details](https://docs.sekha.dev/about/license/)**

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure:
- All tests pass (`pytest`)
- Code is formatted (`black .`)
- Type checks pass (`mypy sekha/`)
- Coverage remains above 90%

---

## 📝 Release Notes

### v0.2.0 (Current Release)

**Major Features:**
- ✅ Complete BridgeClient implementation (LLM completions, embeddings, streaming)
- ✅ Complete MCPClient implementation (memory stats, search)
- ✅ 5 unified workflow convenience methods
- ✅ Comprehensive test suite (2,000+ lines)
- ✅ Full async/await support across all clients
- ✅ Streaming support for LLM completions

[Full Changelog](CHANGELOG.md)
