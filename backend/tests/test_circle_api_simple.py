"""
Simplified Circle API tests - Test-Driven Development approach
Testing circle creation API with facilitator assignment
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient

from app.models.circle import Circle, CircleStatus
from app.models.user import User


class TestCircleCreationAPI:
    """Test the POST /api/v1/circles endpoint for creating circles."""

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
            assert response_data["facilitator_id"] == mock_circle.facilitator_id
            assert response_data["status"] == mock_circle.status.value
            assert "id" in response_data

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

    def test_create_circle_validates_capacity_constraints(self, client: TestClient):
        """Test capacity constraint validation."""
        # Test capacity_max over 10
        circle_data = {
            "name": "Test Circle",
            "capacity_max": 15  # Over 10 limit
        }
        
        response = client.post(
            "/api/v1/circles",
            json=circle_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCircleListAPI:
    """Test the GET /api/v1/circles endpoint for listing circles."""

    def test_list_circles_requires_authentication(self, client: TestClient):
        """Test that listing circles requires authentication."""
        # Act
        response = client.get("/api/v1/circles")
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_circles_returns_user_circles(self, client: TestClient, mock_current_user: User):
        """Test that list returns circles user has access to."""
        with patch('app.core.deps.get_current_user', return_value=mock_current_user), \
             patch('app.services.circle_service.get_circle_service') as mock_service_dep:
            
            # Arrange
            mock_service = AsyncMock()
            mock_service.list_circles_for_user.return_value = ([], 0)
            mock_service_dep.return_value = mock_service
            
            # Act
            response = client.get(
                "/api/v1/circles",
                headers={"Authorization": "Bearer fake-token"}
            )
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert isinstance(response_data, list)


class TestCircleDetailAPI:
    """Test the GET /api/v1/circles/{id} endpoint for getting circle details."""

    def test_get_circle_by_id_requires_authentication(self, client: TestClient):
        """Test that getting circle details requires authentication."""
        # Act
        response = client.get("/api/v1/circles/1")
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 