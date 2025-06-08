"""
pytest configuration and fixtures for Men's Circle Management Platform.

This conftest.py file provides shared fixtures and configuration for all tests
in the platform, supporting both unit and integration testing scenarios.

Following TDD principles: This configuration enables test-first development
across all components of the men's circle management platform.
"""

import asyncio
import os
import pytest
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock

# Test environment configuration
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///./test_main.db"
os.environ["CREDS_DATABASE_URL"] = "sqlite:///./test_creds.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["ENCRYPTION_KEY"] = "test-encryption-key-32-bytes-long!"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Get the project root directory for all tests."""
    # Navigate up from tests/ to project root
    current_dir = Path(__file__).parent
    return current_dir.parent


@pytest.fixture
def temp_directory() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    test_env_vars = {
        "DATABASE_URL": "sqlite:///./test_main.db",
        "CREDS_DATABASE_URL": "sqlite:///./test_creds.db", 
        "REDIS_URL": "redis://localhost:6379/1",
        "JWT_SECRET_KEY": "test-jwt-secret-key",
        "ENCRYPTION_KEY": "test-encryption-key-for-testing!",
        "STRIPE_API_KEY": "sk_test_fake_stripe_key",
        "STRIPE_WEBHOOK_SECRET": "whsec_test_webhook_secret",
        "SENDGRID_API_KEY": "SG.test_sendgrid_key",
        "TWILIO_ACCOUNT_SID": "test_twilio_sid",
        "TWILIO_AUTH_TOKEN": "test_twilio_token",
        "DEBUG": "True",
        "LOG_LEVEL": "DEBUG",
        "CORS_ORIGINS": "http://localhost:3000,http://localhost:8080"
    }
    
    for key, value in test_env_vars.items():
        monkeypatch.setenv(key, value)
    
    return test_env_vars


# Database fixtures for testing
@pytest.fixture
async def async_db_session():
    """Create an async database session for testing."""
    # This will be implemented when we create the database layer
    # For now, return a mock that can be used in tests
    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    yield mock_session
    await mock_session.close()


@pytest.fixture
async def async_creds_db_session():
    """Create an async credentials database session for testing."""
    # This will be implemented when we create the credentials database layer
    mock_session = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    yield mock_session
    await mock_session.close()


