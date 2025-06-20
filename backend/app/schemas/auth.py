"""
Authentication schemas for request/response validation
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, max_length=128, description="User's password")
    first_name: str = Field(..., min_length=1, max_length=100, description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="User's last name")
    phone: Optional[str] = Field(None, max_length=20, description="User's phone number")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password complexity"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, and one digit')
        
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format"""
        if v is None:
            return v
        
        # Remove non-digit characters for validation
        digits_only = ''.join(filter(str.isdigit, v))
        
        if len(digits_only) < 10:
            raise ValueError('Phone number must have at least 10 digits')
        
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class UserResponse(BaseModel):
    """Schema for user data in responses"""
    id: int = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    phone: Optional[str] = Field(None, description="User's phone number")
    is_active: bool = Field(..., description="Whether the user account is active")
    is_verified: bool = Field(..., description="Whether the user is verified")
    email_verified: bool = Field(..., description="Whether the email is verified")
    phone_verified: bool = Field(..., description="Whether the phone is verified")
    created_at: datetime = Field(..., description="When the user account was created")
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for authentication token response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str = Field(..., description="Valid refresh token")


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr = Field(..., description="Email address for password reset")


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        """Validate password complexity"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        
        if not (has_upper and has_lower and has_digit):
            raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, and one digit')
        
        return v


class LogoutRequest(BaseModel):
    """Schema for logout request"""
    refresh_token: str = Field(..., description="Refresh token to invalidate")


class EmailVerificationRequest(BaseModel):
    """Schema for email verification request"""
    token: str = Field(..., description="Email verification token")


class PhoneVerificationRequest(BaseModel):
    """Schema for phone verification request"""
    phone: str = Field(..., description="Phone number to verify")


class PhoneVerificationConfirm(BaseModel):
    """Schema for phone verification confirmation"""
    phone: str = Field(..., description="Phone number being verified")
    code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")


class AuthError(BaseModel):
    """Schema for authentication error responses"""
    detail: str = Field(..., description="Error description")
    error_code: Optional[str] = Field(None, description="Specific error code")


class AuthStatus(BaseModel):
    """Schema for authentication status check"""
    authenticated: bool = Field(..., description="Whether user is authenticated")
    user: Optional[UserResponse] = Field(None, description="User information if authenticated")


class SendVerificationSMSRequest(BaseModel):
    """Schema for sending SMS verification code"""
    phone: str = Field(..., description="Phone number to send verification code to")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format"""
        if not v:
            raise ValueError('Phone number is required')
        
        # Remove all non-digit characters for validation
        digits_only = ''.join(filter(str.isdigit, v))
        
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError('Phone number must be between 10 and 15 digits')
        
        return v


class VerifyPhoneSMSRequest(BaseModel):
    """Schema for verifying SMS code"""
    phone: str = Field(..., description="Phone number being verified")
    code: str = Field(..., description="6-digit verification code")
    
    @field_validator('code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate verification code format"""
        if not v:
            raise ValueError('Verification code is required')
        
        if not v.isdigit() or len(v) != 6:
            raise ValueError('Verification code must be 6 digits')
        
        return v


class SMSVerificationResponse(BaseModel):
    """Schema for SMS verification operation responses"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    expires_at: Optional[datetime] = Field(None, description="When the verification code expires")


class GoogleOAuthUrlRequest(BaseModel):
    """Schema for Google OAuth authorization URL request"""
    redirect_uri: str = Field(..., description="Where Google should redirect after authentication")
    state: Optional[str] = Field(None, description="Optional state parameter for CSRF protection")


class GoogleOAuthUrlResponse(BaseModel):
    """Schema for Google OAuth authorization URL response"""
    authorization_url: str = Field(..., description="Google OAuth authorization URL")
    state: str = Field(..., description="State parameter for CSRF protection")


class GoogleOAuthCallbackRequest(BaseModel):
    """Schema for Google OAuth callback request"""
    code: str = Field(..., description="Authorization code from Google")
    state: str = Field(..., description="State parameter from authorization request")
    redirect_uri: str = Field(..., description="Redirect URI used in authorization")


class GoogleOAuthLoginRequest(BaseModel):
    """Schema for Google OAuth login with ID token"""
    id_token: str = Field(..., description="Google ID token")
    access_token: Optional[str] = Field(None, description="Google access token")


class GoogleOAuthResponse(BaseModel):
    """Schema for Google OAuth response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse = Field(..., description="User information")
    is_new_user: bool = Field(..., description="Whether this is a newly created user")


class PermissionResponse(BaseModel):
    """Schema for permission data in responses"""
    id: int = Field(..., description="Permission unique identifier")
    name: str = Field(..., description="Permission name (e.g., 'circles:view')")
    description: str = Field(..., description="Permission description")
    resource: str = Field(..., description="Resource the permission applies to")
    action: str = Field(..., description="Action the permission allows")
    
    class Config:
        from_attributes = True


class RoleResponse(BaseModel):
    """Schema for role data in responses"""
    id: int = Field(..., description="Role unique identifier")
    name: str = Field(..., description="Role name")
    description: str = Field(..., description="Role description")
    priority: int = Field(..., description="Role priority for hierarchy")
    permissions: List[PermissionResponse] = Field(default=[], description="Role permissions")
    
    class Config:
        from_attributes = True


class UserRoleResponse(BaseModel):
    """Schema for user role assignment data"""
    role: RoleResponse = Field(..., description="Role information")
    is_primary: bool = Field(..., description="Whether this is the user's primary role")
    assigned_at: datetime = Field(..., description="When the role was assigned")
    
    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """Extended user response with role information"""
    id: int = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    phone: Optional[str] = Field(None, description="User's phone number")
    is_active: bool = Field(..., description="Whether the user account is active")
    is_verified: bool = Field(..., description="Whether the user is verified")
    email_verified: bool = Field(..., description="Whether the email is verified")
    phone_verified: bool = Field(..., description="Whether the phone is verified")
    created_at: datetime = Field(..., description="When the user account was created")
    roles: List[UserRoleResponse] = Field(default=[], description="User's assigned roles")
    permissions: List[str] = Field(default=[], description="All user permissions (aggregated from roles)")
    
    class Config:
        from_attributes = True 