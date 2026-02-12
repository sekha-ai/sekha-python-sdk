"""
Type Guards and Validation Helpers

Provides runtime type checking and validation functions for Sekha types.
Uses Python's TypeGuard (3.10+) for proper type narrowing.
"""

from typing import Any, Dict, List, TypeGuard, Union
import sys

# Import all types
from .types import (
    Message,
    MessageContent,
    ContentPart,
    TextPart,
    ImagePart,
    Conversation,
    SearchResult,
    QueryResponse,
    PruneResponse,
    ConversationStatus,
    PruneRecommendation,
)

# Check Python version for TypeGuard support
PY310_PLUS = sys.version_info >= (3, 10)


# ============================================
# CONTENT TYPE GUARDS
# ============================================

if PY310_PLUS:
    def is_multi_modal_content(content: MessageContent) -> TypeGuard[List[ContentPart]]:
        """
        Check if content is multi-modal (array of content parts)
        
        Args:
            content: Message content to check
            
        Returns:
            True if content is multi-modal (list of parts)
            
        Example:
            ```python
            if is_multi_modal_content(message['content']):
                # Type narrowed to List[ContentPart]
                for part in message['content']:
                    print(part['type'])
            ```
        """
        return isinstance(content, list)
else:
    def is_multi_modal_content(content: MessageContent) -> bool:
        """Check if content is multi-modal (has images)"""
        return isinstance(content, list)


if PY310_PLUS:
    def is_text_part(part: Any) -> TypeGuard[TextPart]:
        """
        Check if content part is text
        
        Args:
            part: Content part to check
            
        Returns:
            True if part is a text content part
            
        Example:
            ```python
            if is_text_part(part):
                # Type narrowed to TextPart
                print(part['text'])
            ```
        """
        return (
            isinstance(part, dict) and
            part.get("type") == "text" and
            "text" in part and
            isinstance(part["text"], str)
        )
else:
    def is_text_part(part: Any) -> bool:
        """Check if content part is text"""
        return (
            isinstance(part, dict) and
            part.get("type") == "text" and
            "text" in part
        )


if PY310_PLUS:
    def is_image_part(part: Any) -> TypeGuard[ImagePart]:
        """
        Check if content part is image
        
        Args:
            part: Content part to check
            
        Returns:
            True if part is an image content part
            
        Example:
            ```python
            if is_image_part(part):
                # Type narrowed to ImagePart
                print(part['image_url']['url'])
            ```
        """
        return (
            isinstance(part, dict) and
            part.get("type") == "image_url" and
            "image_url" in part and
            isinstance(part["image_url"], dict) and
            "url" in part["image_url"]
        )
else:
    def is_image_part(part: Any) -> bool:
        """Check if content part is image"""
        return (
            isinstance(part, dict) and
            part.get("type") == "image_url" and
            "image_url" in part
        )


# ============================================
# CONTENT EXTRACTION HELPERS
# ============================================

def extract_text(content: MessageContent) -> str:
    """
    Extract text from message content
    
    Handles both simple string content and multi-modal content with text parts.
    
    Args:
        content: Message content (string or list of parts)
        
    Returns:
        Extracted text content
        
    Example:
        ```python
        text = extract_text(message['content'])
        print(f"Text: {text}")
        ```
    """
    if isinstance(content, str):
        return content
    
    if not is_multi_modal_content(content):
        return ""
    
    text_parts = [
        part["text"] 
        for part in content 
        if is_text_part(part)
    ]
    return " ".join(text_parts)


def extract_image_urls(content: MessageContent) -> List[str]:
    """
    Extract image URLs from message content
    
    Args:
        content: Message content (string or list of parts)
        
    Returns:
        List of image URLs (empty if no images)
        
    Example:
        ```python
        urls = extract_image_urls(message['content'])
        print(f"Found {len(urls)} images")
        for url in urls:
            print(f"  - {url}")
        ```
    """
    if isinstance(content, str):
        return []
    
    if not is_multi_modal_content(content):
        return []
    
    return [
        part["image_url"]["url"]
        for part in content
        if is_image_part(part)
    ]