# Redis fixtures for testing
@pytest.fixture
async def mock_redis():
    """Create a mock Redis client for testing."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.delete = AsyncMock(return_value=1)
    mock_redis.exists = AsyncMock(return_value=False)
    mock_redis.expire = AsyncMock(return_value=True)
    mock_redis.ping = AsyncMock(return_value=b"PONG")
    return mock_redis


# FastAPI testing fixtures
@pytest.fixture
async def async_client():
    """Create an async test client for FastAPI application."""
    # This will be implemented when we create the FastAPI application
    # For now, return a mock that can be used in API tests
    mock_client = AsyncMock()
    mock_client.get = AsyncMock()
    mock_client.post = AsyncMock()
    mock_client.put = AsyncMock()
    mock_client.delete = AsyncMock()
    mock_client.patch = AsyncMock()
    return mock_client


# Authentication fixtures
@pytest.fixture
def mock_current_user():
    """Create a mock current user for authentication tests."""
    mock_user = Mock()
    mock_user.id = 1
    mock_user.email = "test@example.com"
    mock_user.is_active = True
    mock_user.first_name = "Test"
    mock_user.last_name = "User"
    mock_user.role = "member"
    return mock_user


@pytest.fixture
def mock_jwt_token():
    """Create a mock JWT token for authentication tests."""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test.token"


# Payment processing fixtures
@pytest.fixture
def mock_stripe_customer():
    """Create a mock Stripe customer for payment tests."""
    mock_customer = Mock()
    mock_customer.id = "cus_test_customer_id"
    mock_customer.email = "test@example.com"
    mock_customer.created = 1234567890
    mock_customer.subscriptions = Mock()
    mock_customer.subscriptions.data = []
    return mock_customer


@pytest.fixture
def mock_stripe_payment_intent():
    """Create a mock Stripe payment intent for payment tests."""
    mock_intent = Mock()
    mock_intent.id = "pi_test_payment_intent"
    mock_intent.amount = 2000  # $20.00
    mock_intent.currency = "usd"
    mock_intent.status = "succeeded"
    mock_intent.client_secret = "pi_test_client_secret"
    return mock_intent


# Circle management fixtures
@pytest.fixture
def mock_circle():
    """Create a mock circle for circle management tests."""
    mock_circle = Mock()
    mock_circle.id = 1
    mock_circle.name = "Test Circle"
    mock_circle.description = "A test circle for development"
    mock_circle.capacity = 8
    mock_circle.current_members = 3
    mock_circle.facilitator_id = 1
    mock_circle.is_active = True
    mock_circle.created_at = "2024-01-01T00:00:00Z"
    return mock_circle


@pytest.fixture
def mock_event():
    """Create a mock event for event management tests."""
    mock_event = Mock()
    mock_event.id = 1
    mock_event.title = "Test Movie Night"
    mock_event.description = "Weekly movie night event"
    mock_event.event_type = "MOVIE_NIGHT"
    mock_event.start_time = "2024-06-15T19:00:00Z"
    mock_event.duration_minutes = 120
    mock_event.capacity = 10
    mock_event.circle_id = 1
    mock_event.facilitator_id = 1
    mock_event.is_active = True
    return mock_event


# Communication fixtures
@pytest.fixture
def mock_email_service():
    """Create a mock email service for communication tests."""
    mock_service = AsyncMock()
    mock_service.send_email = AsyncMock(return_value=True)
    mock_service.send_bulk_email = AsyncMock(return_value=True)
    mock_service.validate_email = Mock(return_value=True)
    return mock_service


@pytest.fixture
def mock_sms_service():
    """Create a mock SMS service for communication tests."""
    mock_service = AsyncMock()
    mock_service.send_sms = AsyncMock(return_value=True)
    mock_service.validate_phone = Mock(return_value=True)
    mock_service.format_phone = Mock(return_value="+1234567890")
    return mock_service


# File and media fixtures
@pytest.fixture
def sample_image_file():
    """Create a sample image file for upload tests."""
    import io
    from PIL import Image
    
    # Create a simple test image
    image = Image.new('RGB', (100, 100), color='red')
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='JPEG')
    image_bytes.seek(0)
    
    mock_file = Mock()
    mock_file.filename = "test_image.jpg"
    mock_file.content_type = "image/jpeg"
    mock_file.file = image_bytes
    mock_file.size = len(image_bytes.getvalue())
    
    return mock_file


# Data factory fixtures
@pytest.fixture
def user_factory():
    """Factory for creating test user data."""
    def create_user(**kwargs):
        default_data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "phone": "+1234567890",
            "is_active": True,
            "email_verified": True,
            "role": "member"
        }
        default_data.update(kwargs)
        return Mock(**default_data)
    
    return create_user


@pytest.fixture
def circle_factory():
    """Factory for creating test circle data."""
    def create_circle(**kwargs):
        default_data = {
            "name": "Test Circle",
            "description": "A test circle",
            "capacity": 8,
            "current_members": 0,
            "is_active": True,
            "location": "Test Location"
        }
        default_data.update(kwargs)
        return Mock(**default_data)
    
    return create_circle


@pytest.fixture
def event_factory():
    """Factory for creating test event data."""
    def create_event(**kwargs):
        default_data = {
            "title": "Test Event",
            "description": "A test event",
            "event_type": "MOVIE_NIGHT",
            "capacity": 10,
            "duration_minutes": 120,
            "is_active": True
        }
        default_data.update(kwargs)
        return Mock(**default_data)
    
    return create_event


# Test data cleanup
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Automatically cleanup test data after each test."""
    yield
    # Cleanup logic will be implemented when we have database models
    # For now, this is a placeholder that ensures clean test state


# pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "auth: mark test as authentication-related"
    )
    config.addinivalue_line(
        "markers", "payment: mark test as payment-related"
    )
    config.addinivalue_line(
        "markers", "circle: mark test as circle management-related"
    )
    config.addinivalue_line(
        "markers", "event: mark test as event management-related"
    )
    config.addinivalue_line(
        "markers", "communication: mark test as communication-related"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Collection and reporting hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location."""
    for item in items:
        # Add markers based on test file location
        if "auth" in str(item.fspath):
            item.add_marker(pytest.mark.auth)
        if "payment" in str(item.fspath):
            item.add_marker(pytest.mark.payment)
        if "circle" in str(item.fspath):
            item.add_marker(pytest.mark.circle)
        if "event" in str(item.fspath):
            item.add_marker(pytest.mark.event)
        if "communication" in str(item.fspath):
            item.add_marker(pytest.mark.communication)
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        else:
            item.add_marker(pytest.mark.unit) 