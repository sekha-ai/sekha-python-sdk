"""
Sekha Python SDK - AI-Powered Memory System

Provides both async and sync clients for interacting with Sekha Memory Controller.
"""

from .client import SekhaClient, SyncSekhaClient, MemoryController
from .errors import (
    SekhaError,
    SekhaAPIError,
    SekhaAuthError,
    SekhaConnectionError,
    SekhaNotFoundError,
    SekhaValidationError,
)
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
    # Type Guards
    is_multi_modal_content,
    extract_text,
    extract_image_urls,
    has_images,
)

__version__ = "0.6.0"

__all__ = [
    # Clients
    "SekhaClient",
    "SyncSekhaClient",
    "MemoryController",
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
    # Type Guards
    "is_multi_modal_content",
    "extract_text",
    "extract_image_urls",
    "has_images",
]
