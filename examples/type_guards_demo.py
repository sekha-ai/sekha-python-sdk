"""
Type Guards Demo

Demonstrates all 8 type guard functions and validation helpers
for runtime type checking and API response validation.
"""

from typing import List
import asyncio

from sekha import (
    # Type Guards
    is_multi_modal_content,
    is_text_part,
    is_image_part,
    extract_text,
    extract_image_urls,
    has_images,
    is_valid_status,
    is_valid_recommendation,
    # Validators
    validate_message,
    validate_conversation,
    validate_api_response,
    validate_request_payload,
    # Types
    Message,
    MessageContent,
)


def demo_content_type_guards():
    """
    Demo: Content type guards for multi-modal messages
    """
    print("\n=== Content Type Guards ===")
    
    # 1. Simple text content
    print("\n1. Simple Text Content")
    simple_content: MessageContent = "Hello, world!"
    
    print(f"  Is multi-modal: {is_multi_modal_content(simple_content)}")
    print(f"  Extracted text: {extract_text(simple_content)}")
    print(f"  Image URLs: {extract_image_urls(simple_content)}")
    
    # 2. Multi-modal content
    print("\n2. Multi-Modal Content (Text + Image)")
    multi_modal_content: MessageContent = [
        {"type": "text", "text": "Check out this image:"},
        {
            "type": "image_url",
            "image_url": {
                "url": "https://example.com/image.png",
                "detail": "high"
            }
        },
        {"type": "text", "text": "What do you think?"}
    ]
    
    print(f"  Is multi-modal: {is_multi_modal_content(multi_modal_content)}")
    print(f"  Extracted text: {extract_text(multi_modal_content)}")
    print(f"  Image URLs: {extract_image_urls(multi_modal_content)}")
    
    # 3. Type-safe iteration with type guards
    print("\n3. Type-Safe Content Iteration")
    if is_multi_modal_content(multi_modal_content):
        for i, part in enumerate(multi_modal_content):
            print(f"  Part {i}:")
            if is_text_part(part):
                print(f"    Type: Text")
                print(f"    Content: {part['text']}")
            elif is_image_part(part):
                print(f"    Type: Image")
                print(f"    URL: {part['image_url']['url']}")
                if 'detail' in part['image_url']:
                    print(f"    Detail: {part['image_url']['detail']}")


def demo_message_type_guards():
    """
    Demo: Message-level type guards
    """
    print("\n=== Message Type Guards ===")
    
    # 1. Text-only message
    print("\n1. Text-Only Message")
    text_message: Message = {
        "role": "user",
        "content": "Simple text message"
    }
    
    print(f"  Has images: {has_images(text_message)}")
    print(f"  Text: {extract_text(text_message['content'])}")
    
    # 2. Message with images
    print("\n2. Message with Images")
    image_message: Message = {
        "role": "user",
        "content": [
            {"type": "text", "text": "Look at these:"},
            {"type": "image_url", "image_url": {"url": "https://example.com/1.png"}},
            {"type": "image_url", "image_url": {"url": "https://example.com/2.png"}},
        ]
    }
    
    print(f"  Has images: {has_images(image_message)}")
    if has_images(image_message):
        urls = extract_image_urls(image_message['content'])
        print(f"  Image count: {len(urls)}")
        for i, url in enumerate(urls):
            print(f"    Image {i+1}: {url}")


def demo_enum_validators():
    """
    Demo: Enum validation type guards
    """
    print("\n=== Enum Validators ===")
    
    # 1. Conversation status validation
    print("\n1. Conversation Status Validation")
    statuses = ["active", "archived", "pinned", "invalid", "deleted"]
    for status in statuses:
        is_valid = is_valid_status(status)
        print(f"  '{status}': {'✓ Valid' if is_valid else '✗ Invalid'}")
    
    # 2. Prune recommendation validation
    print("\n2. Prune Recommendation Validation")
    recommendations = ["archive", "keep", "review", "delete", "ignore"]
    for rec in recommendations:
        is_valid = is_valid_recommendation(rec)
        print(f"  '{rec}': {'✓ Valid' if is_valid else '✗ Invalid'}")


