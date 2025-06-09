"""
Pydantic schemas for meeting and attendance management
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum

from ..models.meeting import MeetingStatus, AttendanceStatus


class MeetingStatusSchema(str, Enum):
    """Meeting status schema enum."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AttendanceStatusSchema(str, Enum):
    """Attendance status schema enum."""
    PRESENT = "present"
    ABSENT = "absent"
    EXCUSED = "excused"
    LATE = "late"


# Base schemas
class MeetingBase(BaseModel):
    """Base meeting schema with common fields."""
    title: str = Field(..., min_length=1, max_length=200, description="Meeting title")
    description: Optional[str] = Field(None, max_length=2000, description="Meeting description")
    scheduled_date: datetime = Field(..., description="Scheduled date and time for the meeting")
    location_name: Optional[str] = Field(None, max_length=200, description="Meeting location name")
    location_address: Optional[str] = Field(None, max_length=500, description="Meeting location address")
    agenda: Optional[Dict[str, Any]] = Field(None, description="Meeting agenda as JSON")


class MeetingAttendanceBase(BaseModel):
    """Base attendance schema with common fields."""
    attendance_status: AttendanceStatusSchema = Field(
        AttendanceStatusSchema.PRESENT,
        description="Attendance status"
    )
    check_in_time: Optional[datetime] = Field(None, description="Check-in time")
    check_out_time: Optional[datetime] = Field(None, description="Check-out time") 
    notes: Optional[str] = Field(None, max_length=1000, description="Attendance notes")


# Create schemas
class MeetingCreate(MeetingBase):
    """Schema for creating a new meeting."""
    circle_id: int = Field(..., description="ID of the circle this meeting belongs to")
    facilitator_id: Optional[int] = Field(None, description="ID of the meeting facilitator (defaults to current user)")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate meeting title."""
        if not v or v.strip() == '':
            raise ValueError("title cannot be empty")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Weekly Circle Meeting",
                "description": "Regular weekly circle meeting for personal development",
                "scheduled_date": "2024-01-15T19:00:00Z",
                "circle_id": 1,
                "location_name": "Community Center",
                "location_address": "123 Main St, City, State",
                "agenda": {
                    "items": [
                        "Check-in round",
                        "Weekly goals review", 
                        "Discussion topic",
                        "Action items"
                    ],
                    "duration_minutes": 90
                }
            }
        }


class MeetingUpdate(BaseModel):
    """Schema for updating an existing meeting."""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Meeting title")
    description: Optional[str] = Field(None, max_length=2000, description="Meeting description")
    scheduled_date: Optional[datetime] = Field(None, description="Scheduled date and time")
    location_name: Optional[str] = Field(None, max_length=200, description="Meeting location name")
    location_address: Optional[str] = Field(None, max_length=500, description="Meeting location address")
    meeting_notes: Optional[str] = Field(None, max_length=5000, description="Meeting notes")
    agenda: Optional[Dict[str, Any]] = Field(None, description="Meeting agenda as JSON")

    @field_validator('title')
    @classmethod
    def validate_title(cls, v):
        """Validate meeting title."""
        if v is not None and (not v or v.strip() == ''):
            raise ValueError("title cannot be empty")
        return v.strip() if v else v


class MeetingAttendanceCreate(MeetingAttendanceBase):
    """Schema for creating attendance records."""
    user_id: int = Field(..., description="ID of the user")
    meeting_id: int = Field(..., description="ID of the meeting")


class MeetingAttendanceUpdate(BaseModel):
    """Schema for updating attendance records."""
    attendance_status: Optional[AttendanceStatusSchema] = Field(None, description="Attendance status")
    check_in_time: Optional[datetime] = Field(None, description="Check-in time")
    check_out_time: Optional[datetime] = Field(None, description="Check-out time")
    notes: Optional[str] = Field(None, max_length=1000, description="Attendance notes")


# Response schemas
class MeetingAttendanceResponse(MeetingAttendanceBase):
    """Schema for attendance response."""
    meeting_id: int = Field(..., description="Meeting ID")
    user_id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Created timestamp")
    updated_at: datetime = Field(..., description="Updated timestamp")

    class Config:
        from_attributes = True


class AttendanceSummary(BaseModel):
    """Schema for attendance summary."""
    present: int = Field(..., description="Number of present members")
    absent: int = Field(..., description="Number of absent members")
    excused: int = Field(..., description="Number of excused members")
    late: int = Field(..., description="Number of late members")


class MeetingResponse(MeetingBase):
    """Schema for meeting response."""
    id: int = Field(..., description="Meeting ID")
    circle_id: int = Field(..., description="Circle ID")
    facilitator_id: int = Field(..., description="Facilitator user ID")
    status: MeetingStatusSchema = Field(..., description="Meeting status")
    is_active: bool = Field(..., description="Whether the meeting is active")
    started_at: Optional[datetime] = Field(None, description="Meeting start time")
    ended_at: Optional[datetime] = Field(None, description="Meeting end time")
    meeting_notes: Optional[str] = Field(None, description="Meeting notes")
    duration_minutes: Optional[int] = Field(None, description="Meeting duration in minutes")
    attendance_summary: AttendanceSummary = Field(..., description="Attendance summary")
    created_at: datetime = Field(..., description="Created timestamp")
    updated_at: datetime = Field(..., description="Updated timestamp")

    class Config:
        from_attributes = True


class MeetingListResponse(BaseModel):
    """Schema for meeting list response."""
    meetings: List[MeetingResponse] = Field(..., description="List of meetings")
    total: int = Field(..., description="Total number of meetings")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")


class MeetingWithAttendance(MeetingResponse):
    """Schema for meeting response with full attendance records."""
    attendance_records: List[MeetingAttendanceResponse] = Field(..., description="Full attendance records")

    class Config:
        from_attributes = True


# Action schemas
class MeetingStatusUpdate(BaseModel):
    """Schema for updating meeting status."""
    status: MeetingStatusSchema = Field(..., description="New meeting status")
    notes: Optional[str] = Field(None, max_length=1000, description="Optional notes about status change")


class BulkAttendanceUpdate(BaseModel):
    """Schema for bulk attendance updates."""
    attendance_records: List[MeetingAttendanceUpdate] = Field(
        ..., 
        description="List of attendance updates"
    )

    @field_validator('attendance_records')
    @classmethod
    def validate_attendance_records(cls, v):
        """Validate attendance records list."""
        if not v:
            raise ValueError("attendance_records cannot be empty")
        if len(v) > 50:  # Reasonable limit for circle size
            raise ValueError("attendance_records cannot exceed 50 records")
        return v


# Search and filter schemas
class MeetingSearchParams(BaseModel):
    """Schema for meeting search parameters."""
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(10, ge=1, le=100, description="Items per page")
    circle_id: Optional[int] = Field(None, description="Filter by circle ID")
    facilitator_id: Optional[int] = Field(None, description="Filter by facilitator ID")
    status: Optional[MeetingStatusSchema] = Field(None, description="Filter by meeting status")
    date_from: Optional[datetime] = Field(None, description="Filter meetings from this date")
    date_to: Optional[datetime] = Field(None, description="Filter meetings to this date")
    search: Optional[str] = Field(None, max_length=100, description="Search in title and description")

    @field_validator('date_from', 'date_to')
    @classmethod
    def validate_dates(cls, v):
        """Validate date filters."""
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "per_page": 10,
                "circle_id": 1,
                "status": "completed",
                "date_from": "2024-01-01T00:00:00Z",
                "date_to": "2024-01-31T23:59:59Z",
                "search": "weekly meeting"
            }
        } 