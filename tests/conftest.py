"""Shared test fixtures for all test files"""

import pytest
from sekha import ClientConfig


@pytest.fixture
def test_config():
    """Create test client configuration with valid test API key"""
    return ClientConfig(
        api_key="sk-test-12345678901234567890123456789012",  # Valid test key format
        base_url="http://localhost:8080",
        timeout=5.0,
    )
