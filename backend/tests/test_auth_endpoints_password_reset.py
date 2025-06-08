"""
Unit tests for Password Reset API endpoints

This test suite verifies:
1. Password reset request endpoint
2. Password reset confirmation endpoint
3. Request validation and error handling
4. Integration with auth service
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException, status

from app.main import app


class TestPasswordResetEndpoints:
    """Test cases for password reset API endpoints"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
    
    @patch('app.services.auth_service.get_auth_service')
    def test_request_password_reset_success(self, mock_get_auth_service):
        """Test successful password reset request via API"""
        # Mock auth service
        mock_auth_service = Mock()
        mock_auth_service.request_password_reset.return_value = {
            "message": "If the email address exists in our system, a password reset link has been sent."
        }
        mock_get_auth_service.return_value = mock_auth_service
        
        # Test request
        response = self.client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": "test@example.com"}
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "password reset link has been sent" in data["message"]
        
        # Verify service was called
        mock_auth_service.request_password_reset.assert_called_once()
        call_args = mock_auth_service.request_password_reset.call_args[0][0]
        assert call_args.email == "test@example.com"
    
    def test_request_password_reset_invalid_email_format(self):
        """Test password reset request with invalid email format"""
        # Test request with invalid email
        response = self.client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": "invalid-email"}
        )
        
        # Should return validation error
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert any("email" in str(error).lower() for error in data["detail"])
    
    def test_request_password_reset_missing_email(self):
        """Test password reset request with missing email"""
        # Test request without email
        response = self.client.post(
            "/api/v1/auth/password-reset/request",
            json={}
        )
        
        # Should return validation error
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    @patch('app.services.auth_service.get_auth_service')
    def test_request_password_reset_too_many_attempts(self, mock_get_auth_service):
        """Test password reset request with too many attempts via API"""
        # Mock auth service to raise rate limit exception
        mock_auth_service = Mock()
        mock_auth_service.request_password_reset.side_effect = HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password reset attempts. Please try again later."
        )
        mock_get_auth_service.return_value = mock_auth_service
        
        # Test request
        response = self.client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": "test@example.com"}
        )
        
        # Assertions
        assert response.status_code == 429
        data = response.json()
        assert "Too many password reset attempts" in data["detail"]
    
    @patch('app.services.auth_service.get_auth_service')
    def test_request_password_reset_service_error(self, mock_get_auth_service):
        """Test password reset request with service error via API"""
        # Mock auth service to raise unexpected exception
        mock_auth_service = Mock()
        mock_auth_service.request_password_reset.side_effect = Exception("Unexpected error")
        mock_get_auth_service.return_value = mock_auth_service
        
        # Test request
        response = self.client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": "test@example.com"}
        )
        
        # Assertions
        assert response.status_code == 500
        data = response.json()
        assert "Failed to process password reset request" in data["detail"]
    
    @patch('app.services.auth_service.get_auth_service')
    def test_confirm_password_reset_success(self, mock_get_auth_service):
        """Test successful password reset confirmation via API"""
        # Mock auth service
        mock_auth_service = Mock()
        mock_auth_service.confirm_password_reset.return_value = {
            "message": "Password has been successfully reset. Please log in with your new password."
        }
        mock_get_auth_service.return_value = mock_auth_service
        
        # Test request
        response = self.client.post(
            "/api/v1/auth/password-reset/confirm",
            json={
                "token": "valid_reset_token_123",
                "new_password": "NewSecurePassword123"
            }
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "Password has been successfully reset" in data["message"]
        
        # Verify service was called
        mock_auth_service.confirm_password_reset.assert_called_once()
        call_args = mock_auth_service.confirm_password_reset.call_args[0][0]
        assert call_args.token == "valid_reset_token_123"
        assert call_args.new_password == "NewSecurePassword123"
    
    def test_confirm_password_reset_invalid_token_format(self):
        """Test password reset confirmation with invalid token format"""
        # Test request with empty token
        response = self.client.post(
            "/api/v1/auth/password-reset/confirm",
            json={
                "token": "",
                "new_password": "NewSecurePassword123"
            }
        )
        
        # Should return validation error
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    def test_confirm_password_reset_weak_password(self):
        """Test password reset confirmation with weak password"""
        # Test request with weak password
        response = self.client.post(
            "/api/v1/auth/password-reset/confirm",
            json={
                "token": "valid_token_123",
                "new_password": "weak"
            }
        )
        
        # Should return validation error
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert any("password" in str(error).lower() for error in data["detail"])
    
    def test_confirm_password_reset_missing_fields(self):
        """Test password reset confirmation with missing fields"""
        # Test request without token
        response = self.client.post(
            "/api/v1/auth/password-reset/confirm",
            json={"new_password": "NewSecurePassword123"}
        )
        
        # Should return validation error
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        
        # Test request without password
        response = self.client.post(
            "/api/v1/auth/password-reset/confirm",
            json={"token": "valid_token_123"}
        )
        
        # Should return validation error
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    @patch('app.services.auth_service.get_auth_service')
    def test_confirm_password_reset_invalid_token(self, mock_get_auth_service):
        """Test password reset confirmation with invalid token via API"""
        # Mock auth service to raise invalid token exception
        mock_auth_service = Mock()
        mock_auth_service.confirm_password_reset.side_effect = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
        mock_get_auth_service.return_value = mock_auth_service
        
        # Test request
        response = self.client.post(
            "/api/v1/auth/password-reset/confirm",
            json={
                "token": "invalid_token",
                "new_password": "NewSecurePassword123"
            }
        )
        
        # Assertions
        assert response.status_code == 400
        data = response.json()
        assert "Invalid or expired reset token" in data["detail"]
    
    @patch('app.services.auth_service.get_auth_service')
    def test_confirm_password_reset_expired_token(self, mock_get_auth_service):
        """Test password reset confirmation with expired token via API"""
        # Mock auth service to raise expired token exception
        mock_auth_service = Mock()
        mock_auth_service.confirm_password_reset.side_effect = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has expired"
        )
        mock_get_auth_service.return_value = mock_auth_service
        
        # Test request
        response = self.client.post(
            "/api/v1/auth/password-reset/confirm",
            json={
                "token": "expired_token",
                "new_password": "NewSecurePassword123"
            }
        )
        
        # Assertions
        assert response.status_code == 400
        data = response.json()
        assert "Password reset token has expired" in data["detail"]
    
    @patch('app.services.auth_service.get_auth_service')
    def test_confirm_password_reset_service_error(self, mock_get_auth_service):
        """Test password reset confirmation with service error via API"""
        # Mock auth service to raise unexpected exception
        mock_auth_service = Mock()
        mock_auth_service.confirm_password_reset.side_effect = Exception("Unexpected error")
        mock_get_auth_service.return_value = mock_auth_service
        
        # Test request
        response = self.client.post(
            "/api/v1/auth/password-reset/confirm",
            json={
                "token": "valid_token_123",
                "new_password": "NewSecurePassword123"
            }
        )
        
        # Assertions
        assert response.status_code == 500
        data = response.json()
        assert "Failed to reset password" in data["detail"]
    
    def test_password_complexity_validation(self):
        """Test password complexity validation in reset confirmation"""
        # Test various weak passwords
        weak_passwords = [
            "short",  # Too short
            "nouppercase123",  # No uppercase
            "NOLOWERCASE123",  # No lowercase
            "NoNumbers",  # No digits
        ]
        
        for weak_password in weak_passwords:
            response = self.client.post(
                "/api/v1/auth/password-reset/confirm",
                json={
                    "token": "valid_token_123",
                    "new_password": weak_password
                }
            )
            
            # Should return validation error
            assert response.status_code == 422
            data = response.json()
            assert "detail" in data
    
    def test_password_reset_endpoints_exist(self):
        """Test that password reset endpoints are properly registered"""
        # Test that endpoints exist by checking OPTIONS
        response = self.client.options("/api/v1/auth/password-reset/request")
        assert response.status_code in [200, 405]  # 405 if OPTIONS not implemented
        
        response = self.client.options("/api/v1/auth/password-reset/confirm")
        assert response.status_code in [200, 405]  # 405 if OPTIONS not implemented
    
    @patch('app.services.auth_service.get_auth_service')
    def test_request_password_reset_email_service_error(self, mock_get_auth_service):
        """Test password reset request when email service fails via API"""
        # Mock auth service to raise email service exception
        mock_auth_service = Mock()
        mock_auth_service.request_password_reset.side_effect = HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Email service temporarily unavailable"
        )
        mock_get_auth_service.return_value = mock_auth_service
        
        # Test request
        response = self.client.post(
            "/api/v1/auth/password-reset/request",
            json={"email": "test@example.com"}
        )
        
        # Assertions
        assert response.status_code == 503
        data = response.json()
        assert "Email service temporarily unavailable" in data["detail"] 