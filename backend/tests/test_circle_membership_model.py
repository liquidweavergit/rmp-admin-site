"""
Tests for CircleMembership model - Test-Driven Development approach
Testing circle membership management and payment status tracking before implementation
"""
import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from app.models.circle_membership import CircleMembership, PaymentStatus
from app.core.exceptions import ValidationError, BusinessRuleViolation


class TestCircleMembershipModel:
    """Test the CircleMembership model implementation."""

    def test_circle_membership_creation_with_valid_data(self):
        """Test circle membership can be created with valid data."""
        # Arrange
        membership_data = {
            "circle_id": 1,
            "user_id": 2,
            "payment_status": PaymentStatus.CURRENT,
            "stripe_subscription_id": "sub_test123",
            "next_payment_due": datetime.now() + timedelta(days=30)
        }
        
        # Act
        membership = CircleMembership(**membership_data)
        
        # Assert
        assert membership.circle_id == 1
        assert membership.user_id == 2
        assert membership.payment_status == PaymentStatus.CURRENT.value
        assert membership.stripe_subscription_id == "sub_test123"
        assert membership.is_active is True
        assert membership.joined_at is not None

    def test_circle_membership_required_fields(self):
        """Test that circle_id and user_id are required."""
        # Test missing circle_id
        with pytest.raises(ValidationError) as exc_info:
            CircleMembership(user_id=1)
        assert "circle_id is required" in str(exc_info.value)
        
        # Test missing user_id
        with pytest.raises(ValidationError) as exc_info:
            CircleMembership(circle_id=1)
        assert "user_id is required" in str(exc_info.value)

    def test_circle_membership_default_values(self):
        """Test default values are set correctly."""
        # Act - Create membership with minimal required data
        membership = CircleMembership(circle_id=1, user_id=2)
        
        # Assert - Check defaults
        assert membership.payment_status == PaymentStatus.PENDING.value
        assert membership.is_active is True
        assert membership.stripe_subscription_id is None
        assert membership.next_payment_due is None
        assert membership.joined_at is not None

    def test_payment_status_enum_values(self):
        """Test payment status enum has correct values."""
        # Assert all expected enum values exist
        assert PaymentStatus.PENDING.value == "pending"
        assert PaymentStatus.CURRENT.value == "current"
        assert PaymentStatus.OVERDUE.value == "overdue"
        assert PaymentStatus.PAUSED.value == "paused"

    def test_payment_status_transitions(self):
        """Test valid payment status transitions."""
        # Arrange
        membership = CircleMembership(circle_id=1, user_id=2)
        
        # Test PENDING -> CURRENT
        membership.payment_status = PaymentStatus.CURRENT.value
        assert membership.payment_status == PaymentStatus.CURRENT.value
        
        # Test CURRENT -> OVERDUE
        membership.payment_status = PaymentStatus.OVERDUE.value
        assert membership.payment_status == PaymentStatus.OVERDUE.value
        
        # Test OVERDUE -> CURRENT
        membership.payment_status = PaymentStatus.CURRENT.value
        assert membership.payment_status == PaymentStatus.CURRENT.value
        
        # Test CURRENT -> PAUSED
        membership.payment_status = PaymentStatus.PAUSED.value
        assert membership.payment_status == PaymentStatus.PAUSED.value

    def test_stripe_subscription_id_validation(self):
        """Test Stripe subscription ID validation."""
        # Test valid Stripe subscription ID
        membership = CircleMembership(
            circle_id=1,
            user_id=2,
            stripe_subscription_id="sub_1234567890abcdef"
        )
        assert membership.stripe_subscription_id == "sub_1234567890abcdef"
        
        # Test too long subscription ID
        long_id = "sub_" + "a" * 300  # Over 255 character limit
        with pytest.raises(ValidationError) as exc_info:
            CircleMembership(
                circle_id=1,
                user_id=2,
                stripe_subscription_id=long_id
            )
        assert "stripe_subscription_id cannot exceed 255 characters" in str(exc_info.value)

    def test_next_payment_due_validation(self):
        """Test next payment due date validation."""
        # Test future date is valid
        future_date = datetime.now() + timedelta(days=30)
        membership = CircleMembership(
            circle_id=1,
            user_id=2,
            next_payment_due=future_date
        )
        assert membership.next_payment_due == future_date
        
        # Test past date validation (business rule)
        past_date = datetime.now() - timedelta(days=30)
        with pytest.raises(ValidationError) as exc_info:
            CircleMembership(
                circle_id=1,
                user_id=2,
                next_payment_due=past_date
            )
        assert "next_payment_due cannot be in the past" in str(exc_info.value)

    def test_circle_membership_string_representation(self):
        """Test circle membership string representation."""
        # Arrange
        membership = CircleMembership(
            circle_id=1,
            user_id=2,
            payment_status=PaymentStatus.CURRENT.value
        )
        
        # Act
        repr_str = repr(membership)
        
        # Assert
        assert "CircleMembership" in repr_str
        assert "circle_id=1" in repr_str
        assert "user_id=2" in repr_str
        assert "current" in repr_str

    def test_circle_membership_composite_key(self):
        """Test that circle_id and user_id form a composite primary key."""
        # This will be tested with database constraints
        # For now, test the model structure
        membership = CircleMembership(circle_id=1, user_id=2)
        assert hasattr(membership, 'circle_id')
        assert hasattr(membership, 'user_id')

    def test_timestamps_are_set(self):
        """Test that joined_at timestamp is properly set."""
        # Arrange
        membership = CircleMembership(circle_id=1, user_id=2)
        
        # Assert
        assert hasattr(membership, 'joined_at')
        assert membership.joined_at is not None


