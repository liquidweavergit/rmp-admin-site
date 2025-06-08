"""
JWT-based Authentication Service

This service handles user authentication including:
- User registration with password hashing
- User login with credential validation
- JWT token generation and verification
- Password reset functionality
- Account lockout protection
- SMS phone verification
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status, Depends
import secrets

from ..models.user import User
from ..models.credentials import UserCredentials
from ..core.security import (
    create_access_token, 
    create_refresh_token,
    verify_token,
    get_password_hash,
    verify_password,
    generate_reset_token,
    generate_verification_code
)
from ..core.database import get_main_db, get_credentials_db
from ..schemas.auth import (
    UserCreate, 
    UserLogin, 
    TokenResponse, 
    UserResponse,
    SendVerificationSMSRequest,
    VerifyPhoneSMSRequest,
    SMSVerificationResponse,
    GoogleOAuthLoginRequest,
    GoogleOAuthResponse,
    PasswordResetRequest,
    PasswordResetConfirm
)
from .sms_service import SMSService, get_sms_service
from .google_oauth_service import GoogleOAuthService, get_google_oauth_service
from .email_service import EmailService, get_email_service


class AuthService:
    """Service class for handling authentication operations"""
    
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    MAX_SMS_ATTEMPTS = 3
    SMS_EXPIRY_MINUTES = 10
    MAX_PASSWORD_RESET_ATTEMPTS = 3
    PASSWORD_RESET_EXPIRY_MINUTES = 60
    
    def __init__(self, main_db: AsyncSession, credentials_db: AsyncSession, sms_service: SMSService = None, google_oauth_service: GoogleOAuthService = None, email_service: EmailService = None):
        self.main_db = main_db
        self.credentials_db = credentials_db
        self.sms_service = sms_service or get_sms_service()
        self.google_oauth_service = google_oauth_service or get_google_oauth_service()
        self.email_service = email_service or get_email_service()
    
    async def register_user(self, user_data: UserCreate) -> UserResponse:
        """
        Register a new user with email and password
        
        Args:
            user_data: User registration data
            
        Returns:
            UserResponse: Created user information
            
        Raises:
            HTTPException: If email already exists or registration fails
        """
        # Check if user already exists
        existing_user = await self._get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user in main database
        user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
            is_active=True,
            is_verified=False,
            email_verified=False,
            phone_verified=False
        )
        
        self.main_db.add(user)
        await self.main_db.commit()
        await self.main_db.refresh(user)
        
        # Create credentials in credentials database
        salt = secrets.token_urlsafe(32)
        password_hash = get_password_hash(user_data.password + salt)
        
        credentials = UserCredentials(
            user_id=user.id,
            password_hash=password_hash,
            salt=salt,
            failed_login_attempts=0
        )
        
        self.credentials_db.add(credentials)
        await self.credentials_db.commit()
        
        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            is_active=user.is_active,
            is_verified=user.is_verified,
            email_verified=user.email_verified,
            phone_verified=user.phone_verified,
            created_at=user.created_at
        )
    
    async def authenticate_user(self, login_data: UserLogin) -> TokenResponse:
        """
        Authenticate user and return JWT tokens
        
        Args:
            login_data: User login credentials
            
        Returns:
            TokenResponse: Access and refresh tokens
            
        Raises:
            HTTPException: If authentication fails or account is locked
        """
        # Get user and credentials
        user = await self._get_user_by_email(login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        credentials = await self._get_user_credentials(user.id)
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if account is locked
        if self._is_account_locked(credentials):
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account temporarily locked due to too many failed attempts"
            )
        
        # Verify password
        if not verify_password(login_data.password + credentials.salt, credentials.password_hash):
            await self._handle_failed_login(credentials)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive"
            )
        
        # Reset failed login attempts on successful login
        await self._reset_failed_login_attempts(credentials)
        
        # Update last login time
        await self._update_last_login(user)
        
        # Create tokens
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Store refresh token hash
        await self._store_refresh_token(credentials, refresh_token)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Generate new access token using refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            TokenResponse: New access and refresh tokens
            
        Raises:
            HTTPException: If refresh token is invalid or expired
        """
        # Verify refresh token
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user and verify token is stored
        user = await self._get_user_by_id(int(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        credentials = await self._get_user_credentials(user.id)
        if not credentials or not self._verify_stored_refresh_token(credentials, refresh_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new tokens
        token_data = {"sub": str(user.id), "email": user.email}
        new_access_token = create_access_token(token_data)
        new_refresh_token = create_refresh_token(token_data)
        
        # Store new refresh token
        await self._store_refresh_token(credentials, new_refresh_token)
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )
    
    async def verify_access_token(self, token: str) -> Optional[User]:
        """
        Verify access token and return user
        
        Args:
            token: JWT access token
            
        Returns:
            User: User object if token is valid, None otherwise
        """
        payload = verify_token(token)
        if not payload or payload.get("type") != "access":
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        return await self._get_user_by_id(int(user_id))
    
    async def logout_user(self, refresh_token: str) -> bool:
        """
        Logout user by invalidating refresh token
        
        Args:
            refresh_token: Refresh token to invalidate
            
        Returns:
            bool: True if logout successful
        """
        payload = verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return False
        
        user_id = payload.get("sub")
        if not user_id:
            return False
        
        credentials = await self._get_user_credentials(int(user_id))
        if credentials:
            await self._clear_refresh_token(credentials)
        
        return True
    
    async def send_phone_verification_sms(self, request: SendVerificationSMSRequest) -> SMSVerificationResponse:
        """
        Send SMS verification code to phone number
        
        Args:
            request: SMS verification request
            
        Returns:
            SMSVerificationResponse: Response with send status
            
        Raises:
            HTTPException: If phone number is invalid or send fails
        """
        # Validate phone number
        if not self.sms_service.validate_phone_number(request.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone number format"
            )
        
        # Find user by phone number
        user = await self._get_user_by_phone(request.phone)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phone number not found in system"
            )
        
        # Get or create credentials
        credentials = await self._get_user_credentials(user.id)
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User credentials not found"
            )
        
        # Check if too many SMS attempts
        if credentials.phone_verification_attempts >= self.MAX_SMS_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many SMS verification attempts. Please try again later."
            )
        
        # Generate verification code
        verification_code = self.sms_service.generate_verification_code()
        expires_at = datetime.utcnow() + timedelta(minutes=self.SMS_EXPIRY_MINUTES)
        
        # Store verification code
        credentials.phone_verification_code = verification_code
        credentials.phone_verification_expires_at = expires_at
        credentials.phone_verification_attempts += 1
        await self.credentials_db.commit()
        
        # Send SMS
        try:
            await self.sms_service.send_verification_code(request.phone, verification_code)
            return SMSVerificationResponse(
                success=True,
                message="Verification code sent successfully",
                expires_at=expires_at
            )
        except HTTPException:
            # Roll back the attempt count if SMS fails
            credentials.phone_verification_attempts -= 1
            await self.credentials_db.commit()
            raise
    
    async def verify_phone_sms_code(self, request: VerifyPhoneSMSRequest) -> SMSVerificationResponse:
        """
        Verify SMS verification code
        
        Args:
            request: SMS verification request with code
            
        Returns:
            SMSVerificationResponse: Response with verification status
            
        Raises:
            HTTPException: If verification fails
        """
        # Find user by phone number
        user = await self._get_user_by_phone(request.phone)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Phone number not found in system"
            )
        
        # Get credentials
        credentials = await self._get_user_credentials(user.id)
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User credentials not found"
            )
        
        # Check if verification code exists
        if not credentials.phone_verification_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No verification code found. Please request a new code."
            )
        
        # Check if code has expired
        if (credentials.phone_verification_expires_at and 
            self.sms_service.is_code_expired(credentials.phone_verification_expires_at, 0)):
            # Clear expired code
            await self._clear_phone_verification_code(credentials)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code has expired. Please request a new code."
            )
        
        # Verify code
        if credentials.phone_verification_code != request.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )
        
        # Mark phone as verified
        user.phone_verified = True
        await self.main_db.commit()
        
        # Clear verification code and reset attempts
        await self._clear_phone_verification_code(credentials)
        credentials.phone_verification_attempts = 0
        await self.credentials_db.commit()
        
        return SMSVerificationResponse(
            success=True,
            message="Phone number verified successfully"
        )
    
    async def authenticate_google_oauth(self, request: GoogleOAuthLoginRequest) -> GoogleOAuthResponse:
        """
        Authenticate user with Google OAuth ID token
        
        Args:
            request: Google OAuth login request with ID token
            
        Returns:
            GoogleOAuthResponse: Authentication response with tokens and user info
            
        Raises:
            HTTPException: If authentication fails
        """
        # Verify the Google ID token
        google_user_info = await self.google_oauth_service.verify_id_token(request.id_token)
        
        google_user_id = google_user_info.get("sub")
        email = google_user_info.get("email")
        email_verified = google_user_info.get("email_verified", False)
        
        if not google_user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Google token: missing required user information"
            )
        
        if not email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google email not verified"
            )
        
        # Check if user exists by Google ID
        existing_user = await self._get_user_by_google_id(google_user_id)
        is_new_user = False
        
        if existing_user:
            user = existing_user
        else:
            # Check if user exists by email
            existing_user_by_email = await self._get_user_by_email(email)
            
            if existing_user_by_email:
                # Link Google account to existing user
                user = existing_user_by_email
                await self._link_google_account(user.id, google_user_id, request.access_token)
            else:
                # Create new user
                user = await self._create_google_user(google_user_info)
                await self._link_google_account(user.id, google_user_id, request.access_token)
                is_new_user = True
        
        # Update last login
        await self._update_last_login(user)
        
        # Create JWT tokens
        token_data = {"sub": str(user.id), "email": user.email}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        # Store refresh token
        credentials = await self._get_user_credentials(user.id)
        if credentials:
            await self._store_refresh_token(credentials, refresh_token)
        
        user_response = UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            is_active=user.is_active,
            is_verified=user.is_verified,
            email_verified=user.email_verified,
            phone_verified=user.phone_verified,
            created_at=user.created_at
        )
        
        return GoogleOAuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=user_response,
            is_new_user=is_new_user
        )
    
    async def request_password_reset(self, request: PasswordResetRequest) -> dict:
        """
        Initiate password reset process by sending reset email
        
        Args:
            request: Password reset request with email
            
        Returns:
            dict: Response indicating email was sent
            
        Raises:
            HTTPException: If user not found or too many attempts
        """
        # Find user by email
        user = await self._get_user_by_email(request.email)
        if not user:
            # For security, don't reveal if email exists
            return {
                "message": "If the email address exists in our system, a password reset link has been sent."
            }
        
        # Get credentials
        credentials = await self._get_user_credentials(user.id)
        if not credentials:
            # For security, don't reveal if email exists
            return {
                "message": "If the email address exists in our system, a password reset link has been sent."
            }
        
        # Check if too many reset attempts
        if credentials.password_reset_attempts >= self.MAX_PASSWORD_RESET_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many password reset attempts. Please try again later."
            )
        
        # Generate reset token
        reset_token = generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(minutes=self.PASSWORD_RESET_EXPIRY_MINUTES)
        
        # Store reset token
        credentials.password_reset_token = reset_token
        credentials.password_reset_expires_at = expires_at
        credentials.password_reset_attempts += 1
        await self.credentials_db.commit()
        
        # Send password reset email
        try:
            await self.email_service.send_password_reset_email(
                to_email=user.email,
                first_name=user.first_name,
                reset_token=reset_token
            )
            
            return {
                "message": "If the email address exists in our system, a password reset link has been sent."
            }
        except HTTPException:
            # Roll back the attempt count if email fails
            credentials.password_reset_attempts -= 1
            await self.credentials_db.commit()
            raise
    
    async def confirm_password_reset(self, request: PasswordResetConfirm) -> dict:
        """
        Confirm password reset with token and set new password
        
        Args:
            request: Password reset confirmation with token and new password
            
        Returns:
            dict: Success message
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        # Find credentials by reset token
        credentials = await self._get_credentials_by_reset_token(request.token)
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Check if token has expired
        if (credentials.password_reset_expires_at and 
            credentials.password_reset_expires_at < datetime.utcnow()):
            # Clear expired token
            await self._clear_password_reset_token(credentials)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password reset token has expired"
            )
        
        # Get user
        user = await self._get_user_by_id(credentials.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        # Update password
        salt = secrets.token_urlsafe(32)
        password_hash = get_password_hash(request.new_password + salt)
        
        credentials.password_hash = password_hash
        credentials.salt = salt
        credentials.password_changed_at = datetime.utcnow()
        
        # Clear reset token and reset attempts
        await self._clear_password_reset_token(credentials)
        credentials.password_reset_attempts = 0
        
        # Clear any existing sessions (logout all devices)
        credentials.refresh_token_hash = None
        
        # Reset login attempts if account was locked
        credentials.failed_login_attempts = 0
        credentials.locked_until = None
        
        await self.credentials_db.commit()
        
        return {
            "message": "Password has been successfully reset. Please log in with your new password."
        }
    
    # Private helper methods
    
    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email from main database"""
        result = await self.main_db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def _get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID from main database"""
        result = await self.main_db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def _get_user_credentials(self, user_id: int) -> Optional[UserCredentials]:
        """Get user credentials from credentials database"""
        result = await self.credentials_db.execute(
            select(UserCredentials).where(UserCredentials.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    def _is_account_locked(self, credentials: UserCredentials) -> bool:
        """Check if account is locked due to failed login attempts"""
        if credentials.locked_until and credentials.locked_until > datetime.utcnow():
            return True
        return False
    
    async def _handle_failed_login(self, credentials: UserCredentials) -> None:
        """Handle failed login attempt"""
        credentials.failed_login_attempts += 1
        credentials.last_password_attempt = datetime.utcnow()
        
        if credentials.failed_login_attempts >= self.MAX_LOGIN_ATTEMPTS:
            credentials.locked_until = datetime.utcnow() + timedelta(minutes=self.LOCKOUT_DURATION_MINUTES)
        
        await self.credentials_db.commit()
    
    async def _reset_failed_login_attempts(self, credentials: UserCredentials) -> None:
        """Reset failed login attempts on successful login"""
        credentials.failed_login_attempts = 0
        credentials.locked_until = None
        await self.credentials_db.commit()
    
    async def _update_last_login(self, user: User) -> None:
        """Update user's last login timestamp"""
        user.last_login_at = datetime.utcnow()
        await self.main_db.commit()
    
    async def _store_refresh_token(self, credentials: UserCredentials, refresh_token: str) -> None:
        """Store hashed refresh token"""
        credentials.refresh_token_hash = get_password_hash(refresh_token)
        await self.credentials_db.commit()
    
    def _verify_stored_refresh_token(self, credentials: UserCredentials, refresh_token: str) -> bool:
        """Verify refresh token against stored hash"""
        if not credentials.refresh_token_hash:
            return False
        return verify_password(refresh_token, credentials.refresh_token_hash)
    
    async def _clear_refresh_token(self, credentials: UserCredentials) -> None:
        """Clear stored refresh token"""
        credentials.refresh_token_hash = None
        await self.credentials_db.commit()
    
    async def _get_user_by_phone(self, phone: str) -> Optional[User]:
        """Get user by phone number from main database"""
        result = await self.main_db.execute(
            select(User).where(User.phone == phone)
        )
        return result.scalar_one_or_none()
    
    async def _clear_phone_verification_code(self, credentials: UserCredentials) -> None:
        """Clear phone verification code and expiry"""
        credentials.phone_verification_code = None
        credentials.phone_verification_expires_at = None
        await self.credentials_db.commit()
    
    async def _get_user_by_google_id(self, google_user_id: str) -> Optional[User]:
        """Get user by Google user ID from credentials database"""
        # First get the user_id from credentials
        result = await self.credentials_db.execute(
            select(UserCredentials).where(UserCredentials.google_user_id == google_user_id)
        )
        credentials = result.scalar_one_or_none()
        
        if not credentials:
            return None
        
        # Then get the user from main database
        return await self._get_user_by_id(credentials.user_id)
    
    async def _create_google_user(self, google_user_info: dict) -> User:
        """Create a new user from Google user information"""
        # Extract user information from Google
        email = google_user_info.get("email")
        given_name = google_user_info.get("given_name", "")
        family_name = google_user_info.get("family_name", "")
        
        # Create user in main database
        user = User(
            email=email,
            first_name=given_name,
            last_name=family_name,
            phone=None,
            is_active=True,
            is_verified=True,  # Google users are pre-verified
            email_verified=True,  # Google email is verified
            phone_verified=False
        )
        
        self.main_db.add(user)
        await self.main_db.commit()
        await self.main_db.refresh(user)
        
        # Create credentials entry (without password for OAuth users)
        credentials = UserCredentials(
            user_id=user.id,
            password_hash="",  # No password for OAuth users
            salt="",
            failed_login_attempts=0
        )
        
        self.credentials_db.add(credentials)
        await self.credentials_db.commit()
        
        return user
    
    async def _link_google_account(self, user_id: int, google_user_id: str, access_token: Optional[str] = None) -> None:
        """Link Google account to existing user"""
        credentials = await self._get_user_credentials(user_id)
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User credentials not found"
            )
        
        # Store Google user ID and optionally access token
        credentials.google_user_id = google_user_id
        
        # Note: In production, you would encrypt the access token
        # For now, we'll store it as-is for simplicity
        if access_token:
            credentials.google_access_token = access_token.encode('utf-8')
        
        await self.credentials_db.commit()
    
    async def _get_credentials_by_reset_token(self, reset_token: str) -> Optional[UserCredentials]:
        """Get user credentials by password reset token"""
        result = await self.credentials_db.execute(
            select(UserCredentials).where(UserCredentials.password_reset_token == reset_token)
        )
        return result.scalar_one_or_none()
    
    async def _clear_password_reset_token(self, credentials: UserCredentials) -> None:
        """Clear password reset token and expiry"""
        credentials.password_reset_token = None
        credentials.password_reset_expires_at = None
        await self.credentials_db.commit()


def get_auth_service(
    main_db: AsyncSession = Depends(get_main_db),
    credentials_db: AsyncSession = Depends(get_credentials_db)
) -> AuthService:
    """
    Dependency to get AuthService instance
    
    Args:
        main_db: Main database session
        credentials_db: Credentials database session
        
    Returns:
        AuthService: Configured auth service instance
    """
    return AuthService(main_db, credentials_db) 