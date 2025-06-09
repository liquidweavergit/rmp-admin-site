"""
Circle service for managing circle business logic and database operations
"""
from typing import List, Optional, Dict, Any
from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status, Depends

from ..models.circle import Circle, CircleStatus
from ..models.circle_membership import CircleMembership, PaymentStatus
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
        Create a new circle with automatic facilitator assignment.
        
        Args:
            circle_data: Circle creation data
            facilitator_id: ID of the user who will be the facilitator
            
        Returns:
            Circle: The created circle
            
        Raises:
            ValidationError: If circle data is invalid
            HTTPException: If creation fails
        """
        try:
            # Create new circle
            circle = Circle(
                name=circle_data.name,
                description=circle_data.description,
                facilitator_id=facilitator_id,  # Automatic assignment
                capacity_min=circle_data.capacity_min or 2,
                capacity_max=circle_data.capacity_max or 8,
                location_name=circle_data.location_name,
                location_address=circle_data.location_address,
                meeting_schedule=circle_data.meeting_schedule,
                status=CircleStatus.FORMING  # New circles start as forming
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
        Get a circle by ID with access control.
        
        Args:
            circle_id: ID of the circle to retrieve
            user_id: ID of the requesting user
            
        Returns:
            Circle: The circle if found and accessible
            None: If circle not found or not accessible
        """
        try:
            # Get circle with member count
            query = select(Circle).where(Circle.id == circle_id)
            result = await self.db.execute(query)
            circle = result.scalar_one_or_none()
            
            if not circle:
                return None
            
            # Check access permissions
            if not await self._user_can_access_circle(user_id, circle):
                return None
            
            return circle
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve circle: {str(e)}"
            )
    
    async def list_circles_for_user(
        self, 
        user_id: int, 
        search_params: CircleSearchParams
    ) -> Tuple[List[Circle], int]:
        """
        List circles that a user has access to with filtering and pagination.
        
        Args:
            user_id: ID of the requesting user
            search_params: Search and filter parameters
            
        Returns:
            tuple: (List of circles, Total count)
            
        Raises:
            HTTPException: If listing fails
        """
        try:
            # Build base query with user access filtering
            base_query = select(Circle).where(
                or_(
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
            )
            
            # Apply filters
            if search_params.search:
                search_term = f"%{search_params.search}%"
                base_query = base_query.where(
                    or_(
                        Circle.name.ilike(search_term),
                        Circle.description.ilike(search_term)
                    )
                )
            
            if search_params.status:
                base_query = base_query.where(Circle.status == search_params.status)
            
            if search_params.facilitator_id:
                base_query = base_query.where(Circle.facilitator_id == search_params.facilitator_id)
            
            if search_params.location:
                location_term = f"%{search_params.location}%"
                base_query = base_query.where(
                    or_(
                        Circle.location_name.ilike(location_term),
                        Circle.location_address.ilike(location_term)
                    )
                )
            
            if search_params.capacity_min:
                base_query = base_query.where(Circle.capacity_min >= search_params.capacity_min)
            
            if search_params.capacity_max:
                base_query = base_query.where(Circle.capacity_max <= search_params.capacity_max)
            
            # Get total count
            count_query = select(func.count()).select_from(base_query.subquery())
            count_result = await self.db.execute(count_query)
            total = count_result.scalar()
            
            # Apply sorting
            sort_field = getattr(Circle, search_params.sort_by, Circle.created_at)
            if search_params.sort_order.lower() == "asc":
                query = base_query.order_by(asc(sort_field))
            else:
                query = base_query.order_by(desc(sort_field))
            
            # Apply pagination
            query = query.offset((search_params.page - 1) * search_params.per_page)
            query = query.limit(search_params.per_page)
            
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
    
    async def remove_member_from_circle(
        self,
        circle_id: int,
        user_id: int,
        facilitator_id: int
    ) -> bool:
        """
        Remove a member from a circle (facilitator only).
        
        Args:
            circle_id: ID of the circle
            user_id: ID of the user to remove
            facilitator_id: ID of the requesting facilitator
            
        Returns:
            bool: True if member was removed, False if not found
            
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
                    detail="Only facilitators can remove members"
                )
            
            # Find existing membership
            membership_query = select(CircleMembership).where(
                and_(
                    CircleMembership.circle_id == circle_id,
                    CircleMembership.user_id == user_id,
                    CircleMembership.is_active == True
                )
            )
            result = await self.db.execute(membership_query)
            membership = result.scalar_one_or_none()
            
            if not membership:
                return False
            
            # Mark membership as inactive instead of deleting
            membership.is_active = False
            
            await self.db.commit()
            return True
            
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to remove member: {str(e)}"
            )
    
    async def transfer_member_between_circles(
        self,
        source_circle_id: int,
        target_circle_id: int,
        user_id: int,
        facilitator_id: int,
        reason: Optional[str] = None
    ) -> CircleMembership:
        """
        Transfer a member from one circle to another (facilitator only).
        
        Args:
            source_circle_id: ID of the source circle
            target_circle_id: ID of the target circle
            user_id: ID of the user to transfer
            facilitator_id: ID of the requesting facilitator
            reason: Optional reason for the transfer
            
        Returns:
            CircleMembership: The new membership in target circle
            
        Raises:
            HTTPException: If operation fails or not permitted
        """
        try:
            # Get both circles and verify facilitator permission
            source_circle = await self.get_circle_by_id(source_circle_id, facilitator_id)
            target_circle = await self.get_circle_by_id(target_circle_id, facilitator_id)
            
            if not source_circle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Source circle not found"
                )
            
            if not target_circle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Target circle not found"
                )
            
            # Check facilitator permissions for both circles
            if (source_circle.facilitator_id != facilitator_id and 
                target_circle.facilitator_id != facilitator_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only facilitators can transfer members"
                )
            
            # Check target circle capacity
            if not target_circle.can_accept_members():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Target circle is at maximum capacity"
                )
            
            # Check if user is already in target circle
            existing_target_membership = await self.db.execute(
                select(CircleMembership).where(
                    and_(
                        CircleMembership.circle_id == target_circle_id,
                        CircleMembership.user_id == user_id,
                        CircleMembership.is_active == True
                    )
                )
            )
            if existing_target_membership.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="User is already a member of the target circle"
                )
            
            # Find source membership
            source_membership_query = select(CircleMembership).where(
                and_(
                    CircleMembership.circle_id == source_circle_id,
                    CircleMembership.user_id == user_id,
                    CircleMembership.is_active == True
                )
            )
            result = await self.db.execute(source_membership_query)
            source_membership = result.scalar_one_or_none()
            
            if not source_membership:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User is not an active member of the source circle"
                )
            
            # Deactivate source membership
            source_membership.is_active = False
            
            # Create new membership in target circle
            new_membership = CircleMembership(
                circle_id=target_circle_id,
                user_id=user_id,
                payment_status=source_membership.payment_status  # Preserve payment status
            )
            
            self.db.add(new_membership)
            await self.db.commit()
            await self.db.refresh(new_membership)
            
            return new_membership
            
        except HTTPException:
            await self.db.rollback()
            raise
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to transfer member: {str(e)}"
            )
    
    async def get_circle_members(
        self,
        circle_id: int,
        user_id: int
    ) -> List[CircleMembership]:
        """
        Get all active members of a circle.
        
        Args:
            circle_id: ID of the circle
            user_id: ID of the requesting user
            
        Returns:
            List[CircleMembership]: List of active memberships
            
        Raises:
            HTTPException: If operation fails or not permitted
        """
        try:
            # Get circle and verify access
            circle = await self.get_circle_by_id(circle_id, user_id)
            if not circle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Circle not found or access denied"
                )
            
            # Get active memberships
            memberships_query = select(CircleMembership).where(
                and_(
                    CircleMembership.circle_id == circle_id,
                    CircleMembership.is_active == True
                )
            ).order_by(CircleMembership.joined_at)
            
            result = await self.db.execute(memberships_query)
            memberships = result.scalars().all()
            
            return list(memberships)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get circle members: {str(e)}"
            )
    
    async def update_member_payment_status(
        self,
        circle_id: int,
        user_id: int,
        payment_status: str,
        facilitator_id: int
    ) -> Optional[CircleMembership]:
        """
        Update a member's payment status (facilitator only).
        
        Args:
            circle_id: ID of the circle
            user_id: ID of the member
            payment_status: New payment status
            facilitator_id: ID of the requesting facilitator
            
        Returns:
            CircleMembership: The updated membership if successful
            None: If membership not found
            
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
                    detail="Only facilitators can update payment status"
                )
            
            # Find existing membership
            membership_query = select(CircleMembership).where(
                and_(
                    CircleMembership.circle_id == circle_id,
                    CircleMembership.user_id == user_id,
                    CircleMembership.is_active == True
                )
            )
            result = await self.db.execute(membership_query)
            membership = result.scalar_one_or_none()
            
            if not membership:
                return None
            
            # Update payment status
            membership.payment_status = PaymentStatus(payment_status)
            
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
                detail=f"Failed to update payment status: {str(e)}"
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