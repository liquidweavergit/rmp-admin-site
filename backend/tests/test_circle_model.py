"""
Tests for Circle model - Test-Driven Development approach
Testing circle business rules and capacity constraints before implementation
"""
import pytest
from unittest.mock import Mock
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from app.models.circle import Circle, CircleStatus
from app.core.exceptions import CapacityExceeded, ValidationError


class TestCircleModel:
    """Test the Circle model implementation."""

    def test_circle_creation_with_valid_data(self):
        """Test circle can be created with valid data."""
        # Arrange
        circle_data = {
            "name": "Men's Growth Circle",
            "description": "A supportive circle for personal development",
            "facilitator_id": 1,
            "capacity_min": 4,
            "capacity_max": 8,
            "location_name": "Community Center",
            "location_address": "123 Main St, City, State"
        }
        
        # Act
        circle = Circle(**circle_data)
        
        # Assert
        assert circle.name == "Men's Growth Circle"
        assert circle.description == "A supportive circle for personal development"
        assert circle.facilitator_id == 1
        assert circle.capacity_min == 4
        assert circle.capacity_max == 8
        assert circle.location_name == "Community Center"
        assert circle.location_address == "123 Main St, City, State"
        assert circle.status == CircleStatus.FORMING.value
        assert circle.is_active is True

    def test_circle_capacity_constraints_validation(self):
        """Test capacity constraints are enforced (2-10 members)."""
        # Test minimum capacity constraint
        with pytest.raises(ValidationError) as exc_info:
            Circle(
                name="Test Circle",
                facilitator_id=1,
                capacity_min=1,  # Below minimum of 2
                capacity_max=5
            )
        assert "capacity_min must be at least 2" in str(exc_info.value)
        
        # Test maximum capacity constraint
        with pytest.raises(ValidationError) as exc_info:
            Circle(
                name="Test Circle",
                facilitator_id=1,
                capacity_min=2,
                capacity_max=12  # Above maximum of 10
            )
        assert "capacity_max cannot exceed 10" in str(exc_info.value)
        
        # Test min > max constraint
        with pytest.raises(ValidationError) as exc_info:
            Circle(
                name="Test Circle",
                facilitator_id=1,
                capacity_min=8,
                capacity_max=6  # Min greater than max
            )
        assert "capacity_min cannot be greater than capacity_max" in str(exc_info.value)

    def test_circle_name_validation(self):
        """Test circle name validation requirements."""
        # Test empty name
        with pytest.raises(ValidationError) as exc_info:
            Circle(name="", facilitator_id=1)
        assert "name cannot be empty" in str(exc_info.value)
        
        # Test name too long
        long_name = "A" * 101  # Over 100 character limit
        with pytest.raises(ValidationError) as exc_info:
            Circle(name=long_name, facilitator_id=1)
        assert "name cannot exceed 100 characters" in str(exc_info.value)

    def test_circle_default_values(self):
        """Test default values are set correctly."""
        # Act - Create circle with minimal required data
        circle = Circle(name="Test Circle", facilitator_id=1)
        
        # Assert - Check defaults
        assert circle.capacity_min == 2  # Default minimum
        assert circle.capacity_max == 8   # Default capacity
        assert circle.status == CircleStatus.FORMING.value
        assert circle.is_active is True
        assert circle.description is None  # Optional field
        assert circle.location_name is None  # Optional field
        assert circle.location_address is None  # Optional field

    def test_circle_status_transitions(self):
        """Test valid circle status transitions."""
        # Arrange
        circle = Circle(name="Test Circle", facilitator_id=1)
        
        # Test FORMING -> ACTIVE
        circle.status = CircleStatus.ACTIVE.value
        assert circle.status == CircleStatus.ACTIVE.value
        
        # Test ACTIVE -> PAUSED
        circle.status = CircleStatus.PAUSED.value
        assert circle.status == CircleStatus.PAUSED.value
        
        # Test PAUSED -> ACTIVE
        circle.status = CircleStatus.ACTIVE.value
        assert circle.status == CircleStatus.ACTIVE.value
        
        # Test ACTIVE -> CLOSED
        circle.status = CircleStatus.CLOSED.value
        assert circle.status == CircleStatus.CLOSED.value

    def test_circle_meeting_schedule_validation(self):
        """Test meeting schedule JSON field validation."""
        # Arrange - Valid meeting schedule
        valid_schedule = {
            "day": "Wednesday",
            "time": "19:00",
            "frequency": "weekly",
            "timezone": "America/New_York"
        }
        
        # Act
        circle = Circle(
            name="Test Circle",
            facilitator_id=1,
            meeting_schedule=valid_schedule
        )
        
        # Assert
        assert circle.meeting_schedule == valid_schedule
        assert circle.meeting_schedule["day"] == "Wednesday"
        assert circle.meeting_schedule["time"] == "19:00"

    def test_circle_string_representation(self):
        """Test circle string representation."""
        # Arrange
        circle = Circle(
            id=1,
            name="Men's Growth Circle",
            facilitator_id=2
        )
        
        # Act
        repr_str = repr(circle)
        
        # Assert
        assert "Circle(id=1" in repr_str
        assert "name='Men's Growth Circle'" in repr_str
        assert "facilitator_id=2" in repr_str

    def test_circle_current_member_count_property(self):
        """Test current member count calculation."""
        # This will be implemented when CircleMembership relationship is added
        # For now, test that the property exists and returns 0 for new circles
        circle = Circle(name="Test Circle", facilitator_id=1)
        
        # Should return 0 for new circle with no members
        assert circle.current_member_count == 0

    def test_circle_can_accept_members_method(self):
        """Test method to check if circle can accept new members."""
        # Arrange
        circle = Circle(
            name="Test Circle",
            facilitator_id=1,
            capacity_max=5
        )
        
        # Test with space available
        assert circle.can_accept_members() is True
        
        # Mock current member count at capacity
        circle._current_member_count = 5
        assert circle.can_accept_members() is False

    def test_circle_is_facilitator_method(self):
        """Test method to check if user is the circle facilitator."""
        # Arrange
        circle = Circle(name="Test Circle", facilitator_id=1)
        
        # Test facilitator check
        assert circle.is_facilitator(1) is True
        assert circle.is_facilitator(2) is False

    def test_circle_location_validation(self):
        """Test location field validation."""
        # Test location name too long
        long_location = "A" * 201  # Over 200 character limit
        with pytest.raises(ValidationError):
            Circle(
                name="Test Circle",
                facilitator_id=1,
                location_name=long_location
            )
        
        # Test location address too long
        long_address = "A" * 501  # Over 500 character limit
        with pytest.raises(ValidationError):
            Circle(
                name="Test Circle",
                facilitator_id=1,
                location_address=long_address
            )

    def test_circle_description_validation(self):
        """Test description field validation."""
        # Test description too long
        long_description = "A" * 1001  # Over 1000 character limit
        with pytest.raises(ValidationError):
            Circle(
                name="Test Circle",
                facilitator_id=1,
                description=long_description
            )

    def test_circle_facilitator_id_required(self):
        """Test that facilitator_id is required."""
        with pytest.raises(ValidationError) as exc_info:
            Circle(name="Test Circle")  # Missing facilitator_id
        assert "facilitator_id is required" in str(exc_info.value)

    def test_circle_timestamps_are_set(self):
        """Test that created_at and updated_at timestamps are properly set."""
        # Arrange
        circle = Circle(name="Test Circle", facilitator_id=1)
        
        # Note: In actual implementation, these would be set by SQLAlchemy
        # This test validates the model structure exists
        assert hasattr(circle, 'created_at')
        assert hasattr(circle, 'updated_at')


