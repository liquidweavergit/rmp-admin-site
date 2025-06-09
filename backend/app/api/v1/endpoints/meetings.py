"""
Meeting API endpoints for creating and managing meetings and attendance
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPAuthorizationCredentials

from ....schemas.meeting import (
    MeetingCreate,
    MeetingUpdate,
    MeetingResponse,
    MeetingListResponse,
    MeetingSearchParams,
    MeetingWithAttendance,
    MeetingAttendanceUpdate,
    MeetingAttendanceResponse,
    MeetingStatusUpdate,
    AttendanceSummary
)
from ....services.meeting_service import MeetingService, get_meeting_service
from ....core.deps import get_current_user
from ....models.user import User
from ....models.meeting import MeetingStatus

router = APIRouter()


@router.post(
    "",
    response_model=MeetingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new meeting",
    description="Create a new meeting for a circle with automatic attendance record creation"
)
async def create_meeting(
    meeting_data: MeetingCreate,
    current_user: User = Depends(get_current_user),
    meeting_service: MeetingService = Depends(get_meeting_service)
) -> MeetingResponse:
    """
    Create a new meeting for a circle.
    
    - **title**: Meeting title (required, 1-200 characters)
    - **description**: Meeting description (optional, max 2000 characters)
    - **scheduled_date**: Scheduled date and time (required)
    - **circle_id**: ID of the circle this meeting belongs to (required)
    - **facilitator_id**: ID of the meeting facilitator (optional, defaults to current user)
    - **location_name**: Meeting location name (optional, max 200 characters)
    - **location_address**: Meeting location address (optional, max 500 characters)
    - **agenda**: Meeting agenda as JSON object (optional)
    
    The current authenticated user will be assigned as facilitator if not specified.
    Attendance records will be automatically created for all active circle members.
    
    Returns the created meeting information with attendance summary.
    """
    try:
        meeting = await meeting_service.create_meeting(meeting_data, current_user.id)
        
        # Convert to response format
        return MeetingResponse(
            id=meeting.id,
            title=meeting.title,
            description=meeting.description,
            scheduled_date=meeting.scheduled_date,
            circle_id=meeting.circle_id,
            facilitator_id=meeting.facilitator_id,
            location_name=meeting.location_name,
            location_address=meeting.location_address,
            agenda=meeting.agenda,
            status=meeting.status,
            is_active=meeting.is_active,
            started_at=meeting.started_at,
            ended_at=meeting.ended_at,
            meeting_notes=meeting.meeting_notes,
            duration_minutes=meeting.duration_minutes,
            attendance_summary=AttendanceSummary(**meeting.attendance_summary),
            created_at=meeting.created_at,
            updated_at=meeting.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create meeting"
        )


@router.get(
    "",
    response_model=MeetingListResponse,
    summary="List meetings",
    description="Get a list of meetings the user has access to"
)
async def list_meetings(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page (1-100)"),
    circle_id: Optional[int] = Query(None, description="Filter by circle ID"),
    facilitator_id: Optional[int] = Query(None, description="Filter by facilitator ID"),
    status: Optional[MeetingStatus] = Query(None, description="Filter by meeting status"),
    date_from: Optional[str] = Query(None, description="Filter meetings from this date (ISO format)"),
    date_to: Optional[str] = Query(None, description="Filter meetings to this date (ISO format)"),
    search: Optional[str] = Query(None, description="Search term for meeting title or description"),
    current_user: User = Depends(get_current_user),
    meeting_service: MeetingService = Depends(get_meeting_service)
) -> MeetingListResponse:
    """
    List meetings that the current user has access to.
    
    Access is determined by:
    - User is the facilitator of the meeting
    - User is a member of the circle the meeting belongs to
    - User has role-based permissions (TODO: implement)
    
    Supports filtering by:
    - **circle_id**: Filter by circle ID
    - **facilitator_id**: Filter by facilitator user ID
    - **status**: Filter by meeting status (scheduled, in_progress, completed, cancelled)
    - **date_from/date_to**: Filter by date range
    - **search**: Text search in meeting title or description
    
    Supports pagination with page and per_page parameters.
    """
    try:
        from datetime import datetime
        
        # Parse date filters
        date_from_parsed = None
        date_to_parsed = None
        if date_from:
            date_from_parsed = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        if date_to:
            date_to_parsed = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        
        search_params = MeetingSearchParams(
            page=page,
            per_page=per_page,
            circle_id=circle_id,
            facilitator_id=facilitator_id,
            status=status,
            date_from=date_from_parsed,
            date_to=date_to_parsed,
            search=search
        )
        
        meetings, total = await meeting_service.list_meetings_for_user(
            current_user.id, 
            search_params
        )
        
        # Convert to response format
        meeting_responses = []
        for meeting in meetings:
            meeting_responses.append(MeetingResponse(
                id=meeting.id,
                title=meeting.title,
                description=meeting.description,
                scheduled_date=meeting.scheduled_date,
                circle_id=meeting.circle_id,
                facilitator_id=meeting.facilitator_id,
                location_name=meeting.location_name,
                location_address=meeting.location_address,
                agenda=meeting.agenda,
                status=meeting.status,
                is_active=meeting.is_active,
                started_at=meeting.started_at,
                ended_at=meeting.ended_at,
                meeting_notes=meeting.meeting_notes,
                duration_minutes=meeting.duration_minutes,
                attendance_summary=AttendanceSummary(**meeting.attendance_summary),
                created_at=meeting.created_at,
                updated_at=meeting.updated_at
            ))
        
        return MeetingListResponse(
            meetings=meeting_responses,
            total=total,
            page=page,
            per_page=per_page
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list meetings"
        )


@router.get(
    "/{meeting_id}",
    response_model=MeetingWithAttendance,
    summary="Get meeting details",
    description="Get detailed information about a specific meeting including attendance records"
)
async def get_meeting(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    meeting_service: MeetingService = Depends(get_meeting_service)
) -> MeetingWithAttendance:
    """
    Get detailed information about a specific meeting.
    
    - **meeting_id**: ID of the meeting to retrieve
    
    Access is verified based on user permissions:
    - Facilitator can always access their meetings
    - Circle members can access meetings for their circles
    - Role-based access control (TODO: implement)
    
    Returns detailed meeting information including full attendance records.
    """
    try:
        meeting = await meeting_service.get_meeting_by_id(meeting_id, current_user.id)
        
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting not found or access denied"
            )
        
        # Convert attendance records
        attendance_responses = []
        for attendance in meeting.attendance_records:
            attendance_responses.append(MeetingAttendanceResponse(
                meeting_id=attendance.meeting_id,
                user_id=attendance.user_id,
                attendance_status=attendance.attendance_status,
                check_in_time=attendance.check_in_time,
                check_out_time=attendance.check_out_time,
                notes=attendance.notes,
                created_at=attendance.created_at,
                updated_at=attendance.updated_at
            ))
        
        # Convert to response format
        return MeetingWithAttendance(
            id=meeting.id,
            title=meeting.title,
            description=meeting.description,
            scheduled_date=meeting.scheduled_date,
            circle_id=meeting.circle_id,
            facilitator_id=meeting.facilitator_id,
            location_name=meeting.location_name,
            location_address=meeting.location_address,
            agenda=meeting.agenda,
            status=meeting.status,
            is_active=meeting.is_active,
            started_at=meeting.started_at,
            ended_at=meeting.ended_at,
            meeting_notes=meeting.meeting_notes,
            duration_minutes=meeting.duration_minutes,
            attendance_summary=AttendanceSummary(**meeting.attendance_summary),
            attendance_records=attendance_responses,
            created_at=meeting.created_at,
            updated_at=meeting.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get meeting"
        )


@router.put(
    "/{meeting_id}",
    response_model=MeetingResponse,
    summary="Update meeting",
    description="Update meeting information (facilitator or circle facilitator only)"
)
async def update_meeting(
    meeting_id: int,
    meeting_data: MeetingUpdate,
    current_user: User = Depends(get_current_user),
    meeting_service: MeetingService = Depends(get_meeting_service)
) -> MeetingResponse:
    """
    Update meeting information.
    
    - **meeting_id**: ID of the meeting to update
    
    Only the meeting facilitator or circle facilitator can update meetings.
    
    All fields are optional - only provided fields will be updated.
    """
    try:
        meeting = await meeting_service.update_meeting(meeting_id, meeting_data, current_user.id)
        
        return MeetingResponse(
            id=meeting.id,
            title=meeting.title,
            description=meeting.description,
            scheduled_date=meeting.scheduled_date,
            circle_id=meeting.circle_id,
            facilitator_id=meeting.facilitator_id,
            location_name=meeting.location_name,
            location_address=meeting.location_address,
            agenda=meeting.agenda,
            status=meeting.status,
            is_active=meeting.is_active,
            started_at=meeting.started_at,
            ended_at=meeting.ended_at,
            meeting_notes=meeting.meeting_notes,
            duration_minutes=meeting.duration_minutes,
            attendance_summary=AttendanceSummary(**meeting.attendance_summary),
            created_at=meeting.created_at,
            updated_at=meeting.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update meeting"
        )


@router.post(
    "/{meeting_id}/start",
    response_model=MeetingResponse,
    summary="Start meeting",
    description="Start a scheduled meeting"
)
async def start_meeting(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    meeting_service: MeetingService = Depends(get_meeting_service)
) -> MeetingResponse:
    """
    Start a scheduled meeting.
    
    Changes the meeting status from 'scheduled' to 'in_progress' and records the start time.
    Only the meeting facilitator or circle facilitator can start meetings.
    """
    try:
        meeting = await meeting_service.start_meeting(meeting_id, current_user.id)
        
        return MeetingResponse(
            id=meeting.id,
            title=meeting.title,
            description=meeting.description,
            scheduled_date=meeting.scheduled_date,
            circle_id=meeting.circle_id,
            facilitator_id=meeting.facilitator_id,
            location_name=meeting.location_name,
            location_address=meeting.location_address,
            agenda=meeting.agenda,
            status=meeting.status,
            is_active=meeting.is_active,
            started_at=meeting.started_at,
            ended_at=meeting.ended_at,
            meeting_notes=meeting.meeting_notes,
            duration_minutes=meeting.duration_minutes,
            attendance_summary=AttendanceSummary(**meeting.attendance_summary),
            created_at=meeting.created_at,
            updated_at=meeting.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start meeting"
        )


@router.post(
    "/{meeting_id}/end",
    response_model=MeetingResponse,
    summary="End meeting",
    description="End a meeting in progress"
)
async def end_meeting(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    meeting_service: MeetingService = Depends(get_meeting_service)
) -> MeetingResponse:
    """
    End a meeting that is in progress.
    
    Changes the meeting status from 'in_progress' to 'completed' and records the end time.
    Only the meeting facilitator or circle facilitator can end meetings.
    """
    try:
        meeting = await meeting_service.end_meeting(meeting_id, current_user.id)
        
        return MeetingResponse(
            id=meeting.id,
            title=meeting.title,
            description=meeting.description,
            scheduled_date=meeting.scheduled_date,
            circle_id=meeting.circle_id,
            facilitator_id=meeting.facilitator_id,
            location_name=meeting.location_name,
            location_address=meeting.location_address,
            agenda=meeting.agenda,
            status=meeting.status,
            is_active=meeting.is_active,
            started_at=meeting.started_at,
            ended_at=meeting.ended_at,
            meeting_notes=meeting.meeting_notes,
            duration_minutes=meeting.duration_minutes,
            attendance_summary=AttendanceSummary(**meeting.attendance_summary),
            created_at=meeting.created_at,
            updated_at=meeting.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to end meeting"
        )


@router.post(
    "/{meeting_id}/cancel",
    response_model=MeetingResponse,
    summary="Cancel meeting",
    description="Cancel a scheduled meeting"
)
async def cancel_meeting(
    meeting_id: int,
    current_user: User = Depends(get_current_user),
    meeting_service: MeetingService = Depends(get_meeting_service)
) -> MeetingResponse:
    """
    Cancel a scheduled meeting.
    
    Changes the meeting status to 'cancelled'.
    Only the meeting facilitator or circle facilitator can cancel meetings.
    Cannot cancel meetings that are already completed.
    """
    try:
        meeting = await meeting_service.cancel_meeting(meeting_id, current_user.id)
        
        return MeetingResponse(
            id=meeting.id,
            title=meeting.title,
            description=meeting.description,
            scheduled_date=meeting.scheduled_date,
            circle_id=meeting.circle_id,
            facilitator_id=meeting.facilitator_id,
            location_name=meeting.location_name,
            location_address=meeting.location_address,
            agenda=meeting.agenda,
            status=meeting.status,
            is_active=meeting.is_active,
            started_at=meeting.started_at,
            ended_at=meeting.ended_at,
            meeting_notes=meeting.meeting_notes,
            duration_minutes=meeting.duration_minutes,
            attendance_summary=AttendanceSummary(**meeting.attendance_summary),
            created_at=meeting.created_at,
            updated_at=meeting.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel meeting"
        )


@router.patch(
    "/{meeting_id}/attendance/{user_id}",
    response_model=MeetingAttendanceResponse,
    summary="Update attendance record",
    description="Update attendance status for a specific user at a meeting"
)
async def update_attendance(
    meeting_id: int,
    user_id: int,
    attendance_data: MeetingAttendanceUpdate,
    current_user: User = Depends(get_current_user),
    meeting_service: MeetingService = Depends(get_meeting_service)
) -> MeetingAttendanceResponse:
    """
    Update attendance record for a specific user at a meeting.
    
    - **meeting_id**: ID of the meeting
    - **user_id**: ID of the user whose attendance to update
    
    Only the meeting facilitator or circle facilitator can record attendance.
    
    Attendance status options:
    - **present**: Member was present for the meeting
    - **absent**: Member was absent from the meeting
    - **excused**: Member was absent but excused
    - **late**: Member arrived late but attended
    """
    try:
        attendance = await meeting_service.update_attendance(
            meeting_id, user_id, attendance_data, current_user.id
        )
        
        return MeetingAttendanceResponse(
            meeting_id=attendance.meeting_id,
            user_id=attendance.user_id,
            attendance_status=attendance.attendance_status,
            check_in_time=attendance.check_in_time,
            check_out_time=attendance.check_out_time,
            notes=attendance.notes,
            created_at=attendance.created_at,
            updated_at=attendance.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update attendance"
        ) 