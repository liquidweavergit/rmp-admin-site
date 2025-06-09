"""
TransferRequest model for managing member transfer requests between circles.
Implements the request/approval workflow for circle member transfers.
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class TransferRequestStatus(str, Enum):
    """Enum for transfer request status."""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    CANCELLED = "cancelled"


class TransferRequest(Base):
    """
    Transfer request model representing a member's request to transfer between circles.
    
    Attributes:
        id: Primary key
        requester_id: ID of the user requesting the transfer
        source_circle_id: ID of the current circle (auto-populated)
        target_circle_id: ID of the desired target circle
        reason: Optional reason for the transfer request
        status: Current status of the request (pending/approved/denied/cancelled)
        created_at: When the request was created
        reviewed_by_id: ID of the facilitator who reviewed the request
        reviewed_at: When the request was reviewed
        review_notes: Notes from the facilitator's review
    """
    __tablename__ = "transfer_requests"

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    source_circle_id = Column(Integer, ForeignKey("circles.id"), nullable=False, index=True)
    target_circle_id = Column(Integer, ForeignKey("circles.id"), nullable=False, index=True)
    reason = Column(String(1000), nullable=True)
    status = Column(SQLEnum(TransferRequestStatus), nullable=False, default=TransferRequestStatus.PENDING, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    reviewed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_notes = Column(String(1000), nullable=True)

    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], back_populates="transfer_requests")
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])
    source_circle = relationship("Circle", foreign_keys=[source_circle_id])
    target_circle = relationship("Circle", foreign_keys=[target_circle_id])

    def approve(self, reviewer_id: int, review_notes: Optional[str] = None) -> None:
        """
        Approve the transfer request.
        
        Args:
            reviewer_id: ID of the facilitator approving the request
            review_notes: Optional notes from the reviewer
            
        Raises:
            ValueError: If the request is not in pending status
        """
        if self.status != TransferRequestStatus.PENDING:
            raise ValueError("Only pending requests can be approved")
        
        self.status = TransferRequestStatus.APPROVED
        self.reviewed_by_id = reviewer_id
        self.reviewed_at = datetime.utcnow()
        self.review_notes = review_notes

    def deny(self, reviewer_id: int, review_notes: Optional[str] = None) -> None:
        """
        Deny the transfer request.
        
        Args:
            reviewer_id: ID of the facilitator denying the request
            review_notes: Optional notes from the reviewer
            
        Raises:
            ValueError: If the request is not in pending status
        """
        if self.status != TransferRequestStatus.PENDING:
            raise ValueError("Only pending requests can be denied")
        
        self.status = TransferRequestStatus.DENIED
        self.reviewed_by_id = reviewer_id
        self.reviewed_at = datetime.utcnow()
        self.review_notes = review_notes

    def cancel(self) -> None:
        """
        Cancel the transfer request.
        
        Raises:
            ValueError: If the request is not in pending status
        """
        if self.status != TransferRequestStatus.PENDING:
            raise ValueError("Only pending requests can be cancelled")
        
        self.status = TransferRequestStatus.CANCELLED

    @property
    def is_pending(self) -> bool:
        """Check if the request is in pending status."""
        return self.status == TransferRequestStatus.PENDING

    def __str__(self) -> str:
        """String representation of the transfer request."""
        return f"TransferRequest(id={self.id}, requester_id={self.requester_id}, status={self.status.value})"

    def __repr__(self) -> str:
        """Detailed representation of the transfer request."""
        return (
            f"<TransferRequest(id={self.id}, requester_id={self.requester_id}, "
            f"source_circle_id={self.source_circle_id}, target_circle_id={self.target_circle_id}, "
            f"status={self.status.value}, created_at={self.created_at})>"
        ) 