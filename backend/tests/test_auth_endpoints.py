"""
Integration tests for Authentication API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from datetime import datetime

from app.main import app
from app.schemas.auth import UserCreate, UserLogin, UserResponse, TokenResponse
from app.models.user import User
from app.models.credentials import UserCredentials


class TestAuthEndpoints:
    """Test suite for authentication API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user registration data"""
        return {
            "email": "test@example.com",
            "password": "TestPassword123",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1234567890"
        }
    
    @pytest.fixture
    def sample_login_data(self):
        """Sample login data"""
        return {
            "email": "test@example.com",
            "password": "TestPassword123"
        }
    
    @pytest.fixture
    def sample_user_response(self):
        """Sample user response data"""
        return {
            "id": 1,
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1234567890",
            "is_active": True,
            "is_verified": False,
            "email_verified": False,
            "phone_verified": False,
            "created_at": datetime.utcnow().isoformat()
        }
    
    @pytest.fixture
    def sample_token_response(self):
        """Sample token response data"""
        return {
            "access_token": "sample.access.token",
            "refresh_token": "sample.refresh.token",
            "token_type": "bearer"
        }
    
    def test_register_endpoint_success(self, client, sample_user_data, sample_user_response):
        """Test successful user registration endpoint"""
        with patch('app.services.auth_service.AuthService.register_user') as mock_register:
            # Mock successful registration
            mock_register.return_value = UserResponse(**sample_user_response)
            
            # Make request
            response = client.post("/api/v1/auth/register", json=sample_user_data)
            
            # Verify response
            assert response.status_code == 201
            data = response.json()
            assert data["email"] == sample_user_data["email"]
            assert data["first_name"] == sample_user_data["first_name"]
            assert data["last_name"] == sample_user_data["last_name"]
            assert data["phone"] == sample_user_data["phone"]
            assert data["is_active"] is True
            assert data["is_verified"] is False
    
    def test_register_endpoint_email_exists(self, client, sample_user_data):
        """Test registration with existing email"""
        with patch('app.services.auth_service.AuthService.register_user') as mock_register:
            from fastapi import HTTPException, status
            # Mock email already exists
            mock_register.side_effect = HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
            
            # Make request
            response = client.post("/api/v1/auth/register", json=sample_user_data)
            
            # Verify response
            assert response.status_code == 400
            assert "Email already registered" in response.json()["detail"]
    
    def test_register_endpoint_invalid_data(self, client):
        """Test registration with invalid data"""
        invalid_data = {
            "email": "not-an-email",
            "password": "weak",
            "first_name": "",
            "last_name": ""
        }
        
        # Make request
        response = client.post("/api/v1/auth/register", json=invalid_data)
        
        # Verify response
        assert response.status_code == 422  # Validation error
    
    def test_login_endpoint_success(self, client, sample_login_data, sample_token_response):
        """Test successful login endpoint"""
        with patch('app.services.auth_service.AuthService.authenticate_user') as mock_auth:
            # Mock successful authentication
            mock_auth.return_value = TokenResponse(**sample_token_response)
            
            # Make request
            response = client.post("/api/v1/auth/login", json=sample_login_data)
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == sample_token_response["access_token"]
            assert data["refresh_token"] == sample_token_response["refresh_token"]
            assert data["token_type"] == "bearer"
    
    def test_login_endpoint_invalid_credentials(self, client, sample_login_data):
        """Test login with invalid credentials"""
        with patch('app.services.auth_service.AuthService.authenticate_user') as mock_auth:
            from fastapi import HTTPException, status
            # Mock invalid credentials
            mock_auth.side_effect = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
            
            # Make request
            response = client.post("/api/v1/auth/login", json=sample_login_data)
            
            # Verify response
            assert response.status_code == 401
            assert "Invalid email or password" in response.json()["detail"]
    
    def test_login_endpoint_account_locked(self, client, sample_login_data):
        """Test login with locked account"""
        with patch('app.services.auth_service.AuthService.authenticate_user') as mock_auth:
            from fastapi import HTTPException, status
            # Mock account locked
            mock_auth.side_effect = HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account temporarily locked due to too many failed attempts"
            )
            
            # Make request
            response = client.post("/api/v1/auth/login", json=sample_login_data)
            
            # Verify response
            assert response.status_code == 423
            assert "Account temporarily locked" in response.json()["detail"]
    
    def test_refresh_token_endpoint_success(self, client, sample_token_response):
        """Test successful token refresh endpoint"""
        with patch('app.services.auth_service.AuthService.refresh_access_token') as mock_refresh:
            # Mock successful refresh
            mock_refresh.return_value = TokenResponse(**sample_token_response)
            
            refresh_data = {"refresh_token": "valid.refresh.token"}
            
            # Make request
            response = client.post("/api/v1/auth/refresh", json=refresh_data)
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == sample_token_response["access_token"]
            assert data["refresh_token"] == sample_token_response["refresh_token"]
            assert data["token_type"] == "bearer"
    
    def test_refresh_token_endpoint_invalid_token(self, client):
        """Test token refresh with invalid token"""
        with patch('app.services.auth_service.AuthService.refresh_access_token') as mock_refresh:
            from fastapi import HTTPException, status
            # Mock invalid token
            mock_refresh.side_effect = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
            
            refresh_data = {"refresh_token": "invalid.refresh.token"}
            
            # Make request
            response = client.post("/api/v1/auth/refresh", json=refresh_data)
            
            # Verify response
            assert response.status_code == 401
            assert "Invalid refresh token" in response.json()["detail"]
    
    def test_logout_endpoint_success(self, client):
        """Test successful logout endpoint"""
        with patch('app.services.auth_service.AuthService.logout_user') as mock_logout:
            # Mock successful logout
            mock_logout.return_value = True
            
            logout_data = {"refresh_token": "valid.refresh.token"}
            
            # Make request
            response = client.post("/api/v1/auth/logout", json=logout_data)
            
            # Verify response
            assert response.status_code == 204
    
    def test_logout_endpoint_invalid_token(self, client):
        """Test logout with invalid token"""
        with patch('app.services.auth_service.AuthService.logout_user') as mock_logout:
            # Mock invalid token
            mock_logout.return_value = False
            
            logout_data = {"refresh_token": "invalid.refresh.token"}
            
            # Make request
            response = client.post("/api/v1/auth/logout", json=logout_data)
            
            # Verify response
            assert response.status_code == 400
            assert "Invalid refresh token" in response.json()["detail"]
    
    def test_get_current_user_endpoint_success(self, client, sample_user_response):
        """Test get current user endpoint with valid token"""
        with patch('app.core.deps.get_current_user') as mock_get_user:
            # Mock current user
            user = User(**{k: v for k, v in sample_user_response.items() if k != 'created_at'})
            user.created_at = datetime.utcnow()
            mock_get_user.return_value = user
            
            # Make request with authorization header
            headers = {"Authorization": "Bearer valid.access.token"}
            response = client.get("/api/v1/auth/me", headers=headers)
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == sample_user_response["email"]
            assert data["first_name"] == sample_user_response["first_name"]
            assert data["last_name"] == sample_user_response["last_name"]
    
    def test_get_current_user_endpoint_no_token(self, client):
        """Test get current user endpoint without token"""
        # Make request without authorization header
        response = client.get("/api/v1/auth/me")
        
        # Verify response
        assert response.status_code == 401
        assert "Authentication required" in response.json()["detail"]
    
    def test_get_current_user_endpoint_invalid_token(self, client):
        """Test get current user endpoint with invalid token"""
        with patch('app.core.deps.get_current_user') as mock_get_user:
            from fastapi import HTTPException, status
            # Mock invalid token
            mock_get_user.side_effect = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
            
            # Make request with invalid token
            headers = {"Authorization": "Bearer invalid.access.token"}
            response = client.get("/api/v1/auth/me", headers=headers)
            
            # Verify response
            assert response.status_code == 401
            assert "Invalid or expired token" in response.json()["detail"]
    
    def test_auth_status_endpoint_authenticated(self, client, sample_user_response):
        """Test auth status endpoint with authenticated user"""
        with patch('app.core.deps.get_current_user_optional') as mock_get_user:
            # Mock authenticated user
            user = User(**{k: v for k, v in sample_user_response.items() if k != 'created_at'})
            user.created_at = datetime.utcnow()
            mock_get_user.return_value = user
            
            # Make request with authorization header
            headers = {"Authorization": "Bearer valid.access.token"}
            response = client.get("/api/v1/auth/status", headers=headers)
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["authenticated"] is True
            assert data["user"] is not None
            assert data["user"]["email"] == sample_user_response["email"]
    
    def test_auth_status_endpoint_not_authenticated(self, client):
        """Test auth status endpoint without authentication"""
        with patch('app.core.deps.get_current_user_optional') as mock_get_user:
            # Mock no user
            mock_get_user.return_value = None
            
            # Make request without authorization header
            response = client.get("/api/v1/auth/status")
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["authenticated"] is False
            assert data["user"] is None
    
    def test_password_complexity_validation(self, client):
        """Test password complexity validation"""
        weak_passwords = [
            "short",
            "nouppercase123",
            "NOLOWERCASE123",
            "NoNumbers"
        ]
        
        for weak_password in weak_passwords:
            user_data = {
                "email": "test@example.com",
                "password": weak_password,
                "first_name": "John",
                "last_name": "Doe"
            }
            
            response = client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code == 422  # Validation error
    
    def test_email_validation(self, client):
        """Test email validation"""
        invalid_emails = [
            "not-an-email",
            "@example.com",
            "test@",
            "test.example.com"
        ]
        
        for invalid_email in invalid_emails:
            user_data = {
                "email": invalid_email,
                "password": "ValidPassword123",
                "first_name": "John",
                "last_name": "Doe"
            }
            
            response = client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code == 422  # Validation error 