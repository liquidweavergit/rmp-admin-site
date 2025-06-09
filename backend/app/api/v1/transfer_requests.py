"""
Transfer Request API endpoints for managing member transfer requests.
Implements the request/approval workflow for circle member transfers.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_main_db
from app.core.deps import get_current_user
from app.models.user import User
from app.services.transfer_request_service import TransferRequestService
from app.schemas.transfer_request import (
    TransferRequestCreate,
    TransferRequestResponse,
    TransferRequestListResponse,
    TransferRequestReview,
    TransferRequestStats,
    TransferRequestDetailResponse
)

router = APIRouter()


def get_transfer_request_service(db: AsyncSession = Depends(get_main_db)) -> TransferRequestService:
    """Dependency to get TransferRequestService instance."""
    return TransferRequestService(db)


@router.post(
    "",
    response_model=TransferRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a transfer request",
    description="Create a new transfer request for the authenticated user"
)
async def create_transfer_request(
    request_data: TransferRequestCreate,
    current_user: User = Depends(get_current_user),
    service: TransferRequestService = Depends(get_transfer_request_service)
) -> TransferRequestResponse:
    """
    Create a new transfer request.
    
    - **target_circle_id**: ID of the circle to transfer to
    - **reason**: Optional reason for the transfer request
    """
    transfer_request = await service.create_transfer_request(
        user_id=current_user.id,
        target_circle_id=request_data.target_circle_id,
        reason=request_data.reason
    )
    return TransferRequestResponse.from_orm(transfer_request)


@router.get(
    "/my",
    response_model=TransferRequestListResponse,
    summary="Get my transfer requests",
    description="Get all transfer requests made by the authenticated user"
)
async def get_my_transfer_requests(
    current_user: User = Depends(get_current_user),
    service: TransferRequestService = Depends(get_transfer_request_service)
) -> TransferRequestListResponse:
    """Get all transfer requests made by the current user."""
    requests = await service.get_user_transfer_requests(user_id=current_user.id)
    return TransferRequestListResponse(
        requests=[TransferRequestResponse.from_orm(req) for req in requests],
        total=len(requests)
    )


@router.get(
    "/pending",
    response_model=TransferRequestListResponse,
    summary="Get pending requests for facilitator",
    description="Get all pending transfer requests for circles facilitated by the authenticated user"
)
async def get_pending_requests_for_facilitator(
    circle_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    service: TransferRequestService = Depends(get_transfer_request_service)
) -> TransferRequestListResponse:
    """Get all pending transfer requests for circles facilitated by the current user."""
    requests = await service.get_pending_requests_for_facilitator(facilitator_id=current_user.id)
    
    # Filter by circle_id if provided
    if circle_id:
        requests = [req for req in requests if req.target_circle_id == circle_id]
    
    return TransferRequestListResponse(
        requests=[TransferRequestResponse.from_orm(req) for req in requests],
        total=len(requests)
    )


@router.get(
    "/{request_id}",
    response_model=TransferRequestDetailResponse,
    summary="Get transfer request by ID",
    description="Get a specific transfer request by ID (with access control)"
)
async def get_transfer_request_by_id(
    request_id: int,
    current_user: User = Depends(get_current_user),
    service: TransferRequestService = Depends(get_transfer_request_service)
) -> TransferRequestDetailResponse:
    """Get a transfer request by ID with access control."""
    transfer_request = await service.get_transfer_request_by_id(
        request_id=request_id,
        user_id=current_user.id
    )
    
    # Convert to detailed response with related data
    response_data = TransferRequestResponse.from_orm(transfer_request).dict()
    
    # Add related data if available
    if hasattr(transfer_request, 'requester') and transfer_request.requester:
        response_data['requester_name'] = f"{transfer_request.requester.first_name} {transfer_request.requester.last_name}"
    
    if hasattr(transfer_request, 'source_circle') and transfer_request.source_circle:
        response_data['source_circle_name'] = transfer_request.source_circle.name
    
    if hasattr(transfer_request, 'target_circle') and transfer_request.target_circle:
        response_data['target_circle_name'] = transfer_request.target_circle.name
    
    if hasattr(transfer_request, 'reviewed_by') and transfer_request.reviewed_by:
        response_data['reviewer_name'] = f"{transfer_request.reviewed_by.first_name} {transfer_request.reviewed_by.last_name}"
    
    return TransferRequestDetailResponse(**response_data)


@router.post(
    "/{request_id}/approve",
    response_model=TransferRequestResponse,
    summary="Approve transfer request",
    description="Approve a transfer request (facilitators only)"
)
async def approve_transfer_request(
    request_id: int,
    review_data: TransferRequestReview,
    current_user: User = Depends(get_current_user),
    service: TransferRequestService = Depends(get_transfer_request_service)
) -> TransferRequestResponse:
    """
    Approve a transfer request.
    
    - **review_notes**: Optional notes for the approval
    - **execute_transfer**: Whether to execute the transfer immediately
    """
    if review_data.execute_transfer:
        # Approve and execute transfer in one operation
        transfer_request = await service.approve_and_execute_transfer(
            request_id=request_id,
            reviewer_id=current_user.id,
            review_notes=review_data.review_notes
        )
    else:
        # Just approve the request
        transfer_request = await service.approve_transfer_request(
            request_id=request_id,
            reviewer_id=current_user.id,
            review_notes=review_data.review_notes
        )
    
    return TransferRequestResponse.from_orm(transfer_request)


@router.post(
    "/{request_id}/deny",
    response_model=TransferRequestResponse,
    summary="Deny transfer request",
    description="Deny a transfer request (facilitators only)"
)
async def deny_transfer_request(
    request_id: int,
    review_data: TransferRequestReview,
    current_user: User = Depends(get_current_user),
    service: TransferRequestService = Depends(get_transfer_request_service)
) -> TransferRequestResponse:
    """
    Deny a transfer request.
    
    - **review_notes**: Optional notes for the denial
    """
    transfer_request = await service.deny_transfer_request(
        request_id=request_id,
        reviewer_id=current_user.id,
        review_notes=review_data.review_notes
    )
    
    return TransferRequestResponse.from_orm(transfer_request)


@router.delete(
    "/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel transfer request",
    description="Cancel a transfer request (requester only)"
)
async def cancel_transfer_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    service: TransferRequestService = Depends(get_transfer_request_service)
) -> None:
    """Cancel a transfer request (requester only)."""
    await service.cancel_transfer_request(
        request_id=request_id,
        user_id=current_user.id
    )


@router.get(
    "/stats/overview",
    response_model=TransferRequestStats,
    summary="Get transfer request statistics",
    description="Get statistics about transfer requests (admin only)"
)
async def get_transfer_request_statistics(
    current_user: User = Depends(get_current_user),
    service: TransferRequestService = Depends(get_transfer_request_service)
) -> TransferRequestStats:
    """Get transfer request statistics."""
    # TODO: Add admin role check when role system is integrated
    stats = await service.get_transfer_request_statistics()
    return TransferRequestStats(**stats) 