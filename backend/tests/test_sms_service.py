"""
Unit tests for SMS service
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from app.services.sms_service import SMSService


class TestSMSService:
    """Test cases for SMS service"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.sms_service = SMSService()
    
    def test_generate_verification_code(self):
        """Test verification code generation"""
        code = self.sms_service.generate_verification_code()
        
        # Should be 6 digits
        assert len(code) == 6
        assert code.isdigit()
        
        # Should be different each time
        code2 = self.sms_service.generate_verification_code()
        assert code != code2
    
    def test_format_phone_number_10_digits(self):
        """Test phone number formatting for 10-digit US numbers"""
        # Test various 10-digit formats
        test_cases = [
            ("5551234567", "+15551234567"),
            ("555-123-4567", "+15551234567"),
            ("(555) 123-4567", "+15551234567"),
            ("555.123.4567", "+15551234567"),
            ("555 123 4567", "+15551234567"),
        ]
        
        for input_phone, expected in test_cases:
            result = self.sms_service.format_phone_number(input_phone)
            assert result == expected
    
    def test_format_phone_number_11_digits(self):
        """Test phone number formatting for 11-digit numbers with country code"""
        # Test 11-digit numbers starting with 1
        test_cases = [
            ("15551234567", "+15551234567"),
            ("1-555-123-4567", "+15551234567"),
            ("1 (555) 123-4567", "+15551234567"),
        ]
        
        for input_phone, expected in test_cases:
            result = self.sms_service.format_phone_number(input_phone)
            assert result == expected
    
    def test_format_phone_number_international(self):
        """Test phone number formatting for international numbers"""
        # Test numbers that are already formatted or international
        test_cases = [
            ("+15551234567", "+15551234567"),
            ("+447700900123", "+447700900123"),  # UK number
            ("447700900123", "+447700900123"),   # UK without +
        ]
        
        for input_phone, expected in test_cases:
            result = self.sms_service.format_phone_number(input_phone)
            assert result == expected
    
    def test_validate_phone_number_valid(self):
        """Test phone number validation for valid numbers"""
        valid_numbers = [
            "5551234567",           # 10 digits
            "15551234567",          # 11 digits
            "+15551234567",         # With country code
            "(555) 123-4567",       # Formatted
            "555-123-4567",         # Dashed
            "+447700900123",        # International
        ]
        
        for phone in valid_numbers:
            assert self.sms_service.validate_phone_number(phone) is True
    
    def test_validate_phone_number_invalid(self):
        """Test phone number validation for invalid numbers"""
        invalid_numbers = [
            "",                     # Empty
            None,                   # None
            "123",                  # Too short
            "12345678901234567890", # Too long
            "abcdefghij",           # Non-numeric
            "555-123",              # Incomplete
        ]
        
        for phone in invalid_numbers:
            assert self.sms_service.validate_phone_number(phone) is False
    
    def test_is_code_expired_not_expired(self):
        """Test code expiry check for non-expired codes"""
        # Code created 5 minutes ago, expires in 10 minutes
        created_at = datetime.utcnow() - timedelta(minutes=5)
        assert self.sms_service.is_code_expired(created_at, 10) is False
    
    def test_is_code_expired_expired(self):
        """Test code expiry check for expired codes"""
        # Code created 15 minutes ago, expires in 10 minutes
        created_at = datetime.utcnow() - timedelta(minutes=15)
        assert self.sms_service.is_code_expired(created_at, 10) is True
    
    def test_is_code_expired_just_expired(self):
        """Test code expiry check for codes that just expired"""
        # Code created exactly 10 minutes ago
        created_at = datetime.utcnow() - timedelta(minutes=10, seconds=1)
        assert self.sms_service.is_code_expired(created_at, 10) is True
    
    @patch('app.services.sms_service.Client')
    @pytest.mark.asyncio
    async def test_send_verification_code_success(self, mock_client_class):
        """Test successful SMS sending"""
        # Mock Twilio client
        mock_client = Mock()
        mock_message = Mock()
        mock_message.sid = "SM123456789"
        mock_client.messages.create.return_value = mock_message
        mock_client_class.return_value = mock_client
        
        # Create service with mocked credentials
        with patch.dict('os.environ', {
            'TWILIO_ACCOUNT_SID': 'test_sid',
            'TWILIO_AUTH_TOKEN': 'test_token',
            'TWILIO_FROM_NUMBER': '+12345678900'
        }):
            sms_service = SMSService()
            
            result = await sms_service.send_verification_code("+15551234567", "123456")
            
            assert result is True
            mock_client.messages.create.assert_called_once()
            call_args = mock_client.messages.create.call_args
            assert call_args[1]['to'] == "+15551234567"
            assert "123456" in call_args[1]['body']
            assert call_args[1]['from_'] == "+12345678900"
    
    @pytest.mark.asyncio
    async def test_send_verification_code_mock_mode(self):
        """Test SMS sending in mock mode (no credentials)"""
        # Service without credentials should use mock mode
        with patch.dict('os.environ', {}, clear=True):
            sms_service = SMSService()
            
            result = await sms_service.send_verification_code("+15551234567", "123456")
            
            assert result is True
            assert sms_service.client is None
    
    @patch('app.services.sms_service.Client')
    @pytest.mark.asyncio
    async def test_send_verification_code_twilio_error(self, mock_client_class):
        """Test SMS sending with Twilio error"""
        from twilio.base.exceptions import TwilioException
        
        # Mock Twilio client to raise exception
        mock_client = Mock()
        mock_client.messages.create.side_effect = TwilioException("Invalid phone number")
        mock_client_class.return_value = mock_client
        
        with patch.dict('os.environ', {
            'TWILIO_ACCOUNT_SID': 'test_sid',
            'TWILIO_AUTH_TOKEN': 'test_token'
        }):
            sms_service = SMSService()
            
            with pytest.raises(HTTPException) as exc_info:
                await sms_service.send_verification_code("+15551234567", "123456")
            
            assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
            assert "SMS service temporarily unavailable" in str(exc_info.value.detail)
    
    @patch('app.services.sms_service.Client')
    @pytest.mark.asyncio
    async def test_send_verification_code_unexpected_error(self, mock_client_class):
        """Test SMS sending with unexpected error"""
        # Mock Twilio client to raise unexpected exception
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("Unexpected error")
        mock_client_class.return_value = mock_client
        
        with patch.dict('os.environ', {
            'TWILIO_ACCOUNT_SID': 'test_sid',
            'TWILIO_AUTH_TOKEN': 'test_token'
        }):
            sms_service = SMSService()
            
            with pytest.raises(HTTPException) as exc_info:
                await sms_service.send_verification_code("+15551234567", "123456")
            
            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to send verification code" in str(exc_info.value.detail)
    
    def test_get_sms_service_dependency(self):
        """Test the dependency injection function"""
        from app.services.sms_service import get_sms_service
        
        service = get_sms_service()
        assert isinstance(service, SMSService) 