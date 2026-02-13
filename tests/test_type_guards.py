"""Tests for type_guards module"""

from sekha.type_guards import (
    is_string_content,
    is_multi_modal_content,
    is_text_part,
    is_image_part,
    extract_text,
    extract_image_urls,
    has_images,
    has_text,
    is_valid_role,
    is_valid_conversation_status,
    is_valid_prune_recommendation,
    is_valid_summary_level,
)


class TestContentTypeGuards:
    """Test content type guard functions"""

    def test_is_string_content_with_string(self):
        """Test string content detection"""
        assert is_string_content("Hello world") is True

    def test_is_string_content_with_list(self):
        """Test string content detection with non-string"""
        assert is_string_content([{"type": "text", "text": "Hi"}]) is False

    def test_is_multi_modal_content_with_list(self):
        """Test multi-modal content detection"""
        content = [{"type": "text", "text": "Hello"}]
        assert is_multi_modal_content(content) is True

    def test_is_multi_modal_content_with_empty_list(self):
        """Test multi-modal content detection with empty list"""
        assert is_multi_modal_content([]) is False

    def test_is_multi_modal_content_with_string(self):
        """Test multi-modal content detection with string"""
        assert is_multi_modal_content("Hello") is False

    def test_is_text_part_valid(self):
        """Test text part detection with valid part"""
        part = {"type": "text", "text": "Hello world"}
        assert is_text_part(part) is True

    def test_is_text_part_missing_text(self):
        """Test text part detection with missing text field"""
        part = {"type": "text"}
        assert is_text_part(part) is False

    def test_is_text_part_wrong_type(self):
        """Test text part detection with wrong type"""
        part = {"type": "image_url", "text": "Hello"}
        assert is_text_part(part) is False

    def test_is_text_part_not_dict(self):
        """Test text part detection with non-dict"""
        assert is_text_part("not a dict") is False

    def test_is_image_part_valid(self):
        """Test image part detection with valid part"""
        part = {
            "type": "image_url",
            "image_url": {"url": "https://example.com/image.png"},
        }
        assert is_image_part(part) is True

    def test_is_image_part_missing_url(self):
        """Test image part detection with missing url"""
        part = {"type": "image_url", "image_url": {}}
        assert is_image_part(part) is False

    def test_is_image_part_wrong_type(self):
        """Test image part detection with wrong type"""
        part = {"type": "text", "image_url": {"url": "https://example.com/image.png"}}
        assert is_image_part(part) is False

    def test_is_image_part_image_url_not_dict(self):
        """Test image part detection with image_url not being a dict"""
        part = {"type": "image_url", "image_url": "https://example.com/image.png"}
        assert is_image_part(part) is False

    def test_is_image_part_not_dict(self):
        """Test image part detection with non-dict"""
        assert is_image_part("not a dict") is False