def has_images(message: Message) -> bool:
    """
    Check if message has images
    
    Args:
        message: Message to check
        
    Returns:
        True if message contains at least one image
        
    Example:
        ```python
        if has_images(message):
            print("This message has images")
            urls = extract_image_urls(message['content'])
        ```
    """
    return len(extract_image_urls(message.get("content", ""))) > 0  # type: ignore


# ============================================
# ENUM VALIDATION
# ============================================

if PY310_PLUS:
    def is_valid_status(status: str) -> TypeGuard[ConversationStatus]:
        """
        Validate conversation status
        
        Args:
            status: Status string to validate
            
        Returns:
            True if status is valid
            
        Example:
            ```python
            if is_valid_status(status):
                # Type narrowed to ConversationStatus literal
                conversation['status'] = status
            ```
        """
        return status in ["active", "archived", "pinned"]
else:
    def is_valid_status(status: str) -> bool:
        """Validate conversation status"""
        return status in ["active", "archived", "pinned"]


if PY310_PLUS:
    def is_valid_recommendation(rec: str) -> TypeGuard[PruneRecommendation]:
        """
        Validate prune recommendation
        
        Args:
            rec: Recommendation string to validate
            
        Returns:
            True if recommendation is valid
            
        Example:
            ```python
            if is_valid_recommendation(rec):
                # Type narrowed to PruneRecommendation literal
                apply_recommendation(rec)
            ```
        """
        return rec in ["archive", "keep", "review"]
else:
    def is_valid_recommendation(rec: str) -> bool:
        """Validate prune recommendation"""
        return rec in ["archive", "keep", "review"]


def is_valid_role(role: str) -> bool:
    """
    Validate message role
    
    Args:
        role: Role string to validate
        
    Returns:
        True if role is valid
    """
    return role in ["user", "assistant", "system", "tool"]


# ============================================
# COMPREHENSIVE VALIDATORS
# ============================================

def validate_message(data: Any) -> TypeGuard[Message]:
    """
    Validate message structure
    
    Comprehensive validation ensuring all required fields are present
    and have correct types.
    
    Args:
        data: Data to validate as Message
        
    Returns:
        True if data is a valid Message
        
    Raises:
        ValueError: If validation fails with details
        
    Example:
        ```python
        try:
            if validate_message(data):
                # Safe to use as Message
                print(f"Valid message from {data['role']}")
        except ValueError as e:
            print(f"Invalid message: {e}")
        ```
    """
    if not isinstance(data, dict):
        raise ValueError("Message must be a dictionary")
    
    # Check required fields
    if "role" not in data:
        raise ValueError("Message missing required field: role")
    if "content" not in data:
        raise ValueError("Message missing required field: content")
    
    # Validate role
    if not is_valid_role(data["role"]):
        raise ValueError(f"Invalid role: {data['role']}")
    
    # Validate content
    content = data["content"]
    if isinstance(content, str):
        # Simple text content is valid
        pass
    elif isinstance(content, list):
        # Multi-modal content - validate each part
        for i, part in enumerate(content):
            if not isinstance(part, dict):
                raise ValueError(f"Content part {i} must be a dictionary")
            if "type" not in part:
                raise ValueError(f"Content part {i} missing type field")
            
            part_type = part["type"]
            if part_type == "text":
                if "text" not in part:
                    raise ValueError(f"Text part {i} missing text field")
            elif part_type == "image_url":
                if "image_url" not in part:
                    raise ValueError(f"Image part {i} missing image_url field")
                if "url" not in part["image_url"]:
                    raise ValueError(f"Image part {i} missing url in image_url")
            else:
                raise ValueError(f"Invalid content part type: {part_type}")
    else:
        raise ValueError("Content must be string or list of content parts")
    
    return True


def validate_conversation(data: Any) -> TypeGuard[Conversation]:
    """
    Validate conversation structure
    
    Args:
        data: Data to validate as Conversation
        
    Returns:
        True if data is a valid Conversation
        
    Raises:
        ValueError: If validation fails with details
    """
    if not isinstance(data, dict):
        raise ValueError("Conversation must be a dictionary")
    
    # Check required fields
    required_fields = ["id", "label", "folder", "status", "message_count", "created_at"]
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Conversation missing required field: {field}")
    
    # Validate types
    if not isinstance(data["id"], str):
        raise ValueError("Conversation id must be string")
    if not isinstance(data["label"], str):
        raise ValueError("Conversation label must be string")
    if not isinstance(data["folder"], str):
        raise ValueError("Conversation folder must be string")
    if not isinstance(data["message_count"], int):
        raise ValueError("Conversation message_count must be integer")
    
    # Validate status
    if not is_valid_status(data["status"]):
        raise ValueError(f"Invalid conversation status: {data['status']}")
    
    # Validate optional fields
    if "importance_score" in data:
        score = data["importance_score"]
        if not isinstance(score, (int, float)):
            raise ValueError("importance_score must be a number")
        if not (1 <= score <= 10):
            raise ValueError("importance_score must be between 1 and 10")
    
    return True


