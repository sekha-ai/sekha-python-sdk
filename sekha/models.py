"""Pydantic models for runtime validation"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

# Note: This file maintains Pydantic models for runtime validation.
# For type hints, use types from types.py which are the canonical source.
# These models will eventually be deprecated in favor of pure TypedDicts.

from .types import (
    MemoryConfig as MemoryConfigType,
    MessageRole,
    ConversationStatus,
    PruneRecommendation,
)

# Re-export for backward compatibility
ClientConfig = MemoryConfigType

# Re-export enums for backward compatibility
__all__ = [
    "MessageRole",
    "ConversationStatus",
    "ClientConfig",
    "MessageDto",
    "NewConversation",
    "ConversationResponse",
    "SearchResult",
    "QueryRequest",
    "QueryResponse",
    "QueryResult",
    "ImportanceScore",
    "LabelSuggestion",
    "PruningSuggestion",
]


class MessageDto(BaseModel):
    """Message DTO for API communication"""

    model_config = ConfigDict(use_enum_values=True)

    role: Union[MessageRole, str] = Field(..., description="Message role")
    content: Union[str, List[Dict[str, Any]]] = Field(
        ..., description="Message content"
    )
    timestamp: Optional[datetime] = Field(None, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Message metadata"
    )


class NewConversation(BaseModel):
    """Request to create a new conversation"""

    model_config = ConfigDict(use_enum_values=True)

    messages: List[MessageDto] = Field(..., description="Conversation messages")
    label: str = Field(..., description="Conversation label")
    folder: str = Field(default="/", description="Folder path")
    importance_score: Optional[float] = Field(
        None, ge=1.0, le=10.0, description="Importance score (1-10)"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Conversation metadata"
    )


class ConversationResponse(BaseModel):
    """Response containing conversation data"""

    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(..., description="Conversation UUID")
    messages: List[MessageDto] = Field(..., description="Conversation messages")
    label: str = Field(..., description="Conversation label")
    folder: str = Field(..., description="Folder path")
    importance_score: Optional[float] = Field(
        None, description="Importance score"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    archived: bool = Field(default=False, description="Archived status")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Conversation metadata"
    )


class SearchResult(BaseModel):
    """Search result from query"""

    conversation_id: str = Field(..., description="Conversation UUID")
    label: str = Field(..., description="Conversation label")
    folder: str = Field(..., description="Folder path")
    content: str = Field(..., description="Result content")
    score: float = Field(..., description="Relevance score")
    created_at: datetime = Field(..., description="Creation timestamp")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Result metadata"
    )


class QueryResult(BaseModel):
    """Individual query result (alias for SearchResult for backward compat)"""

    conversation_id: str = Field(..., description="Conversation UUID")
    message_id: str = Field(..., description="Message UUID")
    score: float = Field(..., description="Relevance score")
    content: str = Field(..., description="Result content")
    label: str = Field(..., description="Conversation label")
    folder: str = Field(..., description="Folder path")
    timestamp: datetime = Field(..., description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Result metadata"
    )


class QueryRequest(BaseModel):
    """Semantic query request"""

    query: str = Field(..., description="Search query")
    limit: int = Field(default=10, ge=1, le=100, description="Max results")
    offset: Optional[int] = Field(None, ge=0, description="Pagination offset")
    filters: Optional[Dict[str, Any]] = Field(
        None, description="Metadata filters"
    )


class QueryResponse(BaseModel):
    """Response from semantic query"""

    results: List[SearchResult] = Field(..., description="Search results")
    total: int = Field(..., description="Total matching results")
    query: str = Field(..., description="Original query")


class ImportanceScore(BaseModel):
    """AI-generated importance score for content"""

    score: float = Field(..., ge=1.0, le=10.0, description="Importance score (1-10)")
    reasoning: str = Field(..., description="Explanation for the score")
    model: str = Field(..., description="Model used for scoring")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata"
    )


class LabelSuggestion(BaseModel):
    """AI-generated label suggestion"""

    label: str = Field(..., description="Suggested label")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score (0-1)"
    )
    is_existing: bool = Field(
        default=False, description="Whether label already exists"
    )
    reason: str = Field(..., description="Reasoning for suggestion")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata"
    )


class PruningSuggestion(BaseModel):
    """Suggestion for conversation pruning"""

    conversation_id: str = Field(..., description="Conversation UUID")
    conversation_label: str = Field(..., description="Conversation label")
    last_accessed: datetime = Field(..., description="Last access timestamp")
    message_count: int = Field(..., description="Number of messages")
    token_estimate: int = Field(..., description="Estimated token count")
    importance_score: float = Field(
        ..., ge=1.0, le=10.0, description="Importance score"
    )
    preview: str = Field(..., description="Preview of conversation")
    recommendation: str = Field(..., description="Pruning recommendation")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata"
    )
