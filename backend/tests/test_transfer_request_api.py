"""
Tests for Transfer Request API endpoints - Test-Driven Development approach
Testing member transfer request creation, listing, and facilitator approval operations
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient

from app.models.transfer_request import TransferRequest, TransferRequestStatus
from app.models.circle import Circle, CircleStatus
from app.models.user import User
from app.models.circle_membership import CircleMembership, PaymentStatus


class TestTransferRequestAPI:
    """Test transfer request API endpoints."""

    def test_create_transfer_request_requires_authentication(self, client: TestClient):
        """Test that creating a transfer request requires authentication."""
        # Arrange
        request_data = {
            "target_circle_id": 2,
            "reason": "Looking for better schedule fit"
        }
        
        # Act
        response = client.post("/api/v1/transfer-requests", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_transfer_request_successful(self, client: TestClient, override_get_current_user, override_get_transfer_request_service, mock_transfer_request):
        """Test successful transfer request creation."""
        # Arrange
        override_get_transfer_request_service.create_transfer_request.return_value = mock_transfer_request
        
        request_data = {
            "target_circle_id": 2,
            "reason": "Looking for better schedule fit"
        }
        
        # Act
        response = client.post(
            "/api/v1/transfer-requests",
            json=request_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["requester_id"] == 1
        assert response_data["target_circle_id"] == 2
        assert response_data["status"] == "pending"
        assert response_data["reason"] == "Looking for better schedule fit"

    def test_create_transfer_request_validates_target_circle_id(self, client: TestClient, override_get_current_user):
        """Test that target_circle_id is required."""
        # Arrange
        request_data = {
            "reason": "Looking for better schedule fit"
            # Missing target_circle_id
        }
        
        # Act
        response = client.post(
            "/api/v1/transfer-requests",
            json=request_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        error_detail = response.json()["detail"]
        assert any("target_circle_id" in str(error).lower() for error in error_detail)

    def test_create_transfer_request_without_reason(self, client: TestClient, override_get_current_user, override_get_transfer_request_service, mock_transfer_request):
        """Test creating transfer request without optional reason."""
        # Arrange
        mock_transfer_request.reason = None
        override_get_transfer_request_service.create_transfer_request.return_value = mock_transfer_request
        
        request_data = {
            "target_circle_id": 2
        }
        
        # Act
        response = client.post(
            "/api/v1/transfer-requests",
            json=request_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["reason"] is None

    def test_list_my_transfer_requests_requires_authentication(self, client: TestClient):
        """Test that listing transfer requests requires authentication."""
        # Act
        response = client.get("/api/v1/transfer-requests/my")
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_my_transfer_requests_successful(self, client: TestClient, override_get_current_user, override_get_transfer_request_service, transfer_request_factory):
        """Test successful listing of user's transfer requests."""
        # Arrange
        mock_requests = [
            transfer_request_factory(requester_id=1, target_circle_id=2, status="pending"),
            transfer_request_factory(requester_id=1, target_circle_id=3, status="approved")
        ]
        override_get_transfer_request_service.get_user_transfer_requests.return_value = mock_requests
        
        # Act
        response = client.get(
            "/api/v1/transfer-requests/my",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "requests" in response_data
        assert "total" in response_data
        assert len(response_data["requests"]) == 2
        assert response_data["total"] == 2

    def test_list_pending_requests_for_facilitator_requires_authentication(self, client: TestClient):
        """Test that listing pending requests requires authentication."""
        # Act
        response = client.get("/api/v1/transfer-requests/pending")
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_pending_requests_for_facilitator_successful(self, client: TestClient, override_get_current_user, override_get_transfer_request_service, transfer_request_factory):
        """Test successful listing of pending requests for facilitator."""
        # Arrange
        mock_requests = [
            transfer_request_factory(requester_id=2, target_circle_id=1, status="pending"),
            transfer_request_factory(requester_id=3, target_circle_id=1, status="pending")
        ]
        override_get_transfer_request_service.get_pending_requests_for_facilitator.return_value = mock_requests
        
        # Act
        response = client.get(
            "/api/v1/transfer-requests/pending",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert "requests" in response_data
        assert "total" in response_data
        assert len(response_data["requests"]) == 2

    def test_approve_transfer_request_requires_authentication(self, client: TestClient):
        """Test that approving a transfer request requires authentication."""
        # Arrange
        approval_data = {
            "review_notes": "Approved - good fit for target circle"
        }
        
        # Act
        response = client.post("/api/v1/transfer-requests/1/approve", json=approval_data)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_approve_transfer_request_successful(self, client: TestClient, override_get_current_user, override_get_transfer_request_service, mock_transfer_request):
        """Test successful transfer request approval."""
        # Arrange
        approved_request = mock_transfer_request.copy()
        approved_request.status = TransferRequestStatus.APPROVED
        approved_request.reviewed_by_id = 1
        approved_request.review_notes = "Approved - good fit for target circle"
        
        override_get_transfer_request_service.approve_transfer_request.return_value = approved_request
        
        approval_data = {
            "review_notes": "Approved - good fit for target circle"
        }
        
        # Act
        response = client.post(
            "/api/v1/transfer-requests/1/approve",
            json=approval_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["status"] == "approved"
        assert response_data["reviewed_by_id"] == 1
        assert response_data["review_notes"] == "Approved - good fit for target circle"

    def test_deny_transfer_request_requires_authentication(self, client: TestClient):
        """Test that denying a transfer request requires authentication."""
        # Arrange
        denial_data = {
            "review_notes": "Target circle at capacity"
        }
        
        # Act
        response = client.post("/api/v1/transfer-requests/1/deny", json=denial_data)
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_deny_transfer_request_successful(self, client: TestClient, override_get_current_user, override_get_transfer_request_service, mock_transfer_request):
        """Test successful transfer request denial."""
        # Arrange
        denied_request = mock_transfer_request.copy()
        denied_request.status = TransferRequestStatus.DENIED
        denied_request.reviewed_by_id = 1
        denied_request.review_notes = "Target circle at capacity"
        
        override_get_transfer_request_service.deny_transfer_request.return_value = denied_request
        
        denial_data = {
            "review_notes": "Target circle at capacity"
        }
        
        # Act
        response = client.post(
            "/api/v1/transfer-requests/1/deny",
            json=denial_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["status"] == "denied"
        assert response_data["reviewed_by_id"] == 1
        assert response_data["review_notes"] == "Target circle at capacity"

    def test_cancel_transfer_request_requires_authentication(self, client: TestClient):
        """Test that cancelling a transfer request requires authentication."""
        # Act
        response = client.delete("/api/v1/transfer-requests/1")
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_cancel_transfer_request_successful(self, client: TestClient, override_get_current_user, override_get_transfer_request_service):
        """Test successful transfer request cancellation."""
        # Arrange
        override_get_transfer_request_service.cancel_transfer_request.return_value = True
        
        # Act
        response = client.delete(
            "/api/v1/transfer-requests/1",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_get_transfer_request_by_id_requires_authentication(self, client: TestClient):
        """Test that getting a specific transfer request requires authentication."""
        # Act
        response = client.get("/api/v1/transfer-requests/1")
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_transfer_request_by_id_successful(self, client: TestClient, override_get_current_user, override_get_transfer_request_service, mock_transfer_request):
        """Test successful retrieval of specific transfer request."""
        # Arrange
        override_get_transfer_request_service.get_transfer_request_by_id.return_value = mock_transfer_request
        
        # Act
        response = client.get(
            "/api/v1/transfer-requests/1",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == 1
        assert response_data["requester_id"] == 1
        assert response_data["status"] == "pending"

    def test_get_transfer_request_not_found(self, client: TestClient, override_get_current_user, override_get_transfer_request_service):
        """Test 404 when transfer request doesn't exist."""
        # Arrange
        from fastapi import HTTPException
        override_get_transfer_request_service.get_transfer_request_by_id.side_effect = HTTPException(
            status_code=404, detail="Transfer request not found"
        )
        
        # Act
        response = client.get(
            "/api/v1/transfer-requests/999",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_approve_request_with_execute_transfer_flag(self, client: TestClient, override_get_current_user, override_get_transfer_request_service, mock_transfer_request):
        """Test approving and executing transfer in one operation."""
        # Arrange
        approved_request = mock_transfer_request.copy()
        approved_request.status = TransferRequestStatus.APPROVED
        
        override_get_transfer_request_service.approve_and_execute_transfer.return_value = approved_request
        
        approval_data = {
            "review_notes": "Approved and executed",
            "execute_transfer": True
        }
        
        # Act
        response = client.post(
            "/api/v1/transfer-requests/1/approve",
            json=approval_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["status"] == "approved"

    def test_list_transfer_requests_with_filtering(self, client: TestClient, override_get_current_user, override_get_transfer_request_service, transfer_request_factory):
        """Test listing transfer requests with status filtering."""
        # Arrange
        mock_requests = [
            transfer_request_factory(status="pending"),
            transfer_request_factory(status="pending")
        ]
        override_get_transfer_request_service.get_pending_requests_for_facilitator.return_value = mock_requests
        
        # Act
        response = client.get(
            "/api/v1/transfer-requests/pending?circle_id=1",
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data["requests"]) == 2

    def test_create_transfer_request_prevents_duplicate_pending(self, client: TestClient, override_get_current_user, override_get_transfer_request_service):
        """Test that duplicate pending requests are prevented."""
        # Arrange
        from fastapi import HTTPException
        override_get_transfer_request_service.create_transfer_request.side_effect = HTTPException(
            status_code=422, detail="User already has a pending transfer request for this circle"
        )
        
        request_data = {
            "target_circle_id": 2,
            "reason": "Duplicate request"
        }
        
        # Act
        response = client.post(
            "/api/v1/transfer-requests",
            json=request_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_approve_request_validates_facilitator_permission(self, client: TestClient, override_get_current_user, override_get_transfer_request_service):
        """Test that only facilitators can approve requests."""
        # Arrange
        from fastapi import HTTPException
        override_get_transfer_request_service.approve_transfer_request.side_effect = HTTPException(
            status_code=403, detail="Only facilitators can approve transfer requests"
        )
        
        approval_data = {
            "review_notes": "Trying to approve without permission"
        }
        
        # Act
        response = client.post(
            "/api/v1/transfer-requests/1/approve",
            json=approval_data,
            headers={"Authorization": "Bearer fake-token"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN 