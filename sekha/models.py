"""
Pydantic models for type-safe API interaction
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ConversationStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    PINNED = "pinned"


class SummaryLevel(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class ClientConfig:
    """Client configuration"""

    api_key: str
    base_url: str = "http://localhost:8080"
    timeout: float = 30.0
    max_retries: int = 3
    rate_limit_requests: int = 1000  # per minute
    rate_limit_window: float = 60.0
    default_label: Optional[str] = None

    def __post_init__(self):
        """Validate configuration after initialization"""
        from .utils import validate_api_key, validate_base_url

        validate_api_key(self.api_key)
        validate_base_url(self.base_url)

        if self.timeout <= 0:
            raise ValueError("timeout must be positive")

        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")


class MessageDto(BaseModel):
    """Message data transfer object"""

    role: MessageRole
    content: str
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(use_enum_values=True)


class NewConversation(BaseModel):
    """Create a new conversation"""

    messages: List[MessageDto] = []
    label: str = Field(default="default")
    folder: str = Field(default="default")
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(use_enum_values=True)


class ConversationResponse(BaseModel):
    """Conversation response from API"""

    id: str
    label: str
    folder: str
    status: str
    message_count: int
    created_at: datetime

    model_config = ConfigDict(use_enum_values=True)


class QueryRequest(BaseModel):
    """Query request matching controller DTOs"""

    query: str = Field(..., min_length=1)
    limit: Optional[int] = Field(default=10, ge=1, le=1000)
    offset: Optional[int] = Field(default=0, ge=0)
    filters: Optional[Dict[str, Any]] = None


class QueryResult(BaseModel):
    """Single search result"""

    conversation_id: str
    message_id: str
    score: float
    content: str
    metadata: Optional[Dict[str, Any]] = None
    label: str
    folder: str
    timestamp: datetime


class QueryResponse(BaseModel):
    """Query response"""

    results: List[QueryResult]
    total: int
    page: int
    page_size: int


class LabelSuggestion(BaseModel):
    """Auto-label suggestion"""

    label: str
    confidence: float
    is_existing: bool
    reason: Optional[str] = None


class PruningSuggestion(BaseModel):
    """Intelligent pruning suggestion"""

    conversation_id: str
    conversation_label: str
    last_accessed: datetime
    message_count: int
    token_estimate: int
    importance_score: float
    preview: str
    recommendation: str  # "keep" or "archive"


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    version: str
    uptime_seconds: int


class ImportanceScore(BaseModel):
    """Message importance score"""

    score: float = Field(..., ge=1.0, le=10.0)
    reasoning: Optional[str] = None
    model: str


class SummaryResponse(BaseModel):
    """Generated summary"""

    conversation_id: str
    level: str
    summary: str
    generated_at: datetime
