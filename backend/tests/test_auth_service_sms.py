"""
Unit tests for SMS verification functionality in AuthService (Fixed)
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from app.services.auth_service import AuthService
from app.services.sms_service import SMSService
from app.models.user import User
from app.models.credentials import UserCredentials
from app.schemas.auth import SendVerificationSMSRequest, VerifyPhoneSMSRequest, SMSVerificationResponse


class TestAuthServiceSMSFixed:
    """Test cases for SMS verification in AuthService (Fixed)"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_main_db = AsyncMock()
        self.mock_credentials_db = AsyncMock()
        self.mock_sms_service = Mock(spec=SMSService)
        
        self.auth_service = AuthService(
            main_db=self.mock_main_db,
            credentials_db=self.mock_credentials_db,
            sms_service=self.mock_sms_service
        )
        
        # Mock user and credentials
        self.test_user = User(
            id=1,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            phone="+15551234567",
            is_active=True,
            phone_verified=False
        )
        
        self.test_credentials = UserCredentials(
            user_id=1,
            password_hash="hashed_password",
            salt="salt",
            phone_verification_attempts=0
        )
    
    @pytest.mark.asyncio
    async def test_send_phone_verification_sms_success(self):
        """Test successful SMS verification code sending"""
        # Setup mocks
        self.mock_sms_service.validate_phone_number.return_value = True
        self.mock_sms_service.generate_verification_code.return_value = "123456"
        self.mock_sms_service.send_verification_code = AsyncMock(return_value=True)
        
        # Mock database queries with proper async mocking
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = self.test_user
        self.mock_main_db.execute = AsyncMock(return_value=mock_result)
        
        mock_creds_result = Mock()
        mock_creds_result.scalar_one_or_none.return_value = self.test_credentials
        self.mock_credentials_db.execute = AsyncMock(return_value=mock_creds_result)
        
        # Test request
        request = SendVerificationSMSRequest(phone="+15551234567")
        
        result = await self.auth_service.send_phone_verification_sms(request)
        
        # Assertions
        assert isinstance(result, SMSVerificationResponse)
        assert result.success is True
        assert "sent successfully" in result.message
        assert result.expires_at is not None
        
        # Verify SMS service calls
        self.mock_sms_service.validate_phone_number.assert_called_once_with("+15551234567")
        self.mock_sms_service.generate_verification_code.assert_called_once()
        self.mock_sms_service.send_verification_code.assert_called_once_with("+15551234567", "123456")
        
        # Verify database updates
        assert self.test_credentials.phone_verification_code == "123456"
        assert self.test_credentials.phone_verification_attempts == 1
        assert self.test_credentials.phone_verification_expires_at is not None
        self.mock_credentials_db.commit.assert_called()
    
    @pytest.mark.asyncio
    async def test_send_phone_verification_sms_invalid_phone(self):
        """Test SMS sending with invalid phone number"""
        self.mock_sms_service.validate_phone_number.return_value = False
        
        # Use a phone that passes schema validation but fails service validation
        request = SendVerificationSMSRequest(phone="+1234567890")
        
        with pytest.raises(HTTPException) as exc_info:
            await self.auth_service.send_phone_verification_sms(request)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid phone number format" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_send_phone_verification_sms_user_not_found(self):
        """Test SMS sending when user not found"""
        self.mock_sms_service.validate_phone_number.return_value = True
        
        # Mock database query to return None (user not found)
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        self.mock_main_db.execute = AsyncMock(return_value=mock_result)
        
        request = SendVerificationSMSRequest(phone="+15551234567")
        
        with pytest.raises(HTTPException) as exc_info:
            await self.auth_service.send_phone_verification_sms(request)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "Phone number not found in system" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_send_phone_verification_sms_too_many_attempts(self):
        """Test SMS sending when too many attempts made"""
        self.mock_sms_service.validate_phone_number.return_value = True
        
        # Set up user with too many attempts
        self.test_credentials.phone_verification_attempts = 3  # MAX_SMS_ATTEMPTS
        
        # Mock database queries
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = self.test_user
        self.mock_main_db.execute = AsyncMock(return_value=mock_result)
        
        mock_creds_result = Mock()
        mock_creds_result.scalar_one_or_none.return_value = self.test_credentials
        self.mock_credentials_db.execute = AsyncMock(return_value=mock_creds_result)
        
        request = SendVerificationSMSRequest(phone="+15551234567")
        
        with pytest.raises(HTTPException) as exc_info:
            await self.auth_service.send_phone_verification_sms(request)
        
        assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert "Too many SMS verification attempts" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_verify_phone_sms_code_success(self):
        """Test successful SMS code verification"""
        # Set up credentials with valid code
        self.test_credentials.phone_verification_code = "123456"
        self.test_credentials.phone_verification_expires_at = datetime.utcnow() + timedelta(minutes=5)
        
        self.mock_sms_service.is_code_expired.return_value = False
        
        # Mock database queries
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = self.test_user
        self.mock_main_db.execute = AsyncMock(return_value=mock_result)
        
        mock_creds_result = Mock()
        mock_creds_result.scalar_one_or_none.return_value = self.test_credentials
        self.mock_credentials_db.execute = AsyncMock(return_value=mock_creds_result)
        
        request = VerifyPhoneSMSRequest(phone="+15551234567", code="123456")
        
        result = await self.auth_service.verify_phone_sms_code(request)
        
        # Assertions
        assert isinstance(result, SMSVerificationResponse)
        assert result.success is True
        assert "verified successfully" in result.message
        
        # Verify user phone_verified flag is set
        assert self.test_user.phone_verified is True
        
        # Verify verification code is cleared
        assert self.test_credentials.phone_verification_code is None
        assert self.test_credentials.phone_verification_expires_at is None
        assert self.test_credentials.phone_verification_attempts == 0
        
        # Verify database commits
        self.mock_main_db.commit.assert_called()
        self.mock_credentials_db.commit.assert_called()
    
    @pytest.mark.asyncio
    async def test_verify_phone_sms_code_invalid_code(self):
        """Test SMS verification with invalid code"""
        # Set up credentials with different code
        self.test_credentials.phone_verification_code = "654321"
        self.test_credentials.phone_verification_expires_at = datetime.utcnow() + timedelta(minutes=5)
        
        self.mock_sms_service.is_code_expired.return_value = False
        
        # Mock database queries
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = self.test_user
        self.mock_main_db.execute = AsyncMock(return_value=mock_result)
        
        mock_creds_result = Mock()
        mock_creds_result.scalar_one_or_none.return_value = self.test_credentials
        self.mock_credentials_db.execute = AsyncMock(return_value=mock_creds_result)
        
        request = VerifyPhoneSMSRequest(phone="+15551234567", code="123456")
        
        with pytest.raises(HTTPException) as exc_info:
            await self.auth_service.verify_phone_sms_code(request)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid verification code" in str(exc_info.value.detail) 