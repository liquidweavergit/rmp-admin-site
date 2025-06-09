"""
Circle model for managing men's circles with capacity constraints (2-10 members)
"""
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from typing import Optional, Dict, Any

from ..core.database import Base
from ..core.exceptions import ValidationError, CapacityExceeded


class CircleStatus(enum.Enum):
    """Circle status enumeration."""
    FORMING = "forming"        # Circle is being formed, accepting members
    ACTIVE = "active"          # Circle is active and meeting regularly  
    PAUSED = "paused"          # Circle is temporarily paused
    CLOSED = "closed"          # Circle has been permanently closed


class Circle(Base):
    """
    Circle model representing men's circles for personal development.
    
    Enforces capacity constraints of 2-10 members as per product specification.
    Supports flexible meeting schedules and location management.
    """
    __tablename__ = "circles"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic circle information
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Facilitator relationship
    facilitator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Capacity constraints (2-10 members as per product brief)
    capacity_min = Column(Integer, nullable=False, default=2)
    capacity_max = Column(Integer, nullable=False, default=8)
    
    # Location information
    location_name = Column(String(200), nullable=True)
    location_address = Column(String(500), nullable=True)
    # location_point for PostGIS will be added in future enhancement
    
    # Meeting schedule (stored as JSON)
    meeting_schedule = Column(JSON, nullable=True)
    
    # Circle status and activity
    status = Column(String(20), nullable=False, default=CircleStatus.FORMING.value)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    facilitator = relationship("User", foreign_keys=[facilitator_id])
    members = relationship("CircleMembership", back_populates="circle")
    
    def __init__(self, **kwargs):
        """Initialize Circle with validation."""
        # Validate required fields
        if not kwargs.get('facilitator_id'):
            raise ValidationError("facilitator_id is required")
        
        # Validate name
        name = kwargs.get('name')
        if not name or name.strip() == '':
            raise ValidationError("name cannot be empty")
        if len(name) > 100:
            raise ValidationError("name cannot exceed 100 characters")
        
        # Validate description length
        description = kwargs.get('description')
        if description and len(description) > 1000:
            raise ValidationError("description cannot exceed 1000 characters")
        
        # Validate location fields
        location_name = kwargs.get('location_name')
        if location_name and len(location_name) > 200:
            raise ValidationError("location_name cannot exceed 200 characters")
        
        location_address = kwargs.get('location_address')
        if location_address and len(location_address) > 500:
            raise ValidationError("location_address cannot exceed 500 characters")
        
        # Set defaults if not provided
        if 'capacity_min' not in kwargs:
            kwargs['capacity_min'] = 2
        if 'capacity_max' not in kwargs:
            kwargs['capacity_max'] = 8
        if 'status' not in kwargs:
            kwargs['status'] = CircleStatus.FORMING.value
        if 'is_active' not in kwargs:
            kwargs['is_active'] = True
        
        # Validate capacity constraints
        capacity_min = kwargs.get('capacity_min', 2)
        capacity_max = kwargs.get('capacity_max', 8)
        
        if capacity_min < 2:
            raise ValidationError("capacity_min must be at least 2")
        if capacity_max > 10:
            raise ValidationError("capacity_max cannot exceed 10")
        if capacity_min > capacity_max:
            raise ValidationError("capacity_min cannot be greater than capacity_max")
        
        super().__init__(**kwargs)
    
    @validates('name')
    def validate_name(self, key, name):
        """Validate circle name."""
        if not name or name.strip() == '':
            raise ValidationError("name cannot be empty")
        if len(name) > 100:
            raise ValidationError("name cannot exceed 100 characters")
        return name
    
    @validates('capacity_min')
    def validate_capacity_min(self, key, capacity_min):
        """Validate minimum capacity."""
        if capacity_min < 2:
            raise ValidationError("capacity_min must be at least 2")
        return capacity_min
    
    @validates('capacity_max')
    def validate_capacity_max(self, key, capacity_max):
        """Validate maximum capacity."""
        if capacity_max > 10:
            raise ValidationError("capacity_max cannot exceed 10")
        return capacity_max
    
    @property
    def current_member_count(self) -> int:
        """Get current number of members in the circle."""
        # For testing, allow mock member count
        if hasattr(self, '_current_member_count'):
            return self._current_member_count
        # Count active memberships
        if hasattr(self, 'members') and self.members:
            return len([m for m in self.members if m.is_active])
        return 0
    
    @property
    def status_enum(self) -> CircleStatus:
        """Get status as enum."""
        return CircleStatus(self.status)
    
    @status_enum.setter
    def status_enum(self, status: CircleStatus):
        """Set status from enum."""
        self.status = status.value
    
    def can_accept_members(self) -> bool:
        """Check if circle can accept new members."""
        return self.current_member_count < self.capacity_max
    
    def is_facilitator(self, user_id: int) -> bool:
        """Check if user is the facilitator of this circle."""
        return self.facilitator_id == user_id
    
    def is_capacity_valid(self) -> bool:
        """Validate that capacity settings are within business rules."""
        return (
            2 <= self.capacity_min <= 10 and
            2 <= self.capacity_max <= 10 and
            self.capacity_min <= self.capacity_max
        )
    
    def validate_member_addition(self) -> None:
        """Validate that a new member can be added to the circle."""
        if not self.can_accept_members():
            raise CapacityExceeded(
                resource_type="Circle",
                current=self.current_member_count,
                maximum=self.capacity_max
            )
    
    def activate(self) -> None:
        """Activate the circle."""
        self.status = CircleStatus.ACTIVE.value
        self.is_active = True
    
    def pause(self) -> None:
        """Pause the circle temporarily."""
        self.status = CircleStatus.PAUSED.value
    
    def close(self) -> None:
        """Permanently close the circle."""
        self.status = CircleStatus.CLOSED.value
        self.is_active = False
    
    def __repr__(self):
        return f"<Circle(id={self.id}, name='{self.name}', facilitator_id={self.facilitator_id}, status='{self.status}')>" 