def demo_message_validation():
    """
    Demo: Comprehensive message validation
    """
    print("\n=== Message Validation ===")
    
    # 1. Valid message
    print("\n1. Valid Message")
    valid_msg = {
        "role": "user",
        "content": "This is valid"
    }
    try:
        if validate_message(valid_msg):
            print("  ✓ Message is valid")
    except ValueError as e:
        print(f"  ✗ Validation failed: {e}")
    
    # 2. Missing role
    print("\n2. Invalid Message (Missing Role)")
    invalid_msg_1 = {
        "content": "Missing role field"
    }
    try:
        validate_message(invalid_msg_1)
    except ValueError as e:
        print(f"  ✗ Expected error: {e}")
    
    # 3. Invalid role
    print("\n3. Invalid Message (Bad Role)")
    invalid_msg_2 = {
        "role": "invalid_role",
        "content": "Bad role"
    }
    try:
        validate_message(invalid_msg_2)
    except ValueError as e:
        print(f"  ✗ Expected error: {e}")
    
    # 4. Invalid multi-modal content
    print("\n4. Invalid Message (Bad Content Part)")
    invalid_msg_3 = {
        "role": "user",
        "content": [
            {"type": "text"}  # Missing 'text' field
        ]
    }
    try:
        validate_message(invalid_msg_3)
    except ValueError as e:
        print(f"  ✗ Expected error: {e}")
    
    # 5. Valid multi-modal message
    print("\n5. Valid Multi-Modal Message")
    valid_multimodal = {
        "role": "user",
        "content": [
            {"type": "text", "text": "Valid"},
            {"type": "image_url", "image_url": {"url": "https://example.com/img.png"}}
        ]
    }
    try:
        if validate_message(valid_multimodal):
            print("  ✓ Multi-modal message is valid")
    except ValueError as e:
        print(f"  ✗ Validation failed: {e}")


def demo_conversation_validation():
    """
    Demo: Conversation validation
    """
    print("\n=== Conversation Validation ===")
    
    # 1. Valid conversation
    print("\n1. Valid Conversation")
    valid_conv = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "label": "Engineering",
        "folder": "/work",
        "status": "active",
        "message_count": 10,
        "created_at": "2026-02-12T16:00:00Z",
        "importance_score": 8.5
    }
    try:
        if validate_conversation(valid_conv):
            print("  ✓ Conversation is valid")
    except ValueError as e:
        print(f"  ✗ Validation failed: {e}")
    
    # 2. Missing required field
    print("\n2. Invalid Conversation (Missing Field)")
    invalid_conv_1 = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "label": "Test",
        # Missing 'folder'
        "status": "active",
        "message_count": 5,
        "created_at": "2026-02-12T16:00:00Z"
    }
    try:
        validate_conversation(invalid_conv_1)
    except ValueError as e:
        print(f"  ✗ Expected error: {e}")
    
    # 3. Invalid importance score
    print("\n3. Invalid Conversation (Bad Importance Score)")
    invalid_conv_2 = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "label": "Test",
        "folder": "/",
        "status": "active",
        "message_count": 5,
        "created_at": "2026-02-12T16:00:00Z",
        "importance_score": 15  # Out of range (1-10)
    }
    try:
        validate_conversation(invalid_conv_2)
    except ValueError as e:
        print(f"  ✗ Expected error: {e}")


def demo_request_validation():
    """
    Demo: Request payload validation
    """
    print("\n=== Request Validation ===")
    
    # 1. Valid query request
    print("\n1. Valid Query Request")
    valid_query = {
        "query": "TypeScript patterns",
        "limit": 10
    }
    try:
        if validate_request_payload(valid_query, "QueryRequest"):
            print("  ✓ Query request is valid")
    except ValueError as e:
        print(f"  ✗ Validation failed: {e}")
    
    # 2. Empty query
    print("\n2. Invalid Query (Empty String)")
    invalid_query = {
        "query": "   ",  # Only whitespace
        "limit": 10
    }
    try:
        validate_request_payload(invalid_query, "QueryRequest")
    except ValueError as e:
        print(f"  ✗ Expected error: {e}")
    
    # 3. Valid create conversation request
    print("\n3. Valid Create Conversation Request")
    valid_create = {
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ],
        "label": "Greeting"
    }
    try:
        if validate_request_payload(valid_create, "CreateConversationRequest"):
            print("  ✓ Create request is valid")
    except ValueError as e:
        print(f"  ✗ Validation failed: {e}")
    
    # 4. Invalid create request (empty messages)
    print("\n4. Invalid Create Request (Empty Messages)")
    invalid_create = {
        "messages": [],  # Empty array
        "label": "Test"
    }
    try:
        validate_request_payload(invalid_create, "CreateConversationRequest")
    except ValueError as e:
        print(f"  ✗ Expected error: {e}")


