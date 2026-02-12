"""Pydantic models for runtime validation"""

from datetime import datetime
from typing import Any, Dict, List, Union

from pydantic import BaseModel, ConfigDict, Field

# Note: This file maintains Pydantic models for runtime validation.
# For type hints, use types from types.py which are the canonical source.
# These models will eventually be deprecated in favor of pure TypedDicts.

from .types import MemoryConfig as MemoryConfigType
from .types import MessageRole

# Re-export for backward compatibility
ClientConfig = MemoryConfigType


class MessageDto(BaseModel):
    """Message DTO for API communication"""

    model_config = ConfigDict(use_enum_values=True)

    role: Union[MessageRole, str] = Field(..., description="Message role")
    content: Union[str, List[Dict[str, Any]]] = Field(
        ..., description="Message content"
    )
    timestamp: datetime | None = Field(None, description="Message timestamp")
    metadata: Dict[str, Any] | None = Field(None, description="Message metadata")


class NewConversation(BaseModel):
    """Request to create a new conversation"""

    model_config = ConfigDict(use_enum_values=True)

    messages: List[MessageDto] = Field(..., description="Conversation messages")
    label: str = Field(..., description="Conversation label")
    folder: str = Field(default="/", description="Folder path")
    importance_score: float | None = Field(
        None, ge=1.0, le=10.0, description="Importance score (1-10)"
    )
    metadata: Dict[str, Any] | None = Field(
        None, description="Conversation metadata"
    )


class ConversationResponse(BaseModel):
    """Response containing conversation data"""

    model_config = ConfigDict(use_enum_values=True)

    id: str = Field(..., description="Conversation UUID")
    messages: List[MessageDto] = Field(..., description="Conversation messages")
    label: str = Field(..., description="Conversation label")
    folder: str = Field(..., description="Folder path")
    importance_score: float | None = Field(None, description="Importance score")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    archived: bool = Field(default=False, description="Archived status")
    metadata: Dict[str, Any] | None = Field(
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
    metadata: Dict[str, Any] | None = Field(None, description="Result metadata")


class QueryRequest(BaseModel):
    """Semantic query request"""

    query: str = Field(..., description="Search query")
    limit: int | None = Field(None, ge=1, le=100, description="Max results")
    offset: int | None = Field(None, ge=0, description="Pagination offset")
    filters: Dict[str, Any] | None = Field(None, description="Metadata filters")


class QueryResponse(BaseModel):
    """Response from semantic query"""

    results: List[SearchResult] = Field(..., description="Search results")
    total: int = Field(..., description="Total matching results")
    query: str = Field(..., description="Original query")
