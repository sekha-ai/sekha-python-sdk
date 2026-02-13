"""
Sekha Type Definitions

Comprehensive type system matching JS SDK types.ts
Provides TypedDicts, dataclasses, and enums for complete type coverage.
"""

from typing import (
    Any,
    Dict,
    List,
    TypedDict,
    NotRequired,
    Union,
    Literal,
)
from dataclasses import dataclass
from enum import Enum


# ============================================
# Enums
# ============================================


class MessageRole(str, Enum):
    """Message role in conversation"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationStatus(str, Enum):
    """Conversation status"""

    ACTIVE = "active"
    ARCHIVED = "archived"
    PINNED = "pinned"


class PruneRecommendation(str, Enum):
    """Pruning recommendation level"""

    KEEP = "keep"
    REVIEW = "review"
    ARCHIVE = "archive"


class SummaryLevel(str, Enum):
    """Summary aggregation level"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# ============================================
# Core Message Types
# ============================================


class ImageUrl(TypedDict):
    """Image URL with optional detail level"""

    url: str
    detail: NotRequired[Literal["auto", "low", "high"]]


class TextPart(TypedDict):
    """Text content part"""

    type: Literal["text"]
    text: str


class ImagePart(TypedDict):
    """Image content part"""

    type: Literal["image_url"]
    image_url: ImageUrl


# Union of content parts
ContentPart = Union[TextPart, ImagePart]

# Message content can be simple string or array of parts
MessageContent = Union[str, List[ContentPart]]


class Message(TypedDict):
    """Message in a conversation"""

    role: MessageRole
    content: MessageContent
    timestamp: NotRequired[str]
    metadata: NotRequired[Dict[str, Any]]


class Conversation(TypedDict):
    """Conversation with messages"""

    id: str
    messages: List[Message]
    label: str
    folder: str
    importance_score: NotRequired[float]
    created_at: str
    updated_at: str
    archived: NotRequired[bool]
    metadata: NotRequired[Dict[str, Any]]


# ============================================
# Configuration Types
# ============================================


class MemoryConfig(TypedDict):
    """Memory controller configuration"""

    base_url: str
    api_key: str
    default_label: NotRequired[str]
    timeout: NotRequired[float]
    max_retries: NotRequired[int]
    rate_limit_requests: NotRequired[int]
    rate_limit_window: NotRequired[float]


# ============================================
# Request Types
# ============================================


class CreateConversationRequest(TypedDict):
    """Request to create a conversation"""

    messages: List[Message]
    label: str
    folder: NotRequired[str]
    importance_score: NotRequired[float]
    metadata: NotRequired[Dict[str, Any]]


class QueryRequest(TypedDict):
    """Semantic query request"""

    query: str
    limit: NotRequired[int]
    offset: NotRequired[int]
    filters: NotRequired[Dict[str, Any]]


class ContextAssembleRequest(TypedDict):
    """Request to assemble context for LLM"""

    query: str
    context_budget: NotRequired[int]
    preferred_labels: NotRequired[List[str]]
    excluded_folders: NotRequired[List[str]]


class PruneRequest(TypedDict):
    """Request to prune conversations"""

    threshold_days: NotRequired[int]
    dry_run: NotRequired[bool]


class LabelUpdateRequest(TypedDict):
    """Request to update conversation label"""

    conversation_id: str
    label: str
    folder: NotRequired[str]


class FolderUpdateRequest(TypedDict):
    """Request to update conversation folder"""

    conversation_id: str
    folder: str


class ExportRequest(TypedDict):
    """Request to export conversations"""

    label: NotRequired[str]
    folder: NotRequired[str]
    format: NotRequired[Literal["markdown", "json"]]


class SummarizeRequest(TypedDict):
    """Request to generate summary"""

    conversation_id: str
    level: NotRequired[SummaryLevel]


class MessageScoreRequest(TypedDict):
    """Request to score message importance"""

    message_id: str


class AutoLabelRequest(TypedDict):
    """Request for auto-labeling"""

    conversation_id: str
    threshold: NotRequired[float]


class RebuildEmbeddingsRequest(TypedDict):
    """Request to rebuild all embeddings"""

    force: NotRequired[bool]


class FtsSearchRequest(TypedDict):
    """Full-text search request"""

    query: str
    limit: NotRequired[int]


# ============================================
# Response Types
# ============================================


