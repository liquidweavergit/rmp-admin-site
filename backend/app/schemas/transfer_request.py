"""
Pydantic schemas for transfer request operations.
Defines request/response models for the transfer request API endpoints.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator

from app.models.transfer_request import TransferRequestStatus


class TransferRequestCreate(BaseModel):
    """Schema for creating a transfer request."""
    
    target_circle_id: int = Field(..., description="ID of the target circle for transfer", gt=0)
    reason: Optional[str] = Field(
        None, 
        max_length=1000, 
        description="Optional reason for the transfer request"
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
                "reason": "Looking for a circle with better schedule compatibility"
            }
        }


class TransferRequestResponse(BaseModel):
    """Schema for transfer request response."""
    
    id: int
    requester_id: int
    source_circle_id: int
    target_circle_id: int
    reason: Optional[str]
    status: TransferRequestStatus
    created_at: datetime
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "requester_id": 123,
                "source_circle_id": 1,
                "target_circle_id": 2,
                "reason": "Looking for better schedule fit",
                "status": "pending",
                "created_at": "2024-12-20T10:00:00Z",
                "reviewed_by_id": None,
                "reviewed_at": None,
                "review_notes": None
            }
        }


class TransferRequestListResponse(BaseModel):
    """Schema for listing transfer requests."""
    
    requests: List[TransferRequestResponse]
    total: int
    
    class Config:
        schema_extra = {
            "example": {
                "requests": [
                    {
                        "id": 1,
                        "requester_id": 123,
                        "source_circle_id": 1,
                        "target_circle_id": 2,
                        "reason": "Better schedule fit",
                        "status": "pending",
                        "created_at": "2024-12-20T10:00:00Z",
                        "reviewed_by_id": None,
                        "reviewed_at": None,
                        "review_notes": None
                    }
                ],
                "total": 1
            }
        }


class TransferRequestReview(BaseModel):
    """Schema for reviewing (approving/denying) a transfer request."""
    
    review_notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional notes for the review decision"
    )
    execute_transfer: bool = Field(
        False,
        description="Whether to execute the transfer immediately upon approval"
    )
    
    @validator('review_notes')
    def validate_review_notes_length(cls, v):
        """Ensure review notes is not just whitespace if provided."""
        if v is not None and v.strip() == '':
            return None
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "review_notes": "Approved - member would be a good fit for the target circle",
                "execute_transfer": True
            }
        }


class TransferRequestStats(BaseModel):
    """Schema for transfer request statistics."""
    
    pending: int
    approved: int
    denied: int
    cancelled: int
    total: int
    
    class Config:
        schema_extra = {
            "example": {
                "pending": 5,
                "approved": 12,
                "denied": 3,
                "cancelled": 1,
                "total": 21
            }
        }


class TransferRequestDetailResponse(TransferRequestResponse):
    """Extended schema for detailed transfer request response with related data."""
    
    requester_name: Optional[str] = None
    source_circle_name: Optional[str] = None
    target_circle_name: Optional[str] = None
    reviewer_name: Optional[str] = None
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "requester_id": 123,
                "source_circle_id": 1,
                "target_circle_id": 2,
                "reason": "Looking for better schedule fit",
                "status": "approved",
                "created_at": "2024-12-20T10:00:00Z",
                "reviewed_by_id": 456,
                "reviewed_at": "2024-12-20T14:30:00Z",
                "review_notes": "Approved - good fit for target circle",
                "requester_name": "John Doe",
                "source_circle_name": "Alpha Circle",
                "target_circle_name": "Beta Circle",
                "reviewer_name": "Jane Smith"
            }
        } 