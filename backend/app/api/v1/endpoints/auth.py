"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from ....schemas.auth import (
    UserCreate, 
    UserLogin, 
    UserResponse, 
    TokenResponse, 
    RefreshTokenRequest,
    LogoutRequest,
    AuthStatus,
    SendVerificationSMSRequest,
    VerifyPhoneSMSRequest,
    SMSVerificationResponse,
    GoogleOAuthUrlRequest,
    GoogleOAuthUrlResponse,
    GoogleOAuthCallbackRequest,
    GoogleOAuthLoginRequest,
    GoogleOAuthResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    UserProfileResponse,
    RoleResponse,
    PermissionResponse
)
from ....services.auth_service import AuthService, get_auth_service
from ....services.google_oauth_service import GoogleOAuthService, get_google_oauth_service
from ....core.deps import get_current_user, get_current_user_optional
from ....models.user import User

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password"
)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
) -> UserResponse:
    """
    Register a new user account
    
    - **email**: User's email address (must be unique)
    - **password**: User's password (minimum 8 characters with complexity requirements)
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **phone**: User's phone number (optional)
    
    Returns the created user information (without sensitive data)
    """
    try:
        return await auth_service.register_user(user_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user and return JWT tokens"
)
async def login(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """
    Authenticate user with email and password
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns JWT access and refresh tokens
    """
    try:
        return await auth_service.authenticate_user(login_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Generate new access token using refresh token"
)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """
    Refresh access token using a valid refresh token
    
    - **refresh_token**: Valid refresh token
    
    Returns new JWT access and refresh tokens
    """
    try:
        return await auth_service.refresh_access_token(request.refresh_token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User logout",
    description="Logout user by invalidating refresh token"
)
async def logout(
    request: LogoutRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Logout user by invalidating their refresh token
    
    - **refresh_token**: Refresh token to invalidate
    
    Returns 204 No Content on success
    """
    try:
        success = await auth_service.logout_user(request.refresh_token)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid refresh token"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get information about the currently authenticated user"
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """
    Get current user information
    
    Requires valid JWT token in Authorization header
    
    Returns user profile information
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone=current_user.phone,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        email_verified=current_user.email_verified,
        phone_verified=current_user.phone_verified,
        created_at=current_user.created_at
    )


@router.get(
    "/status",
    response_model=AuthStatus,
    summary="Check authentication status",
    description="Check if user is currently authenticated"
)
async def auth_status(
    current_user: User = Depends(get_current_user_optional)
) -> AuthStatus:
    """
    Check authentication status
    
    Returns authentication status and user information if authenticated.
    This endpoint does not require authentication (returns status for both authenticated and unauthenticated requests).
    """
    if current_user:
        return AuthStatus(
            authenticated=True,
            user=UserResponse(
                id=current_user.id,
                email=current_user.email,
                first_name=current_user.first_name,
                last_name=current_user.last_name,
                phone=current_user.phone,
                is_active=current_user.is_active,
                is_verified=current_user.is_verified,
                email_verified=current_user.email_verified,
                phone_verified=current_user.phone_verified,
                created_at=current_user.created_at
            )
        )
    else:
        return AuthStatus(authenticated=False, user=None)


@router.get(
    "/profile",
    response_model=UserProfileResponse,
    summary="Get current user profile with roles",
    description="Get detailed user profile including roles and permissions"
)
async def get_user_profile(
    current_user: User = Depends(get_current_user)
) -> UserProfileResponse:
    """
    Get current user profile with role and permission information
    
    Requires valid JWT token in Authorization header
    
    Returns user profile with:
    - Basic user information
    - Assigned roles with details
    - Aggregated permissions list
    """
    from ....schemas.auth import UserRoleResponse
    
    # Build user roles response
    user_roles = []
    all_permissions = set()
    
    for user_role in current_user.user_roles:
        if user_role.is_active:
            role = user_role.role
            role_permissions = [
                PermissionResponse(
                    id=perm.id,
                    name=perm.name,
                    description=perm.description,
                    resource=perm.resource,
                    action=perm.action
                )
                for perm in role.permissions
            ]
            
            user_roles.append(UserRoleResponse(
                role=RoleResponse(
                    id=role.id,
                    name=role.name,
                    description=role.description,
                    priority=role.priority,
                    permissions=role_permissions
                ),
                is_primary=user_role.is_primary,
                assigned_at=user_role.assigned_at
            ))
            
            # Collect all permissions
            for perm in role.permissions:
                all_permissions.add(perm.name)
    
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        phone=current_user.phone,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        email_verified=current_user.email_verified,
        phone_verified=current_user.phone_verified,
        created_at=current_user.created_at,
        roles=user_roles,
        permissions=list(all_permissions)
    )


