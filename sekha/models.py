"""
Pydantic models for type-safe API interaction

This module provides Pydantic models for runtime validation.
For type hints, prefer importing from types.py which contains
the canonical TypedDict definitions.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# Import canonical types
from .types import (
    MessageRole,
    ConversationStatus,
    SummaryLevel,
    MemoryConfig as MemoryConfigType,
    MessageContent,
)

# Keep ClientConfig as alias for MemoryConfig
ClientConfig = MemoryConfigType


class MessageDto(BaseModel):
    """Message data transfer object
    
    Note: For type hints, use types.Message instead.
    This Pydantic model is for runtime validation.
    """
    role: MessageRole
    content: str  # Simplified for Pydantic, full MessageContent in types.py
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(use_enum_values=True)


class NewConversation(BaseModel):
    """Create a new conversation
    
    Note: For type hints, use types.CreateConversationRequest instead.
    """
    messages: List[MessageDto] = []
    label: str = Field(default="default")
    folder: str = Field(default="default")
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(use_enum_values=True)


class ConversationResponse(BaseModel):
    """Conversation response from API
    
    Note: For type hints, use types.Conversation instead.
    """
    id: str
    label: str
    folder: str
    status: str
    message_count: int
    created_at: datetime

    model_config = ConfigDict(use_enum_values=True)


class QueryRequest(BaseModel):
    """Query request matching controller DTOs
    
    Note: For type hints, use types.QueryRequest instead.
    """
    query: str = Field(..., min_length=1)
    limit: Optional[int] = Field(default=10, ge=1, le=1000)
    offset: Optional[int] = Field(default=0, ge=0)
    filters: Optional[Dict[str, Any]] = None


class QueryResult(BaseModel):
    """Single search result
    
    Note: For type hints, use types.SearchResult instead.
    """
    conversation_id: str
    message_id: str
    score: float
    content: str
    metadata: Optional[Dict[str, Any]] = None
    label: str
    folder: str
    timestamp: datetime


class QueryResponse(BaseModel):
    """Query response
    
    Note: For type hints, use types.QueryResponse instead.
    """
    results: List[QueryResult]
    total: int
    page: int
    page_size: int


class LabelSuggestion(BaseModel):
    """Auto-label suggestion
    
    Note: For type hints, use types.LabelSuggestion instead.
    """
    label: str
    confidence: float
    is_existing: bool
    reason: Optional[str] = None


class PruningSuggestion(BaseModel):
    """Intelligent pruning suggestion
    
    Note: For type hints, use types.PruningSuggestion instead.
    """
    conversation_id: str
    conversation_label: str
    last_accessed: datetime
    message_count: int
    token_estimate: int
    importance_score: float
    preview: str
    recommendation: str  # "keep" or "archive"


class HealthResponse(BaseModel):
    """Health check response
    
    Note: For type hints, use types.HealthStatus instead.
    """
    status: str
    version: str
    uptime_seconds: int


class ImportanceScore(BaseModel):
    """Message importance score"""
    score: float = Field(..., ge=1.0, le=10.0)
    reasoning: Optional[str] = None
    model: str


class SummaryResponse(BaseModel):
    """Generated summary
    
    Note: For type hints, use types.SummaryResponse instead.
    """
    conversation_id: str
    level: str
    summary: str
    generated_at: datetime
