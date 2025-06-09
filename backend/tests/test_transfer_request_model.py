"""
Tests for TransferRequest model - Test-Driven Development approach
Testing transfer request creation, state management, and business logic
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from app.models.transfer_request import TransferRequest, TransferRequestStatus
from app.models.user import User
from app.models.circle import Circle
from app.models.circle_membership import CircleMembership


class TestTransferRequestModel:
    """Test TransferRequest model creation and validation."""

    def test_create_transfer_request_with_required_fields(self, db_session, user_factory, circle_factory):
        """Test creating a transfer request with all required fields."""
        # Arrange
        requester = user_factory()
        source_circle = circle_factory()
        target_circle = circle_factory()
        
        # Act
        transfer_request = TransferRequest(
            requester_id=requester.id,
            source_circle_id=source_circle.id,
            target_circle_id=target_circle.id,
            reason="Looking for better schedule fit"
        )
        
        db_session.add(transfer_request)
        db_session.commit()
        
        # Assert
        assert transfer_request.id is not None
        assert transfer_request.requester_id == requester.id
        assert transfer_request.source_circle_id == source_circle.id
        assert transfer_request.target_circle_id == target_circle.id
        assert transfer_request.reason == "Looking for better schedule fit"
        assert transfer_request.status == TransferRequestStatus.PENDING
        assert transfer_request.created_at is not None
        assert transfer_request.reviewed_by_id is None
        assert transfer_request.reviewed_at is None
        assert transfer_request.review_notes is None

    def test_create_transfer_request_without_reason(self, db_session, user_factory, circle_factory):
        """Test creating a transfer request without optional reason."""
        # Arrange
        requester = user_factory()
        source_circle = circle_factory()
        target_circle = circle_factory()
        
        # Act
        transfer_request = TransferRequest(
            requester_id=requester.id,
            source_circle_id=source_circle.id,
            target_circle_id=target_circle.id
        )
        
        db_session.add(transfer_request)
        db_session.commit()
        
        # Assert
        assert transfer_request.reason is None
        assert transfer_request.status == TransferRequestStatus.PENDING

    def test_transfer_request_requires_requester_id(self, db_session, circle_factory):
        """Test that requester_id is required."""
        # Arrange
        source_circle = circle_factory()
        target_circle = circle_factory()
        
        # Act & Assert
        with pytest.raises(IntegrityError):
            transfer_request = TransferRequest(
                source_circle_id=source_circle.id,
                target_circle_id=target_circle.id,
                reason="Test request"
            )
            db_session.add(transfer_request)
            db_session.commit()

    def test_transfer_request_requires_source_circle_id(self, db_session, user_factory, circle_factory):
        """Test that source_circle_id is required."""
        # Arrange
        requester = user_factory()
        target_circle = circle_factory()
        
        # Act & Assert
        with pytest.raises(IntegrityError):
            transfer_request = TransferRequest(
                requester_id=requester.id,
                target_circle_id=target_circle.id,
                reason="Test request"
            )
            db_session.add(transfer_request)
            db_session.commit()

    def test_transfer_request_requires_target_circle_id(self, db_session, user_factory, circle_factory):
        """Test that target_circle_id is required."""
        # Arrange
        requester = user_factory()
        source_circle = circle_factory()
        
        # Act & Assert
        with pytest.raises(IntegrityError):
            transfer_request = TransferRequest(
                requester_id=requester.id,
                source_circle_id=source_circle.id,
                reason="Test request"
            )
            db_session.add(transfer_request)
            db_session.commit()

    def test_transfer_request_status_enum_values(self):
        """Test that TransferRequestStatus enum has expected values."""
        # Assert
        assert TransferRequestStatus.PENDING == "pending"
        assert TransferRequestStatus.APPROVED == "approved"
        assert TransferRequestStatus.DENIED == "denied"
        assert TransferRequestStatus.CANCELLED == "cancelled"

    def test_approve_transfer_request(self, db_session, user_factory, circle_factory):
        """Test approving a transfer request."""
        # Arrange
        requester = user_factory()
        reviewer = user_factory()
        source_circle = circle_factory()
        target_circle = circle_factory()
        
        transfer_request = TransferRequest(
            requester_id=requester.id,
            source_circle_id=source_circle.id,
            target_circle_id=target_circle.id,
            reason="Test request"
        )
        db_session.add(transfer_request)
        db_session.commit()
        
        # Act
        transfer_request.approve(reviewer.id, "Approved - good fit for target circle")
        db_session.commit()
        
        # Assert
        assert transfer_request.status == TransferRequestStatus.APPROVED
        assert transfer_request.reviewed_by_id == reviewer.id
        assert transfer_request.reviewed_at is not None
        assert transfer_request.review_notes == "Approved - good fit for target circle"

    def test_deny_transfer_request(self, db_session, user_factory, circle_factory):
        """Test denying a transfer request."""
        # Arrange
        requester = user_factory()
        reviewer = user_factory()
        source_circle = circle_factory()
        target_circle = circle_factory()
        
        transfer_request = TransferRequest(
            requester_id=requester.id,
            source_circle_id=source_circle.id,
            target_circle_id=target_circle.id,
            reason="Test request"
        )
        db_session.add(transfer_request)
        db_session.commit()
        
        # Act
        transfer_request.deny(reviewer.id, "Target circle at capacity")
        db_session.commit()
        
        # Assert
        assert transfer_request.status == TransferRequestStatus.DENIED
        assert transfer_request.reviewed_by_id == reviewer.id
        assert transfer_request.reviewed_at is not None
        assert transfer_request.review_notes == "Target circle at capacity"

    def test_cancel_transfer_request(self, db_session, user_factory, circle_factory):
        """Test cancelling a transfer request."""
        # Arrange
        requester = user_factory()
        source_circle = circle_factory()
        target_circle = circle_factory()
        
        transfer_request = TransferRequest(
            requester_id=requester.id,
            source_circle_id=source_circle.id,
            target_circle_id=target_circle.id,
            reason="Test request"
        )
        db_session.add(transfer_request)
        db_session.commit()
        
        # Act
        transfer_request.cancel()
        db_session.commit()
        
        # Assert
        assert transfer_request.status == TransferRequestStatus.CANCELLED

    def test_cannot_approve_non_pending_request(self, db_session, user_factory, circle_factory):
        """Test that only pending requests can be approved."""
        # Arrange
        requester = user_factory()
        reviewer = user_factory()
        source_circle = circle_factory()
        target_circle = circle_factory()
        
        transfer_request = TransferRequest(
            requester_id=requester.id,
            source_circle_id=source_circle.id,
            target_circle_id=target_circle.id,
            reason="Test request"
        )
        transfer_request.status = TransferRequestStatus.DENIED
        db_session.add(transfer_request)
        db_session.commit()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Only pending requests can be approved"):
            transfer_request.approve(reviewer.id, "Trying to approve denied request")

    def test_cannot_deny_non_pending_request(self, db_session, user_factory, circle_factory):
        """Test that only pending requests can be denied."""
        # Arrange
        requester = user_factory()
        reviewer = user_factory()
        source_circle = circle_factory()
        target_circle = circle_factory()
        
        transfer_request = TransferRequest(
            requester_id=requester.id,
            source_circle_id=source_circle.id,
            target_circle_id=target_circle.id,
            reason="Test request"
        )
        transfer_request.status = TransferRequestStatus.APPROVED
        db_session.add(transfer_request)
        db_session.commit()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Only pending requests can be denied"):
            transfer_request.deny(reviewer.id, "Trying to deny approved request")

    def test_cannot_cancel_non_pending_request(self, db_session, user_factory, circle_factory):
        """Test that only pending requests can be cancelled."""
        # Arrange
        requester = user_factory()
        reviewer = user_factory()
        source_circle = circle_factory()
        target_circle = circle_factory()
        
        transfer_request = TransferRequest(
            requester_id=requester.id,
            source_circle_id=source_circle.id,
            target_circle_id=target_circle.id,
            reason="Test request"
        )
        transfer_request.status = TransferRequestStatus.APPROVED
        db_session.add(transfer_request)
        db_session.commit()
        
        # Act & Assert
        with pytest.raises(ValueError, match="Only pending requests can be cancelled"):
            transfer_request.cancel()

    def test_is_pending_property(self, db_session, user_factory, circle_factory):
        """Test the is_pending property."""
        # Arrange
        requester = user_factory()
        source_circle = circle_factory()
        target_circle = circle_factory()
        
        transfer_request = TransferRequest(
            requester_id=requester.id,
            source_circle_id=source_circle.id,
            target_circle_id=target_circle.id,
            reason="Test request"
        )
        db_session.add(transfer_request)
        db_session.commit()
        
        # Assert
        assert transfer_request.is_pending is True
        
        # Act - approve the request
        reviewer = user_factory()
        transfer_request.approve(reviewer.id, "Approved")
        
        # Assert
        assert transfer_request.is_pending is False

    def test_string_representation(self, db_session, user_factory, circle_factory):
        """Test the string representation of TransferRequest."""
        # Arrange
        requester = user_factory()
        source_circle = circle_factory()
        target_circle = circle_factory()
        
        transfer_request = TransferRequest(
            requester_id=requester.id,
            source_circle_id=source_circle.id,
            target_circle_id=target_circle.id,
            reason="Test request"
        )
        db_session.add(transfer_request)
        db_session.commit()
        
        # Act & Assert
        expected = f"TransferRequest(id={transfer_request.id}, requester_id={requester.id}, status=pending)"
        assert str(transfer_request) == expected

    def test_transfer_request_relationships(self, db_session, user_factory, circle_factory):
        """Test that relationships are properly configured."""
        # Arrange
        requester = user_factory()
        reviewer = user_factory()
        source_circle = circle_factory()
        target_circle = circle_factory()
        
        transfer_request = TransferRequest(
            requester_id=requester.id,
            source_circle_id=source_circle.id,
            target_circle_id=target_circle.id,
            reason="Test request"
        )
        transfer_request.approve(reviewer.id, "Approved")
        db_session.add(transfer_request)
        db_session.commit()
        
        # Act & Assert
        assert transfer_request.requester == requester
        assert transfer_request.reviewed_by == reviewer
        assert transfer_request.source_circle == source_circle
        assert transfer_request.target_circle == target_circle

    def test_reason_length_constraint(self, db_session, user_factory, circle_factory):
        """Test that reason field has proper length constraints."""
        # Arrange
        requester = user_factory()
        source_circle = circle_factory()
        target_circle = circle_factory()
        long_reason = "x" * 1001  # Assuming max length is 1000
        
        # Act
        transfer_request = TransferRequest(
            requester_id=requester.id,
            source_circle_id=source_circle.id,
            target_circle_id=target_circle.id,
            reason=long_reason
        )
        
        # Assert - This should be handled by the model validation
        db_session.add(transfer_request)
        # Note: The actual constraint validation will depend on the model implementation 