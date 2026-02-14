# Changelog

All notable changes to the Sekha Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-02-14

### 🎉 Major Release - Complete Unified Client

This release completes the unified client architecture with full implementations of BridgeClient, MCPClient, and 5 high-level convenience methods for common workflows.

### Added

#### BridgeClient (LLM Bridge Integration)
- **`complete()`** - Generate chat completions via `/v1/chat/completions` (OpenAI-compatible)
- **`stream_complete()`** - Streaming chat completions with SSE
- **`embed()`** - Generate text embeddings via `/embed`
- **`health()`** - Health check for bridge service
- Full retry logic with exponential backoff
- Comprehensive error handling (connection, timeout, API errors)
- Async context manager support
- Type-safe request/response handling

#### MCPClient (Model Context Protocol)
- **`memory_stats()`** - Get memory statistics with filtering (labels, date ranges)
- **`memory_search()`** - Semantic memory search with pagination
- HTTP client with automatic retries
- Exponential backoff retry strategy
- Async context manager support
- Comprehensive error handling

#### Unified Workflow Methods
- **`store_and_query()`** - Store conversation and immediately search (Controller only)
- **`complete_with_context()`** - Assemble context from memory + generate LLM completion (Controller + Bridge)
- **`complete_with_memory()`** - Search memory + use results in LLM prompt (Controller + Bridge)
- **`stream_with_context()`** - Stream LLM response with assembled context (Controller + Bridge)
- **`health_check()`** - Check health of all services concurrently (Controller + Bridge)

#### Testing
- **test_bridge_client.py** (528 lines) - 19 comprehensive BridgeClient tests
  - Completion tests (basic, streaming, with parameters)
  - Embedding tests
  - Health check tests
  - Error handling (404, 500, connection, timeout)
  - Retry logic tests
  - Context manager tests
- **test_mcp_client.py** (442 lines) - 18 comprehensive MCPClient tests
  - Memory stats tests (basic, filters, date ranges)
  - Memory search tests (pagination, filters)
  - Error handling
  - Retry logic tests
  - Context manager tests
- **test_unified_workflows.py** (616 lines) - 15 workflow integration tests
  - store_and_query tests
  - complete_with_context tests
  - complete_with_memory tests
  - stream_with_context tests
  - health_check tests
  - Multi-workflow integration tests

#### Documentation
- Complete docstrings for all BridgeClient methods with examples
- Complete docstrings for all MCPClient methods with examples
- Complete docstrings for all workflow methods with examples
- Type hints for all public APIs
- Usage examples in README

### Changed

#### Breaking Changes
- **SekhaClient** now fully initializes Bridge and MCP clients (no longer stubs)
- **BridgeClient** methods now require proper implementation calls (stubs removed)
- **MCPClient** methods now require proper implementation calls (stubs removed)
- Context manager lifecycle now manages all three clients (Controller, MCP, Bridge)

#### Architecture
- Unified client now coordinates between Controller, MCP, and Bridge services
- Consistent error handling across all clients
- Consistent retry logic with exponential backoff
- Configuration properly propagates to all sub-clients

### Fixed
- Fixed async generator handling in streaming tests
- Fixed SekhaAPIError constructor calls (added missing `response` parameter)
- Fixed Mock attribute handling in f-string formatting tests
- Fixed retry logic to properly handle 4xx vs 5xx errors
- Fixed streaming chunk parsing for SSE format

### Infrastructure
- CI/CD pipeline tests all new clients and workflows
- Test coverage maintained at 90%+
- All linting and type checking passes
- Integration tests validate against real controller

### Migration Guide from v0.1.x

If you were using the unified client stubs:

#### Before (v0.1.x):
```python
from sekha import SekhaClient

client = SekhaClient(
    controller_url="http://localhost:8080",
    api_key="sk-test-key",
    bridge_url="http://localhost:5001"
)

# Only controller methods worked
await client.controller.create_conversation({...})

# Bridge/MCP were stubs (NotImplementedError)
# await client.bridge.complete(...)  # Would fail
# await client.mcp.memory_stats({})  # Would fail
```

