"""
Unit tests for Email Service

This test suite verifies:
1. Email service initialization and configuration
2. Password reset email sending
3. Welcome email sending
4. Email validation
5. Mock mode functionality
6. Error handling for SendGrid failures
"""
import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException, status

from app.services.email_service import EmailService


class TestEmailService:
    """Test suite for EmailService class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Clear environment variables for clean testing
        self.original_env = {}
        for key in ["SENDGRID_API_KEY", "FROM_EMAIL", "FROM_NAME", "FRONTEND_URL"]:
            self.original_env[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]
    
    def teardown_method(self):
        """Clean up after tests"""
        # Restore original environment variables
        for key, value in self.original_env.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]
    
    def test_email_service_init_without_api_key(self):
        """Test email service initialization without API key (mock mode)"""
        email_service = EmailService()
        
        assert email_service.client is None
        assert email_service.from_email == "noreply@menscircle.app"
        assert email_service.from_name == "Men's Circle Management"
    
    @patch('app.services.email_service.SendGridAPIClient')
    def test_email_service_init_with_api_key(self, mock_sendgrid_client):
        """Test email service initialization with API key"""
        os.environ["SENDGRID_API_KEY"] = "test_api_key"
        os.environ["FROM_EMAIL"] = "test@example.com"
        os.environ["FROM_NAME"] = "Test Service"
        
        email_service = EmailService()
        
        assert email_service.client is not None
        assert email_service.from_email == "test@example.com"
        assert email_service.from_name == "Test Service"
        mock_sendgrid_client.assert_called_once_with(api_key="test_api_key")
    
    @pytest.mark.asyncio
    async def test_send_password_reset_email_mock_mode(self):
        """Test password reset email sending in mock mode"""
        email_service = EmailService()
        
        result = await email_service.send_password_reset_email(
            to_email="test@example.com",
            first_name="John",
            reset_token="test_token_123"
        )
        
        assert result is True
    
    @patch('app.services.email_service.SendGridAPIClient')
    @pytest.mark.asyncio
    async def test_send_password_reset_email_success(self, mock_sendgrid_client):
        """Test successful password reset email sending"""
        # Mock SendGrid client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 202
        mock_client.send.return_value = mock_response
        mock_sendgrid_client.return_value = mock_client
        
        os.environ["SENDGRID_API_KEY"] = "test_api_key"
        os.environ["FRONTEND_URL"] = "https://example.com"
        
        email_service = EmailService()
        
        result = await email_service.send_password_reset_email(
            to_email="test@example.com",
            first_name="John",
            reset_token="test_token_123"
        )
        
        assert result is True
        mock_client.send.assert_called_once()
        
        # Verify the email content was properly constructed
        call_args = mock_client.send.call_args[0][0]  # Get the Mail object
        assert "test@example.com" in str(call_args.to)
        assert "Reset Your Men's Circle Password" in str(call_args.subject)
    
    @patch('app.services.email_service.SendGridAPIClient')
    @pytest.mark.asyncio
    async def test_send_password_reset_email_sendgrid_error(self, mock_sendgrid_client):
        """Test password reset email sending with SendGrid error"""
        from sendgrid.exceptions import SendGridException
        
        # Mock SendGrid client to raise exception
        mock_client = Mock()
        mock_client.send.side_effect = SendGridException("API error")
        mock_sendgrid_client.return_value = mock_client
        
        os.environ["SENDGRID_API_KEY"] = "test_api_key"
        
        email_service = EmailService()
        
        with pytest.raises(HTTPException) as exc_info:
            await email_service.send_password_reset_email(
                to_email="test@example.com",
                first_name="John",
                reset_token="test_token_123"
            )
        
        assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "Email service temporarily unavailable" in str(exc_info.value.detail)
    
    @patch('app.services.email_service.SendGridAPIClient')
    @pytest.mark.asyncio
    async def test_send_password_reset_email_bad_status_code(self, mock_sendgrid_client):
        """Test password reset email sending with bad status code"""
        # Mock SendGrid client with bad status code
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 400
        mock_client.send.return_value = mock_response
        mock_sendgrid_client.return_value = mock_client
        
        os.environ["SENDGRID_API_KEY"] = "test_api_key"
        
        email_service = EmailService()
        
        with pytest.raises(HTTPException) as exc_info:
            await email_service.send_password_reset_email(
                to_email="test@example.com",
                first_name="John",
                reset_token="test_token_123"
            )
        
        assert exc_info.value.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "Email service temporarily unavailable" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_send_welcome_email_mock_mode(self):
        """Test welcome email sending in mock mode"""
        email_service = EmailService()
        
        result = await email_service.send_welcome_email(
            to_email="test@example.com",
            first_name="John"
        )
        
        assert result is True
    
    @patch('app.services.email_service.SendGridAPIClient')
    @pytest.mark.asyncio
    async def test_send_welcome_email_success(self, mock_sendgrid_client):
        """Test successful welcome email sending"""
        # Mock SendGrid client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.send.return_value = mock_response
        mock_sendgrid_client.return_value = mock_client
        
        os.environ["SENDGRID_API_KEY"] = "test_api_key"
        
        email_service = EmailService()
        
        result = await email_service.send_welcome_email(
            to_email="test@example.com",
            first_name="John"
        )
        
        assert result is True
        mock_client.send.assert_called_once()
    
    @patch('app.services.email_service.SendGridAPIClient')
    @pytest.mark.asyncio
    async def test_send_welcome_email_error_no_exception(self, mock_sendgrid_client):
        """Test welcome email error handling (should not raise exception)"""
        # Mock SendGrid client to raise exception
        mock_client = Mock()
        mock_client.send.side_effect = Exception("Network error")
        mock_sendgrid_client.return_value = mock_client
        
        os.environ["SENDGRID_API_KEY"] = "test_api_key"
        
        email_service = EmailService()
        
        # Welcome email errors should not raise exceptions
        result = await email_service.send_welcome_email(
            to_email="test@example.com",
            first_name="John"
        )
        
        assert result is False
    
    def test_validate_email_address_valid(self):
        """Test email validation with valid addresses"""
        email_service = EmailService()
        
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@numbers.com"
        ]
        
        for email in valid_emails:
            assert email_service.validate_email_address(email) is True
    
    def test_validate_email_address_invalid(self):
        """Test email validation with invalid addresses"""
        email_service = EmailService()
        
        invalid_emails = [
            "invalid",
            "@example.com",
            "test@",
            "test.example.com",
            "test@.com",
            ""
        ]
        
        for email in invalid_emails:
            assert email_service.validate_email_address(email) is False
    
    @patch('app.services.email_service.SendGridAPIClient')
    @pytest.mark.asyncio
    async def test_send_email_internal_method_html_content(self, mock_sendgrid_client):
        """Test internal _send_email method with HTML content"""
        # Mock SendGrid client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 201
        mock_client.send.return_value = mock_response
        mock_sendgrid_client.return_value = mock_client
        
        os.environ["SENDGRID_API_KEY"] = "test_api_key"
        
        email_service = EmailService()
        
        result = await email_service._send_email(
            to_email="test@example.com",
            subject="Test Subject",
            plain_text="Plain text content",
            html_content="<h1>HTML content</h1>"
        )
        
        assert result is True
        mock_client.send.assert_called_once()
    
    @patch('app.services.email_service.SendGridAPIClient')
    @pytest.mark.asyncio
    async def test_send_email_internal_method_plain_text_only(self, mock_sendgrid_client):
        """Test internal _send_email method with plain text only"""
        # Mock SendGrid client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_client.send.return_value = mock_response
        mock_sendgrid_client.return_value = mock_client
        
        os.environ["SENDGRID_API_KEY"] = "test_api_key"
        
        email_service = EmailService()
        
        result = await email_service._send_email(
            to_email="test@example.com",
            subject="Test Subject",
            plain_text="Plain text content"
        )
        
        assert result is True
        mock_client.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_email_internal_method_mock_mode(self):
        """Test internal _send_email method in mock mode"""
        email_service = EmailService()
        
        result = await email_service._send_email(
            to_email="test@example.com",
            subject="Test Subject",
            plain_text="Plain text content"
        )
        
        assert result is True
    
    @patch('app.services.email_service.SendGridAPIClient')
    @pytest.mark.asyncio
    async def test_send_email_unexpected_error(self, mock_sendgrid_client):
        """Test internal _send_email method with unexpected error"""
        # Mock SendGrid client to raise unexpected exception
        mock_client = Mock()
        mock_client.send.side_effect = Exception("Unexpected error")
        mock_sendgrid_client.return_value = mock_client
        
        os.environ["SENDGRID_API_KEY"] = "test_api_key"
        
        email_service = EmailService()
        
        with pytest.raises(HTTPException) as exc_info:
            await email_service._send_email(
                to_email="test@example.com",
                subject="Test Subject",
                plain_text="Plain text content"
            )
        
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to send email" in str(exc_info.value.detail)
    
    def test_get_email_service_dependency(self):
        """Test the dependency injection function"""
        from app.services.email_service import get_email_service
        
        email_service = get_email_service()
        
        assert isinstance(email_service, EmailService)
    
    @pytest.mark.asyncio
    async def test_password_reset_email_content_verification(self):
        """Test that password reset email contains expected content"""
        email_service = EmailService()
        
        # We'll capture the content by mocking the _send_email method
        original_send_email = email_service._send_email
        captured_content = {}
        
        async def mock_send_email(to_email, subject, plain_text, html_content=None):
            captured_content['to_email'] = to_email
            captured_content['subject'] = subject
            captured_content['plain_text'] = plain_text
            captured_content['html_content'] = html_content
            return True
        
        email_service._send_email = mock_send_email
        
        result = await email_service.send_password_reset_email(
            to_email="john@example.com",
            first_name="John",
            reset_token="abc123token"
        )
        
        assert result is True
        assert captured_content['to_email'] == "john@example.com"
        assert "Reset Your Men's Circle Password" in captured_content['subject']
        assert "Hi John" in captured_content['plain_text']
        assert "abc123token" in captured_content['plain_text']
        assert "1 hour" in captured_content['plain_text']
        assert captured_content['html_content'] is not None
        assert "John" in captured_content['html_content']
        assert "abc123token" in captured_content['html_content']
    
    @pytest.mark.asyncio
    async def test_welcome_email_content_verification(self):
        """Test that welcome email contains expected content"""
        email_service = EmailService()
        
        # We'll capture the content by mocking the _send_email method
        captured_content = {}
        
        async def mock_send_email(to_email, subject, plain_text, html_content=None):
            captured_content['to_email'] = to_email
            captured_content['subject'] = subject
            captured_content['plain_text'] = plain_text
            captured_content['html_content'] = html_content
            return True
        
        email_service._send_email = mock_send_email
        
        result = await email_service.send_welcome_email(
            to_email="jane@example.com",
            first_name="Jane"
        )
        
        assert result is True
        assert captured_content['to_email'] == "jane@example.com"
        assert "Welcome to Men's Circle!" in captured_content['subject']
        assert "Hi Jane" in captured_content['plain_text']
        assert "Welcome to Men's Circle!" in captured_content['plain_text']
        assert captured_content['html_content'] is not None
        assert "Jane" in captured_content['html_content'] 