class TestCircleMembershipBusinessLogic:
    """Test CircleMembership business logic and rules."""

    def test_payment_status_business_rules(self):
        """Test business rules around payment status."""
        membership = CircleMembership(circle_id=1, user_id=2)
        
        # New membership should be PENDING
        assert membership.payment_status == PaymentStatus.PENDING.value
        
        # Should be able to activate membership
        membership.activate_payment()
        assert membership.payment_status == PaymentStatus.CURRENT.value
        
        # Should be able to mark as overdue
        membership.mark_overdue()
        assert membership.payment_status == PaymentStatus.OVERDUE.value
        
        # Should be able to pause membership
        membership.pause_payment()
        assert membership.payment_status == PaymentStatus.PAUSED.value

    def test_membership_activation(self):
        """Test membership activation logic."""
        membership = CircleMembership(circle_id=1, user_id=2)
        
        # Should be able to activate membership
        membership.activate_payment()
        assert membership.payment_status == PaymentStatus.CURRENT.value
        assert membership.is_active is True

    def test_membership_deactivation(self):
        """Test membership deactivation logic."""
        membership = CircleMembership(
            circle_id=1,
            user_id=2,
            payment_status=PaymentStatus.CURRENT.value
        )
        
        # Should be able to deactivate membership
        membership.deactivate()
        assert membership.is_active is False

    def test_payment_due_calculation(self):
        """Test payment due date calculation."""
        membership = CircleMembership(circle_id=1, user_id=2)
        
        # Should be able to set next payment due date
        future_date = datetime.now() + timedelta(days=30)
        membership.set_next_payment_due(future_date)
        assert membership.next_payment_due == future_date

    def test_overdue_payment_logic(self):
        """Test overdue payment business logic."""
        membership = CircleMembership(
            circle_id=1,
            user_id=2,
            payment_status=PaymentStatus.CURRENT.value,
            next_payment_due=datetime.now() - timedelta(days=1),
            _allow_past_payment_dates=True
        )
        
        # Should be able to check if payment is overdue
        assert membership.is_payment_overdue() is True
        
        # Should be able to mark as overdue
        membership.mark_overdue()
        assert membership.payment_status == PaymentStatus.OVERDUE.value

    def test_payment_status_display(self):
        """Test payment status display methods."""
        membership = CircleMembership(
            circle_id=1,
            user_id=2,
            payment_status=PaymentStatus.CURRENT.value
        )
        
        # Should return proper status display
        assert membership.get_payment_status_display() == "Current"
        
        membership.payment_status = PaymentStatus.OVERDUE.value
        assert membership.get_payment_status_display() == "Overdue"

    def test_stripe_integration_methods(self):
        """Test Stripe integration helper methods."""
        membership = CircleMembership(
            circle_id=1,
            user_id=2,
            stripe_subscription_id="sub_test123"
        )
        
        # Should be able to check if has Stripe subscription
        assert membership.has_stripe_subscription() is True
        
        # Should be able to update Stripe subscription
        membership.update_stripe_subscription("sub_new456")
        assert membership.stripe_subscription_id == "sub_new456"

    def test_membership_uniqueness_validation(self):
        """Test that membership is unique per circle-user combination."""
        # This will be enforced by database constraints
        # Test the validation logic exists
        membership = CircleMembership(circle_id=1, user_id=2)
        assert membership.validate_uniqueness() is True

    def test_capacity_enforcement_integration(self):
        """Test integration with circle capacity enforcement."""
        # This will integrate with Circle model's capacity checking
        membership = CircleMembership(circle_id=1, user_id=2)
        
        # Should be able to validate against circle capacity
        # This will be implemented when Circle integration is added
        assert hasattr(membership, 'validate_circle_capacity')


