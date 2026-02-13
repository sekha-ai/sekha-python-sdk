"""
Type Guards Demo

Demonstrates runtime type checking and validation using type guards.
"""

from sekha.type_guards import (
    extract_image_urls,
    extract_text,
    has_images,
    has_text,
    is_image_part,
    is_multi_modal_content,
    is_string_content,
    is_text_part,
)
from sekha.types import Message, MessageContent


def demo_string_content():
    """
    Demo string content checking
    """
    print("\n=== String Content ===")

    simple_content: MessageContent = "This is a simple text message"

    if is_string_content(simple_content):
        print(f"Content is string: {simple_content}")
        print(f"Length: {len(simple_content)} characters")


def demo_multi_modal_content():
    """
    Demo multi-modal content handling
    """
    print("\n=== Multi-Modal Content ===")

    multi_modal: MessageContent = [
        {"type": "text", "text": "Check out this diagram:"},
        {
            "type": "image_url",
            "image_url": {
                "url": "https://example.com/architecture.png",
                "detail": "high",
            },
        },
        {"type": "text", "text": "What do you think?"},
    ]

    if is_multi_modal_content(multi_modal):
        print(f"Content has {len(multi_modal)} parts")

        for i, part in enumerate(multi_modal):
            print(f"  Part {i}:")
            if is_text_part(part):
                print("    Type: Text")
                print(f"    Content: {part['text']}")
            elif is_image_part(part):
                print("    Type: Image")
                print(f"    URL: {part['image_url']['url']}")
                if "detail" in part["image_url"]:
                    print(f"    Detail: {part['image_url']['detail']}")


def demo_content_extraction():
    """
    Demo extracting specific content
    """
    print("\n=== Content Extraction ===")

    mixed_content: MessageContent = [
        {"type": "text", "text": "Here's the before:"},
        {
            "type": "image_url",
            "image_url": {"url": "https://example.com/before.png"},
        },
        {"type": "text", "text": "And here's the after:"},
        {
            "type": "image_url",
            "image_url": {"url": "https://example.com/after.png"},
        },
    ]

    # Extract text
    text = extract_text(mixed_content)
    print(f"Extracted text: {text}")

    # Extract image URLs
    images = extract_image_urls(mixed_content)
    print(f"Found {len(images)} images:")
    for url in images:
        print(f"  - {url}")


def demo_message_checking():
    """
    Demo message-level checks
    """
    print("\n=== Message Checking ===")

    # Text-only message
    text_msg: Message = {"role": "user", "content": "Simple text question"}

    print("\nText message:")
    print(f"  Has text: {has_text(text_msg)}")
    print(f"  Has images: {has_images(text_msg)}")

    # Multi-modal message
    mm_msg: Message = {
        "role": "user",
        "content": [
            {"type": "text", "text": "What's in this image?"},
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/img.png"},
            },
        ],
    }

    print("\nMulti-modal message:")
    print(f"  Has text: {has_text(mm_msg)}")
    print(f"  Has images: {has_images(mm_msg)}")
    print(f"  Text: {extract_text(mm_msg['content'])}")
    print(f"  Images: {extract_image_urls(mm_msg['content'])}")


def demo_type_narrowing():
    """
    Demo type narrowing with type guards
    """
    print("\n=== Type Narrowing ===")

    def process_content(content: MessageContent) -> None:
        """Process content with type-safe branches"""

        if is_string_content(content):
            # Type is narrowed to str
            print(f"Processing string: {content[:50]}...")
            print(f"Length: {len(content)}")

        elif is_multi_modal_content(content):
            # Type is narrowed to List[ContentPart]
            print(f"Processing multi-modal content with {len(content)} parts")

            text_parts = [p for p in content if is_text_part(p)]
            image_parts = [p for p in content if is_image_part(p)]

            print(f"  Text parts: {len(text_parts)}")
            print(f"  Image parts: {len(image_parts)}")

    # Test with different content types
    process_content("Simple string content")
    process_content(
        [
            {"type": "text", "text": "Text part"},
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/img.png"},
            },
        ]
    )


def demo_validation():
    """
    Demo input validation
    """
    print("\n=== Input Validation ===")

    from sekha.type_guards import (
        is_valid_conversation_status,
        is_valid_prune_recommendation,
        is_valid_role,
        is_valid_summary_level,
    )

    # Valid values
    print("\nValid values:")
    print(f"  'user' is valid role: {is_valid_role('user')}")
    print(f"  'active' is valid status: {is_valid_conversation_status('active')}")
    print(
        f"  'archive' is valid recommendation: "
        f"{is_valid_prune_recommendation('archive')}"
    )
    print(f"  'daily' is valid summary level: {is_valid_summary_level('daily')}")

    # Invalid values
    print("\nInvalid values:")
    print(f"  'admin' is valid role: {is_valid_role('admin')}")
    print(f"  'deleted' is valid status: {is_valid_conversation_status('deleted')}")
    print(
        f"  'destroy' is valid recommendation: "
        f"{is_valid_prune_recommendation('destroy')}"
    )
    print(f"  'yearly' is valid summary level: {is_valid_summary_level('yearly')}")


def main():
    """
    Run all type guard demos
    """
    print("\n" + "=" * 60)
    print("Sekha Type Guards Demo")
    print("=" * 60)

    demo_string_content()
    demo_multi_modal_content()
    demo_content_extraction()
    demo_message_checking()
    demo_type_narrowing()
    demo_validation()

    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
