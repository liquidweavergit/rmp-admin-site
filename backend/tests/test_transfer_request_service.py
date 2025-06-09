"""
Tests for TransferRequestService - Test-Driven Development approach
Testing business logic for transfer request creation, approval, and management
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from fastapi import HTTPException

from app.services.transfer_request_service import TransferRequestService
from app.models.transfer_request import TransferRequest, TransferRequestStatus
from app.models.circle import Circle, CircleStatus
from app.models.user import User
from app.models.circle_membership import CircleMembership, PaymentStatus


class TestTransferRequestService:
    """Test TransferRequestService business logic."""

    @pytest.fixture
    def transfer_request_service(self, mock_db_session):
        """Create TransferRequestService instance with mocked dependencies."""
        return TransferRequestService(db=mock_db_session)

    async def test_create_transfer_request_successful(self, transfer_request_service, mock_db_session, user_factory, circle_factory, membership_factory):
        """Test successful transfer request creation."""
        # Arrange
        requester = user_factory(id=1)
        source_circle = circle_factory(id=1)
        target_circle = circle_factory(id=2)
        membership = membership_factory(user_id=1, circle_id=1)
        
        # Mock database queries
        mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [
            membership,  # Active membership check
            None,        # No existing pending request
            target_circle # Target circle exists
        ]
        
        # Act
        result = await transfer_request_service.create_transfer_request(
            user_id=1,
            target_circle_id=2,
            reason="Looking for better schedule fit"
        )
        
        # Assert
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        assert isinstance(result, TransferRequest)
        assert result.requester_id == 1
        assert result.target_circle_id == 2
        assert result.reason == "Looking for better schedule fit"
        assert result.status == TransferRequestStatus.PENDING

    def test_create_transfer_request_validates_active_membership(self, transfer_request_service, mock_db_session):
        """Test that user must be an active member to request transfer."""
        # Arrange
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None  # No active membership
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            transfer_request_service.create_transfer_request(
                user_id=1,
                target_circle_id=2,
                reason="Test"
            )
        
        assert exc_info.value.status_code == 422
        assert "not an active member" in exc_info.value.detail

    def test_create_transfer_request_prevents_duplicate_pending(self, transfer_request_service, mock_db_session, user_factory, circle_factory, membership_factory, transfer_request_factory):
        """Test that duplicate pending requests are prevented."""
        # Arrange
        membership = membership_factory(user_id=1, circle_id=1)
        existing_request = transfer_request_factory(requester_id=1, target_circle_id=2, status="pending")
        
        mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [
            membership,        # Active membership check
            existing_request,  # Existing pending request
        ]
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            transfer_request_service.create_transfer_request(
                user_id=1,
                target_circle_id=2,
                reason="Duplicate request"
            )
        
        assert exc_info.value.status_code == 422
        assert "already has a pending transfer request" in exc_info.value.detail

    def test_create_transfer_request_validates_target_circle_exists(self, transfer_request_service, mock_db_session, membership_factory):
        """Test that target circle must exist."""
        # Arrange
        membership = membership_factory(user_id=1, circle_id=1)
        
        mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [
            membership,  # Active membership check
            None,        # No existing pending request
            None         # Target circle doesn't exist
        ]
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            transfer_request_service.create_transfer_request(
                user_id=1,
                target_circle_id=999,
                reason="Test"
            )
        
        assert exc_info.value.status_code == 404
        assert "Target circle not found" in exc_info.value.detail

    def test_get_user_transfer_requests(self, transfer_request_service, mock_db_session, transfer_request_factory):
        """Test retrieving user's transfer requests."""
        # Arrange
        mock_requests = [
            transfer_request_factory(requester_id=1, status="pending"),
            transfer_request_factory(requester_id=1, status="approved")
        ]
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = mock_requests
        
        # Act
        result = transfer_request_service.get_user_transfer_requests(user_id=1)
        
        # Assert
        assert len(result) == 2
        assert all(req.requester_id == 1 for req in result)

    def test_get_pending_requests_for_facilitator(self, transfer_request_service, mock_db_session, transfer_request_factory, circle_factory):
        """Test retrieving pending requests for facilitator's circles."""
        # Arrange
        facilitator_circles = [circle_factory(id=1, facilitator_id=1), circle_factory(id=2, facilitator_id=1)]
        pending_requests = [
            transfer_request_factory(target_circle_id=1, status="pending"),
            transfer_request_factory(target_circle_id=2, status="pending")
        ]
        
        mock_db_session.execute.return_value.scalars.return_value.all.side_effect = [
            facilitator_circles,
            pending_requests
        ]
        
        # Act
        result = transfer_request_service.get_pending_requests_for_facilitator(facilitator_id=1)
        
        # Assert
        assert len(result) == 2
        assert all(req.status == TransferRequestStatus.PENDING for req in result)

    def test_approve_transfer_request_successful(self, transfer_request_service, mock_db_session, transfer_request_factory, circle_factory):
        """Test successful transfer request approval."""
        # Arrange
        transfer_request = transfer_request_factory(id=1, status="pending", target_circle_id=2)
        target_circle = circle_factory(id=2, facilitator_id=1)
        
        mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [
            transfer_request,  # Get transfer request
            target_circle      # Get target circle
        ]
        
        # Act
        result = transfer_request_service.approve_transfer_request(
            request_id=1,
            reviewer_id=1,
            review_notes="Approved - good fit"
        )
        
        # Assert
        mock_db_session.commit.assert_called_once()
        assert result.status == TransferRequestStatus.APPROVED
        assert result.reviewed_by_id == 1
        assert result.review_notes == "Approved - good fit"

    def test_approve_transfer_request_validates_facilitator_permission(self, transfer_request_service, mock_db_session, transfer_request_factory, circle_factory):
        """Test that only facilitators can approve requests."""
        # Arrange
        transfer_request = transfer_request_factory(id=1, status="pending", target_circle_id=2)
        target_circle = circle_factory(id=2, facilitator_id=2)  # Different facilitator
        
        mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [
            transfer_request,
            target_circle
        ]
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            transfer_request_service.approve_transfer_request(
                request_id=1,
                reviewer_id=1,  # Not the facilitator
                review_notes="Trying to approve"
            )
        
        assert exc_info.value.status_code == 403
        assert "Only facilitators can approve" in exc_info.value.detail

    def test_approve_transfer_request_validates_pending_status(self, transfer_request_service, mock_db_session, transfer_request_factory, circle_factory):
        """Test that only pending requests can be approved."""
        # Arrange
        transfer_request = transfer_request_factory(id=1, status="approved", target_circle_id=2)
        target_circle = circle_factory(id=2, facilitator_id=1)
        
        mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [
            transfer_request,
            target_circle
        ]
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            transfer_request_service.approve_transfer_request(
                request_id=1,
                reviewer_id=1,
                review_notes="Already approved"
            )
        
        assert exc_info.value.status_code == 422
        assert "Only pending requests can be approved" in exc_info.value.detail

    def test_deny_transfer_request_successful(self, transfer_request_service, mock_db_session, transfer_request_factory, circle_factory):
        """Test successful transfer request denial."""
        # Arrange
        transfer_request = transfer_request_factory(id=1, status="pending", target_circle_id=2)
        target_circle = circle_factory(id=2, facilitator_id=1)
        
        mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [
            transfer_request,
            target_circle
        ]
        
        # Act
        result = transfer_request_service.deny_transfer_request(
            request_id=1,
            reviewer_id=1,
            review_notes="Target circle at capacity"
        )
        
        # Assert
        mock_db_session.commit.assert_called_once()
        assert result.status == TransferRequestStatus.DENIED
        assert result.reviewed_by_id == 1
        assert result.review_notes == "Target circle at capacity"

    def test_cancel_transfer_request_successful(self, transfer_request_service, mock_db_session, transfer_request_factory):
        """Test successful transfer request cancellation by requester."""
        # Arrange
        transfer_request = transfer_request_factory(id=1, requester_id=1, status="pending")
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = transfer_request
        
        # Act
        result = transfer_request_service.cancel_transfer_request(request_id=1, user_id=1)
        
        # Assert
        mock_db_session.commit.assert_called_once()
        assert result is True

    def test_cancel_transfer_request_validates_ownership(self, transfer_request_service, mock_db_session, transfer_request_factory):
        """Test that only the requester can cancel their request."""
        # Arrange
        transfer_request = transfer_request_factory(id=1, requester_id=2, status="pending")
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = transfer_request
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            transfer_request_service.cancel_transfer_request(request_id=1, user_id=1)
        
        assert exc_info.value.status_code == 403
        assert "only cancel your own requests" in exc_info.value.detail

    def test_approve_and_execute_transfer_successful(self, transfer_request_service, mock_db_session, transfer_request_factory, circle_factory):
        """Test approving and executing transfer in one operation."""
        # Arrange
        transfer_request = transfer_request_factory(id=1, requester_id=2, source_circle_id=1, target_circle_id=2, status="pending")
        source_circle = circle_factory(id=1, facilitator_id=1)
        target_circle = circle_factory(id=2, facilitator_id=1)
        
        mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [
            transfer_request,
            target_circle,
            source_circle,
            target_circle
        ]
        
        # Mock circle service
        with patch('app.services.transfer_request_service.CircleService') as mock_circle_service:
            mock_circle_service_instance = mock_circle_service.return_value
            mock_membership = Mock()
            mock_circle_service_instance.transfer_member_between_circles.return_value = mock_membership
            
            # Act
            result = transfer_request_service.approve_and_execute_transfer(
                request_id=1,
                reviewer_id=1,
                review_notes="Approved and executed"
            )
        
        # Assert
        assert result.status == TransferRequestStatus.APPROVED
        mock_circle_service_instance.transfer_member_between_circles.assert_called_once()

    def test_get_transfer_request_by_id_successful(self, transfer_request_service, mock_db_session, transfer_request_factory):
        """Test retrieving transfer request by ID."""
        # Arrange
        transfer_request = transfer_request_factory(id=1, requester_id=1)
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = transfer_request
        
        # Act
        result = transfer_request_service.get_transfer_request_by_id(request_id=1, user_id=1)
        
        # Assert
        assert result == transfer_request

    def test_get_transfer_request_by_id_validates_access(self, transfer_request_service, mock_db_session, transfer_request_factory, circle_factory):
        """Test that users can only access their own requests or requests for circles they facilitate."""
        # Arrange
        transfer_request = transfer_request_factory(id=1, requester_id=2, target_circle_id=3)
        mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [
            transfer_request,
            None  # User doesn't facilitate the target circle
        ]
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            transfer_request_service.get_transfer_request_by_id(request_id=1, user_id=1)
        
        assert exc_info.value.status_code == 403
        assert "access this transfer request" in exc_info.value.detail

    def test_create_transfer_request_prevents_same_circle_transfer(self, transfer_request_service, mock_db_session, membership_factory):
        """Test that users cannot request transfer to their current circle."""
        # Arrange
        membership = membership_factory(user_id=1, circle_id=1)
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = membership
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            transfer_request_service.create_transfer_request(
                user_id=1,
                target_circle_id=1,  # Same as current circle
                reason="Test"
            )
        
        assert exc_info.value.status_code == 422
        assert "cannot request transfer to your current circle" in exc_info.value.detail

    def test_create_transfer_request_validates_target_circle_capacity(self, transfer_request_service, mock_db_session, membership_factory, circle_factory):
        """Test that target circle capacity is checked."""
        # Arrange
        membership = membership_factory(user_id=1, circle_id=1)
        target_circle = circle_factory(id=2)
        target_circle.can_accept_members.return_value = False  # At capacity
        
        mock_db_session.execute.return_value.scalar_one_or_none.side_effect = [
            membership,      # Active membership check
            None,           # No existing pending request
            target_circle   # Target circle exists but at capacity
        ]
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            transfer_request_service.create_transfer_request(
                user_id=1,
                target_circle_id=2,
                reason="Test"
            )
        
        assert exc_info.value.status_code == 422
        assert "Target circle is at maximum capacity" in exc_info.value.detail

    def test_get_transfer_request_statistics(self, transfer_request_service, mock_db_session):
        """Test getting transfer request statistics."""
        # Arrange
        mock_stats = [
            ("pending", 5),
            ("approved", 10),
            ("denied", 3)
        ]
        mock_db_session.execute.return_value.all.return_value = mock_stats
        
        # Act
        result = transfer_request_service.get_transfer_request_statistics()
        
        # Assert
        assert result == {
            "pending": 5,
            "approved": 10,
            "denied": 3,
            "total": 18
        } 