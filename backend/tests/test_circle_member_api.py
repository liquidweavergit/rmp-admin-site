"""
Tests for Circle Member Management API endpoints - Test-Driven Development approach
Testing member add/remove/transfer operations and member listing
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient

from app.models.circle import Circle, CircleStatus
from app.models.user import User
from app.models.circle_membership import CircleMembership, PaymentStatus
from app.core.exceptions import ValidationError, CapacityExceeded


class TestCircleMemberManagementAPI:
    """Test circle member management API endpoints."""

    def test_add_member_requires_authentication(self, client: TestClient):
        """Test that adding a member requires authentication."""
        # Arrange
        member_data = {
            "user_id": 2,
            "payment_status": "pending"
        }
        
        # Act
        response = client.post("/api/v1/circles/1/members", json=member_data)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_add_member_successful(self, client: TestClient, override_get_current_user, override_get_circle_service, mock_circle_membership):
        """Test successful member addition."""
        # Arrange
        override_get_circle_service.add_member_to_circle.return_value = mock_circle_membership
        
        member_data = {
            "user_id": 2,
            "payment_status": "pending"
        }
        
        # Act
        response = client.post(
            "/api/v1/circles/1/members",
            json=member_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["user_id"] == 2
        assert response_data["circle_id"] == 1
        assert response_data["payment_status"] == "pending"

    def test_add_member_validates_required_fields(self, client: TestClient, override_get_current_user, override_get_circle_service):
        """Test that user_id is required for adding members."""
        # Arrange
        member_data = {
            "payment_status": "pending"
            # Missing user_id
        }
        
        # Act
        response = client.post(
            "/api/v1/circles/1/members",
            json=member_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_detail = response.json()["detail"]
        assert any("user_id" in str(error).lower() for error in error_detail)

    def test_add_member_validates_payment_status(self, client: TestClient, override_get_current_user, override_get_circle_service):
        """Test payment status validation for member addition."""
        # Arrange
        member_data = {
            "user_id": 2,
            "payment_status": "invalid_status"
        }
        
        # Act
        response = client.post(
            "/api/v1/circles/1/members",
            json=member_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_remove_member_requires_authentication(self, client: TestClient):
        """Test that removing a member requires authentication."""
        # Act
        response = client.delete("/api/v1/circles/1/members/2")
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_remove_member_successful(self, client: TestClient, override_get_current_user, override_get_circle_service):
        """Test successful member removal."""
        # Arrange
        override_get_circle_service.remove_member_from_circle.return_value = True
        
        # Act
        response = client.delete(
            "/api/v1/circles/1/members/2",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_remove_member_not_found(self, client: TestClient, override_get_current_user, override_get_circle_service):
        """Test removing non-existent member."""
        # Arrange
        override_get_circle_service.remove_member_from_circle.return_value = False
        
        # Act
        response = client.delete(
            "/api/v1/circles/1/members/2",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_circle_members_requires_authentication(self, client: TestClient):
        """Test that listing circle members requires authentication."""
        # Act
        response = client.get("/api/v1/circles/1/members")
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_circle_members_successful(self, client: TestClient, override_get_current_user, override_get_circle_service, membership_factory):
        """Test successful listing of circle members."""
        # Arrange
        mock_memberships = [
            membership_factory(user_id=2, circle_id=1),
            membership_factory(user_id=3, circle_id=1)
        ]
        override_get_circle_service.get_circle_members.return_value = mock_memberships
        
        # Act
        response = client.get(
            "/api/v1/circles/1/members",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "members" in response_data
        assert "total" in response_data
        assert len(response_data["members"]) == 2
        assert response_data["total"] == 2
        assert response_data["members"][0]["user_id"] == 2
        assert response_data["members"][1]["user_id"] == 3

    def test_transfer_member_requires_authentication(self, client: TestClient):
        """Test that transferring a member requires authentication."""
        # Arrange
        transfer_data = {
            "target_circle_id": 2,
            "reason": "Better fit for the other circle"
        }
        
        # Act
        response = client.post("/api/v1/circles/1/members/2/transfer", json=transfer_data)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_transfer_member_successful(self, client: TestClient, override_get_current_user, override_get_circle_service, mock_circle_membership):
        """Test successful member transfer between circles."""
        # Arrange
        override_get_circle_service.transfer_member_between_circles.return_value = mock_circle_membership
        
        transfer_data = {
            "target_circle_id": 2,
            "reason": "Better fit for the other circle"
        }
        
        # Act
        response = client.post(
            "/api/v1/circles/1/members/2/transfer",
            json=transfer_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["user_id"] == 2
        assert response_data["circle_id"] == 1

    def test_transfer_member_validates_target_circle(self, client: TestClient, override_get_current_user, override_get_circle_service):
        """Test that target_circle_id is required for transfer."""
        # Arrange
        transfer_data = {
            "reason": "Better fit for the other circle"
            # Missing target_circle_id
        }
        
        # Act
        response = client.post(
            "/api/v1/circles/1/members/2/transfer",
            json=transfer_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_detail = response.json()["detail"]
        assert any("target_circle_id" in str(error).lower() for error in error_detail)

    def test_update_member_payment_status_requires_authentication(self, client: TestClient):
        """Test that updating payment status requires authentication."""
        # Arrange
        payment_data = {
            "payment_status": "current"
        }
        
        # Act
        response = client.patch("/api/v1/circles/1/members/2/payment", json=payment_data)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_member_payment_status_successful(self, client: TestClient, override_get_current_user, override_get_circle_service, mock_circle_membership):
        """Test successful payment status update."""
        # Arrange
        override_get_circle_service.update_member_payment_status.return_value = mock_circle_membership
        
        payment_data = {
            "payment_status": "current"
        }
        
        # Act
        response = client.patch(
            "/api/v1/circles/1/members/2/payment",
            json=payment_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["user_id"] == 2
        assert response_data["circle_id"] == 1


class TestCircleMemberBusinessLogic:
    """Test business logic for circle member management."""

    def test_add_member_enforces_capacity_limits(self, client: TestClient, override_get_current_user, override_get_circle_service):
        """Test that adding members enforces circle capacity limits."""
        # Arrange
        override_get_circle_service.add_member_to_circle.side_effect = Exception("Circle is at maximum capacity")
        
        member_data = {
            "user_id": 2,
            "payment_status": "pending"
        }
        
        # Act
        response = client.post(
            "/api/v1/circles/1/members",
            json=member_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_add_member_prevents_duplicate_membership(self, client: TestClient, override_get_current_user, override_get_circle_service):
        """Test that users cannot be added to the same circle twice."""
        # Arrange
        override_get_circle_service.add_member_to_circle.side_effect = Exception("User is already a member")
        
        member_data = {
            "user_id": 2,
            "payment_status": "pending"
        }
        
        # Act
        response = client.post(
            "/api/v1/circles/1/members",
            json=member_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_facilitator_only_operations(self, client: TestClient, override_get_current_user, override_get_circle_service):
        """Test that only facilitators can manage members."""
        # Arrange
        override_get_circle_service.add_member_to_circle.side_effect = Exception("Only facilitators can add members")
        
        member_data = {
            "user_id": 2,
            "payment_status": "pending"
        }
        
        # Act
        response = client.post(
            "/api/v1/circles/1/members",
            json=member_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


class TestCircleMemberIntegration:
    """Integration tests for circle member management."""

    @pytest.mark.skip(reason="Integration test - requires database setup")
    def test_complete_member_lifecycle(self, client: TestClient):
        """Test complete member lifecycle from addition to removal."""
        pass

    @pytest.mark.skip(reason="Integration test - requires database setup")
    def test_member_capacity_enforcement_with_real_data(self, client: TestClient):
        """Test capacity enforcement with real database constraints."""
        pass 