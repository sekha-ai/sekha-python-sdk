"""
Complete Type Definitions for Sekha Python SDK

All types match controller (Rust) and JS SDK exactly.
Organized by domain: Core, API, MCP, Bridge, Utilities

Note: Uses TypedDict for dict-based types and dataclasses for objects
"""

from typing import (
    TypedDict,
    Union,
    List,
    Dict,
    Any,
    Optional,
    Literal,
    Protocol,
)
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# ============================================
# CORE MODELS
# ============================================

class MessageRole(str, Enum):
    """Message role in conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ConversationStatus(str, Enum):
    """Conversation status"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    PINNED = "pinned"


class PruneRecommendation(str, Enum):
    """Pruning recommendation type"""
    ARCHIVE = "archive"
    KEEP = "keep"
    REVIEW = "review"


class SummaryLevel(str, Enum):
    """Summary aggregation level"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ImageUrl(TypedDict, total=False):
    """Image URL with optional detail level for vision models"""
    url: str  # Required
    detail: Optional[str]  # 'low' | 'high' | 'auto'


class TextPart(TypedDict):
    """Text content part"""
    type: Literal["text"]
    text: str


class ImagePart(TypedDict):
    """Image content part"""
    type: Literal["image_url"]
    image_url: ImageUrl


# Content part for multi-modal messages (text + images)
ContentPart = Union[TextPart, ImagePart]

# Message content - either simple text or multi-modal parts
MessageContent = Union[str, List[ContentPart]]


class Message(TypedDict, total=False):
    """Message in a conversation
    
    Supports both simple text and multi-modal content (text + images)
    """
    role: str  # Required: 'user' | 'assistant' | 'system'
    content: MessageContent  # Required
    timestamp: Optional[str]
    metadata: Optional[Dict[str, Any]]


class Conversation(TypedDict, total=False):
    """Conversation type matching controller ConversationResponse
    
    All fields match src/api/dto.rs exactly
    """
    id: str  # Required
    label: str  # Required
    folder: str  # Required
    status: str  # Required
    message_count: int  # Required, snake_case from controller
    created_at: str  # Required, ISO 8601 datetime
    updated_at: Optional[str]
    importance_score: Optional[float]  # Optional, 1-10
    word_count: Optional[int]
    session_count: Optional[int]


# ============================================
# CONFIGURATION
# ============================================

@dataclass
class MemoryConfig:
    """Memory controller configuration"""
    api_key: str
    base_url: str = "http://localhost:8080"
    default_label: Optional[str] = None
    timeout: float = 30.0
    max_retries: int = 3
    rate_limit_requests: int = 1000  # per minute
    rate_limit_window: float = 60.0


# ============================================
# REQUEST TYPES
# ============================================

class CreateConversationRequest(TypedDict, total=False):
    """Create conversation request"""
    messages: List[Message]  # Required
    label: str  # Required
    folder: Optional[str]
    importance_score: Optional[float]
    metadata: Optional[Dict[str, Any]]


class UpdateLabelRequest(TypedDict):
    """Update label request"""
    label: str
    folder: str  # Required - preserves folder structure


class UpdateFolderRequest(TypedDict):
    """Update folder request"""
    folder: str


class QueryRequest(TypedDict, total=False):
    """Query request"""
    query: str  # Required
    filters: Optional[Any]
    limit: Optional[int]
    offset: Optional[int]


class FtsSearchRequest(TypedDict, total=False):
    """Full-text search request"""
    query: str  # Required
    limit: Optional[int]


class ContextAssembleRequest(TypedDict, total=False):
    """Context assemble request"""
    query: str  # Required
    preferred_labels: Optional[List[str]]
    context_budget: Optional[int]  # Token budget
    excluded_folders: Optional[List[str]]


class SummarizeRequest(TypedDict):
    """Summarize request"""
    conversation_id: str
    level: str  # 'daily' | 'weekly' | 'monthly'


class PruneRequest(TypedDict, total=False):
    """Prune dry-run request"""
    threshold_days: int  # Required
    importance_threshold: Optional[float]


class ExecutePruneRequest(TypedDict):
    """Execute prune request"""
    conversation_ids: List[str]


class LabelSuggestRequest(TypedDict):
    """Label suggest request"""
    conversation_id: str


class ListFilter(TypedDict, total=False):
    """List/filter options for conversations"""
    label: Optional[str]
    folder: Optional[str]
    pinned: Optional[bool]
    archived: Optional[bool]
    page: Optional[int]
    page_size: Optional[int]
    limit: Optional[int]  # Alias for page_size
    offset: Optional[int]  # Alternative pagination


class ExportOptions(TypedDict, total=False):
    """Export options"""
    label: Optional[str]
    format: Optional[str]  # 'markdown' | 'json'
    conversation_id: Optional[str]  # For single conversation export
    include_metadata: Optional[bool]


# ============================================
# RESPONSE TYPES
# ============================================

class SearchResult(TypedDict):
    """Search result matching controller SearchResultDto"""
    conversation_id: str
    message_id: str
    score: float
    content: str
    metadata: Dict[str, Any]
    label: str
    folder: str
    timestamp: str  # ISO 8601


class QueryResponse(TypedDict):
    """Query response with pagination"""
    results: List[SearchResult]
    total: int
    page: int
    page_size: int


class FtsMessage(TypedDict):
    """FTS message result"""
    id: str
    conversation_id: str
    role: str
    content: str
    timestamp: str
    rank: float  # FTS rank/score


class FtsSearchResponse(TypedDict):
    """Full-text search response"""
    results: List[FtsMessage]
    total: int


class ContextAssembly(TypedDict, total=False):
    """Context assembly result"""
    messages: List[Message]  # Required: Assembled messages for LLM context
    estimated_tokens: Optional[int]
    conversations_used: Optional[int]


class PruningSuggestion(TypedDict):
    """Pruning suggestion from controller"""
    conversation_id: str
    conversation_label: str
    last_accessed: str  # ISO 8601
    message_count: int
    token_estimate: int
    importance_score: float
    preview: str
    recommendation: str  # PruneRecommendation


class PruneResponse(TypedDict, total=False):
    """Prune dry-run response"""
    suggestions: List[PruningSuggestion]  # Required
    total: int  # Required
    estimated_token_savings: Optional[int]


class LabelSuggestion(TypedDict):
    """Label suggestion from AI"""
    label: str
    confidence: float  # 0-1
    is_existing: bool  # Whether label already exists
    reason: str  # AI explanation


class LabelSuggestResponse(TypedDict):
    """Label suggest response"""
    conversation_id: str
    suggestions: List[LabelSuggestion]


class SummaryResponse(TypedDict):
    """Summary response"""
    conversation_id: str
    level: str
    summary: str
    generated_at: str  # ISO 8601


class HealthStatus(TypedDict):
    """Health status response"""
    status: str
    version: str
    uptime_seconds: int


class ErrorResponse(TypedDict):
    """Error response"""
    error: str
    code: int


class RebuildEmbeddingsResponse(TypedDict):
    """Rebuild embeddings response"""
    success: bool
    message: str
    estimated_completion_seconds: int


class Metrics(TypedDict):
    """Metrics response (placeholder - controller returns 'not_implemented')"""
    metrics: str
    # Flexible for future metrics


class CountResponse(TypedDict, total=False):
    """Count response"""
    count: int  # Required
    label: Optional[str]
    folder: Optional[str]


# ============================================
# MCP (Model Context Protocol) TYPES
# ============================================

class McpToolResponse(TypedDict, total=False):
    """Standard MCP tool response wrapper"""
    success: bool  # Required
    data: Optional[Any]
    error: Optional[str]


class MemoryStoreRequest(TypedDict):
    """MCP memory store request"""
    label: str
    folder: str
    messages: List[Message]


class MemoryQueryRequest(TypedDict, total=False):
    """MCP memory query request"""
    query: str  # Required
    filters: Optional[Any]
    limit: Optional[int]


class MemoryQueryResponse(TypedDict, total=False):
    """MCP memory query response"""
    success: bool  # Required
    data: QueryResponse  # Required
    error: Optional[str]


# ============================================
# UTILITY TYPES
# ============================================

class PaginationParams(TypedDict, total=False):
    """Pagination parameters"""
    page: Optional[int]
    page_size: Optional[int]
    limit: Optional[int]
    offset: Optional[int]


class FilterParams(TypedDict, total=False):
    """Filter parameters for searches"""
    labels: Optional[List[str]]
    folder: Optional[str]
    status: Optional[str]  # ConversationStatus
    importance_min: Optional[float]
    importance_max: Optional[float]
    date_from: Optional[str]
    date_to: Optional[str]


class SortParams(TypedDict):
    """Sort parameters"""
    field: str  # 'created_at' | 'updated_at' | 'importance_score' | 'message_count'
    order: str  # 'asc' | 'desc'


class BulkOperationResult(TypedDict, total=False):
    """Bulk operation result"""
    success: int  # Required
    failed: int  # Required
    errors: Optional[List[Dict[str, str]]]  # [{"id": "...", "error": "..."}]


# ============================================
# TYPE GUARDS & HELPERS
# ============================================

def is_multi_modal_content(content: MessageContent) -> bool:
    """Check if content is multi-modal (has images)"""
    return isinstance(content, list)


def is_text_part(part: ContentPart) -> bool:
    """Check if content part is text"""
    return isinstance(part, dict) and part.get("type") == "text"


def is_image_part(part: ContentPart) -> bool:
    """Check if content part is image"""
    return isinstance(part, dict) and part.get("type") == "image_url"


def extract_text(content: MessageContent) -> str:
    """Extract text from message content"""
    if isinstance(content, str):
        return content
    
    text_parts = [part["text"] for part in content if is_text_part(part)]
    return " ".join(text_parts)


def extract_image_urls(content: MessageContent) -> List[str]:
    """Extract image URLs from message content"""
    if isinstance(content, str):
        return []
    
    return [
        part["image_url"]["url"]
        for part in content
        if is_image_part(part)
    ]


def has_images(message: Message) -> bool:
    """Check if message has images"""
    return len(extract_image_urls(message["content"])) > 0


def is_valid_status(status: str) -> bool:
    """Validate conversation status"""
    return status in ["active", "archived", "pinned"]


def is_valid_recommendation(rec: str) -> bool:
    """Validate prune recommendation"""
    return rec in ["archive", "keep", "review"]


# ============================================
# BACKWARDS COMPATIBILITY ALIASES
# ============================================

# Deprecated aliases for migration
ConversationDto = Conversation
SearchResultDto = SearchResult
PruningSuggestionDto = PruningSuggestion
LabelSuggestionDto = LabelSuggestion
ClientConfig = MemoryConfig  # Keep for backwards compat
