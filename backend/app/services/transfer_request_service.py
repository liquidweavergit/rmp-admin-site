"""
TransferRequestService - Business logic for managing transfer requests.
Handles creation, approval, denial, and cancellation of member transfer requests.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.transfer_request import TransferRequest, TransferRequestStatus
from app.models.circle import Circle
from app.models.circle_membership import CircleMembership
from app.models.user import User
from app.services.circle_service import CircleService


class TransferRequestService:
    """Service for managing transfer requests."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_transfer_request(
        self,
        user_id: int,
        target_circle_id: int,
        reason: Optional[str] = None
    ) -> TransferRequest:
        """
        Create a new transfer request.
        
        Args:
            user_id: ID of the user requesting the transfer
            target_circle_id: ID of the target circle
            reason: Optional reason for the transfer
            
        Returns:
            TransferRequest: The created transfer request
            
        Raises:
            HTTPException: If validation fails or user is not eligible
        """
        try:
            # Find user's active membership to determine source circle
            membership_query = select(CircleMembership).where(
                and_(
                    CircleMembership.user_id == user_id,
                    CircleMembership.is_active == True
                )
            )
            result = await self.db.execute(membership_query)
            active_membership = result.scalar_one_or_none()
            
            if not active_membership:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="User is not an active member of any circle"
                )
            
            source_circle_id = active_membership.circle_id
            
            # Prevent transfer to same circle
            if source_circle_id == target_circle_id:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Cannot request transfer to your current circle"
                )
            
            # Check for existing pending request to the same target circle
            existing_query = select(TransferRequest).where(
                and_(
                    TransferRequest.requester_id == user_id,
                    TransferRequest.target_circle_id == target_circle_id,
                    TransferRequest.status == TransferRequestStatus.PENDING
                )
            )
            result = await self.db.execute(existing_query)
            existing_request = result.scalar_one_or_none()
            
            if existing_request:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="User already has a pending transfer request for this circle"
                )
            
            # Verify target circle exists and check capacity
            target_circle_query = select(Circle).where(Circle.id == target_circle_id)
            result = await self.db.execute(target_circle_query)
            target_circle = result.scalar_one_or_none()
            
            if not target_circle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Target circle not found"
                )
            
            if not target_circle.can_accept_members():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Target circle is at maximum capacity"
                )
            
            # Create the transfer request
            transfer_request = TransferRequest(
                requester_id=user_id,
                source_circle_id=source_circle_id,
                target_circle_id=target_circle_id,
                reason=reason
            )
            
            self.db.add(transfer_request)
            await self.db.commit()
            await self.db.refresh(transfer_request)
            
            return transfer_request
            
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create transfer request: {str(e)}"
            )
    
    async def get_user_transfer_requests(self, user_id: int) -> List[TransferRequest]:
        """
        Get all transfer requests made by a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List[TransferRequest]: List of user's transfer requests
        """
        query = select(TransferRequest).where(
            TransferRequest.requester_id == user_id
        ).order_by(TransferRequest.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_pending_requests_for_facilitator(self, facilitator_id: int) -> List[TransferRequest]:
        """
        Get all pending transfer requests for circles facilitated by the user.
        
        Args:
            facilitator_id: ID of the facilitator
            
        Returns:
            List[TransferRequest]: List of pending requests for facilitator's circles
        """
        # Get circles facilitated by the user
        circles_query = select(Circle).where(Circle.facilitator_id == facilitator_id)
        result = await self.db.execute(circles_query)
        facilitator_circles = result.scalars().all()
        
        if not facilitator_circles:
            return []
        
        circle_ids = [circle.id for circle in facilitator_circles]
        
        # Get pending requests for those circles
        requests_query = select(TransferRequest).where(
            and_(
                TransferRequest.target_circle_id.in_(circle_ids),
                TransferRequest.status == TransferRequestStatus.PENDING
            )
        ).options(
            selectinload(TransferRequest.requester),
            selectinload(TransferRequest.source_circle),
            selectinload(TransferRequest.target_circle)
        ).order_by(TransferRequest.created_at.asc())
        
        result = await self.db.execute(requests_query)
        return result.scalars().all()
    
    async def approve_transfer_request(
        self,
        request_id: int,
        reviewer_id: int,
        review_notes: Optional[str] = None
    ) -> TransferRequest:
        """
        Approve a transfer request.
        
        Args:
            request_id: ID of the transfer request
            reviewer_id: ID of the facilitator approving the request
            review_notes: Optional notes for the approval
            
        Returns:
            TransferRequest: The approved transfer request
            
        Raises:
            HTTPException: If validation fails or permission denied
        """
        try:
            # Get the transfer request
            request_query = select(TransferRequest).where(TransferRequest.id == request_id)
            result = await self.db.execute(request_query)
            transfer_request = result.scalar_one_or_none()
            
            if not transfer_request:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Transfer request not found"
                )
            
            # Check if request is still pending
            if transfer_request.status != TransferRequestStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Only pending requests can be approved"
                )
            
            # Verify facilitator permission for target circle
            target_circle_query = select(Circle).where(Circle.id == transfer_request.target_circle_id)
            result = await self.db.execute(target_circle_query)
            target_circle = result.scalar_one_or_none()
            
            if not target_circle or target_circle.facilitator_id != reviewer_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only facilitators can approve transfer requests for their circles"
                )
            
            # Approve the request
            transfer_request.approve(reviewer_id, review_notes)
            
            await self.db.commit()
            await self.db.refresh(transfer_request)
            
            return transfer_request
            
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to approve transfer request: {str(e)}"
            )
    
    async def deny_transfer_request(
        self,
        request_id: int,
        reviewer_id: int,
        review_notes: Optional[str] = None
    ) -> TransferRequest:
        """
        Deny a transfer request.
        
        Args:
            request_id: ID of the transfer request
            reviewer_id: ID of the facilitator denying the request
            review_notes: Optional notes for the denial
            
        Returns:
            TransferRequest: The denied transfer request
            
        Raises:
            HTTPException: If validation fails or permission denied
        """
        try:
            # Get the transfer request
            request_query = select(TransferRequest).where(TransferRequest.id == request_id)
            result = await self.db.execute(request_query)
            transfer_request = result.scalar_one_or_none()
            
            if not transfer_request:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Transfer request not found"
                )
            
            # Check if request is still pending
            if transfer_request.status != TransferRequestStatus.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Only pending requests can be denied"
                )
            
            # Verify facilitator permission for target circle
            target_circle_query = select(Circle).where(Circle.id == transfer_request.target_circle_id)
            result = await self.db.execute(target_circle_query)
            target_circle = result.scalar_one_or_none()
            
            if not target_circle or target_circle.facilitator_id != reviewer_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only facilitators can deny transfer requests for their circles"
                )
            
            # Deny the request
            transfer_request.deny(reviewer_id, review_notes)
            
            await self.db.commit()
            await self.db.refresh(transfer_request)
            
            return transfer_request
            
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to deny transfer request: {str(e)}"
            )
    
    async def cancel_transfer_request(self, request_id: int, user_id: int) -> bool:
        """
        Cancel a transfer request (requester only).
        
        Args:
            request_id: ID of the transfer request
            user_id: ID of the user requesting cancellation
            
        Returns:
            bool: True if cancelled successfully
            
        Raises:
            HTTPException: If validation fails or permission denied
        """
        try:
            # Get the transfer request
            request_query = select(TransferRequest).where(TransferRequest.id == request_id)
            result = await self.db.execute(request_query)
            transfer_request = result.scalar_one_or_none()
            
            if not transfer_request:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Transfer request not found"
                )
            
            # Verify ownership
            if transfer_request.requester_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only cancel your own transfer requests"
                )
            
            # Cancel the request
            transfer_request.cancel()
            
            await self.db.commit()
            
            return True
            
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to cancel transfer request: {str(e)}"
            )
    
    async def approve_and_execute_transfer(
        self,
        request_id: int,
        reviewer_id: int,
        review_notes: Optional[str] = None
    ) -> TransferRequest:
        """
        Approve a transfer request and immediately execute the actual transfer.
        
        Args:
            request_id: ID of the transfer request
            reviewer_id: ID of the facilitator
            review_notes: Optional notes for the approval
            
        Returns:
            TransferRequest: The approved transfer request
            
        Raises:
            HTTPException: If validation fails or transfer execution fails
        """
        try:
            # First approve the request
            transfer_request = await self.approve_transfer_request(
                request_id, reviewer_id, review_notes
            )
            
            # Now execute the actual transfer using CircleService
            circle_service = CircleService(self.db)
            await circle_service.transfer_member_between_circles(
                source_circle_id=transfer_request.source_circle_id,
                target_circle_id=transfer_request.target_circle_id,
                user_id=transfer_request.requester_id,
                facilitator_id=reviewer_id,
                reason=f"Transfer request #{transfer_request.id}: {transfer_request.reason or 'No reason provided'}"
            )
            
            return transfer_request
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to approve and execute transfer: {str(e)}"
            )
    
    async def get_transfer_request_by_id(self, request_id: int, user_id: int) -> TransferRequest:
        """
        Get a transfer request by ID (with access control).
        
        Args:
            request_id: ID of the transfer request
            user_id: ID of the requesting user
            
        Returns:
            TransferRequest: The transfer request
            
        Raises:
            HTTPException: If not found or access denied
        """
        request_query = select(TransferRequest).where(TransferRequest.id == request_id)
        result = await self.db.execute(request_query)
        transfer_request = result.scalar_one_or_none()
        
        if not transfer_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer request not found"
            )
        
        # Check if user can access this request (requester or facilitator of target circle)
        if transfer_request.requester_id == user_id:
            return transfer_request
        
        # Check if user is facilitator of target circle
        target_circle_query = select(Circle).where(
            and_(
                Circle.id == transfer_request.target_circle_id,
                Circle.facilitator_id == user_id
            )
        )
        result = await self.db.execute(target_circle_query)
        facilitator_circle = result.scalar_one_or_none()
        
        if facilitator_circle:
            return transfer_request
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this transfer request"
        )
    
    async def get_transfer_request_statistics(self) -> Dict[str, int]:
        """
        Get statistics about transfer requests.
        
        Returns:
            Dict[str, int]: Statistics by status and total
        """
        stats_query = select(
            TransferRequest.status,
            func.count(TransferRequest.id)
        ).group_by(TransferRequest.status)
        
        result = await self.db.execute(stats_query)
        stats_data = result.all()
        
        stats = {
            "pending": 0,
            "approved": 0,
            "denied": 0,
            "cancelled": 0
        }
        
        for status_value, count in stats_data:
            stats[status_value] = count
        
        stats["total"] = sum(stats.values())
        
        return stats 