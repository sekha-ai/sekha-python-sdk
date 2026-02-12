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
    SekhaClient,
    create_sekha_client,
    SekhaConfig,
    MCPClient,
    BridgeClient,
)

# Individual clients (for advanced usage)
from .client import (
    SekhaClient as MemoryController,  # Alias
    SyncSekhaClient,
)

# Errors
from .errors import (
    SekhaError,
    SekhaAPIError,
    SekhaAuthError,
    SekhaConnectionError,
    SekhaNotFoundError,
    SekhaValidationError,
)

# Types
from .types import (
    # Core Models
    Message,
    MessageContent,
    ContentPart,
    Conversation,
    ConversationStatus,
    MessageRole,
    # Configuration
    MemoryConfig,
    # Request Types
    CreateConversationRequest,
    QueryRequest,
    ContextAssembleRequest,
    PruneRequest,
    # Response Types
    QueryResponse,
    SearchResult,
    PruneResponse,
    PruningSuggestion,
    LabelSuggestion,
    SummaryResponse,
    # Enums
    SummaryLevel,
    PruneRecommendation,
)

# Type Guards & Validators
from .type_guards import (
    # Core Type Guards (8)
    is_multi_modal_content,
    is_text_part,
    is_image_part,
    extract_text,
    extract_image_urls,
    has_images,
    is_valid_status,
    is_valid_recommendation,
    # Additional Validators
    is_valid_role,
    validate_message,
    validate_conversation,
    validate_api_response,
    validate_request_payload,
    is_valid_uuid,
    is_valid_iso_datetime,
    is_valid_url,
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
    "QueryRequest",
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
    
    # Type Guards (8 Core)
    "is_multi_modal_content",
    "is_text_part",
    "is_image_part",
    "extract_text",
    "extract_image_urls",
    "has_images",
    "is_valid_status",
    "is_valid_recommendation",
    
    # Validators
    "is_valid_role",
    "validate_message",
    "validate_conversation",
    "validate_api_response",
    "validate_request_payload",
    "is_valid_uuid",
    "is_valid_iso_datetime",
    "is_valid_url",
]

# Convenience: Make SekhaClient the default export equivalent
default = SekhaClient
