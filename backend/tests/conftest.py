"""
pytest configuration and fixtures for backend API tests
"""
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from typing import AsyncGenerator

from app.main import app
from app.models.user import User
from app.models.circle import Circle, CircleStatus
from app.models.circle_membership import CircleMembership, PaymentStatus


@pytest.fixture
def client():
    """Create synchronous test client for FastAPI application."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create asynchronous test client for FastAPI application."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_current_user():
    """Create a mock current user for authentication tests."""
    mock_user = Mock(spec=User)
    mock_user.id = 1
    mock_user.email = "test@example.com"
    mock_user.first_name = "Test"
    mock_user.last_name = "User"
    mock_user.phone = "+1234567890"
    mock_user.is_active = True
    mock_user.is_verified = True
    mock_user.email_verified = True
    mock_user.phone_verified = True
    mock_user.created_at = datetime.utcnow()
    mock_user.updated_at = datetime.utcnow()
    return mock_user


@pytest.fixture
def mock_facilitator_user():
    """Create a mock facilitator user for circle tests."""
    mock_user = Mock(spec=User)
    mock_user.id = 2
    mock_user.email = "facilitator@example.com"
    mock_user.first_name = "Facilitator"
    mock_user.last_name = "User"
    mock_user.phone = "+1234567891"
    mock_user.is_active = True
    mock_user.is_verified = True
    mock_user.email_verified = True
    mock_user.phone_verified = True
    mock_user.created_at = datetime.utcnow()
    mock_user.updated_at = datetime.utcnow()
    return mock_user


@pytest.fixture
def mock_circle():
    """Create a mock circle for testing."""
    mock_circle = Mock(spec=Circle)
    mock_circle.id = 1
    mock_circle.name = "Test Circle"
    mock_circle.description = "A test circle for development"
    mock_circle.facilitator_id = 1
    mock_circle.capacity_min = 2
    mock_circle.capacity_max = 8
    mock_circle.location_name = "Test Location"
    mock_circle.location_address = "123 Test St, Test City"
    mock_circle.meeting_schedule = {"day": "Wednesday", "time": "19:00", "frequency": "weekly"}
    mock_circle.status = CircleStatus.FORMING
    mock_circle.is_active = True
    mock_circle.current_member_count = 0
    mock_circle.created_at = datetime.utcnow()
    mock_circle.updated_at = datetime.utcnow()
    return mock_circle


@pytest.fixture
def mock_circle_membership():
    """Create a mock circle membership for testing."""
    mock_membership = Mock(spec=CircleMembership)
    mock_membership.circle_id = 1
    mock_membership.user_id = 2
    mock_membership.is_active = True
    mock_membership.payment_status = PaymentStatus.PENDING
    mock_membership.joined_at = datetime.utcnow()
    mock_membership.stripe_subscription_id = None
    mock_membership.next_payment_due = None
    return mock_membership


@pytest.fixture
def sample_circle_data():
    """Sample circle creation data."""
    return {
        "name": "Men's Growth Circle",
        "description": "A circle focused on personal growth and development",
        "capacity_min": 4,
        "capacity_max": 8,
        "location_name": "Community Center",
        "location_address": "123 Main St, City, State",
        "meeting_schedule": {
            "day": "Wednesday",
            "time": "19:00",
            "frequency": "weekly"
        }
    }


@pytest.fixture
def sample_circle_response():
    """Sample circle response data."""
    return {
        "id": 1,
        "name": "Men's Growth Circle",
        "description": "A circle focused on personal growth and development",
        "facilitator_id": 1,
        "capacity_min": 4,
        "capacity_max": 8,
        "location_name": "Community Center",
        "location_address": "123 Main St, City, State",
        "meeting_schedule": {
            "day": "Wednesday",
            "time": "19:00",
            "frequency": "weekly"
        },
        "status": "forming",
        "is_active": True,
        "current_member_count": 0,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }


@pytest.fixture
def mock_auth_dependency(mock_current_user):
    """Mock the get_current_user dependency for authenticated endpoints."""
    with patch('app.core.deps.get_current_user', return_value=mock_current_user):
        yield mock_current_user


@pytest.fixture
def mock_circle_service():
    """Mock the circle service for testing."""
    mock_service = AsyncMock()
    
    # Mock create_circle method
    mock_service.create_circle = AsyncMock()
    
    # Mock get_circle_by_id method
    mock_service.get_circle_by_id = AsyncMock()
    
    # Mock list_circles_for_user method
    mock_service.list_circles_for_user = AsyncMock()
    
    # Mock update_circle method
    mock_service.update_circle = AsyncMock()
    
    # Mock add_member_to_circle method
    mock_service.add_member_to_circle = AsyncMock()
    
    return mock_service


@pytest.fixture
def mock_circle_service_dependency(mock_circle_service):
    """Mock the get_circle_service dependency."""
    with patch('app.services.circle_service.get_circle_service', return_value=mock_circle_service):
        yield mock_circle_service


@pytest.fixture
def authenticated_headers():
    """Headers for authenticated requests."""
    return {"Authorization": "Bearer fake-token"}


@pytest.fixture
def mock_db_session():
    """Mock database session for testing."""
    mock_session = AsyncMock()
    mock_session.add = Mock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.close = AsyncMock()
    return mock_session


# Sample data factories
@pytest.fixture
def circle_factory():
    """Factory for creating circle test data."""
    def create_circle(**kwargs):
        defaults = {
            "id": 1,
            "name": "Test Circle",
            "description": "A test circle",
            "facilitator_id": 1,
            "capacity_min": 2,
            "capacity_max": 8,
            "location_name": "Test Location",
            "location_address": "123 Test St",
            "meeting_schedule": {"day": "Wednesday", "time": "19:00"},
            "status": CircleStatus.FORMING,
            "is_active": True,
            "current_member_count": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        defaults.update(kwargs)
        
        mock_circle = Mock(spec=Circle)
        for key, value in defaults.items():
            setattr(mock_circle, key, value)
        
        return mock_circle
    
    return create_circle


@pytest.fixture
def user_factory():
    """Factory for creating user test data."""
    def create_user(**kwargs):
        defaults = {
            "id": 1,
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "phone": "+1234567890",
            "is_active": True,
            "is_verified": True,
            "email_verified": True,
            "phone_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        defaults.update(kwargs)
        
        mock_user = Mock(spec=User)
        for key, value in defaults.items():
            setattr(mock_user, key, value)
        
        return mock_user
    
    return create_user


@pytest.fixture
def membership_factory():
    """Factory for creating membership test data."""
    def create_membership(**kwargs):
        defaults = {
            "circle_id": 1,
            "user_id": 2,
            "is_active": True,
            "payment_status": PaymentStatus.PENDING,
            "joined_at": datetime.utcnow(),
            "stripe_subscription_id": None,
            "next_payment_due": None
        }
        defaults.update(kwargs)
        
        mock_membership = Mock(spec=CircleMembership)
        for key, value in defaults.items():
            setattr(mock_membership, key, value)
        
        return mock_membership
    
    return create_membership 