import pytest
from sekha.types import MemoryConfig


@pytest.fixture
def test_config() -> MemoryConfig:
    """Provide a test configuration"""
    return {
        "base_url": "http://localhost:8080",
        "api_key": "sk-sekha-test-token-123456789012345678901234567890",
    }