class SearchResult(TypedDict):
    """Single search result"""

    conversation_id: str
    label: str
    folder: str
    content: str
    score: float
    created_at: str
    metadata: NotRequired[Dict[str, Any]]


class PaginationInfo(TypedDict):
    """Pagination metadata"""

    page: int
    page_size: int
    total_pages: int
    total_results: int
    has_next: bool
    has_prev: bool


class QueryResponse(TypedDict):
    """Query response with results"""

    results: List[SearchResult]
    total: int
    query: str
    pagination: NotRequired[PaginationInfo]


class PruningSuggestion(TypedDict):
    """Suggestion for conversation pruning"""

    conversation_id: str
    label: str
    last_accessed: str
    days_since_access: int
    recommendation: PruneRecommendation
    reason: str


class PruneResponse(TypedDict):
    """Response from pruning operation"""

    suggestions: List[PruningSuggestion]
    total_reviewed: int
    recommended_archive: int
    recommended_keep: int


class LabelSuggestion(TypedDict):
    """AI-generated label suggestion"""

    label: str
    folder: str
    confidence: float
    reasoning: str


class LabelSuggestResponse(TypedDict):
    """Response with label suggestions"""

    conversation_id: str
    suggestions: List[LabelSuggestion]
    top_suggestion: LabelSuggestion


class SummaryResponse(TypedDict):
    """Response with generated summary"""

    conversation_id: str
    summary: str
    level: SummaryLevel
    token_count: int
    created_at: str


class HealthStatus(TypedDict):
    """Health check status"""

    status: Literal["healthy", "unhealthy", "degraded"]
    version: NotRequired[str]
    uptime: NotRequired[int]
    error: NotRequired[str]


class CountResponse(TypedDict):
    """Response with count"""

    count: int
    filters: NotRequired[Dict[str, Any]]


class ExportResponse(TypedDict):
    """Response with exported content"""

    content: str
    format: Literal["markdown", "json"]
    conversation_count: int


class MessageScoreResponse(TypedDict):
    """Response with message importance score"""

    message_id: str
    importance_score: float
    factors: Dict[str, float]
    reasoning: str


class RebuildEmbeddingsResponse(TypedDict):
    """Response from embedding rebuild"""

    status: Literal["started", "completed", "failed"]
    conversations_processed: NotRequired[int]
    errors: NotRequired[List[str]]


class FtsSearchResponse(TypedDict):
    """Full-text search response"""

    results: List[SearchResult]
    total: int
    query: str


class ContextAssembly(TypedDict):
    """Assembled context for LLM"""

    messages: List[Message]
    token_count: int
    conversation_ids: List[str]
    labels: List[str]


# ============================================
# MCP Types
# ============================================


class McpToolResponse(TypedDict):
    """Response from MCP tool"""

    content: List[Dict[str, Any]]
    isError: NotRequired[bool]


class MemoryQueryRequest(TypedDict):
    """MCP memory query request"""

    query: str
    limit: NotRequired[int]
    filters: NotRequired[Dict[str, Any]]


class MemoryStoreRequest(TypedDict):
    """MCP memory store request"""

    messages: List[Message]
    label: str
    folder: NotRequired[str]


class MemoryStatsRequest(TypedDict):
    """MCP memory stats request"""

    include_details: NotRequired[bool]


# ============================================
# Utility Types
# ============================================


class PaginationParams(TypedDict):
    """Pagination parameters"""

    page: NotRequired[int]
    page_size: NotRequired[int]


class FilterParams(TypedDict):
    """Common filter parameters"""

    label: NotRequired[str]
    folder: NotRequired[str]
    archived: NotRequired[bool]
    pinned: NotRequired[bool]


class SortParams(TypedDict):
    """Sort parameters"""

    field: str
    order: NotRequired[Literal["asc", "desc"]]


class DateRangeFilter(TypedDict):
    """Date range filter"""

    start: NotRequired[str]
    end: NotRequired[str]


class MetadataFilter(TypedDict):
    """Metadata filter"""

    key: str
    value: Any
    operator: NotRequired[Literal["eq", "ne", "gt", "lt", "contains"]]


@dataclass
class ClientConfig:
    """Configuration for Sekha client"""

    api_key: str
    base_url: str = "http://localhost:8080"
    default_label: str = "Conversation"
    timeout: float = 30.0
    max_retries: int = 3
    rate_limit_requests: int = 1000
    rate_limit_window: float = 60.0
