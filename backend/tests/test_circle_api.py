"""
Tests for Circle API endpoints - Test-Driven Development approach
Testing circle creation API with facilitator assignment before implementation
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient

from app.models.circle import Circle, CircleStatus
from app.models.user import User
from app.core.exceptions import ValidationError, CapacityExceeded


class TestCircleCreationAPI:
    """Test the POST /api/v1/circles endpoint for creating circles."""

    def test_create_circle_with_valid_data(self, client: TestClient, mock_current_user: User, mock_circle: Circle, sample_circle_data: dict):
        """Test circle creation with valid data."""
        with patch('app.core.deps.get_current_user', return_value=mock_current_user), \
             patch('app.services.circle_service.get_circle_service') as mock_service_dep:
            
            # Arrange
            mock_service = AsyncMock()
            mock_service.create_circle.return_value = mock_circle
            mock_service_dep.return_value = mock_service
            
            # Act
            response = client.post(
                "/api/v1/circles",
                json=sample_circle_data,
                headers={"Authorization": "Bearer fake-token"}
            )
            
            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            response_data = response.json()
            assert response_data["name"] == mock_circle.name
            assert response_data["description"] == mock_circle.description
            assert response_data["facilitator_id"] == mock_circle.facilitator_id
            assert response_data["capacity_max"] == mock_circle.capacity_max
            assert response_data["status"] == mock_circle.status.value
            assert response_data["is_active"] is True
            assert "id" in response_data
            assert "created_at" in response_data

    def test_create_circle_requires_authentication(self, client: TestClient):
        """Test that circle creation requires authentication."""
        # Arrange
        circle_data = {
            "name": "Test Circle",
            "description": "Test description"
        }
        
        # Act
        response = client.post("/api/v1/circles", json=circle_data)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_circle_with_minimal_data(self, client: TestClient, mock_current_user: User):
        """Test circle creation with minimal required data."""
        # Arrange
        circle_data = {
            "name": "Minimal Circle"
        }
        
        # Act
        response = await async_client.post(
            "/api/v1/circles",
            json=circle_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["name"] == "Minimal Circle"
        assert response_data["facilitator_id"] == mock_current_user.id
        assert response_data["capacity_min"] == 2  # Default value
        assert response_data["capacity_max"] == 8  # Default value
        assert response_data["status"] == CircleStatus.FORMING.value

    def test_create_circle_validates_name_required(self, client: TestClient):
        """Test that circle name is required."""
        # Arrange
        circle_data = {
            "description": "Circle without name"
        }
        
        # Act
        response = client.post(
            "/api/v1/circles",
            json=circle_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_detail = response.json()["detail"]
        assert any("name" in str(error).lower() for error in error_detail)

    async def test_create_circle_validates_name_length(self, async_client: AsyncClient):
        """Test that circle name length is validated."""
        # Arrange
        circle_data = {
            "name": "A" * 101  # Over 100 character limit
        }
        
        # Act
        response = await async_client.post(
            "/api/v1/circles",
            json=circle_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_circle_validates_capacity_constraints(self, async_client: AsyncClient):
        """Test capacity constraint validation."""
        # Test capacity_max over 10
        circle_data = {
            "name": "Test Circle",
            "capacity_max": 15  # Over 10 limit
        }
        
        response = await async_client.post(
            "/api/v1/circles",
            json=circle_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test capacity_min under 2
        circle_data = {
            "name": "Test Circle",
            "capacity_min": 1  # Under 2 limit
        }
        
        response = await async_client.post(
            "/api/v1/circles",
            json=circle_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_circle_validates_description_length(self, async_client: AsyncClient):
        """Test description length validation."""
        # Arrange
        circle_data = {
            "name": "Test Circle",
            "description": "A" * 1001  # Over 1000 character limit
        }
        
        # Act
        response = await async_client.post(
            "/api/v1/circles",
            json=circle_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_circle_validates_location_length(self, async_client: AsyncClient):
        """Test location field length validation."""
        # Test location_name too long
        circle_data = {
            "name": "Test Circle",
            "location_name": "A" * 201  # Over 200 character limit
        }
        
        response = await async_client.post(
            "/api/v1/circles",
            json=circle_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Test location_address too long
        circle_data = {
            "name": "Test Circle",
            "location_address": "A" * 501  # Over 500 character limit
        }
        
        response = await async_client.post(
            "/api/v1/circles",
            json=circle_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_circle_sets_facilitator_as_current_user(self, async_client: AsyncClient, mock_current_user: User):
        """Test that facilitator is automatically set to current user."""
        # Arrange
        circle_data = {
            "name": "Test Circle",
            "facilitator_id": 999  # This should be ignored and set to current user
        }
        
        # Act
        response = await async_client.post(
            "/api/v1/circles",
            json=circle_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["facilitator_id"] == mock_current_user.id
        assert response_data["facilitator_id"] != 999

    async def test_create_circle_validates_meeting_schedule_format(self, async_client: AsyncClient):
        """Test meeting schedule JSON validation."""
        # Valid schedule should work
        circle_data = {
            "name": "Test Circle",
            "meeting_schedule": {
                "day": "Wednesday",
                "time": "19:00",
                "frequency": "weekly"
            }
        }
        
        response = await async_client.post(
            "/api/v1/circles",
            json=circle_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Invalid schedule format should fail
        circle_data = {
            "name": "Test Circle",
            "meeting_schedule": "invalid-not-json"
        }
        
        response = await async_client.post(
            "/api/v1/circles",
            json=circle_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_circle_handles_service_errors(self, async_client: AsyncClient):
        """Test error handling when service layer fails."""
        # This test will verify proper error handling when the service layer
        # encounters database errors or other issues
        pass  # Will be implemented when service layer is created

    async def test_create_circle_response_format(self, async_client: AsyncClient, mock_current_user: User):
        """Test that response includes all expected fields."""
        # Arrange
        circle_data = {
            "name": "Response Format Test",
            "description": "Testing response format",
            "capacity_max": 6,
            "location_name": "Test Location"
        }
        
        # Act
        response = await async_client.post(
            "/api/v1/circles",
            json=circle_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        
        # Check all expected fields are present
        expected_fields = [
            "id", "name", "description", "facilitator_id", "capacity_min", 
            "capacity_max", "location_name", "location_address", "meeting_schedule",
            "status", "is_active", "created_at", "updated_at"
        ]
        
        for field in expected_fields:
            assert field in response_data

    async def test_create_circle_with_custom_capacity(self, async_client: AsyncClient):
        """Test circle creation with custom capacity settings."""
        # Arrange
        circle_data = {
            "name": "Custom Capacity Circle",
            "capacity_min": 4,
            "capacity_max": 6
        }
        
        # Act
        response = await async_client.post(
            "/api/v1/circles",
            json=circle_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["capacity_min"] == 4
        assert response_data["capacity_max"] == 6


class TestCircleListAPI:
    """Test the GET /api/v1/circles endpoint for listing circles."""

    async def test_list_circles_requires_authentication(self, async_client: AsyncClient):
        """Test that listing circles requires authentication."""
        # Act
        response = await async_client.get("/api/v1/circles")
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_list_circles_returns_user_circles(self, async_client: AsyncClient, mock_current_user: User):
        """Test that list returns circles user has access to."""
        # Act
        response = await async_client.get(
            "/api/v1/circles",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert isinstance(response_data, list)
        # Additional assertions will be added when service layer is implemented

    async def test_list_circles_filters_by_permissions(self, async_client: AsyncClient):
        """Test that circles are filtered based on user permissions."""
        # This test will verify that users only see circles they have access to
        # based on their role and permissions
        pass  # Will be implemented when permissions logic is added


class TestCircleDetailAPI:
    """Test the GET /api/v1/circles/{id} endpoint for getting circle details."""

    async def test_get_circle_by_id_requires_authentication(self, async_client: AsyncClient):
        """Test that getting circle details requires authentication."""
        # Act
        response = await async_client.get("/api/v1/circles/1")
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_circle_by_id_returns_details(self, async_client: AsyncClient):
        """Test getting circle details by ID."""
        # Act
        response = await async_client.get(
            "/api/v1/circles/1",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # This test structure will be completed when service layer is implemented
        # Should return 200 with circle details or 404 if not found
        pass

    async def test_get_circle_by_id_checks_permissions(self, async_client: AsyncClient):
        """Test that circle access is checked based on permissions."""
        # This test will verify that users can only access circles
        # they have permission to see based on their role
        pass  # Will be implemented when permissions logic is added


# Integration tests will be added when database fixtures are available
class TestCircleAPIIntegration:
    """Integration tests for Circle API with database."""

    async def test_circle_creation_saves_to_database(self):
        """Test that circle creation properly saves to database."""
        # This will be implemented when database integration is available
        pass

    async def test_circle_creation_with_real_authentication(self):
        """Test circle creation with real authentication flow."""
        # This will be implemented when authentication integration is complete
        pass

    async def test_circle_list_with_real_data(self):
        """Test circle listing with real database data."""
        # This will be implemented when database integration is available
        pass 