class TestContentExtraction:
    """Test content extraction helpers"""

    def test_extract_text_from_string(self):
        """Test text extraction from string content"""
        assert extract_text("Hello world") == "Hello world"

    def test_extract_text_from_multi_modal(self):
        """Test text extraction from multi-modal content"""
        content = [
            {"type": "text", "text": "Hello"},
            {"type": "text", "text": "world"},
        ]
        assert extract_text(content) == "Hello world"

    def test_extract_text_from_multi_modal_with_images(self):
        """Test text extraction from multi-modal content with images"""
        content = [
            {"type": "text", "text": "Check this out"},
            {"type": "image_url", "image_url": {"url": "https://example.com/img.png"}},
            {"type": "text", "text": "Amazing!"},
        ]
        assert extract_text(content) == "Check this out Amazing!"

    def test_extract_text_from_empty_content(self):
        """Test text extraction from empty/invalid content"""
        assert extract_text(None) == ""
        assert extract_text([]) == ""

    def test_extract_image_urls_from_string(self):
        """Test image URL extraction from string content"""
        assert extract_image_urls("Hello") == []

    def test_extract_image_urls_from_multi_modal(self):
        """Test image URL extraction from multi-modal content"""
        content = [
            {"type": "text", "text": "Hello"},
            {"type": "image_url", "image_url": {"url": "https://example.com/1.png"}},
            {"type": "image_url", "image_url": {"url": "https://example.com/2.png"}},
        ]
        urls = extract_image_urls(content)
        assert len(urls) == 2
        assert "https://example.com/1.png" in urls
        assert "https://example.com/2.png" in urls

    def test_extract_image_urls_from_empty_content(self):
        """Test image URL extraction from empty content"""
        assert extract_image_urls([]) == []
        assert extract_image_urls(None) == []

    def test_has_images_with_images(self):
        """Test has_images detection with images present"""
        message = {
            "role": "user",
            "content": [
                {"type": "text", "text": "Look at this"},
                {
                    "type": "image_url",
                    "image_url": {"url": "https://example.com/img.png"},
                },
            ],
        }
        assert has_images(message) is True

    def test_has_images_without_images(self):
        """Test has_images detection without images"""
        message = {
            "role": "user",
            "content": "Just text",
        }
        assert has_images(message) is False

    def test_has_images_with_empty_content(self):
        """Test has_images with empty content"""
        message = {"role": "user", "content": None}
        assert has_images(message) is False

    def test_has_text_with_string_content(self):
        """Test has_text detection with string content"""
        message = {"role": "user", "content": "Hello"}
        assert has_text(message) is True

    def test_has_text_with_multi_modal_content(self):
        """Test has_text detection with multi-modal content"""
        message = {
            "role": "user",
            "content": [
                {"type": "text", "text": "Hello"},
                {
                    "type": "image_url",
                    "image_url": {"url": "https://example.com/img.png"},
                },
            ],
        }
        assert has_text(message) is True

    def test_has_text_with_empty_string(self):
        """Test has_text detection with empty string"""
        message = {"role": "user", "content": ""}
        assert has_text(message) is False

    def test_has_text_with_empty_content(self):
        """Test has_text with empty content"""
        message = {"role": "user", "content": None}
        assert has_text(message) is False

    def test_has_text_with_only_images(self):
        """Test has_text with only images"""
        message = {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": "https://example.com/img.png"},
                },
            ],
        }
        assert has_text(message) is False


class TestEnumValidators:
    """Test enum validation functions"""

    def test_is_valid_role_with_valid_roles(self):
        """Test role validation with valid roles"""
        assert is_valid_role("user") is True
        assert is_valid_role("assistant") is True
        assert is_valid_role("system") is True

    def test_is_valid_role_with_invalid_role(self):
        """Test role validation with invalid role"""
        assert is_valid_role("invalid") is False
        assert is_valid_role("") is False

    def test_is_valid_conversation_status_with_valid_statuses(self):
        """Test status validation with valid statuses"""
        assert is_valid_conversation_status("active") is True
        assert is_valid_conversation_status("archived") is True

    def test_is_valid_conversation_status_with_invalid_status(self):
        """Test status validation with invalid status"""
        assert is_valid_conversation_status("invalid") is False
        assert is_valid_conversation_status("") is False

    def test_is_valid_prune_recommendation_with_valid_recommendations(self):
        """Test prune recommendation validation with valid values"""
        assert is_valid_prune_recommendation("keep") is True
        assert is_valid_prune_recommendation("review") is True
        assert is_valid_prune_recommendation("archive") is True

    def test_is_valid_prune_recommendation_with_invalid_recommendation(self):
        """Test prune recommendation validation with invalid value"""
        assert is_valid_prune_recommendation("invalid") is False
        assert is_valid_prune_recommendation("") is False

    def test_is_valid_summary_level_with_valid_levels(self):
        """Test summary level validation with valid levels"""
        assert is_valid_summary_level("daily") is True
        assert is_valid_summary_level("weekly") is True
        assert is_valid_summary_level("monthly") is True

    def test_is_valid_summary_level_with_invalid_level(self):
        """Test summary level validation with invalid level"""
        assert is_valid_summary_level("invalid") is False
        assert is_valid_summary_level("") is False
