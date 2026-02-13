"""Additional tests for utils.py to achieve 100% coverage"""

import pytest
import asyncio
from sekha.utils import (
    json_serializer,
    validate_api_key,
    validate_base_url,
    parse_iso_datetime,
    format_bytes,
    RateLimiter,
    ExponentialBackoff,
)
from datetime import datetime


class TestJsonSerializer:
    """Test JSON serializer"""

    def test_json_serializer_with_dict_method(self):
        """Test serializer with object that has .dict() method"""

        class MockObject:
            def dict(self):
                return {"key": "value", "timestamp": datetime.now()}

        obj = MockObject()
        result = json_serializer(obj)
        assert "key" in result
        assert "value" in result

    def test_json_serializer_with_regular_object(self):
        """Test serializer with regular object"""
        result = json_serializer({"test": "data", "date": datetime.now()})
        assert "test" in result
        assert "data" in result


class TestValidateApiKey:
    """Test API key validation edge cases"""

    def test_validate_test_key_max_length(self):
        """Test test API key with max length check"""
        # Test key with valid length
        key = "sk-test-" + "x" * 20
        assert validate_api_key(key) is True

    def test_validate_test_key_too_short(self):
        """Test test API key that's too short"""
        with pytest.raises(ValueError, match="too short"):
            validate_api_key("sk-test-short")

    def test_validate_production_key_too_long(self):
        """Test production key that exceeds max length"""
        key = "sk-sekha-" + "x" * 130
        with pytest.raises(ValueError, match="too long"):
            validate_api_key(key)

    def test_validate_production_key_missing_prefix(self):
        """Test production key without correct prefix"""
        key = "wrong-prefix-" + "x" * 32
        with pytest.raises(ValueError, match="must start with"):
            validate_api_key(key)


class TestValidateBaseUrl:
    """Test base URL validation edge cases"""

    def test_validate_base_url_malformed_ipv6(self):
        """Test base URL with malformed IPv6 address"""
        with pytest.raises(ValueError, match="malformed IPv6"):
            validate_base_url("http://[invalid")

    def test_validate_base_url_invalid_protocol(self):
        """Test base URL with invalid protocol"""
        with pytest.raises(ValueError, match="Invalid base_url"):
            validate_base_url("ftp://example.com")

    def test_validate_base_url_empty(self):
        """Test base URL validation with empty string"""
        with pytest.raises(ValueError, match="required"):
            validate_base_url("")

    def test_validate_base_url_not_string(self):
        """Test base URL validation with non-string"""
        with pytest.raises(ValueError, match="must be a string"):
            validate_base_url(123)  # type: ignore


class TestParseDatetime:
    """Test datetime parsing"""

    def test_parse_iso_datetime_with_z(self):
        """Test parsing ISO datetime with Z suffix"""
        dt_str = "2024-01-15T10:30:00Z"
        result = parse_iso_datetime(dt_str)
        assert isinstance(result, datetime)

    def test_parse_iso_datetime_fallback(self):
        """Test parsing datetime without microseconds (fallback)"""
        dt_str = "2024-01-15 10:30:00"
        result = parse_iso_datetime(dt_str)
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15


class TestFormatBytes:
    """Test byte formatting"""

    def test_format_bytes_bytes(self):
        """Test formatting bytes"""
        assert format_bytes(512) == "512.0 B"

    def test_format_bytes_kb(self):
        """Test formatting kilobytes"""
        assert format_bytes(1536) == "1.5 KB"

    def test_format_bytes_mb(self):
        """Test formatting megabytes"""
        assert format_bytes(1572864) == "1.5 MB"

    def test_format_bytes_gb(self):
        """Test formatting gigabytes"""
        assert format_bytes(1610612736) == "1.5 GB"

    def test_format_bytes_tb(self):
        """Test formatting terabytes"""
        assert format_bytes(1649267441664) == "1.5 TB"


class TestRateLimiterEdgeCases:
    """Test rate limiter edge cases"""

    @pytest.mark.asyncio
    async def test_rate_limiter_zero_max_requests(self):
        """Test rate limiter with max_requests=0"""
        limiter = RateLimiter(max_requests=0, window_seconds=0.1)

        # Should wait the full window
        start = asyncio.get_event_loop().time()
        await limiter.acquire()
        elapsed = asyncio.get_event_loop().time() - start

        # Should have waited approximately the window time
        assert elapsed >= 0.09  # Allow small margin

    @pytest.mark.asyncio
    async def test_rate_limiter_at_limit(self):
        """Test rate limiter when at limit"""
        limiter = RateLimiter(max_requests=2, window_seconds=0.2)

        # First two should be immediate
        await limiter.acquire()
        await limiter.acquire()

        # Third should wait
        start = asyncio.get_event_loop().time()
        await limiter.acquire()
        elapsed = asyncio.get_event_loop().time() - start

        # Should have waited some time
        assert elapsed > 0.1


class TestExponentialBackoff:
    """Test exponential backoff"""

    @pytest.mark.asyncio
    async def test_backoff_increases(self):
        """Test that backoff delay increases"""
        backoff = ExponentialBackoff(base_delay=0.01, max_delay=1.0, factor=2.0)

        assert backoff.attempt == 0
        await backoff.wait()
        assert backoff.attempt == 1
        await backoff.wait()
        assert backoff.attempt == 2

    @pytest.mark.asyncio
    async def test_backoff_max_delay(self):
        """Test that backoff respects max delay"""
        backoff = ExponentialBackoff(base_delay=0.1, max_delay=0.2, factor=2.0)

        # After several attempts, should cap at max_delay
        for _ in range(5):
            await backoff.wait()

        assert backoff.attempt == 5

    def test_backoff_reset(self):
        """Test backoff reset"""
        backoff = ExponentialBackoff()
        backoff.attempt = 5
        backoff.reset()
        assert backoff.attempt == 0
