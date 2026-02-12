"""
Sekha Python SDK - AI-Powered Memory System

Provides unified client interface plus individual clients for
Controller, MCP, and Bridge services.

Recommended usage:
    from sekha import SekhaClient

    sekha = SekhaClient(
        controller_url='http://localhost:8080',
        bridge_url='http://localhost:5001',
        api_key='your-api-key'
    )

    # Access individual clients
    await sekha.controller.query('search term')
    await sekha.mcp.memory_stats({})
    await sekha.bridge.complete(...)

    # Or use convenience methods
    response = await sekha.complete_with_memory('prompt', 'context')
"""

# Unified client (recommended)
from .unified import (
    BridgeClient,
    MCPClient,
    SekhaClient,
    SekhaConfig,
    create_sekha_client,
)

# Individual clients (for advanced usage)
from .client import (
    SekhaClient as MemoryController,  # Alias
    SyncSekhaClient,
)

# Pydantic models (for backward compatibility with tests)
from .models import (
    ConversationResponse,
    MessageDto,
    NewConversation,
    QueryRequest,
    QueryResponse as QueryResponseModel,
    SearchResult as SearchResultModel,
)

# Errors
from .errors import (
    SekhaAPIError,
    SekhaAuthError,
    SekhaConnectionError,
    SekhaError,
    SekhaNotFoundError,
    SekhaValidationError,
)

# Types
from .types import (
    # Core Models
    ContentPart,
    Conversation,
    ConversationStatus,
    Message,
    MessageContent,
    MessageRole,
    # Configuration
    MemoryConfig,
    # Request Types
    ContextAssembleRequest,
    CreateConversationRequest,
    PruneRequest,
    QueryRequest as QueryRequestType,
    # Response Types
    LabelSuggestion,
    PruneResponse,
    PruningSuggestion,
    QueryResponse,
    SearchResult,
    SummaryResponse,
    # Enums
    PruneRecommendation,
    SummaryLevel,
)

# Type Guards
from .type_guards import (
    extract_image_urls,
    extract_text,
    has_images,
    has_text,
    is_image_part,
    is_multi_modal_content,
    is_string_content,
    is_text_part,
    is_valid_conversation_status,
    is_valid_prune_recommendation,
    is_valid_role,
    is_valid_summary_level,
)

__version__ = "0.6.0"

__all__ = [
    # Unified Client (Recommended)
    "SekhaClient",
    "create_sekha_client",
    "SekhaConfig",
    # Individual Clients
    "MemoryController",
    "SyncSekhaClient",
    "MCPClient",
    "BridgeClient",
    # Pydantic Models (backward compatibility)
    "MessageDto",
    "NewConversation",
    "ConversationResponse",
    "QueryRequest",
    "QueryResponseModel",
    "SearchResultModel",
    # Errors
    "SekhaError",
    "SekhaAPIError",
    "SekhaAuthError",
    "SekhaConnectionError",
    "SekhaNotFoundError",
    "SekhaValidationError",
    # Types - Core
    "Message",
    "MessageContent",
    "ContentPart",
    "Conversation",
    "ConversationStatus",
    "MessageRole",
    # Types - Config
    "MemoryConfig",
    # Types - Requests
    "CreateConversationRequest",
    "QueryRequestType",
    "ContextAssembleRequest",
    "PruneRequest",
    # Types - Responses
    "QueryResponse",
    "SearchResult",
    "PruneResponse",
    "PruningSuggestion",
    "LabelSuggestion",
    "SummaryResponse",
    # Enums
    "SummaryLevel",
    "PruneRecommendation",
    # Type Guards
    "is_string_content",
    "is_multi_modal_content",
    "is_text_part",
    "is_image_part",
    "extract_text",
    "extract_image_urls",
    "has_images",
    "has_text",
    "is_valid_role",
    "is_valid_conversation_status",
    "is_valid_prune_recommendation",
    "is_valid_summary_level",
]

# Convenience: Make SekhaClient the default export equivalent
default = SekhaClient
