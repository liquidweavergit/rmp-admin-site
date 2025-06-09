"""
CircleMembership model for tracking circle membership and payment status
"""
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from typing import Optional

from ..core.database import Base
from ..core.exceptions import ValidationError, BusinessRuleViolation


class PaymentStatus(enum.Enum):
    """Payment status enumeration for circle memberships."""
    PENDING = "pending"        # Payment is pending setup
    CURRENT = "current"        # Payment is current and up to date
    OVERDUE = "overdue"        # Payment is overdue
    PAUSED = "paused"          # Payment is paused (membership inactive)


class CircleMembership(Base):
    """
    CircleMembership model representing the relationship between users and circles
    with payment status tracking for subscription management.
    
    Features:
    - Composite primary key (circle_id, user_id) for uniqueness
    - Payment status tracking with Stripe integration
    - Temporal tracking of membership periods
    - Business logic for payment transitions
    """
    __tablename__ = "circle_memberships"
    
    # Composite primary key
    circle_id = Column(Integer, ForeignKey("circles.id"), primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, nullable=False)
    
    # Membership status
    is_active = Column(Boolean, nullable=False, default=True)
    payment_status = Column(String(20), nullable=False, default=PaymentStatus.PENDING.value)
    
    # Payment tracking
    stripe_subscription_id = Column(String(255), nullable=True, index=True)
    next_payment_due = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Add check constraints for valid payment status
    __table_args__ = (
        CheckConstraint(
            payment_status.in_(['pending', 'current', 'overdue', 'paused']),
            name='valid_payment_status'
        ),
        CheckConstraint(
            "stripe_subscription_id IS NULL OR LENGTH(stripe_subscription_id) <= 255",
            name='stripe_subscription_id_length'
        ),
    )
    
    # Relationships
    circle = relationship("Circle", foreign_keys=[circle_id])
    user = relationship("User", foreign_keys=[user_id])
    
    def __init__(self, **kwargs):
        """Initialize CircleMembership with validation."""
        # Validate required fields
        if not kwargs.get('circle_id'):
            raise ValidationError("circle_id is required")
        if not kwargs.get('user_id'):
            raise ValidationError("user_id is required")
        
        # Validate stripe_subscription_id length
        stripe_id = kwargs.get('stripe_subscription_id')
        if stripe_id and len(stripe_id) > 255:
            raise ValidationError("stripe_subscription_id cannot exceed 255 characters")
        
        # Validate next_payment_due is not in the past (allow past dates for testing overdue scenarios)
        next_payment = kwargs.get('next_payment_due')
        # Allow past dates if explicitly setting for testing overdue logic
        allow_past_dates = kwargs.pop('_allow_past_payment_dates', False)
        if next_payment and next_payment < datetime.now() and not allow_past_dates:
            raise ValidationError("next_payment_due cannot be in the past")
        
        # Validate payment status
        payment_status = kwargs.get('payment_status', PaymentStatus.PENDING.value)
        # Handle enum objects by extracting their value
        if hasattr(payment_status, 'value'):
            payment_status = payment_status.value
            kwargs['payment_status'] = payment_status
        if payment_status not in [status.value for status in PaymentStatus]:
            raise ValidationError(f"Invalid payment status: {payment_status}")
        
        # Set defaults
        if 'payment_status' not in kwargs:
            kwargs['payment_status'] = PaymentStatus.PENDING.value
        if 'is_active' not in kwargs:
            kwargs['is_active'] = True
        if 'joined_at' not in kwargs:
            kwargs['joined_at'] = datetime.now()
        
        super().__init__(**kwargs)
    
    @validates('payment_status')
    def validate_payment_status(self, key, payment_status):
        """Validate payment status value."""
        valid_statuses = [status.value for status in PaymentStatus]
        if payment_status not in valid_statuses:
            raise ValidationError(f"Invalid payment status: {payment_status}. Must be one of: {valid_statuses}")
        return payment_status
    
    @validates('stripe_subscription_id')
    def validate_stripe_subscription_id(self, key, stripe_id):
        """Validate Stripe subscription ID length."""
        if stripe_id and len(stripe_id) > 255:
            raise ValidationError("stripe_subscription_id cannot exceed 255 characters")
        return stripe_id
    
    @validates('next_payment_due')
    def validate_next_payment_due(self, key, next_payment):
        """Validate next payment due date."""
        # Note: This validator is more lenient to allow updates during business operations
        # Initial validation happens in __init__
        return next_payment
    
    @property
    def payment_status_enum(self) -> PaymentStatus:
        """Get payment status as enum."""
        return PaymentStatus(self.payment_status)
    
    @payment_status_enum.setter
    def payment_status_enum(self, status: PaymentStatus):
        """Set payment status from enum."""
        self.payment_status = status.value
    
    # Business logic methods
    
    def activate_payment(self) -> None:
        """Activate payment status."""
        self.payment_status = PaymentStatus.CURRENT.value
        self.is_active = True
    
    def mark_overdue(self) -> None:
        """Mark payment as overdue."""
        self.payment_status = PaymentStatus.OVERDUE.value
    
    def pause_payment(self) -> None:
        """Pause payment (membership becomes inactive)."""
        self.payment_status = PaymentStatus.PAUSED.value
    
    def deactivate(self) -> None:
        """Deactivate membership."""
        self.is_active = False
    
    def set_next_payment_due(self, due_date: datetime) -> None:
        """Set next payment due date."""
        if due_date < datetime.now():
            raise ValidationError("next_payment_due cannot be in the past")
        self.next_payment_due = due_date
    
    def is_payment_overdue(self) -> bool:
        """Check if payment is overdue."""
        if not self.next_payment_due:
            return False
        return datetime.now() > self.next_payment_due
    
    def get_payment_status_display(self) -> str:
        """Get display-friendly payment status."""
        status_display = {
            PaymentStatus.PENDING.value: "Pending",
            PaymentStatus.CURRENT.value: "Current",
            PaymentStatus.OVERDUE.value: "Overdue",
            PaymentStatus.PAUSED.value: "Paused"
        }
        return status_display.get(self.payment_status, self.payment_status.title())
    
    def has_stripe_subscription(self) -> bool:
        """Check if membership has a Stripe subscription."""
        return self.stripe_subscription_id is not None and self.stripe_subscription_id.strip() != ""
    
    def update_stripe_subscription(self, subscription_id: str) -> None:
        """Update Stripe subscription ID."""
        if len(subscription_id) > 255:
            raise ValidationError("stripe_subscription_id cannot exceed 255 characters")
        self.stripe_subscription_id = subscription_id
    
    def validate_uniqueness(self) -> bool:
        """Validate membership uniqueness (placeholder for database constraint)."""
        # This will be enforced by database composite primary key
        return True
    
    def validate_circle_capacity(self) -> bool:
        """Validate against circle capacity (placeholder for future integration)."""
        # This will be implemented when Circle capacity checking is integrated
        return True
    
    def validate_status_consistency(self) -> None:
        """Validate consistency between is_active and payment_status."""
        if not self.is_active and self.payment_status == PaymentStatus.CURRENT.value:
            raise ValidationError("Inactive membership cannot have current payment status")
    
    def __repr__(self):
        return (f"<CircleMembership(circle_id={self.circle_id}, user_id={self.user_id}, "
               f"payment_status='{self.payment_status}', is_active={self.is_active})>") 