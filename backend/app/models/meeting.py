"""
Meeting model for tracking circle meetings and attendance
"""
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from typing import Optional, Dict, Any, List

from ..core.database import Base
from ..core.exceptions import ValidationError


class MeetingStatus(enum.Enum):
    """Meeting status enumeration."""
    SCHEDULED = "scheduled"    # Meeting is scheduled but not started
    IN_PROGRESS = "in_progress"  # Meeting is currently in progress
    COMPLETED = "completed"    # Meeting has been completed
    CANCELLED = "cancelled"    # Meeting was cancelled


class AttendanceStatus(enum.Enum):
    """Attendance status enumeration."""
    PRESENT = "present"        # Member was present for the meeting
    ABSENT = "absent"          # Member was absent from the meeting
    EXCUSED = "excused"        # Member was absent but excused
    LATE = "late"              # Member arrived late but attended


class Meeting(Base):
    """
    Meeting model representing circle meetings for attendance tracking.
    
    Each meeting belongs to a circle and tracks when it occurred,
    who facilitated it, and attendance records for all members.
    """
    __tablename__ = "meetings"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Circle relationship
    circle_id = Column(Integer, ForeignKey("circles.id"), nullable=False, index=True)
    
    # Meeting information
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Meeting timing
    scheduled_date = Column(DateTime(timezone=True), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Facilitator for this specific meeting (may differ from circle facilitator)
    facilitator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Meeting location (can override circle's default location)
    location_name = Column(String(200), nullable=True)
    location_address = Column(String(500), nullable=True)
    
    # Meeting metadata
    meeting_notes = Column(Text, nullable=True)
    agenda = Column(JSON, nullable=True)  # Structured agenda as JSON
    
    # Status tracking
    status = Column(String(20), nullable=False, default=MeetingStatus.SCHEDULED.value)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    circle = relationship("Circle", foreign_keys=[circle_id])
    facilitator = relationship("User", foreign_keys=[facilitator_id])
    attendance_records = relationship("MeetingAttendance", back_populates="meeting", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        """Initialize Meeting with validation."""
        # Validate required fields
        if not kwargs.get('circle_id'):
            raise ValidationError("circle_id is required")
        if not kwargs.get('facilitator_id'):
            raise ValidationError("facilitator_id is required")
        if not kwargs.get('scheduled_date'):
            raise ValidationError("scheduled_date is required")
        
        # Validate title
        title = kwargs.get('title')
        if not title or title.strip() == '':
            raise ValidationError("title cannot be empty")
        if len(title) > 200:
            raise ValidationError("title cannot exceed 200 characters")
        
        # Validate description length
        description = kwargs.get('description')
        if description and len(description) > 2000:
            raise ValidationError("description cannot exceed 2000 characters")
        
        # Validate meeting notes length
        meeting_notes = kwargs.get('meeting_notes')
        if meeting_notes and len(meeting_notes) > 5000:
            raise ValidationError("meeting_notes cannot exceed 5000 characters")
        
        # Validate location fields
        location_name = kwargs.get('location_name')
        if location_name and len(location_name) > 200:
            raise ValidationError("location_name cannot exceed 200 characters")
        
        location_address = kwargs.get('location_address')
        if location_address and len(location_address) > 500:
            raise ValidationError("location_address cannot exceed 500 characters")
        
        # Set defaults if not provided
        if 'status' not in kwargs:
            kwargs['status'] = MeetingStatus.SCHEDULED.value
        if 'is_active' not in kwargs:
            kwargs['is_active'] = True
        
        super().__init__(**kwargs)
    
    @validates('title')
    def validate_title(self, key, title):
        """Validate meeting title."""
        if not title or title.strip() == '':
            raise ValidationError("title cannot be empty")
        if len(title) > 200:
            raise ValidationError("title cannot exceed 200 characters")
        return title
    
    @validates('status')
    def validate_status(self, key, status):
        """Validate meeting status."""
        valid_statuses = [s.value for s in MeetingStatus]
        if status not in valid_statuses:
            raise ValidationError(f"status must be one of: {', '.join(valid_statuses)}")
        return status
    
    @property
    def status_enum(self) -> MeetingStatus:
        """Get status as enum."""
        return MeetingStatus(self.status)
    
    @status_enum.setter
    def status_enum(self, status: MeetingStatus):
        """Set status from enum."""
        self.status = status.value
    
    @property
    def duration_minutes(self) -> Optional[int]:
        """Calculate meeting duration in minutes if both start and end times are set."""
        if self.started_at and self.ended_at:
            return int((self.ended_at - self.started_at).total_seconds() / 60)
        return None
    
    @property
    def attendance_summary(self) -> Dict[str, int]:
        """Get attendance summary counts."""
        if not hasattr(self, 'attendance_records') or not self.attendance_records:
            return {"present": 0, "absent": 0, "excused": 0, "late": 0}
        
        summary = {"present": 0, "absent": 0, "excused": 0, "late": 0}
        for record in self.attendance_records:
            if record.attendance_status in summary:
                summary[record.attendance_status] += 1
        return summary
    
    def start_meeting(self) -> None:
        """Start the meeting."""
        if self.status != MeetingStatus.SCHEDULED.value:
            raise ValidationError("Can only start scheduled meetings")
        self.status = MeetingStatus.IN_PROGRESS.value
        self.started_at = func.now()
    
    def end_meeting(self) -> None:
        """End the meeting."""
        if self.status != MeetingStatus.IN_PROGRESS.value:
            raise ValidationError("Can only end meetings that are in progress")
        self.status = MeetingStatus.COMPLETED.value
        self.ended_at = func.now()
    
    def cancel_meeting(self) -> None:
        """Cancel the meeting."""
        if self.status in [MeetingStatus.COMPLETED.value, MeetingStatus.CANCELLED.value]:
            raise ValidationError("Cannot cancel completed or already cancelled meetings")
        self.status = MeetingStatus.CANCELLED.value
    
    def __repr__(self):
        return f"<Meeting(id={self.id}, title='{self.title}', circle_id={self.circle_id}, status='{self.status}')>"


class MeetingAttendance(Base):
    """
    Meeting attendance model for tracking member attendance at meetings.
    
    Links users to meetings with their attendance status and optional notes.
    """
    __tablename__ = "meeting_attendance"
    
    # Composite primary key
    meeting_id = Column(Integer, ForeignKey("meetings.id"), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True, index=True)
    
    # Attendance information
    attendance_status = Column(String(20), nullable=False, default=AttendanceStatus.PRESENT.value)
    check_in_time = Column(DateTime(timezone=True), nullable=True)
    check_out_time = Column(DateTime(timezone=True), nullable=True)
    
    # Optional notes about attendance
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    meeting = relationship("Meeting", back_populates="attendance_records")
    user = relationship("User", foreign_keys=[user_id])
    
    def __init__(self, **kwargs):
        """Initialize MeetingAttendance with validation."""
        # Validate required fields
        if not kwargs.get('meeting_id'):
            raise ValidationError("meeting_id is required")
        if not kwargs.get('user_id'):
            raise ValidationError("user_id is required")
        
        # Validate notes length
        notes = kwargs.get('notes')
        if notes and len(notes) > 1000:
            raise ValidationError("notes cannot exceed 1000 characters")
        
        # Set defaults if not provided
        if 'attendance_status' not in kwargs:
            kwargs['attendance_status'] = AttendanceStatus.PRESENT.value
        
        super().__init__(**kwargs)
    
    @validates('attendance_status')
    def validate_attendance_status(self, key, attendance_status):
        """Validate attendance status."""
        valid_statuses = [s.value for s in AttendanceStatus]
        if attendance_status not in valid_statuses:
            raise ValidationError(f"attendance_status must be one of: {', '.join(valid_statuses)}")
        return attendance_status
    
    @property
    def attendance_status_enum(self) -> AttendanceStatus:
        """Get attendance status as enum."""
        return AttendanceStatus(self.attendance_status)
    
    @attendance_status_enum.setter
    def attendance_status_enum(self, status: AttendanceStatus):
        """Set attendance status from enum."""
        self.attendance_status = status.value
    
    def mark_present(self, check_in_time: Optional[DateTime] = None) -> None:
        """Mark member as present."""
        self.attendance_status = AttendanceStatus.PRESENT.value
        self.check_in_time = check_in_time or func.now()
    
    def mark_absent(self, notes: Optional[str] = None) -> None:
        """Mark member as absent."""
        self.attendance_status = AttendanceStatus.ABSENT.value
        if notes:
            self.notes = notes
    
    def mark_excused(self, notes: Optional[str] = None) -> None:
        """Mark member as excused absence."""
        self.attendance_status = AttendanceStatus.EXCUSED.value
        if notes:
            self.notes = notes
    
    def mark_late(self, check_in_time: Optional[DateTime] = None, notes: Optional[str] = None) -> None:
        """Mark member as late but present."""
        self.attendance_status = AttendanceStatus.LATE.value
        self.check_in_time = check_in_time or func.now()
        if notes:
            self.notes = notes
    
    def __repr__(self):
        return f"<MeetingAttendance(meeting_id={self.meeting_id}, user_id={self.user_id}, status='{self.attendance_status}')>" 