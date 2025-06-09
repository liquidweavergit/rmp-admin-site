"""
Circle service for managing circle business logic and database operations
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status, Depends

from ..models.circle import Circle, CircleStatus
from ..models.circle_membership import CircleMembership
from ..models.user import User
from ..schemas.circle import CircleCreate, CircleUpdate, CircleSearchParams
from ..core.database import get_main_db
from ..core.exceptions import ValidationError, CapacityExceeded


class CircleService:
    """Service class for circle business logic and database operations."""
    
    def __init__(self, db: AsyncSession):
        """Initialize the circle service with database session."""
        self.db = db
    
    async def create_circle(self, circle_data: CircleCreate, facilitator_id: int) -> Circle:
        """
        Create a new circle with the specified facilitator.
        
        Args:
            circle_data: Circle creation data
            facilitator_id: ID of the user who will be the facilitator
            
        Returns:
            Circle: The created circle
            
        Raises:
            ValidationError: If circle data is invalid
            HTTPException: If database operation fails
        """
        try:
            # Create circle with facilitator assignment
            circle = Circle(
                name=circle_data.name,
                description=circle_data.description,
                facilitator_id=facilitator_id,
                capacity_min=circle_data.capacity_min,
                capacity_max=circle_data.capacity_max,
                location_name=circle_data.location_name,
                location_address=circle_data.location_address,
                meeting_schedule=circle_data.meeting_schedule
            )
            
            self.db.add(circle)
            await self.db.commit()
            await self.db.refresh(circle)
            
            return circle
            
        except ValidationError:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create circle: {str(e)}"
            )
    
    async def get_circle_by_id(self, circle_id: int, user_id: int) -> Optional[Circle]:
        """
        Get a circle by ID with permission checking.
        
        Args:
            circle_id: ID of the circle to retrieve
            user_id: ID of the requesting user
            
        Returns:
            Circle: The circle if found and accessible
            None: If circle not found or not accessible
        """
        try:
            # For now, return circle if user is facilitator or member
            # TODO: Implement proper permission checking based on roles
            query = select(Circle).where(Circle.id == circle_id)
            result = await self.db.execute(query)
            circle = result.scalar_one_or_none()
            
            if not circle:
                return None
            
            # Basic permission check: facilitator or member can access
            if await self._user_can_access_circle(user_id, circle):
                return circle
            
            return None
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve circle: {str(e)}"
            )
    
    async def list_circles_for_user(
        self, 
        user_id: int, 
        search_params: CircleSearchParams
    ) -> tuple[List[Circle], int]:
        """
        List circles that the user has access to.
        
        Args:
            user_id: ID of the requesting user
            search_params: Search and filtering parameters
            
        Returns:
            tuple: (list of circles, total count)
        """
        try:
            # Build base query
            query = select(Circle)
            
            # Apply filters
            filters = []
            
            # Search by name or description
            if search_params.search:
                search_term = f"%{search_params.search}%"
                filters.append(
                    or_(
                        Circle.name.ilike(search_term),
                        Circle.description.ilike(search_term)
                    )
                )
            
            # Filter by status
            if search_params.status:
                filters.append(Circle.status == search_params.status.value)
            
            # Filter by facilitator
            if search_params.facilitator_id:
                filters.append(Circle.facilitator_id == search_params.facilitator_id)
            
            # Filter by location
            if search_params.location:
                location_term = f"%{search_params.location}%"
                filters.append(
                    or_(
                        Circle.location_name.ilike(location_term),
                        Circle.location_address.ilike(location_term)
                    )
                )
            
            # TODO: Add permission filtering based on user roles and memberships
            # For now, show circles where user is facilitator or member
            user_access_filter = or_(
                Circle.facilitator_id == user_id,
                Circle.id.in_(
                    select(CircleMembership.circle_id).where(
                        and_(
                            CircleMembership.user_id == user_id,
                            CircleMembership.is_active == True
                        )
                    )
                )
            )
            filters.append(user_access_filter)
            
            if filters:
                query = query.where(and_(*filters))
            
            # Get total count
            count_result = await self.db.execute(
                select(Circle.id).where(query.whereclause if filters else True)
            )
            total = len(count_result.all())
            
            # Apply pagination
            offset = (search_params.page - 1) * search_params.per_page
            query = query.offset(offset).limit(search_params.per_page)
            
            # Execute query
            result = await self.db.execute(query)
            circles = result.scalars().all()
            
            return list(circles), total
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list circles: {str(e)}"
            )
    
    async def update_circle(
        self, 
        circle_id: int, 
        circle_data: CircleUpdate, 
        user_id: int
    ) -> Optional[Circle]:
        """
        Update a circle (facilitator only).
        
        Args:
            circle_id: ID of the circle to update
            circle_data: Updated circle data
            user_id: ID of the requesting user
            
        Returns:
            Circle: The updated circle if successful
            None: If circle not found or no permission
            
        Raises:
            ValidationError: If update data is invalid
            HTTPException: If database operation fails
        """
        try:
            # Get existing circle
            circle = await self.get_circle_by_id(circle_id, user_id)
            if not circle:
                return None
            
            # Check if user is facilitator
            if circle.facilitator_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only facilitators can update circles"
                )
            
            # Update circle fields
            update_data = circle_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(circle, field):
                    setattr(circle, field, value)
            
            await self.db.commit()
            await self.db.refresh(circle)
            
            return circle
            
        except ValidationError:
            await self.db.rollback()
            raise
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update circle: {str(e)}"
            )
    
    async def add_member_to_circle(
        self, 
        circle_id: int, 
        user_id: int, 
        facilitator_id: int,
        payment_status: str = "pending"
    ) -> CircleMembership:
        """
        Add a member to a circle (facilitator only).
        
        Args:
            circle_id: ID of the circle
            user_id: ID of the user to add
            facilitator_id: ID of the requesting facilitator
            payment_status: Initial payment status
            
        Returns:
            CircleMembership: The created membership
            
        Raises:
            HTTPException: If operation fails or not permitted
        """
        try:
            # Get circle and verify facilitator permission
            circle = await self.get_circle_by_id(circle_id, facilitator_id)
            if not circle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Circle not found"
                )
            
            if circle.facilitator_id != facilitator_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only facilitators can add members"
                )
            
            # Check capacity
            if not circle.can_accept_members():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Circle is at maximum capacity"
                )
            
            # Check if user is already a member
            existing_membership = await self.db.execute(
                select(CircleMembership).where(
                    and_(
                        CircleMembership.circle_id == circle_id,
                        CircleMembership.user_id == user_id
                    )
                )
            )
            if existing_membership.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="User is already a member of this circle"
                )
            
            # Create membership
            membership = CircleMembership(
                circle_id=circle_id,
                user_id=user_id,
                payment_status=payment_status
            )
            
            self.db.add(membership)
            await self.db.commit()
            await self.db.refresh(membership)
            
            return membership
            
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to add member: {str(e)}"
            )
    
    async def _user_can_access_circle(self, user_id: int, circle: Circle) -> bool:
        """
        Check if user can access a circle.
        
        Args:
            user_id: ID of the user
            circle: Circle to check access for
            
        Returns:
            bool: True if user can access the circle
        """
        # User is facilitator
        if circle.facilitator_id == user_id:
            return True
        
        # User is a member
        membership_query = select(CircleMembership).where(
            and_(
                CircleMembership.circle_id == circle.id,
                CircleMembership.user_id == user_id,
                CircleMembership.is_active == True
            )
        )
        result = await self.db.execute(membership_query)
        membership = result.scalar_one_or_none()
        
        if membership:
            return True
        
        # TODO: Add role-based permissions
        # - Managers and Directors can access all circles
        # - PTMs can access circles they're assigned to
        
        return False


# Dependency injection
async def get_circle_service(db: AsyncSession = Depends(get_main_db)) -> CircleService:
    """
    Dependency function to get CircleService instance.
    
    Args:
        db: Database session
        
    Returns:
        CircleService: Service instance
    """
    return CircleService(db) 