#### After (v0.2.0):
```python
from sekha import SekhaClient

client = SekhaClient(
    controller_url="http://localhost:8080",
    api_key="sk-test-key",
    bridge_url="http://localhost:5001"
)

# All clients now fully functional
await client.controller.create_conversation({...})
await client.bridge.complete(messages=[...])
await client.mcp.memory_stats({})

# New: Convenience workflows
response = await client.complete_with_memory(
    prompt="Explain our architecture",
    search_query="architecture"
)

# New: Health checks
health = await client.health_check()
print(f"Controller: {health['controller']['status']}")
print(f"Bridge: {health['bridge']['status']}")
```

### Pull Requests

- [#18](https://github.com/sekha-ai/sekha-python-sdk/pull/18) - feat: Implement BridgeClient with full LLM Bridge API support (v0.2.0)
- [#19](https://github.com/sekha-ai/sekha-python-sdk/pull/19) - feat: Implement MCPClient with memory operations (v0.2.0)
- [#20](https://github.com/sekha-ai/sekha-python-sdk/pull/20) - feat: Complete unified workflows with all convenience methods (v0.2.0)

### Commits

See [full commit history](https://github.com/sekha-ai/sekha-python-sdk/commits/main/) for detailed changes.

---

## [0.1.0] - 2026-01-XX (Baseline)

### Initial Release

#### Added
- **MemoryController client** - Full REST API coverage (19 endpoints)
- **SekhaClient** - Unified client interface (Controller, Bridge stub, MCP stub)
- **Type system** - Complete type definitions with runtime validation
- **Error hierarchy** - SekhaError, SekhaAPIError, SekhaAuthError, etc.
- **Rate limiting** - Built-in token bucket rate limiter
- **Retry logic** - Automatic retries with exponential backoff
- **Test coverage** - 90%+ coverage with unit and integration tests
- **CI/CD** - GitHub Actions pipeline with lint, test, security checks

#### API Coverage (19 Endpoints)

**Conversation Management (9 endpoints)**
- `create_conversation` - Store new conversations
- `get_conversation` - Retrieve by ID
- `list_conversations` - List with filtering
- `update_label` - Update conversation label
- `update_folder` - Move to folder
- `pin_conversation` - Pin important conversations
- `archive_conversation` - Archive old conversations
- `delete_conversation` - Delete permanently
- `count_conversations` - Get total count

**Search & Query (3 endpoints)**
- `query` - Semantic search
- `full_text_search` - FTS5 search
- `rebuild_embeddings` - Rebuild embeddings

**Memory Orchestration (5 endpoints)**
- `assemble_context` - Intelligent context assembly
- `summarize` - Hierarchical summaries
- `prune_dry_run` - Pruning suggestions
- `prune_execute` - Execute pruning
- `suggest_labels` - AI label suggestions

**Health & Metrics (2 endpoints)**
- Health checks
- Prometheus metrics

---

## [Unreleased]

### Planned Features
- Streaming support for summaries
- Batch operations
- Connection pooling optimizations
- WebSocket support for real-time updates
- Enhanced rate limiting with quota tracking
- Caching layer for frequently accessed data

---

## Version History

- **v0.2.0** (2026-02-14) - Complete unified client with Bridge + MCP
- **v0.1.0** (2026-01-XX) - Initial release with Controller client

---

## Links

- [GitHub Repository](https://github.com/sekha-ai/sekha-python-sdk)
- [Documentation](https://docs.sekha.dev/sdks/python-sdk/)
- [Issue Tracker](https://github.com/sekha-ai/sekha-python-sdk/issues)
- [PyPI Package](https://pypi.org/project/sekha-python-sdk/) (coming soon)
