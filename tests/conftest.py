import pytest
from sekha.models import ClientConfig


@pytest.fixture
def test_config() -> ClientConfig:
    """Provide a test configuration"""
    return ClientConfig(
        base_url="http://localhost:8080",
        api_key="sk-sekha-test-token-123456789012345678901234567890",
        timeout=5.0,
        max_retries=3,
    )
