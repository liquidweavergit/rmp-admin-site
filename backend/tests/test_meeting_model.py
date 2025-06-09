"""
Tests for Meeting and MeetingAttendance models - Test-Driven Development approach
Testing meeting creation, validation, and attendance tracking before implementation
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, PropertyMock

from app.models.meeting import Meeting, MeetingAttendance, MeetingStatus, AttendanceStatus
from app.core.exceptions import ValidationError


class TestMeetingModel:
    """Test the Meeting model functionality."""

    def test_meeting_creation_with_valid_data(self):
        """Test meeting creation with valid data."""
        # Arrange
        meeting_data = {
            "circle_id": 1,
            "facilitator_id": 1,
            "title": "Weekly Circle Meeting",
            "description": "Regular weekly meeting for personal development",
            "scheduled_date": datetime.now() + timedelta(days=1)
        }
        
        # Act
        meeting = Meeting(**meeting_data)
        
        # Assert
        assert meeting.circle_id == 1
        assert meeting.facilitator_id == 1
        assert meeting.title == "Weekly Circle Meeting"
        assert meeting.description == "Regular weekly meeting for personal development"
        assert meeting.status == MeetingStatus.SCHEDULED.value
        assert meeting.is_active is True
        assert meeting.started_at is None
        assert meeting.ended_at is None

    def test_meeting_creation_with_minimal_data(self):
        """Test meeting creation with minimal required data."""
        # Arrange
        meeting_data = {
            "circle_id": 1,
            "facilitator_id": 1,
            "title": "Test Meeting",
            "scheduled_date": datetime.now() + timedelta(days=1)
        }
        
        # Act
        meeting = Meeting(**meeting_data)
        
        # Assert
        assert meeting.circle_id == 1
        assert meeting.facilitator_id == 1
        assert meeting.title == "Test Meeting"
        assert meeting.description is None
        assert meeting.status == MeetingStatus.SCHEDULED.value
        assert meeting.is_active is True

    def test_meeting_creation_validates_required_fields(self):
        """Test that required fields are validated."""
        # Test missing circle_id
        with pytest.raises(ValidationError, match="circle_id is required"):
            Meeting(facilitator_id=1, title="Test", scheduled_date=datetime.now())
        
        # Test missing facilitator_id
        with pytest.raises(ValidationError, match="facilitator_id is required"):
            Meeting(circle_id=1, title="Test", scheduled_date=datetime.now())
        
        # Test missing title
        with pytest.raises(ValidationError, match="title cannot be empty"):
            Meeting(circle_id=1, facilitator_id=1, scheduled_date=datetime.now())
        
        # Test missing scheduled_date
        with pytest.raises(ValidationError, match="scheduled_date is required"):
            Meeting(circle_id=1, facilitator_id=1, title="Test")

    def test_meeting_title_validation(self):
        """Test meeting title validation."""
        base_data = {
            "circle_id": 1,
            "facilitator_id": 1,
            "scheduled_date": datetime.now() + timedelta(days=1)
        }
        
        # Test empty title
        with pytest.raises(ValidationError, match="title cannot be empty"):
            Meeting(title="", **base_data)
        
        # Test whitespace-only title
        with pytest.raises(ValidationError, match="title cannot be empty"):
            Meeting(title="   ", **base_data)
        
        # Test title too long
        with pytest.raises(ValidationError, match="title cannot exceed 200 characters"):
            Meeting(title="A" * 201, **base_data)
        
        # Test valid title
        meeting = Meeting(title="Valid Title", **base_data)
        assert meeting.title == "Valid Title"

    def test_meeting_description_validation(self):
        """Test meeting description validation."""
        base_data = {
            "circle_id": 1,
            "facilitator_id": 1,
            "title": "Test Meeting",
            "scheduled_date": datetime.now() + timedelta(days=1)
        }
        
        # Test description too long
        with pytest.raises(ValidationError, match="description cannot exceed 2000 characters"):
            Meeting(description="A" * 2001, **base_data)
        
        # Test valid description
        meeting = Meeting(description="Valid description", **base_data)
        assert meeting.description == "Valid description"
        
        # Test None description
        meeting = Meeting(description=None, **base_data)
        assert meeting.description is None

    def test_meeting_location_validation(self):
        """Test meeting location field validation."""
        base_data = {
            "circle_id": 1,
            "facilitator_id": 1,
            "title": "Test Meeting",
            "scheduled_date": datetime.now() + timedelta(days=1)
        }
        
        # Test location_name too long
        with pytest.raises(ValidationError, match="location_name cannot exceed 200 characters"):
            Meeting(location_name="A" * 201, **base_data)
        
        # Test location_address too long
        with pytest.raises(ValidationError, match="location_address cannot exceed 500 characters"):
            Meeting(location_address="A" * 501, **base_data)
        
        # Test valid location fields
        meeting = Meeting(
            location_name="Community Center",
            location_address="123 Main St, City, State",
            **base_data
        )
        assert meeting.location_name == "Community Center"
        assert meeting.location_address == "123 Main St, City, State"

    def test_meeting_notes_validation(self):
        """Test meeting notes validation."""
        base_data = {
            "circle_id": 1,
            "facilitator_id": 1,
            "title": "Test Meeting",
            "scheduled_date": datetime.now() + timedelta(days=1)
        }
        
        # Test meeting_notes too long
        with pytest.raises(ValidationError, match="meeting_notes cannot exceed 5000 characters"):
            Meeting(meeting_notes="A" * 5001, **base_data)
        
        # Test valid meeting_notes
        meeting = Meeting(meeting_notes="Valid notes", **base_data)
        assert meeting.meeting_notes == "Valid notes"

    def test_meeting_status_enum_property(self):
        """Test meeting status enum property."""
        # Arrange
        meeting = Meeting(
            circle_id=1,
            facilitator_id=1,
            title="Test Meeting",
            scheduled_date=datetime.now() + timedelta(days=1)
        )
        
        # Test getter
        assert meeting.status_enum == MeetingStatus.SCHEDULED
        
        # Test setter
        meeting.status_enum = MeetingStatus.IN_PROGRESS
        assert meeting.status == MeetingStatus.IN_PROGRESS.value
        assert meeting.status_enum == MeetingStatus.IN_PROGRESS

    def test_meeting_duration_calculation(self):
        """Test meeting duration calculation."""
        # Arrange
        meeting = Meeting(
            circle_id=1,
            facilitator_id=1,
            title="Test Meeting",
            scheduled_date=datetime.now() + timedelta(days=1)
        )
        
        # Test no duration when times not set
        assert meeting.duration_minutes is None
        
        # Test duration calculation
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=90)
        meeting.started_at = start_time
        meeting.ended_at = end_time
        
        assert meeting.duration_minutes == 90

    def test_meeting_attendance_summary_empty(self):
        """Test attendance summary with no records."""
        # Arrange
        meeting = Meeting(
            circle_id=1,
            facilitator_id=1,
            title="Test Meeting",
            scheduled_date=datetime.now() + timedelta(days=1)
        )
        
        # Act & Assert
        summary = meeting.attendance_summary
        assert summary == {"present": 0, "absent": 0, "excused": 0, "late": 0}

    @pytest.mark.skip(reason="Complex SQLAlchemy relationship mocking - tested in integration tests")
    def test_meeting_attendance_summary_with_records(self):
        """Test attendance summary with mock records."""
        # This test is skipped because mocking SQLAlchemy relationships is complex
        # The attendance_summary functionality is tested in integration tests
        pass

    def test_meeting_start_meeting(self):
        """Test starting a meeting."""
        # Arrange
        meeting = Meeting(
            circle_id=1,
            facilitator_id=1,
            title="Test Meeting",
            scheduled_date=datetime.now() + timedelta(days=1)
        )
        
        # Act
        with patch('app.models.meeting.func.now') as mock_now:
            mock_time = datetime.now()
            mock_now.return_value = mock_time
            meeting.start_meeting()
        
        # Assert
        assert meeting.status == MeetingStatus.IN_PROGRESS.value
        assert meeting.started_at == mock_time

    def test_meeting_start_meeting_validation(self):
        """Test start meeting validation."""
        # Arrange
        meeting = Meeting(
            circle_id=1,
            facilitator_id=1,
            title="Test Meeting",
            scheduled_date=datetime.now() + timedelta(days=1),
            status=MeetingStatus.COMPLETED.value
        )
        
        # Act & Assert
        with pytest.raises(ValidationError, match="Can only start scheduled meetings"):
            meeting.start_meeting()

    def test_meeting_end_meeting(self):
        """Test ending a meeting."""
        # Arrange
        meeting = Meeting(
            circle_id=1,
            facilitator_id=1,
            title="Test Meeting",
            scheduled_date=datetime.now() + timedelta(days=1),
            status=MeetingStatus.IN_PROGRESS.value
        )
        
        # Act
        with patch('app.models.meeting.func.now') as mock_now:
            mock_time = datetime.now()
            mock_now.return_value = mock_time
            meeting.end_meeting()
        
        # Assert
        assert meeting.status == MeetingStatus.COMPLETED.value
        assert meeting.ended_at == mock_time

    def test_meeting_end_meeting_validation(self):
        """Test end meeting validation."""
        # Arrange
        meeting = Meeting(
            circle_id=1,
            facilitator_id=1,
            title="Test Meeting",
            scheduled_date=datetime.now() + timedelta(days=1),
            status=MeetingStatus.SCHEDULED.value
        )
        
        # Act & Assert
        with pytest.raises(ValidationError, match="Can only end meetings that are in progress"):
            meeting.end_meeting()

    def test_meeting_cancel_meeting(self):
        """Test cancelling a meeting."""
        # Arrange
        meeting = Meeting(
            circle_id=1,
            facilitator_id=1,
            title="Test Meeting",
            scheduled_date=datetime.now() + timedelta(days=1),
            status=MeetingStatus.SCHEDULED.value
        )
        
        # Act
        meeting.cancel_meeting()
        
        # Assert
        assert meeting.status == MeetingStatus.CANCELLED.value

    def test_meeting_cancel_meeting_validation(self):
        """Test cancel meeting validation."""
        # Test cancelling completed meeting
        meeting = Meeting(
            circle_id=1,
            facilitator_id=1,
            title="Test Meeting",
            scheduled_date=datetime.now() + timedelta(days=1),
            status=MeetingStatus.COMPLETED.value
        )
        
        with pytest.raises(ValidationError, match="Cannot cancel completed or already cancelled meetings"):
            meeting.cancel_meeting()
        
        # Test cancelling already cancelled meeting
        meeting.status = MeetingStatus.CANCELLED.value
        with pytest.raises(ValidationError, match="Cannot cancel completed or already cancelled meetings"):
            meeting.cancel_meeting()

    def test_meeting_repr(self):
        """Test meeting string representation."""
        # Arrange
        meeting = Meeting(
            circle_id=1,
            facilitator_id=1,
            title="Test Meeting",
            scheduled_date=datetime.now() + timedelta(days=1)
        )
        meeting.id = 123
        
        # Act & Assert
        expected = "<Meeting(id=123, title='Test Meeting', circle_id=1, status='scheduled')>"
        assert repr(meeting) == expected


class TestMeetingAttendanceModel:
    """Test the MeetingAttendance model functionality."""

    def test_attendance_creation_with_valid_data(self):
        """Test attendance creation with valid data."""
        # Arrange
        attendance_data = {
            "meeting_id": 1,
            "user_id": 1,
            "attendance_status": AttendanceStatus.PRESENT.value,
            "check_in_time": datetime.now(),
            "notes": "Arrived on time"
        }
        
        # Act
        attendance = MeetingAttendance(**attendance_data)
        
        # Assert
        assert attendance.meeting_id == 1
        assert attendance.user_id == 1
        assert attendance.attendance_status == AttendanceStatus.PRESENT.value
        assert attendance.notes == "Arrived on time"

    def test_attendance_creation_with_minimal_data(self):
        """Test attendance creation with minimal required data."""
        # Arrange
        attendance_data = {
            "meeting_id": 1,
            "user_id": 1
        }
        
        # Act
        attendance = MeetingAttendance(**attendance_data)
        
        # Assert
        assert attendance.meeting_id == 1
        assert attendance.user_id == 1
        assert attendance.attendance_status == AttendanceStatus.PRESENT.value
        assert attendance.check_in_time is None
        assert attendance.notes is None

    def test_attendance_creation_validates_required_fields(self):
        """Test that required fields are validated."""
        # Test missing meeting_id
        with pytest.raises(ValidationError, match="meeting_id is required"):
            MeetingAttendance(user_id=1)
        
        # Test missing user_id
        with pytest.raises(ValidationError, match="user_id is required"):
            MeetingAttendance(meeting_id=1)

    def test_attendance_notes_validation(self):
        """Test attendance notes validation."""
        base_data = {
            "meeting_id": 1,
            "user_id": 1
        }
        
        # Test notes too long
        with pytest.raises(ValidationError, match="notes cannot exceed 1000 characters"):
            MeetingAttendance(notes="A" * 1001, **base_data)
        
        # Test valid notes
        attendance = MeetingAttendance(notes="Valid notes", **base_data)
        assert attendance.notes == "Valid notes"

    def test_attendance_status_validation(self):
        """Test attendance status validation."""
        # Arrange
        attendance = MeetingAttendance(meeting_id=1, user_id=1)
        
        # Test valid status
        attendance.attendance_status = AttendanceStatus.LATE.value
        assert attendance.attendance_status == AttendanceStatus.LATE.value
        
        # Test invalid status (this would be caught by SQLAlchemy enum validation)
        # We test the validator method directly
        with pytest.raises(ValidationError, match="attendance_status must be one of"):
            attendance.validate_attendance_status("attendance_status", "invalid_status")

    def test_attendance_status_enum_property(self):
        """Test attendance status enum property."""
        # Arrange
        attendance = MeetingAttendance(meeting_id=1, user_id=1)
        
        # Test getter
        assert attendance.attendance_status_enum == AttendanceStatus.PRESENT
        
        # Test setter
        attendance.attendance_status_enum = AttendanceStatus.LATE
        assert attendance.attendance_status == AttendanceStatus.LATE.value
        assert attendance.attendance_status_enum == AttendanceStatus.LATE

    def test_attendance_mark_present(self):
        """Test marking attendance as present."""
        # Arrange
        attendance = MeetingAttendance(meeting_id=1, user_id=1)
        
        # Act
        with patch('app.models.meeting.func.now') as mock_now:
            mock_time = datetime.now()
            mock_now.return_value = mock_time
            attendance.mark_present()
        
        # Assert
        assert attendance.attendance_status == AttendanceStatus.PRESENT.value
        assert attendance.check_in_time == mock_time

    def test_attendance_mark_present_with_time(self):
        """Test marking attendance as present with specific time."""
        # Arrange
        attendance = MeetingAttendance(meeting_id=1, user_id=1)
        check_in_time = datetime.now()
        
        # Act
        attendance.mark_present(check_in_time)
        
        # Assert
        assert attendance.attendance_status == AttendanceStatus.PRESENT.value
        assert attendance.check_in_time == check_in_time

    def test_attendance_mark_absent(self):
        """Test marking attendance as absent."""
        # Arrange
        attendance = MeetingAttendance(meeting_id=1, user_id=1)
        
        # Act
        attendance.mark_absent("Family emergency")
        
        # Assert
        assert attendance.attendance_status == AttendanceStatus.ABSENT.value
        assert attendance.notes == "Family emergency"

    def test_attendance_mark_excused(self):
        """Test marking attendance as excused."""
        # Arrange
        attendance = MeetingAttendance(meeting_id=1, user_id=1)
        
        # Act
        attendance.mark_excused("Pre-approved absence")
        
        # Assert
        assert attendance.attendance_status == AttendanceStatus.EXCUSED.value
        assert attendance.notes == "Pre-approved absence"

    def test_attendance_mark_late(self):
        """Test marking attendance as late."""
        # Arrange
        attendance = MeetingAttendance(meeting_id=1, user_id=1)
        
        # Act
        with patch('app.models.meeting.func.now') as mock_now:
            mock_time = datetime.now()
            mock_now.return_value = mock_time
            attendance.mark_late(notes="Traffic delay")
        
        # Assert
        assert attendance.attendance_status == AttendanceStatus.LATE.value
        assert attendance.check_in_time == mock_time
        assert attendance.notes == "Traffic delay"

    def test_attendance_mark_late_with_time(self):
        """Test marking attendance as late with specific time."""
        # Arrange
        attendance = MeetingAttendance(meeting_id=1, user_id=1)
        check_in_time = datetime.now()
        
        # Act
        attendance.mark_late(check_in_time, "Traffic delay")
        
        # Assert
        assert attendance.attendance_status == AttendanceStatus.LATE.value
        assert attendance.check_in_time == check_in_time
        assert attendance.notes == "Traffic delay"

    def test_attendance_repr(self):
        """Test attendance string representation."""
        # Arrange
        attendance = MeetingAttendance(
            meeting_id=1,
            user_id=2,
            attendance_status=AttendanceStatus.PRESENT.value
        )
        
        # Act & Assert
        expected = "<MeetingAttendance(meeting_id=1, user_id=2, status='present')>"
        assert repr(attendance) == expected


class TestMeetingBusinessLogic:
    """Test meeting business logic and edge cases."""

    def test_meeting_agenda_json_field(self):
        """Test meeting agenda JSON field handling."""
        # Arrange
        agenda = {
            "items": [
                "Check-in round",
                "Weekly goals review",
                "Discussion topic",
                "Action items"
            ],
            "duration_minutes": 90,
            "facilitator_notes": "Focus on goal accountability"
        }
        
        meeting = Meeting(
            circle_id=1,
            facilitator_id=1,
            title="Test Meeting",
            scheduled_date=datetime.now() + timedelta(days=1),
            agenda=agenda
        )
        
        # Act & Assert
        assert meeting.agenda == agenda
        assert meeting.agenda["items"] == agenda["items"]
        assert meeting.agenda["duration_minutes"] == 90

    def test_meeting_status_transitions(self):
        """Test valid meeting status transitions."""
        # Arrange
        meeting = Meeting(
            circle_id=1,
            facilitator_id=1,
            title="Test Meeting",
            scheduled_date=datetime.now() + timedelta(days=1)
        )
        
        # Test scheduled -> in_progress -> completed
        assert meeting.status == MeetingStatus.SCHEDULED.value
        
        meeting.start_meeting()
        assert meeting.status == MeetingStatus.IN_PROGRESS.value
        
        meeting.end_meeting()
        assert meeting.status == MeetingStatus.COMPLETED.value
        
        # Test scheduled -> cancelled
        meeting2 = Meeting(
            circle_id=1,
            facilitator_id=1,
            title="Test Meeting 2",
            scheduled_date=datetime.now() + timedelta(days=1)
        )
        
        meeting2.cancel_meeting()
        assert meeting2.status == MeetingStatus.CANCELLED.value

    def test_meeting_with_location_override(self):
        """Test meeting with location different from circle default."""
        # Arrange
        meeting = Meeting(
            circle_id=1,
            facilitator_id=1,
            title="Special Location Meeting",
            scheduled_date=datetime.now() + timedelta(days=1),
            location_name="Special Venue",
            location_address="456 Special St, City, State"
        )
        
        # Act & Assert
        assert meeting.location_name == "Special Venue"
        assert meeting.location_address == "456 Special St, City, State"

    def test_meeting_facilitator_different_from_circle(self):
        """Test meeting with facilitator different from circle facilitator."""
        # Arrange
        meeting = Meeting(
            circle_id=1,
            facilitator_id=2,  # Different from circle facilitator
            title="Guest Facilitated Meeting",
            scheduled_date=datetime.now() + timedelta(days=1)
        )
        
        # Act & Assert
        assert meeting.facilitator_id == 2
        assert meeting.circle_id == 1

    def test_attendance_check_in_check_out_workflow(self):
        """Test complete attendance workflow with check-in and check-out."""
        # Arrange
        attendance = MeetingAttendance(meeting_id=1, user_id=1)
        
        # Act - Check in
        check_in_time = datetime.now()
        attendance.mark_present(check_in_time)
        
        # Later - Check out
        check_out_time = check_in_time + timedelta(hours=1, minutes=30)
        attendance.check_out_time = check_out_time
        
        # Assert
        assert attendance.attendance_status == AttendanceStatus.PRESENT.value
        assert attendance.check_in_time == check_in_time
        assert attendance.check_out_time == check_out_time 