"""
Meeting service for handling meeting and attendance business logic
"""
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status, Depends

from ..core.database import get_main_db
from ..core.exceptions import ValidationError, ResourceNotFound, PermissionDenied
from ..models.meeting import Meeting, MeetingAttendance, MeetingStatus, AttendanceStatus
from ..models.circle import Circle
from ..models.circle_membership import CircleMembership
from ..models.user import User
from ..schemas.meeting import (
    MeetingCreate, MeetingUpdate, MeetingSearchParams,
    MeetingAttendanceCreate, MeetingAttendanceUpdate,
    BulkAttendanceUpdate
)


class MeetingService:
    """Service for managing meetings and attendance."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_meeting(self, meeting_data: MeetingCreate, current_user_id: int) -> Meeting:
        """
        Create a new meeting for a circle.
        
        Args:
            meeting_data: Meeting creation data
            current_user_id: ID of the user creating the meeting
            
        Returns:
            Created meeting instance
            
        Raises:
            ValidationError: If validation fails
            PermissionDenied: If user lacks permission
            ResourceNotFound: If circle not found
        """
        # Verify circle exists and user has permission
        circle = await self._get_circle_with_permission_check(
            meeting_data.circle_id, 
            current_user_id, 
            "meetings:schedule"
        )
        
        # Set facilitator to current user if not specified
        facilitator_id = meeting_data.facilitator_id or current_user_id
        
        # Verify facilitator has permission
        if facilitator_id != current_user_id:
            await self._verify_user_has_permission(facilitator_id, "meetings:schedule")
        
        # Create meeting
        meeting = Meeting(
            circle_id=meeting_data.circle_id,
            facilitator_id=facilitator_id,
            title=meeting_data.title,
            description=meeting_data.description,
            scheduled_date=meeting_data.scheduled_date,
            location_name=meeting_data.location_name,
            location_address=meeting_data.location_address,
            agenda=meeting_data.agenda
        )
        
        self.session.add(meeting)
        await self.session.commit()
        await self.session.refresh(meeting)
        
        # Create attendance records for all active circle members
        await self._create_attendance_records_for_meeting(meeting.id, circle.id)
        
        return meeting
    
    async def get_meeting_by_id(self, meeting_id: int, current_user_id: int) -> Optional[Meeting]:
        """
        Get a meeting by ID with permission check.
        
        Args:
            meeting_id: Meeting ID
            current_user_id: Current user ID
            
        Returns:
            Meeting instance or None if not found/no permission
        """
        query = select(Meeting).options(
            selectinload(Meeting.attendance_records),
            selectinload(Meeting.circle),
            selectinload(Meeting.facilitator)
        ).where(Meeting.id == meeting_id)
        
        result = await self.session.execute(query)
        meeting = result.scalar_one_or_none()
        
        if not meeting:
            return None
        
        # Check if user has access to this meeting
        if not await self._user_can_access_meeting(meeting, current_user_id):
            return None
        
        return meeting
    
    async def list_meetings_for_user(
        self, 
        current_user_id: int, 
        search_params: MeetingSearchParams
    ) -> Tuple[List[Meeting], int]:
        """
        List meetings accessible to the user with filtering and pagination.
        
        Args:
            current_user_id: Current user ID
            search_params: Search and filter parameters
            
        Returns:
            Tuple of (meetings list, total count)
        """
        # Build base query with joins
        query = select(Meeting).options(
            selectinload(Meeting.attendance_records),
            selectinload(Meeting.circle),
            selectinload(Meeting.facilitator)
        )
        
        # Apply filters
        conditions = []
        
        # Circle filter
        if search_params.circle_id:
            conditions.append(Meeting.circle_id == search_params.circle_id)
        
        # Facilitator filter
        if search_params.facilitator_id:
            conditions.append(Meeting.facilitator_id == search_params.facilitator_id)
        
        # Status filter
        if search_params.status:
            conditions.append(Meeting.status == search_params.status.value)
        
        # Date range filters
        if search_params.date_from:
            conditions.append(Meeting.scheduled_date >= search_params.date_from)
        if search_params.date_to:
            conditions.append(Meeting.scheduled_date <= search_params.date_to)
        
        # Text search
        if search_params.search:
            search_term = f"%{search_params.search}%"
            conditions.append(
                or_(
                    Meeting.title.ilike(search_term),
                    Meeting.description.ilike(search_term)
                )
            )
        
        # Add permission-based filtering
        # User can see meetings for circles they're involved with
        accessible_circles_query = select(Circle.id).where(
            or_(
                Circle.facilitator_id == current_user_id,
                Circle.id.in_(
                    select(CircleMembership.circle_id).where(
                        and_(
                            CircleMembership.user_id == current_user_id,
                            CircleMembership.is_active == True
                        )
                    )
                )
            )
        )
        
        conditions.append(Meeting.circle_id.in_(accessible_circles_query))
        
        # Apply all conditions
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count(Meeting.id)).where(and_(*conditions))
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()
        
        # Apply ordering and pagination
        query = query.order_by(desc(Meeting.scheduled_date))
        offset = (search_params.page - 1) * search_params.per_page
        query = query.offset(offset).limit(search_params.per_page)
        
        # Execute query
        result = await self.session.execute(query)
        meetings = result.scalars().all()
        
        return list(meetings), total
    
    async def update_meeting(
        self, 
        meeting_id: int, 
        meeting_data: MeetingUpdate, 
        current_user_id: int
    ) -> Meeting:
        """
        Update a meeting.
        
        Args:
            meeting_id: Meeting ID
            meeting_data: Update data
            current_user_id: Current user ID
            
        Returns:
            Updated meeting
            
        Raises:
            ResourceNotFound: If meeting not found
            PermissionDenied: If user lacks permission
        """
        meeting = await self.get_meeting_by_id(meeting_id, current_user_id)
        if not meeting:
            raise ResourceNotFound("Meeting", meeting_id)
        
        # Check permission to edit meetings
        if not await self._user_can_edit_meeting(meeting, current_user_id):
            raise PermissionDenied("Insufficient permissions to edit this meeting")
        
        # Update fields
        update_data = meeting_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(meeting, field, value)
        
        await self.session.commit()
        await self.session.refresh(meeting)
        
        return meeting
    
    async def start_meeting(self, meeting_id: int, current_user_id: int) -> Meeting:
        """Start a meeting."""
        meeting = await self.get_meeting_by_id(meeting_id, current_user_id)
        if not meeting:
            raise ResourceNotFound("Meeting", meeting_id)
        
        if not await self._user_can_edit_meeting(meeting, current_user_id):
            raise PermissionDenied("Insufficient permissions to start this meeting")
        
        meeting.start_meeting()
        await self.session.commit()
        await self.session.refresh(meeting)
        
        return meeting
    
    async def end_meeting(self, meeting_id: int, current_user_id: int) -> Meeting:
        """End a meeting."""
        meeting = await self.get_meeting_by_id(meeting_id, current_user_id)
        if not meeting:
            raise ResourceNotFound("Meeting", meeting_id)
        
        if not await self._user_can_edit_meeting(meeting, current_user_id):
            raise PermissionDenied("Insufficient permissions to end this meeting")
        
        meeting.end_meeting()
        await self.session.commit()
        await self.session.refresh(meeting)
        
        return meeting
    
    async def cancel_meeting(self, meeting_id: int, current_user_id: int) -> Meeting:
        """Cancel a meeting."""
        meeting = await self.get_meeting_by_id(meeting_id, current_user_id)
        if not meeting:
            raise ResourceNotFound("Meeting", meeting_id)
        
        if not await self._user_can_edit_meeting(meeting, current_user_id):
            raise PermissionDenied("Insufficient permissions to cancel this meeting")
        
        meeting.cancel_meeting()
        await self.session.commit()
        await self.session.refresh(meeting)
        
        return meeting
    
    async def update_attendance(
        self, 
        meeting_id: int, 
        user_id: int, 
        attendance_data: MeetingAttendanceUpdate,
        current_user_id: int
    ) -> MeetingAttendance:
        """
        Update attendance for a specific user at a meeting.
        
        Args:
            meeting_id: Meeting ID
            user_id: User ID whose attendance to update
            attendance_data: Attendance update data
            current_user_id: Current user ID
            
        Returns:
            Updated attendance record
        """
        # Get meeting and verify permissions
        meeting = await self.get_meeting_by_id(meeting_id, current_user_id)
        if not meeting:
            raise ResourceNotFound("Meeting", meeting_id)
        
        if not await self._user_can_record_attendance(meeting, current_user_id):
            raise PermissionDenied("Insufficient permissions to record attendance")
        
        # Get or create attendance record
        query = select(MeetingAttendance).where(
            and_(
                MeetingAttendance.meeting_id == meeting_id,
                MeetingAttendance.user_id == user_id
            )
        )
        result = await self.session.execute(query)
        attendance = result.scalar_one_or_none()
        
        if not attendance:
            # Create new attendance record
            attendance = MeetingAttendance(
                meeting_id=meeting_id,
                user_id=user_id
            )
            self.session.add(attendance)
        
        # Update fields
        update_data = attendance_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(attendance, field, value)
        
        await self.session.commit()
        await self.session.refresh(attendance)
        
        return attendance
    
    async def bulk_update_attendance(
        self, 
        meeting_id: int, 
        bulk_data: BulkAttendanceUpdate,
        current_user_id: int
    ) -> List[MeetingAttendance]:
        """
        Bulk update attendance records for a meeting.
        
        Args:
            meeting_id: Meeting ID
            bulk_data: Bulk attendance update data
            current_user_id: Current user ID
            
        Returns:
            List of updated attendance records
        """
        # Get meeting and verify permissions
        meeting = await self.get_meeting_by_id(meeting_id, current_user_id)
        if not meeting:
            raise ResourceNotFound("Meeting", meeting_id)
        
        if not await self._user_can_record_attendance(meeting, current_user_id):
            raise PermissionDenied("Insufficient permissions to record attendance")
        
        updated_records = []
        
        for i, attendance_update in enumerate(bulk_data.attendance_records):
            # Each record should have user_id in the update data
            # For now, we'll assume the order matches circle members
            # In a real implementation, you'd want user_id in each update
            
            # This is a simplified implementation - in practice you'd want
            # to include user_id in the MeetingAttendanceUpdate schema
            # or handle this differently
            pass
        
        return updated_records
    
    # Private helper methods
    
    async def _get_circle_with_permission_check(
        self, 
        circle_id: int, 
        user_id: int, 
        permission: str
    ) -> Circle:
        """Get circle and verify user has permission."""
        query = select(Circle).where(Circle.id == circle_id)
        result = await self.session.execute(query)
        circle = result.scalar_one_or_none()
        
        if not circle:
            raise NotFoundError("Circle not found")
        
        # Check if user is facilitator or has permission
        if circle.facilitator_id == user_id:
            return circle
        
        # TODO: Implement role-based permission checking
        # For now, allow circle members to schedule meetings
        membership_query = select(CircleMembership).where(
            and_(
                CircleMembership.circle_id == circle_id,
                CircleMembership.user_id == user_id,
                CircleMembership.is_active == True
            )
        )
        membership_result = await self.session.execute(membership_query)
        membership = membership_result.scalar_one_or_none()
        
        if not membership:
            raise PermissionDeniedError("Insufficient permissions for this circle")
        
        return circle
    
    async def _verify_user_has_permission(self, user_id: int, permission: str) -> bool:
        """Verify user has specific permission."""
        # TODO: Implement role-based permission checking
        # For now, return True (simplified)
        return True
    
    async def _user_can_access_meeting(self, meeting: Meeting, user_id: int) -> bool:
        """Check if user can access a meeting."""
        # User can access if they are:
        # 1. The facilitator
        # 2. A member of the circle
        # 3. Have appropriate role permissions
        
        if meeting.facilitator_id == user_id:
            return True
        
        # Check circle membership
        membership_query = select(CircleMembership).where(
            and_(
                CircleMembership.circle_id == meeting.circle_id,
                CircleMembership.user_id == user_id,
                CircleMembership.is_active == True
            )
        )
        result = await self.session.execute(membership_query)
        membership = result.scalar_one_or_none()
        
        return membership is not None
    
    async def _user_can_edit_meeting(self, meeting: Meeting, user_id: int) -> bool:
        """Check if user can edit a meeting."""
        # User can edit if they are:
        # 1. The meeting facilitator
        # 2. The circle facilitator
        # 3. Have appropriate role permissions
        
        if meeting.facilitator_id == user_id:
            return True
        
        # Check if user is circle facilitator
        if meeting.circle and meeting.circle.facilitator_id == user_id:
            return True
        
        # TODO: Add role-based permission checking
        return False
    
    async def _user_can_record_attendance(self, meeting: Meeting, user_id: int) -> bool:
        """Check if user can record attendance."""
        # Same permissions as editing meetings for now
        return await self._user_can_edit_meeting(meeting, user_id)
    
    async def _create_attendance_records_for_meeting(self, meeting_id: int, circle_id: int) -> None:
        """Create attendance records for all active circle members."""
        # Get all active circle members
        members_query = select(CircleMembership.user_id).where(
            and_(
                CircleMembership.circle_id == circle_id,
                CircleMembership.is_active == True
            )
        )
        result = await self.session.execute(members_query)
        member_ids = result.scalars().all()
        
        # Create attendance records
        for user_id in member_ids:
            attendance = MeetingAttendance(
                meeting_id=meeting_id,
                user_id=user_id,
                attendance_status=AttendanceStatus.ABSENT.value  # Default to absent
            )
            self.session.add(attendance)
        
        await self.session.commit()


# Dependency injection
async def get_meeting_service(session: AsyncSession = Depends(get_main_db)) -> MeetingService:
    """Get meeting service instance."""
    return MeetingService(session) 