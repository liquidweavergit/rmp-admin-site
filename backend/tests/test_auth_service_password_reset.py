"""
Unit tests for Password Reset functionality in AuthService

This test suite verifies:
1. Password reset request functionality
2. Password reset confirmation functionality
3. Token generation and validation
4. Rate limiting for reset attempts
5. Security measures and error handling
6. Integration with email service
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from app.services.auth_service import AuthService
from app.services.email_service import EmailService
from app.models.user import User
from app.models.credentials import UserCredentials
from app.schemas.auth import PasswordResetRequest, PasswordResetConfirm
from app.core.security import get_password_hash, verify_password


class TestAuthServicePasswordReset:
    """Test cases for password reset functionality in AuthService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_main_db = AsyncMock()
        self.mock_credentials_db = AsyncMock()
        self.mock_email_service = Mock(spec=EmailService)
        
        self.auth_service = AuthService(
            main_db=self.mock_main_db,
            credentials_db=self.mock_credentials_db,
            email_service=self.mock_email_service
        )
        
        # Mock user and credentials
        self.test_user = User(
            id=1,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone="+15551234567",
            is_active=True,
            is_verified=True
        )
        
        self.test_credentials = UserCredentials(
            user_id=1,
            password_hash="old_hashed_password",
            salt="old_salt",
            password_reset_attempts=0,
            password_reset_token=None,
            password_reset_expires_at=None
        )
    
    @pytest.mark.asyncio
    async def test_request_password_reset_success(self):
        """Test successful password reset request"""
        # Setup mocks
        self.mock_email_service.send_password_reset_email = AsyncMock(return_value=True)
        
        # Mock database queries
        mock_user_result = Mock()
        mock_user_result.scalar_one_or_none.return_value = self.test_user
        self.mock_main_db.execute = AsyncMock(return_value=mock_user_result)
        
        mock_creds_result = Mock()
        mock_creds_result.scalar_one_or_none.return_value = self.test_credentials
        self.mock_credentials_db.execute = AsyncMock(return_value=mock_creds_result)
        
        # Test request
        request = PasswordResetRequest(email="test@example.com")
        
        result = await self.auth_service.request_password_reset(request)
        
        # Assertions
        assert "password reset link has been sent" in result["message"]
        
        # Verify email service was called
        self.mock_email_service.send_password_reset_email.assert_called_once()
        call_args = self.mock_email_service.send_password_reset_email.call_args
        assert call_args[1]["to_email"] == "test@example.com"
        assert call_args[1]["first_name"] == "John"
        assert call_args[1]["reset_token"] is not None
        
        # Verify database updates
        assert self.test_credentials.password_reset_token is not None
        assert self.test_credentials.password_reset_expires_at is not None
        assert self.test_credentials.password_reset_attempts == 1
        self.mock_credentials_db.commit.assert_called()
    
    @pytest.mark.asyncio
    async def test_request_password_reset_user_not_found(self):
        """Test password reset request when user not found (security)"""
        # Mock database query to return None (user not found)
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_main_db.execute = AsyncMock(return_value=mock_result)
        
        request = PasswordResetRequest(email="nonexistent@example.com")
        
        result = await self.auth_service.request_password_reset(request)
        
        # Should return same message for security (don't reveal if email exists)
        assert "password reset link has been sent" in result["message"]
        
        # Email service should not be called
        self.mock_email_service.send_password_reset_email.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_request_password_reset_credentials_not_found(self):
        """Test password reset request when credentials not found"""
        # Mock user exists but no credentials
        mock_user_result = Mock()
        mock_user_result.scalar_one_or_none.return_value = self.test_user
        self.mock_main_db.execute = AsyncMock(return_value=mock_user_result)
        
        mock_creds_result = Mock()
        mock_creds_result.scalar_one_or_none.return_value = None
        self.mock_credentials_db.execute = AsyncMock(return_value=mock_creds_result)
        
        request = PasswordResetRequest(email="test@example.com")
        
        result = await self.auth_service.request_password_reset(request)
        
        # Should return same message for security
        assert "password reset link has been sent" in result["message"]
        
        # Email service should not be called
        self.mock_email_service.send_password_reset_email.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_request_password_reset_too_many_attempts(self):
        """Test password reset request with too many attempts"""
        # Set up credentials with max attempts
        self.test_credentials.password_reset_attempts = 3  # MAX_PASSWORD_RESET_ATTEMPTS
        
        # Mock database queries
        mock_user_result = Mock()
        mock_user_result.scalar_one_or_none.return_value = self.test_user
        self.mock_main_db.execute = AsyncMock(return_value=mock_user_result)
        
        mock_creds_result = Mock()
        mock_creds_result.scalar_one_or_none.return_value = self.test_credentials
        self.mock_credentials_db.execute = AsyncMock(return_value=mock_creds_result)
        
        request = PasswordResetRequest(email="test@example.com")
        
        with pytest.raises(HTTPException) as exc_info:
            await self.auth_service.request_password_reset(request)
        
        assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Too many password reset attempts" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_request_password_reset_email_service_error(self):
        """Test password reset request when email service fails"""
        # Setup email service to raise exception
        self.mock_email_service.send_password_reset_email = AsyncMock(
            side_effect=HTTPException(status_code=503, detail="Email service error")
        )
        
        # Mock database queries
        mock_user_result = Mock()
        mock_user_result.scalar_one_or_none.return_value = self.test_user
        self.mock_main_db.execute = AsyncMock(return_value=mock_user_result)
        
        mock_creds_result = Mock()
        mock_creds_result.scalar_one_or_none.return_value = self.test_credentials
        self.mock_credentials_db.execute = AsyncMock(return_value=mock_creds_result)
        
        request = PasswordResetRequest(email="test@example.com")
        
        with pytest.raises(HTTPException) as exc_info:
            await self.auth_service.request_password_reset(request)
        
        assert exc_info.value.status_code == 503
        
        # Verify attempt count was rolled back
        assert self.test_credentials.password_reset_attempts == 0
    
    @pytest.mark.asyncio
    async def test_confirm_password_reset_success(self):
        """Test successful password reset confirmation"""
        # Setup credentials with valid reset token
        reset_token = "valid_reset_token_123"
        self.test_credentials.password_reset_token = reset_token
        self.test_credentials.password_reset_expires_at = datetime.utcnow() + timedelta(minutes=30)
        
        # Mock database queries
        mock_creds_result = Mock()
        mock_creds_result.scalar_one_or_none.return_value = self.test_credentials
        self.mock_credentials_db.execute = AsyncMock(return_value=mock_creds_result)
        
        mock_user_result = Mock()
        mock_user_result.scalar_one_or_none.return_value = self.test_user
        self.mock_main_db.execute = AsyncMock(return_value=mock_user_result)
        
        # Test request
        request = PasswordResetConfirm(
            token=reset_token,
            new_password="NewSecurePassword123"
        )
        
        result = await self.auth_service.confirm_password_reset(request)
        
        # Assertions
        assert "Password has been successfully reset" in result["message"]
        
        # Verify password was updated
        assert self.test_credentials.password_hash != "old_hashed_password"
        assert self.test_credentials.salt != "old_salt"
        assert self.test_credentials.password_changed_at is not None
        
        # Verify reset token was cleared
        assert self.test_credentials.password_reset_token is None
        assert self.test_credentials.password_reset_expires_at is None
        assert self.test_credentials.password_reset_attempts == 0
        
        # Verify sessions were cleared (logout all devices)
        assert self.test_credentials.refresh_token_hash is None
        
        # Verify login attempts were reset
        assert self.test_credentials.failed_login_attempts == 0
        assert self.test_credentials.locked_until is None
        
        self.mock_credentials_db.commit.assert_called()
    
    @pytest.mark.asyncio
    async def test_confirm_password_reset_invalid_token(self):
        """Test password reset confirmation with invalid token"""
        # Mock database query to return None (token not found)
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_credentials_db.execute = AsyncMock(return_value=mock_result)
        
        request = PasswordResetConfirm(
            token="invalid_token",
            new_password="NewSecurePassword123"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await self.auth_service.confirm_password_reset(request)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid or expired reset token" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_confirm_password_reset_expired_token(self):
        """Test password reset confirmation with expired token"""
        # Setup credentials with expired reset token
        reset_token = "expired_token_123"
        self.test_credentials.password_reset_token = reset_token
        self.test_credentials.password_reset_expires_at = datetime.utcnow() - timedelta(minutes=30)  # Expired
        
        # Mock database queries
        mock_creds_result = Mock()
        mock_creds_result.scalar_one_or_none.return_value = self.test_credentials
        self.mock_credentials_db.execute = AsyncMock(return_value=mock_creds_result)
        
        request = PasswordResetConfirm(
            token=reset_token,
            new_password="NewSecurePassword123"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await self.auth_service.confirm_password_reset(request)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Password reset token has expired" in str(exc_info.value.detail)
        
        # Verify expired token was cleared
        assert self.test_credentials.password_reset_token is None
        assert self.test_credentials.password_reset_expires_at is None
    
    @pytest.mark.asyncio
    async def test_confirm_password_reset_inactive_user(self):
        """Test password reset confirmation with inactive user"""
        # Setup credentials with valid reset token
        reset_token = "valid_token_123"
        self.test_credentials.password_reset_token = reset_token
        self.test_credentials.password_reset_expires_at = datetime.utcnow() + timedelta(minutes=30)
        
        # Setup inactive user
        inactive_user = User(
            id=1,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            is_active=False  # Inactive user
        )
        
        # Mock database queries
        mock_creds_result = Mock()
        mock_creds_result.scalar_one_or_none.return_value = self.test_credentials
        self.mock_credentials_db.execute = AsyncMock(return_value=mock_creds_result)
        
        mock_user_result = Mock()
        mock_user_result.scalar_one_or_none.return_value = inactive_user
        self.mock_main_db.execute = AsyncMock(return_value=mock_user_result)
        
        request = PasswordResetConfirm(
            token=reset_token,
            new_password="NewSecurePassword123"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await self.auth_service.confirm_password_reset(request)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid reset token" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_confirm_password_reset_user_not_found(self):
        """Test password reset confirmation when user not found"""
        # Setup credentials with valid reset token
        reset_token = "valid_token_123"
        self.test_credentials.password_reset_token = reset_token
        self.test_credentials.password_reset_expires_at = datetime.utcnow() + timedelta(minutes=30)
        
        # Mock database queries
        mock_creds_result = Mock()
        mock_creds_result.scalar_one_or_none.return_value = self.test_credentials
        self.mock_credentials_db.execute = AsyncMock(return_value=mock_creds_result)
        
        mock_user_result = Mock()
        mock_user_result.scalar_one_or_none.return_value = None  # User not found
        self.mock_main_db.execute = AsyncMock(return_value=mock_user_result)
        
        request = PasswordResetConfirm(
            token=reset_token,
            new_password="NewSecurePassword123"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await self.auth_service.confirm_password_reset(request)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid reset token" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_credentials_by_reset_token_helper(self):
        """Test the helper method for getting credentials by reset token"""
        reset_token = "test_token_123"
        
        # Mock database query
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = self.test_credentials
        self.mock_credentials_db.execute = AsyncMock(return_value=mock_result)
        
        result = await self.auth_service._get_credentials_by_reset_token(reset_token)
        
        assert result == self.test_credentials
        
        # Verify correct query was made
        self.mock_credentials_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_clear_password_reset_token_helper(self):
        """Test the helper method for clearing password reset token"""
        # Setup credentials with reset token
        self.test_credentials.password_reset_token = "token_to_clear"
        self.test_credentials.password_reset_expires_at = datetime.utcnow()
        
        await self.auth_service._clear_password_reset_token(self.test_credentials)
        
        # Verify token was cleared
        assert self.test_credentials.password_reset_token is None
        assert self.test_credentials.password_reset_expires_at is None
        self.mock_credentials_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_password_reset_token_generation_uniqueness(self):
        """Test that password reset tokens are unique"""
        # Mock database queries for multiple requests
        mock_user_result = Mock()
        mock_user_result.scalar_one_or_none.return_value = self.test_user
        self.mock_main_db.execute = AsyncMock(return_value=mock_user_result)
        
        mock_creds_result = Mock()
        mock_creds_result.scalar_one_or_none.return_value = self.test_credentials
        self.mock_credentials_db.execute = AsyncMock(return_value=mock_creds_result)
        
        self.mock_email_service.send_password_reset_email = AsyncMock(return_value=True)
        
        request = PasswordResetRequest(email="test@example.com")
        
        # Make multiple requests and capture tokens
        tokens = []
        for _ in range(3):
            # Reset attempts for each request
            self.test_credentials.password_reset_attempts = 0
            await self.auth_service.request_password_reset(request)
            tokens.append(self.test_credentials.password_reset_token)
        
        # Verify all tokens are unique
        assert len(set(tokens)) == len(tokens), "Password reset tokens should be unique"
        
        # Verify all tokens are non-empty strings
        for token in tokens:
            assert isinstance(token, str)
            assert len(token) > 0
    
    @pytest.mark.asyncio
    async def test_password_reset_expiry_time_setting(self):
        """Test that password reset expiry time is set correctly"""
        # Mock database queries
        mock_user_result = Mock()
        mock_user_result.scalar_one_or_none.return_value = self.test_user
        self.mock_main_db.execute = AsyncMock(return_value=mock_user_result)
        
        mock_creds_result = Mock()
        mock_creds_result.scalar_one_or_none.return_value = self.test_credentials
        self.mock_credentials_db.execute = AsyncMock(return_value=mock_creds_result)
        
        self.mock_email_service.send_password_reset_email = AsyncMock(return_value=True)
        
        request = PasswordResetRequest(email="test@example.com")
        
        before_request = datetime.utcnow()
        await self.auth_service.request_password_reset(request)
        after_request = datetime.utcnow()
        
        # Verify expiry time is set correctly (60 minutes from now)
        expected_expiry_min = before_request + timedelta(minutes=60)
        expected_expiry_max = after_request + timedelta(minutes=60)
        
        assert expected_expiry_min <= self.test_credentials.password_reset_expires_at <= expected_expiry_max
    
    @pytest.mark.asyncio
    async def test_password_hash_verification_after_reset(self):
        """Test that new password hash can be verified after reset"""
        # Setup credentials with valid reset token
        reset_token = "valid_token_123"
        self.test_credentials.password_reset_token = reset_token
        self.test_credentials.password_reset_expires_at = datetime.utcnow() + timedelta(minutes=30)
        
        # Mock database queries
        mock_creds_result = Mock()
        mock_creds_result.scalar_one_or_none.return_value = self.test_credentials
        self.mock_credentials_db.execute = AsyncMock(return_value=mock_creds_result)
        
        mock_user_result = Mock()
        mock_user_result.scalar_one_or_none.return_value = self.test_user
        self.mock_main_db.execute = AsyncMock(return_value=mock_user_result)
        
        new_password = "NewSecurePassword123"
        request = PasswordResetConfirm(
            token=reset_token,
            new_password=new_password
        )
        
        await self.auth_service.confirm_password_reset(request)
        
        # Verify the new password can be verified with the stored hash and salt
        password_with_salt = new_password + self.test_credentials.salt
        assert verify_password(password_with_salt, self.test_credentials.password_hash)
        
        # Verify old password no longer works
        old_password_with_old_salt = "old_password" + "old_salt"
        assert not verify_password(old_password_with_old_salt, self.test_credentials.password_hash) 