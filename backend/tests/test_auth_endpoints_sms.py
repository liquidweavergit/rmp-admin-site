"""
Integration tests for SMS verification API endpoints
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
from app.models.user import User
from app.models.credentials import UserCredentials


class TestSMSVerificationEndpoints:
    """Test cases for SMS verification API endpoints"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        
        # Test data
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
    
    @patch('app.services.auth_service.get_auth_service')
    def test_send_sms_verification_success(self, mock_get_auth_service):
        """Test successful SMS verification code sending via API"""
        # Mock auth service
        mock_auth_service = Mock()
        mock_auth_service.send_phone_verification_sms.return_value = {
            "success": True,
            "message": "Verification code sent successfully",
            "expires_at": datetime.utcnow() + timedelta(minutes=10)
        }
        mock_get_auth_service.return_value = mock_auth_service
        
        # Test request
        response = self.client.post(
            "/api/v1/auth/send-sms-verification",
            json={"phone": "+15551234567"}
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "sent successfully" in data["message"]
        assert "expires_at" in data
        
        # Verify service was called
        mock_auth_service.send_phone_verification_sms.assert_called_once()
    
    @patch('app.services.auth_service.get_auth_service')
    def test_send_sms_verification_invalid_phone(self, mock_get_auth_service):
        """Test SMS sending with invalid phone number via API"""
        # Test request with invalid phone
        response = self.client.post(
            "/api/v1/auth/send-sms-verification",
            json={"phone": "123"}  # Too short
        )
        
        # Should fail validation before reaching service
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    @patch('app.services.auth_service.get_auth_service')
    def test_send_sms_verification_user_not_found(self, mock_get_auth_service):
        """Test SMS sending when user not found via API"""
        from fastapi import HTTPException, status
        
        # Mock auth service to raise exception
        mock_auth_service = Mock()
        mock_auth_service.send_phone_verification_sms.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone number not found in system"
        )
        mock_get_auth_service.return_value = mock_auth_service
        
        # Test request
        response = self.client.post(
            "/api/v1/auth/send-sms-verification",
            json={"phone": "+15551234567"}
        )
        
        # Assertions
        assert response.status_code == 404
        data = response.json()
        assert "Phone number not found in system" in data["detail"]
    
    @patch('app.services.auth_service.get_auth_service')
    def test_send_sms_verification_too_many_attempts(self, mock_get_auth_service):
        """Test SMS sending with too many attempts via API"""
        from fastapi import HTTPException, status
        
        # Mock auth service to raise rate limit exception
        mock_auth_service = Mock()
        mock_auth_service.send_phone_verification_sms.side_effect = HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many SMS verification attempts. Please try again later."
        )
        mock_get_auth_service.return_value = mock_auth_service
        
        # Test request
        response = self.client.post(
            "/api/v1/auth/send-sms-verification",
            json={"phone": "+15551234567"}
        )
        
        # Assertions
        assert response.status_code == 429
        data = response.json()
        assert "Too many SMS verification attempts" in data["detail"]
    
    @patch('app.services.auth_service.get_auth_service')
    def test_send_sms_verification_service_error(self, mock_get_auth_service):
        """Test SMS sending with service error via API"""
        # Mock auth service to raise unexpected exception
        mock_auth_service = Mock()
        mock_auth_service.send_phone_verification_sms.side_effect = Exception("Unexpected error")
        mock_get_auth_service.return_value = mock_auth_service
        
        # Test request
        response = self.client.post(
            "/api/v1/auth/send-sms-verification",
            json={"phone": "+15551234567"}
        )
        
        # Assertions
        assert response.status_code == 500
        data = response.json()
        assert "Failed to send SMS verification code" in data["detail"]
    
    @patch('app.services.auth_service.get_auth_service')
    def test_verify_sms_code_success(self, mock_get_auth_service):
        """Test successful SMS code verification via API"""
        # Mock auth service
        mock_auth_service = Mock()
        mock_auth_service.verify_phone_sms_code.return_value = {
            "success": True,
            "message": "Phone number verified successfully"
        }
        mock_get_auth_service.return_value = mock_auth_service
        
        # Test request
        response = self.client.post(
            "/api/v1/auth/verify-sms-code",
            json={
                "phone": "+15551234567",
                "code": "123456"
            }
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "verified successfully" in data["message"]
        
        # Verify service was called
        mock_auth_service.verify_phone_sms_code.assert_called_once()
    
    @patch('app.services.auth_service.get_auth_service')
    def test_verify_sms_code_invalid_format(self, mock_get_auth_service):
        """Test SMS verification with invalid code format via API"""
        # Test request with invalid code format
        response = self.client.post(
            "/api/v1/auth/verify-sms-code",
            json={
                "phone": "+15551234567",
                "code": "12345"  # Too short
            }
        )
        
        # Should fail validation before reaching service
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    @patch('app.services.auth_service.get_auth_service')
    def test_verify_sms_code_invalid_code(self, mock_get_auth_service):
        """Test SMS verification with invalid code via API"""
        from fastapi import HTTPException, status
        
        # Mock auth service to raise exception
        mock_auth_service = Mock()
        mock_auth_service.verify_phone_sms_code.side_effect = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
        mock_get_auth_service.return_value = mock_auth_service
        
        # Test request
        response = self.client.post(
            "/api/v1/auth/verify-sms-code",
            json={
                "phone": "+15551234567",
                "code": "123456"
            }
        )
        
        # Assertions
        assert response.status_code == 400
        data = response.json()
        assert "Invalid verification code" in data["detail"]
    
    @patch('app.services.auth_service.get_auth_service')
    def test_verify_sms_code_expired(self, mock_get_auth_service):
        """Test SMS verification with expired code via API"""
        from fastapi import HTTPException, status
        
        # Mock auth service to raise exception
        mock_auth_service = Mock()
        mock_auth_service.verify_phone_sms_code.side_effect = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired. Please request a new code."
        )
        mock_get_auth_service.return_value = mock_auth_service
        
        # Test request
        response = self.client.post(
            "/api/v1/auth/verify-sms-code",
            json={
                "phone": "+15551234567",
                "code": "123456"
            }
        )
        
        # Assertions
        assert response.status_code == 400
        data = response.json()
        assert "Verification code has expired" in data["detail"]
    
    @patch('app.services.auth_service.get_auth_service')
    def test_verify_sms_code_no_code_found(self, mock_get_auth_service):
        """Test SMS verification when no code exists via API"""
        from fastapi import HTTPException, status
        
        # Mock auth service to raise exception
        mock_auth_service = Mock()
        mock_auth_service.verify_phone_sms_code.side_effect = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification code found. Please request a new code."
        )
        mock_get_auth_service.return_value = mock_auth_service
        
        # Test request
        response = self.client.post(
            "/api/v1/auth/verify-sms-code",
            json={
                "phone": "+15551234567",
                "code": "123456"
            }
        )
        
        # Assertions
        assert response.status_code == 400
        data = response.json()
        assert "No verification code found" in data["detail"]
    
    @patch('app.services.auth_service.get_auth_service')
    def test_verify_sms_code_user_not_found(self, mock_get_auth_service):
        """Test SMS verification when user not found via API"""
        from fastapi import HTTPException, status
        
        # Mock auth service to raise exception
        mock_auth_service = Mock()
        mock_auth_service.verify_phone_sms_code.side_effect = HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone number not found in system"
        )
        mock_get_auth_service.return_value = mock_auth_service
        
        # Test request
        response = self.client.post(
            "/api/v1/auth/verify-sms-code",
            json={
                "phone": "+15551234567",
                "code": "123456"
            }
        )
        
        # Assertions
        assert response.status_code == 404
        data = response.json()
        assert "Phone number not found in system" in data["detail"]
    
    @patch('app.services.auth_service.get_auth_service')
    def test_verify_sms_code_service_error(self, mock_get_auth_service):
        """Test SMS verification with service error via API"""
        # Mock auth service to raise unexpected exception
        mock_auth_service = Mock()
        mock_auth_service.verify_phone_sms_code.side_effect = Exception("Unexpected error")
        mock_get_auth_service.return_value = mock_auth_service
        
        # Test request
        response = self.client.post(
            "/api/v1/auth/verify-sms-code",
            json={
                "phone": "+15551234567",
                "code": "123456"
            }
        )
        
        # Assertions
        assert response.status_code == 500
        data = response.json()
        assert "Failed to verify SMS code" in data["detail"]
    
    def test_send_sms_verification_missing_phone(self):
        """Test SMS sending with missing phone number"""
        # Test request without phone
        response = self.client.post(
            "/api/v1/auth/send-sms-verification",
            json={}
        )
        
        # Should fail validation
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_verify_sms_code_missing_fields(self):
        """Test SMS verification with missing fields"""
        # Test request without code
        response = self.client.post(
            "/api/v1/auth/verify-sms-code",
            json={"phone": "+15551234567"}
        )
        
        # Should fail validation
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        
        # Test request without phone
        response = self.client.post(
            "/api/v1/auth/verify-sms-code",
            json={"code": "123456"}
        )
        
        # Should fail validation
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data 