@router.post(
    "/send-sms-verification",
    response_model=SMSVerificationResponse,
    summary="Send SMS verification code",
    description="Send a verification code to the user's phone number via SMS"
)
async def send_sms_verification(
    request: SendVerificationSMSRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> SMSVerificationResponse:
    """
    Send SMS verification code to phone number
    
    - **phone**: Phone number to send verification code to
    
    Returns confirmation that SMS was sent with expiry time
    """
    try:
        return await auth_service.send_phone_verification_sms(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send SMS verification code"
        )


@router.post(
    "/verify-sms-code",
    response_model=SMSVerificationResponse,
    summary="Verify SMS code",
    description="Verify the SMS verification code sent to the user's phone"
)
async def verify_sms_code(
    request: VerifyPhoneSMSRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> SMSVerificationResponse:
    """
    Verify SMS verification code
    
    - **phone**: Phone number that received the verification code
    - **code**: 6-digit verification code from SMS
    
    Returns confirmation that phone number has been verified
    """
    try:
        return await auth_service.verify_phone_sms_code(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify SMS code"
        )


@router.post(
    "/google/auth-url",
    response_model=GoogleOAuthUrlResponse,
    summary="Get Google OAuth authorization URL",
    description="Generate Google OAuth authorization URL for frontend redirect"
)
async def get_google_auth_url(
    request: GoogleOAuthUrlRequest,
    google_oauth_service: GoogleOAuthService = Depends(get_google_oauth_service)
) -> GoogleOAuthUrlResponse:
    """
    Get Google OAuth authorization URL
    
    - **redirect_uri**: Where Google should redirect after authentication
    - **state**: Optional state parameter for CSRF protection
    
    Returns Google OAuth authorization URL and state parameter
    """
    try:
        authorization_url = google_oauth_service.get_authorization_url(
            redirect_uri=request.redirect_uri,
            state=request.state
        )
        
        # Extract state from URL if not provided
        state = request.state
        if not state and "state=" in authorization_url:
            state = authorization_url.split("state=")[1].split("&")[0]
        
        return GoogleOAuthUrlResponse(
            authorization_url=authorization_url,
            state=state or "default"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate Google OAuth URL"
        )


@router.post(
    "/google/callback",
    response_model=GoogleOAuthResponse,
    summary="Handle Google OAuth callback",
    description="Process Google OAuth callback with authorization code"
)
async def google_oauth_callback(
    request: GoogleOAuthCallbackRequest,
    auth_service: AuthService = Depends(get_auth_service),
    google_oauth_service: GoogleOAuthService = Depends(get_google_oauth_service)
) -> GoogleOAuthResponse:
    """
    Handle Google OAuth callback
    
    - **code**: Authorization code from Google
    - **state**: State parameter from authorization request
    - **redirect_uri**: Redirect URI used in authorization
    
    Returns JWT tokens and user information
    """
    try:
        # Exchange code for tokens
        token_data = await google_oauth_service.exchange_code_for_tokens(
            code=request.code,
            redirect_uri=request.redirect_uri
        )
        
        # Create login request with ID token
        login_request = GoogleOAuthLoginRequest(
            id_token=token_data.get("id_token"),
            access_token=token_data.get("access_token")
        )
        
        # Authenticate user
        return await auth_service.authenticate_google_oauth(login_request)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth authentication failed"
        )


@router.post(
    "/google/login",
    response_model=GoogleOAuthResponse,
    summary="Login with Google ID token",
    description="Authenticate user directly with Google ID token"
)
async def google_oauth_login(
    request: GoogleOAuthLoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> GoogleOAuthResponse:
    """
    Login with Google ID token
    
    - **id_token**: Google ID token from client-side authentication
    - **access_token**: Optional Google access token
    
    Returns JWT tokens and user information
    """
    try:
        return await auth_service.authenticate_google_oauth(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth login failed"
        )


@router.post(
    "/password-reset/request",
    summary="Request password reset",
    description="Send password reset email to user"
)
async def request_password_reset(
    request: PasswordResetRequest,
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """
    Request password reset
    
    - **email**: Email address to send reset link to
    
    Returns confirmation message (same message regardless of whether email exists for security)
    """
    try:
        return await auth_service.request_password_reset(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset request"
        )


@router.post(
    "/password-reset/confirm",
    summary="Confirm password reset",
    description="Reset password using token from email"
)
async def confirm_password_reset(
    request: PasswordResetConfirm,
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """
    Confirm password reset
    
    - **token**: Password reset token from email
    - **new_password**: New password (must meet complexity requirements)
    
    Returns success message
    """
    try:
        return await auth_service.confirm_password_reset(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        ) 