class TestCircleMembershipRelationships:
    """Test CircleMembership model relationships."""

    def test_circle_relationship(self):
        """Test relationship to Circle model."""
        membership = CircleMembership(circle_id=1, user_id=2)
        
        # Should have circle relationship defined
        assert hasattr(membership, 'circle')

    def test_user_relationship(self):
        """Test relationship to User model."""
        membership = CircleMembership(circle_id=1, user_id=2)
        
        # Should have user relationship defined
        assert hasattr(membership, 'user')

    def test_foreign_key_constraints(self):
        """Test foreign key constraints are properly defined."""
        membership = CircleMembership(circle_id=1, user_id=2)
        
        # Check that foreign key fields exist
        assert membership.circle_id == 1
        assert membership.user_id == 2


class TestCircleMembershipValidation:
    """Test CircleMembership validation logic."""

    def test_payment_status_validation(self):
        """Test payment status field validation."""
        # Valid payment status should work
        for status in PaymentStatus:
            membership = CircleMembership(
                circle_id=1,
                user_id=2,
                payment_status=status.value
            )
            assert membership.payment_status == status.value

    def test_invalid_payment_status(self):
        """Test invalid payment status validation."""
        with pytest.raises(ValidationError) as exc_info:
            CircleMembership(
                circle_id=1,
                user_id=2,
                payment_status="invalid_status"
            )
        assert "invalid payment status" in str(exc_info.value).lower()

    def test_future_date_validation(self):
        """Test future date validation for payment due dates."""
        # Future date should be valid
        future_date = datetime.now() + timedelta(days=30)
        membership = CircleMembership(
            circle_id=1,
            user_id=2,
            next_payment_due=future_date
        )
        assert membership.next_payment_due == future_date

    def test_membership_status_consistency(self):
        """Test membership status consistency rules."""
        membership = CircleMembership(circle_id=1, user_id=2)
        
        # Inactive membership with current payment should be invalid
        membership.is_active = False
        membership.payment_status = PaymentStatus.CURRENT.value
        
        with pytest.raises(ValidationError) as exc_info:
            membership.validate_status_consistency()
        assert "inactive membership cannot have current payment status" in str(exc_info.value).lower()


# Integration tests will be added when database fixtures are available
class TestCircleMembershipIntegration:
    """Integration tests for CircleMembership model with database."""

    def test_membership_creation_with_circle_capacity_check(self):
        """Test membership creation respects circle capacity."""
        # This will be implemented when database integration is available
        pass

    def test_membership_uniqueness_database_constraint(self):
        """Test database-level uniqueness constraint."""
        # This will be implemented when database integration is available
        pass

    def test_foreign_key_constraints_database(self):
        """Test database foreign key constraints."""
        # This will be implemented when database integration is available
        pass 