def demo_api_response_validation():
    """
    Demo: API response validation
    """
    print("\n=== API Response Validation ===")
    
    # 1. Valid query response
    print("\n1. Valid Query Response")
    valid_response = {
        "results": [
            {
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "message_id": "660e8400-e29b-41d4-a716-446655440001",
                "score": 0.95,
                "content": "Result content",
                "metadata": {},
                "label": "Test",
                "folder": "/",
                "timestamp": "2026-02-12T16:00:00Z"
            }
        ],
        "total": 1,
        "page": 1,
        "page_size": 10
    }
    try:
        if validate_api_response(valid_response, "QueryResponse"):
            print("  ✓ Query response is valid")
    except ValueError as e:
        print(f"  ✗ Validation failed: {e}")
    
    # 2. Invalid response (missing field)
    print("\n2. Invalid Response (Missing Field)")
    invalid_response = {
        "results": [],
        "total": 0
        # Missing 'page' and 'page_size'
    }
    try:
        validate_api_response(invalid_response, "QueryResponse")
    except ValueError as e:
        print(f"  ✗ Expected error: {e}")


def demo_practical_usage():
    """
    Demo: Practical type guard usage patterns
    """
    print("\n=== Practical Usage Patterns ===")
    
    # Pattern 1: Safe content extraction
    print("\n1. Safe Content Extraction")
    messages: List[Message] = [
        {"role": "user", "content": "Text only"},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "With image"},
                {"type": "image_url", "image_url": {"url": "https://example.com/img.png"}}
            ]
        }
    ]
    
    for i, msg in enumerate(messages):
        print(f"  Message {i+1}:")
        print(f"    Role: {msg['role']}")
        print(f"    Text: {extract_text(msg['content'])}")
        if has_images(msg):
            print(f"    Images: {len(extract_image_urls(msg['content']))}")
    
    # Pattern 2: Conditional processing
    print("\n2. Conditional Processing Based on Type")
    content: MessageContent = [
        {"type": "text", "text": "Process this"},
        {"type": "image_url", "image_url": {"url": "https://example.com/img.png"}}
    ]
    
    if is_multi_modal_content(content):
        text_count = sum(1 for p in content if is_text_part(p))
        image_count = sum(1 for p in content if is_image_part(p))
        print(f"  Text parts: {text_count}")
        print(f"  Image parts: {image_count}")
    
    # Pattern 3: Input validation before API call
    print("\n3. Pre-API Validation")
    user_input = {
        "query": "search term",
        "limit": 5
    }
    
    try:
        validate_request_payload(user_input, "QueryRequest")
        print("  ✓ Input valid, safe to call API")
        # await client.query(**user_input)
    except ValueError as e:
        print(f"  ✗ Invalid input, preventing API call: {e}")


def main():
    """
    Run all type guard demos
    """
    print("\n" + "="*60)
    print("Sekha Type Guards Demo")
    print("Demonstrating all 8 type guards + validators")
    print("="*60)
    
    demo_content_type_guards()
    demo_message_type_guards()
    demo_enum_validators()
    demo_message_validation()
    demo_conversation_validation()
    demo_request_validation()
    demo_api_response_validation()
    demo_practical_usage()
    
    print("\n" + "="*60)
    print("Demo Complete!")
    print("\nCore Type Guards (8):")
    print("  1. is_multi_modal_content()")
    print("  2. is_text_part()")
    print("  3. is_image_part()")
    print("  4. extract_text()")
    print("  5. extract_image_urls()")
    print("  6. has_images()")
    print("  7. is_valid_status()")
    print("  8. is_valid_recommendation()")
    print("\nAdditional Validators:")
    print("  - validate_message()")
    print("  - validate_conversation()")
    print("  - validate_api_response()")
    print("  - validate_request_payload()")
    print("="*60)


if __name__ == "__main__":
    main()
