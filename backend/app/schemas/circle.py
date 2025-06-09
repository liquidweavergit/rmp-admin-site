"""
Pydantic schemas for Circle API requests and responses
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

from ..models.circle import CircleStatus


class CircleCreate(BaseModel):
    """Schema for creating a new circle."""
    
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="Circle name (required, 1-100 characters)"
    )
    description: Optional[str] = Field(
        None, 
        max_length=1000, 
        description="Circle description (optional, max 1000 characters)"
    )
    capacity_min: Optional[int] = Field(
        2, 
        ge=2, 
        le=10, 
        description="Minimum circle capacity (2-10 members)"
    )
    capacity_max: Optional[int] = Field(
        8, 
        ge=2, 
        le=10, 
        description="Maximum circle capacity (2-10 members)"
    )
    location_name: Optional[str] = Field(
        None, 
        max_length=200, 
        description="Location name (optional, max 200 characters)"
    )
    location_address: Optional[str] = Field(
        None, 
        max_length=500, 
        description="Location address (optional, max 500 characters)"
    )
    meeting_schedule: Optional[Dict[str, Any]] = Field(
        None, 
        description="Meeting schedule as JSON object (e.g., {'day': 'Wednesday', 'time': '19:00', 'frequency': 'weekly'})"
    )
    
    @validator('capacity_max')
    def validate_capacity_max_greater_than_min(cls, v, values):
        """Ensure capacity_max is greater than or equal to capacity_min."""
        capacity_min = values.get('capacity_min', 2)
        if v < capacity_min:
            raise ValueError('capacity_max must be greater than or equal to capacity_min')
        return v
    
    @validator('name')
    def validate_name_not_empty(cls, v):
        """Ensure name is not just whitespace."""
        if not v or not v.strip():
            raise ValueError('name cannot be empty or whitespace')
        return v.strip()
    
    @validator('description')
    def validate_description_length(cls, v):
        """Ensure description is not just whitespace if provided."""
        if v is not None and v.strip() == '':
            return None
        return v
    
    @validator('location_name')
    def validate_location_name_length(cls, v):
        """Ensure location_name is not just whitespace if provided."""
        if v is not None and v.strip() == '':
            return None
        return v
    
    @validator('location_address')
    def validate_location_address_length(cls, v):
        """Ensure location_address is not just whitespace if provided."""
        if v is not None and v.strip() == '':
            return None
        return v

    class Config:
        schema_extra = {
            "example": {
                "name": "Men's Growth Circle",
                "description": "A supportive circle for personal growth and development",
                "capacity_min": 2,
                "capacity_max": 8,
                "location_name": "Community Center",
                "location_address": "123 Main St, City, State 12345",
                "meeting_schedule": {
                    "day": "Wednesday",
                    "time": "19:00",
                    "frequency": "weekly",
                    "duration": "2 hours"
                }
            }
        }


class CircleUpdate(BaseModel):
    """Schema for updating an existing circle."""
    
    name: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=100, 
        description="Circle name (1-100 characters)"
    )
    description: Optional[str] = Field(
        None, 
        max_length=1000, 
        description="Circle description (max 1000 characters)"
    )
    capacity_min: Optional[int] = Field(
        None, 
        ge=2, 
        le=10, 
        description="Minimum circle capacity (2-10 members)"
    )
    capacity_max: Optional[int] = Field(
        None, 
        ge=2, 
        le=10, 
        description="Maximum circle capacity (2-10 members)"
    )
    location_name: Optional[str] = Field(
        None, 
        max_length=200, 
        description="Location name (max 200 characters)"
    )
    location_address: Optional[str] = Field(
        None, 
        max_length=500, 
        description="Location address (max 500 characters)"
    )
    meeting_schedule: Optional[Dict[str, Any]] = Field(
        None, 
        description="Meeting schedule as JSON object"
    )
    status: Optional[CircleStatus] = Field(
        None, 
        description="Circle status"
    )
    is_active: Optional[bool] = Field(
        None, 
        description="Whether the circle is active"
    )
    
    @validator('name')
    def validate_name_not_empty(cls, v):
        """Ensure name is not just whitespace if provided."""
        if v is not None and (not v or not v.strip()):
            raise ValueError('name cannot be empty or whitespace')
        return v.strip() if v else v

    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "name": "Updated Circle Name",
                "description": "Updated description",
                "capacity_max": 10,
                "location_name": "New Location"
            }
        }


class CircleResponse(BaseModel):
    """Schema for circle response data."""
    
    id: int = Field(..., description="Circle ID")
    name: str = Field(..., description="Circle name")
    description: Optional[str] = Field(None, description="Circle description")
    facilitator_id: int = Field(..., description="Facilitator user ID")
    capacity_min: int = Field(..., description="Minimum circle capacity")
    capacity_max: int = Field(..., description="Maximum circle capacity")
    location_name: Optional[str] = Field(None, description="Location name")
    location_address: Optional[str] = Field(None, description="Location address")
    meeting_schedule: Optional[Dict[str, Any]] = Field(None, description="Meeting schedule")
    status: str = Field(..., description="Circle status")
    is_active: bool = Field(..., description="Whether the circle is active")
    current_member_count: int = Field(..., description="Current number of members")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Men's Growth Circle",
                "description": "A circle focused on personal growth",
                "facilitator_id": 123,
                "capacity_min": 2,
                "capacity_max": 8,
                "location_name": "Community Center",
                "location_address": "123 Main St, City, State",
                "meeting_schedule": {
                    "day": "Wednesday",
                    "time": "19:00",
                    "frequency": "weekly"
                },
                "status": "forming",
                "is_active": True,
                "current_member_count": 0,
                "created_at": "2024-06-08T18:30:00Z",
                "updated_at": "2024-06-08T18:30:00Z"
            }
        }


class CircleListResponse(BaseModel):
    """Schema for circle list response."""
    
    circles: List[CircleResponse] = Field(..., description="List of circles")
    total: int = Field(..., description="Total number of circles")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(10, description="Items per page")
    
    class Config:
        schema_extra = {
            "example": {
                "circles": [
                    {
                        "id": 1,
                        "name": "Men's Growth Circle",
                        "description": "A circle focused on personal growth",
                        "facilitator_id": 123,
                        "capacity_min": 2,
                        "capacity_max": 8,
                        "location_name": "Community Center",
                        "status": "forming",
                        "is_active": True,
                        "current_member_count": 0,
                        "created_at": "2024-06-08T18:30:00Z",
                        "updated_at": "2024-06-08T18:30:00Z"
                    }
                ],
                "total": 1,
                "page": 1,
                "per_page": 10
            }
        }


class CircleSearchParams(BaseModel):
    """Schema for circle search parameters."""
    
    page: int = Field(1, ge=1, description="Page number (starts at 1)")
    per_page: int = Field(10, ge=1, le=100, description="Items per page (1-100)")
    search: Optional[str] = Field(None, description="Search term for circle name or description")
    status: Optional[CircleStatus] = Field(None, description="Filter by circle status")
    facilitator_id: Optional[int] = Field(None, description="Filter by facilitator ID")
    location: Optional[str] = Field(None, description="Filter by location")
    
    class Config:
        use_enum_values = True
        schema_extra = {
            "example": {
                "page": 1,
                "per_page": 10,
                "search": "growth",
                "status": "active",
                "facilitator_id": 123
            }
        }


class CircleMemberAdd(BaseModel):
    """Schema for adding a member to a circle."""
    
    user_id: int = Field(..., description="User ID to add to the circle")
    payment_status: Optional[str] = Field(
        "pending", 
        description="Initial payment status for the membership"
    )
    
    @validator('payment_status')
    def validate_payment_status(cls, v):
        """Validate payment status is one of the allowed values."""
        if v is None:
            return "pending"  # Default value
        allowed_statuses = {"pending", "current", "overdue", "paused"}
        if v not in allowed_statuses:
            raise ValueError(f'payment_status must be one of: {", ".join(allowed_statuses)}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": 456,
                "payment_status": "pending"
            }
        }


class CircleMemberResponse(BaseModel):
    """Schema for circle member response."""
    
    user_id: int = Field(..., description="User ID")
    circle_id: int = Field(..., description="Circle ID")
    is_active: bool = Field(..., description="Whether membership is active")
    payment_status: str = Field(..., description="Payment status")
    joined_at: datetime = Field(..., description="When the user joined the circle")
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "user_id": 456,
                "circle_id": 1,
                "is_active": True,
                "payment_status": "current",
                "joined_at": "2024-06-08T18:30:00Z"
            }
        }


class CircleMemberTransfer(BaseModel):
    """Schema for transferring a member between circles."""
    
    target_circle_id: int = Field(..., description="Target circle ID for the transfer")
    reason: Optional[str] = Field(
        None, 
        max_length=500, 
        description="Reason for the transfer (optional, max 500 characters)"
    )
    
    @validator('reason')
    def validate_reason_length(cls, v):
        """Ensure reason is not just whitespace if provided."""
        if v is not None and v.strip() == '':
            return None
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "target_circle_id": 2,
                "reason": "Better fit for the member's schedule and goals"
            }
        }


class CircleMemberPaymentUpdate(BaseModel):
    """Schema for updating a member's payment status."""
    
    payment_status: str = Field(
        ..., 
        description="New payment status (pending, current, overdue, paused)"
    )
    
    @validator('payment_status')
    def validate_payment_status(cls, v):
        """Validate payment status is one of the allowed values."""
        allowed_statuses = {"pending", "current", "overdue", "paused"}
        if v not in allowed_statuses:
            raise ValueError(f'payment_status must be one of: {", ".join(allowed_statuses)}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "payment_status": "current"
            }
        }


class CircleMemberListResponse(BaseModel):
    """Schema for circle member list response."""
    
    members: List[CircleMemberResponse] = Field(..., description="List of circle members")
    total: int = Field(..., description="Total number of members")
    
    class Config:
        schema_extra = {
            "example": {
                "members": [
                    {
                        "user_id": 456,
                        "circle_id": 1,
                        "is_active": True,
                        "payment_status": "current",
                        "joined_at": "2024-06-08T18:30:00Z"
                    },
                    {
                        "user_id": 789,
                        "circle_id": 1,
                        "is_active": True,
                        "payment_status": "pending",
                        "joined_at": "2024-06-09T12:00:00Z"
                    }
                ],
                "total": 2
            }
        } 