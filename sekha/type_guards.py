"""
Type Guards for Runtime Type Checking

Provides type guard functions to validate types at runtime,
especially useful for multi-modal content validation.
"""

from typing import Any, List, TypeGuard
import sys

# Python 3.10+ type guard support
if sys.version_info >= (3, 10):
    from typing import TypeGuard

from .types import (
    MessageContent,
    ContentPart,
    TextPart,
    ImagePart,
    ConversationStatus,
    PruneRecommendation,
    SummaryLevel,
    Message,
)


# ============================================
# Content Type Guards
# ============================================


def is_string_content(content: MessageContent) -> TypeGuard[str]:
    """
    Check if content is a simple string
    
    Args:
        content: Message content to check
        
    Returns:
        True if content is a string
    """
    return isinstance(content, str)


def is_multi_modal_content(content: MessageContent) -> TypeGuard[List[ContentPart]]:
    """
    Check if content is multi-modal (array of content parts)
    
    Args:
        content: Message content to check
        
    Returns:
        True if content is a list of ContentPart
    """
    return isinstance(content, list) and len(content) > 0


def is_text_part(part: Any) -> TypeGuard[TextPart]:
    """
    Check if content part is a text part
    
    Args:
        part: Content part to check
        
    Returns:
        True if part is a TextPart
    """
    return (
        isinstance(part, dict)
        and part.get("type") == "text"
        and "text" in part
    )


def is_image_part(part: Any) -> TypeGuard[ImagePart]:
    """
    Check if content part is an image part
    
    Args:
        part: Content part to check
        
    Returns:
        True if part is an ImagePart
    """
    return (
        isinstance(part, dict)
        and part.get("type") == "image_url"
        and "image_url" in part
        and isinstance(part["image_url"], dict)
        and "url" in part["image_url"]
    )


# ============================================
# Content Extraction Helpers
# ============================================


def extract_text(content: MessageContent) -> str:
    """
    Extract text from message content
    
    Works with both string content and multi-modal content.
    For multi-modal, extracts and joins all text parts.
    
    Args:
        content: Message content
        
    Returns:
        Extracted text content
    """
    if is_string_content(content):
        return content
    
    if is_multi_modal_content(content):
        text_parts = [
            part["text"]
            for part in content
            if is_text_part(part)
        ]
        return " ".join(text_parts)
    
    return ""


def extract_image_urls(content: MessageContent) -> List[str]:
    """
    Extract image URLs from message content
    
    Args:
        content: Message content
        
    Returns:
        List of image URLs
    """
    if is_string_content(content):
        return []
    
    if is_multi_modal_content(content):
        return [
            part["image_url"]["url"]
            for part in content
            if is_image_part(part)
        ]
    
    return []


def has_images(message: Message) -> bool:
    """
    Check if message contains images
    
    Args:
        message: Message to check
        
    Returns:
        True if message contains at least one image
    """
    content = message.get("content")
    if not content:
        return False
    
    return len(extract_image_urls(content)) > 0


def has_text(message: Message) -> bool:
    """
    Check if message contains text
    
    Args:
        message: Message to check
        
    Returns:
        True if message contains text
    """
    content = message.get("content")
    if not content:
        return False
    
    return len(extract_text(content)) > 0


# ============================================
# Enum Type Guards
# ============================================


def is_valid_role(role: str) -> bool:
    """
    Check if role is valid
    
    Args:
        role: Role string to check
        
    Returns:
        True if role is valid MessageRole
    """
    from .types import MessageRole
    try:
        MessageRole(role)
        return True
    except ValueError:
        return False


def is_valid_conversation_status(status: str) -> bool:
    """
    Check if status is valid
    
    Args:
        status: Status string to check
        
    Returns:
        True if status is valid ConversationStatus
    """
    try:
        ConversationStatus(status)
        return True
    except ValueError:
        return False


def is_valid_prune_recommendation(recommendation: str) -> bool:
    """
    Check if recommendation is valid
    
    Args:
        recommendation: Recommendation string to check
        
    Returns:
        True if recommendation is valid PruneRecommendation
    """
    try:
        PruneRecommendation(recommendation)
        return True
    except ValueError:
        return False


def is_valid_summary_level(level: str) -> bool:
    """
    Check if summary level is valid
    
    Args:
        level: Level string to check
        
    Returns:
        True if level is valid SummaryLevel
    """
    try:
        SummaryLevel(level)
        return True
    except ValueError:
        return False