class TestCircleBusinessLogic:
    """Test Circle business logic and rules."""

    def test_circle_capacity_business_rules(self):
        """Test business rules around circle capacity."""
        # Arrange
        circle = Circle(
            name="Test Circle",
            facilitator_id=1,
            capacity_min=4,
            capacity_max=8
        )
        
        # Test capacity within bounds
        assert circle.is_capacity_valid() is True
        
        # Test capacity at minimum edge case
        circle.capacity_min = 2
        circle.capacity_max = 2
        assert circle.is_capacity_valid() is True
        
        # Test capacity at maximum edge case
        circle.capacity_min = 10
        circle.capacity_max = 10
        assert circle.is_capacity_valid() is True

    def test_circle_member_capacity_enforcement(self):
        """Test that member capacity is enforced."""
        # This test will be expanded when CircleMembership is implemented
        circle = Circle(
            name="Test Circle",
            facilitator_id=1,
            capacity_max=3
        )
        
        # Mock adding members to capacity
        circle._current_member_count = 3
        
        # Should not accept more members
        assert circle.can_accept_members() is False
        
        # Should raise exception when trying to add member
        with pytest.raises(CapacityExceeded) as exc_info:
            circle.validate_member_addition()
        assert "Circle capacity exceeded" in str(exc_info.value)

    def test_circle_status_business_rules(self):
        """Test business rules for circle status changes."""
        circle = Circle(name="Test Circle", facilitator_id=1)
        
        # New circle should be FORMING
        assert circle.status == CircleStatus.FORMING.value
        
        # Should be able to activate circle
        circle.activate()
        assert circle.status == CircleStatus.ACTIVE.value
        
        # Should be able to pause active circle
        circle.pause()
        assert circle.status == CircleStatus.PAUSED.value
        
        # Should be able to close circle
        circle.close()
        assert circle.status == CircleStatus.CLOSED.value
        assert circle.is_active is False

    def test_circle_meeting_schedule_business_rules(self):
        """Test business rules for meeting schedules."""
        # Valid schedule formats should be accepted
        valid_schedules = [
            {
                "day": "Wednesday",
                "time": "19:00",
                "frequency": "weekly"
            },
            {
                "day": "Tuesday",
                "time": "18:30",
                "frequency": "bi-weekly"
            },
            {
                "day": "Saturday",
                "time": "10:00",
                "frequency": "monthly"
            }
        ]
        
        for schedule in valid_schedules:
            circle = Circle(
                name="Test Circle",
                facilitator_id=1,
                meeting_schedule=schedule
            )
            assert circle.meeting_schedule == schedule


# Integration tests will be added when database fixtures are available 