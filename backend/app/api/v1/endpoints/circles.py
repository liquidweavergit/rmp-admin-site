"""
Circle API endpoints for creating and managing circles
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPAuthorizationCredentials

from ....schemas.circle import (
    CircleCreate,
    CircleUpdate,
    CircleResponse,
    CircleListResponse,
    CircleSearchParams,
    CircleMemberAdd,
    CircleMemberResponse
)
from ....services.circle_service import CircleService, get_circle_service
from ....core.deps import get_current_user
from ....models.user import User
from ....models.circle import CircleStatus

router = APIRouter()


@router.post(
    "",
    response_model=CircleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new circle",
    description="Create a new circle with the current user as facilitator"
)
async def create_circle(
    circle_data: CircleCreate,
    current_user: User = Depends(get_current_user),
    circle_service: CircleService = Depends(get_circle_service)
) -> CircleResponse:
    """
    Create a new circle with automatic facilitator assignment.
    
    - **name**: Circle name (required, 1-100 characters)
    - **description**: Circle description (optional, max 1000 characters)
    - **capacity_min**: Minimum circle capacity (2-10 members, default: 2)
    - **capacity_max**: Maximum circle capacity (2-10 members, default: 8)
    - **location_name**: Location name (optional, max 200 characters)
    - **location_address**: Location address (optional, max 500 characters)
    - **meeting_schedule**: Meeting schedule as JSON object (optional)
    
    The current authenticated user will automatically be assigned as the facilitator.
    
    Returns the created circle information with assigned facilitator.
    """
    try:
        circle = await circle_service.create_circle(circle_data, current_user.id)
        
        # Convert to response format
        return CircleResponse(
            id=circle.id,
            name=circle.name,
            description=circle.description,
            facilitator_id=circle.facilitator_id,
            capacity_min=circle.capacity_min,
            capacity_max=circle.capacity_max,
            location_name=circle.location_name,
            location_address=circle.location_address,
            meeting_schedule=circle.meeting_schedule,
            status=circle.status.value,
            is_active=circle.is_active,
            current_member_count=circle.current_member_count,
            created_at=circle.created_at,
            updated_at=circle.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create circle"
        )


@router.get(
    "",
    response_model=List[CircleResponse],
    summary="List circles",
    description="Get a list of circles the user has access to"
)
async def list_circles(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page (1-100)"),
    search: Optional[str] = Query(None, description="Search term for circle name or description"),
    status: Optional[CircleStatus] = Query(None, description="Filter by circle status"),
    facilitator_id: Optional[int] = Query(None, description="Filter by facilitator ID"),
    location: Optional[str] = Query(None, description="Filter by location"),
    current_user: User = Depends(get_current_user),
    circle_service: CircleService = Depends(get_circle_service)
) -> List[CircleResponse]:
    """
    List circles that the current user has access to.
    
    Access is determined by:
    - User is the facilitator of the circle
    - User is a member of the circle
    - User has role-based permissions (TODO: implement)
    
    Supports filtering by:
    - **search**: Text search in circle name or description
    - **status**: Filter by circle status (forming, active, paused, archived)
    - **facilitator_id**: Filter by facilitator user ID
    - **location**: Text search in location name or address
    
    Supports pagination with page and per_page parameters.
    """
    try:
        search_params = CircleSearchParams(
            page=page,
            per_page=per_page,
            search=search,
            status=status,
            facilitator_id=facilitator_id,
            location=location
        )
        
        circles, total = await circle_service.list_circles_for_user(
            current_user.id, 
            search_params
        )
        
        # Convert to response format
        circle_responses = []
        for circle in circles:
            circle_responses.append(CircleResponse(
                id=circle.id,
                name=circle.name,
                description=circle.description,
                facilitator_id=circle.facilitator_id,
                capacity_min=circle.capacity_min,
                capacity_max=circle.capacity_max,
                location_name=circle.location_name,
                location_address=circle.location_address,
                meeting_schedule=circle.meeting_schedule,
                status=circle.status.value,
                is_active=circle.is_active,
                current_member_count=circle.current_member_count,
                created_at=circle.created_at,
                updated_at=circle.updated_at
            ))
        
        return circle_responses
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list circles"
        )


@router.get(
    "/{circle_id}",
    response_model=CircleResponse,
    summary="Get circle details",
    description="Get detailed information about a specific circle"
)
async def get_circle(
    circle_id: int,
    current_user: User = Depends(get_current_user),
    circle_service: CircleService = Depends(get_circle_service)
) -> CircleResponse:
    """
    Get detailed information about a specific circle.
    
    - **circle_id**: ID of the circle to retrieve
    
    Access is verified based on user permissions:
    - Facilitator can always access their circles
    - Members can access circles they belong to
    - Role-based access control (TODO: implement)
    
    Returns detailed circle information including current member count.
    """
    try:
        circle = await circle_service.get_circle_by_id(circle_id, current_user.id)
        
        if not circle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Circle not found or access denied"
            )
        
        # Convert to response format
        return CircleResponse(
            id=circle.id,
            name=circle.name,
            description=circle.description,
            facilitator_id=circle.facilitator_id,
            capacity_min=circle.capacity_min,
            capacity_max=circle.capacity_max,
            location_name=circle.location_name,
            location_address=circle.location_address,
            meeting_schedule=circle.meeting_schedule,
            status=circle.status.value,
            is_active=circle.is_active,
            current_member_count=circle.current_member_count,
            created_at=circle.created_at,
            updated_at=circle.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve circle"
        )


@router.put(
    "/{circle_id}",
    response_model=CircleResponse,
    summary="Update circle",
    description="Update circle information (facilitator only)"
)
async def update_circle(
    circle_id: int,
    circle_data: CircleUpdate,
    current_user: User = Depends(get_current_user),
    circle_service: CircleService = Depends(get_circle_service)
) -> CircleResponse:
    """
    Update circle information.
    
    - **circle_id**: ID of the circle to update
    - **circle_data**: Updated circle information
    
    Only the circle facilitator can update circle information.
    
    Updatable fields:
    - name, description, capacity settings
    - location information, meeting schedule
    - status and active flag
    
    Returns the updated circle information.
    """
    try:
        circle = await circle_service.update_circle(
            circle_id, 
            circle_data, 
            current_user.id
        )
        
        if not circle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Circle not found or access denied"
            )
        
        # Convert to response format
        return CircleResponse(
            id=circle.id,
            name=circle.name,
            description=circle.description,
            facilitator_id=circle.facilitator_id,
            capacity_min=circle.capacity_min,
            capacity_max=circle.capacity_max,
            location_name=circle.location_name,
            location_address=circle.location_address,
            meeting_schedule=circle.meeting_schedule,
            status=circle.status.value,
            is_active=circle.is_active,
            current_member_count=circle.current_member_count,
            created_at=circle.created_at,
            updated_at=circle.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update circle"
        )


@router.post(
    "/{circle_id}/members",
    response_model=CircleMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add member to circle",
    description="Add a new member to the circle (facilitator only)"
)
async def add_circle_member(
    circle_id: int,
    member_data: CircleMemberAdd,
    current_user: User = Depends(get_current_user),
    circle_service: CircleService = Depends(get_circle_service)
) -> CircleMemberResponse:
    """
    Add a new member to the circle.
    
    - **circle_id**: ID of the circle
    - **user_id**: ID of the user to add to the circle
    - **payment_status**: Initial payment status (default: "pending")
    
    Only the circle facilitator can add members.
    
    Validates:
    - Circle capacity constraints
    - User is not already a member
    - Circle is accepting new members
    
    Returns the created membership information.
    """
    try:
        membership = await circle_service.add_member_to_circle(
            circle_id,
            member_data.user_id,
            current_user.id,
            member_data.payment_status
        )
        
        # Convert to response format
        return CircleMemberResponse(
            user_id=membership.user_id,
            circle_id=membership.circle_id,
            is_active=membership.is_active,
            payment_status=membership.payment_status.value,
            joined_at=membership.joined_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add member to circle"
        ) 