def validate_api_response(data: Any, expected_type: str) -> bool:
    """
    Validate API response structure
    
    Args:
        data: Response data to validate
        expected_type: Expected response type name
        
    Returns:
        True if response is valid
        
    Raises:
        ValueError: If validation fails
        
    Example:
        ```python
        response = await client.query('term')
        validate_api_response(response, 'QueryResponse')
        ```
    """
    if not isinstance(data, dict):
        raise ValueError(f"{expected_type} must be a dictionary")
    
    if expected_type == "QueryResponse":
        required = ["results", "total", "page", "page_size"]
        for field in required:
            if field not in data:
                raise ValueError(f"QueryResponse missing field: {field}")
        if not isinstance(data["results"], list):
            raise ValueError("QueryResponse results must be a list")
    
    elif expected_type == "PruneResponse":
        required = ["suggestions", "total"]
        for field in required:
            if field not in data:
                raise ValueError(f"PruneResponse missing field: {field}")
        if not isinstance(data["suggestions"], list):
            raise ValueError("PruneResponse suggestions must be a list")
    
    elif expected_type == "Conversation":
        return validate_conversation(data)
    
    return True


def validate_request_payload(payload: Dict[str, Any], request_type: str) -> bool:
    """
    Validate request payload before API call
    
    Args:
        payload: Request payload to validate
        request_type: Type of request
        
    Returns:
        True if payload is valid
        
    Raises:
        ValueError: If validation fails
        
    Example:
        ```python
        payload = {'query': 'search', 'limit': 10}
        validate_request_payload(payload, 'QueryRequest')
        ```
    """
    if request_type == "QueryRequest":
        if "query" not in payload:
            raise ValueError("QueryRequest requires 'query' field")
        if not isinstance(payload["query"], str):
            raise ValueError("Query must be a string")
        if len(payload["query"].strip()) == 0:
            raise ValueError("Query cannot be empty")
        
        if "limit" in payload:
            limit = payload["limit"]
            if not isinstance(limit, int) or limit < 1:
                raise ValueError("Limit must be a positive integer")
    
    elif request_type == "CreateConversationRequest":
        if "messages" not in payload:
            raise ValueError("CreateConversationRequest requires 'messages' field")
        if not isinstance(payload["messages"], list):
            raise ValueError("Messages must be a list")
        if len(payload["messages"]) == 0:
            raise ValueError("Messages cannot be empty")
        
        # Validate each message
        for i, msg in enumerate(payload["messages"]):
            try:
                validate_message(msg)
            except ValueError as e:
                raise ValueError(f"Invalid message at index {i}: {e}")
        
        if "label" not in payload:
            raise ValueError("CreateConversationRequest requires 'label' field")
    
    return True


# ============================================
# UTILITY VALIDATORS
# ============================================

def is_valid_uuid(value: str) -> bool:
    """
    Check if string is a valid UUID
    
    Args:
        value: String to check
        
    Returns:
        True if value is a valid UUID format
    """
    import re
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(value))


def is_valid_iso_datetime(value: str) -> bool:
    """
    Check if string is a valid ISO 8601 datetime
    
    Args:
        value: String to check
        
    Returns:
        True if value is valid ISO 8601 format
    """
    from datetime import datetime
    try:
        datetime.fromisoformat(value.replace('Z', '+00:00'))
        return True
    except (ValueError, AttributeError):
        return False


def is_valid_url(value: str) -> bool:
    """
    Check if string is a valid URL
    
    Args:
        value: String to check
        
    Returns:
        True if value is a valid URL
    """
    import re
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$',
        re.IGNORECASE
    )
    return bool(url_pattern.match(value))
