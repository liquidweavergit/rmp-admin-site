"""
Tests for Google OAuth API endpoints

This module tests the Google OAuth API endpoints including:
- Authorization URL generation
- OAuth callback handling
- Direct ID token login
- Error handling
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app
from app.schemas.auth import GoogleOAuthResponse, UserResponse


class TestGoogleOAuthEndpoints:
    """Test cases for Google OAuth API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Test client for API endpoints"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_google_oauth_service(self):
        """Mock Google OAuth service"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_auth_service(self):
        """Mock auth service"""
        return AsyncMock()
    
    @pytest.fixture
    def sample_oauth_response(self):
        """Sample Google OAuth response"""
        return GoogleOAuthResponse(
            access_token="jwt_access_token",
            refresh_token="jwt_refresh_token",
            token_type="bearer",
            user=UserResponse(
                id=1,
                email="test@example.com",
                first_name="Test",
                last_name="User",
                phone=None,
                is_active=True,
                is_verified=True,
                email_verified=True,
                phone_verified=False,
                created_at="2024-01-01T00:00:00Z"
            ),
            is_new_user=False
        )
    
    def test_get_google_auth_url_success(self, client, mock_google_oauth_service):
        """Test successful Google OAuth URL generation"""
        # Mock the service
        mock_google_oauth_service.get_authorization_url.return_value = (
            "https://accounts.google.com/o/oauth2/auth?client_id=test&state=test_state"
        )
        
        with patch('app.api.v1.endpoints.auth.get_google_oauth_service', return_value=mock_google_oauth_service):
            response = client.post(
                "/api/v1/auth/google/auth-url",
                json={
                    "redirect_uri": "http://localhost:3000/auth/callback",
                    "state": "test_state"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "authorization_url" in data
        assert data["state"] == "test_state"
    
    def test_get_google_auth_url_without_state(self, client, mock_google_oauth_service):
        """Test Google OAuth URL generation without state"""
        mock_google_oauth_service.get_authorization_url.return_value = (
            "https://accounts.google.com/o/oauth2/auth?client_id=test&state=generated_state"
        )
        
        with patch('app.api.v1.endpoints.auth.get_google_oauth_service', return_value=mock_google_oauth_service):
            response = client.post(
                "/api/v1/auth/google/auth-url",
                json={
                    "redirect_uri": "http://localhost:3000/auth/callback"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "authorization_url" in data
        assert "state" in data
    
    def test_get_google_auth_url_service_error(self, client, mock_google_oauth_service):
        """Test Google OAuth URL generation with service error"""
        mock_google_oauth_service.get_authorization_url.side_effect = Exception("Service error")
        
        with patch('app.api.v1.endpoints.auth.get_google_oauth_service', return_value=mock_google_oauth_service):
            response = client.post(
                "/api/v1/auth/google/auth-url",
                json={
                    "redirect_uri": "http://localhost:3000/auth/callback"
                }
            )
        
        assert response.status_code == 500
        assert "Failed to generate Google OAuth URL" in response.json()["detail"]
    
    def test_google_oauth_callback_success(self, client, mock_google_oauth_service, mock_auth_service, sample_oauth_response):
        """Test successful Google OAuth callback"""
        # Mock token exchange
        mock_google_oauth_service.exchange_code_for_tokens.return_value = {
            "access_token": "google_access_token",
            "id_token": "google_id_token",
            "token_type": "Bearer",
            "expires_in": 3600
        }
        
        # Mock authentication
        mock_auth_service.authenticate_google_oauth.return_value = sample_oauth_response
        
        with patch('app.api.v1.endpoints.auth.get_google_oauth_service', return_value=mock_google_oauth_service), \
             patch('app.api.v1.endpoints.auth.get_auth_service', return_value=mock_auth_service):
            
            response = client.post(
                "/api/v1/auth/google/callback",
                json={
                    "code": "auth_code_123",
                    "state": "test_state",
                    "redirect_uri": "http://localhost:3000/auth/callback"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "jwt_access_token"
        assert data["user"]["email"] == "test@example.com"
        assert data["is_new_user"] is False
    
    def test_google_oauth_callback_token_exchange_error(self, client, mock_google_oauth_service, mock_auth_service):
        """Test Google OAuth callback with token exchange error"""
        mock_google_oauth_service.exchange_code_for_tokens.side_effect = HTTPException(
            status_code=400, detail="Invalid authorization code"
        )
        
        with patch('app.api.v1.endpoints.auth.get_google_oauth_service', return_value=mock_google_oauth_service), \
             patch('app.api.v1.endpoints.auth.get_auth_service', return_value=mock_auth_service):
            
            response = client.post(
                "/api/v1/auth/google/callback",
                json={
                    "code": "invalid_code",
                    "state": "test_state",
                    "redirect_uri": "http://localhost:3000/auth/callback"
                }
            )
        
        assert response.status_code == 400
        assert "Invalid authorization code" in response.json()["detail"]
    
    def test_google_oauth_callback_auth_error(self, client, mock_google_oauth_service, mock_auth_service):
        """Test Google OAuth callback with authentication error"""
        # Mock successful token exchange
        mock_google_oauth_service.exchange_code_for_tokens.return_value = {
            "access_token": "google_access_token",
            "id_token": "google_id_token"
        }
        
        # Mock authentication failure
        mock_auth_service.authenticate_google_oauth.side_effect = HTTPException(
            status_code=400, detail="Invalid Google token"
        )
        
        with patch('app.api.v1.endpoints.auth.get_google_oauth_service', return_value=mock_google_oauth_service), \
             patch('app.api.v1.endpoints.auth.get_auth_service', return_value=mock_auth_service):
            
            response = client.post(
                "/api/v1/auth/google/callback",
                json={
                    "code": "auth_code_123",
                    "state": "test_state",
                    "redirect_uri": "http://localhost:3000/auth/callback"
                }
            )
        
        assert response.status_code == 400
        assert "Invalid Google token" in response.json()["detail"]
    
    def test_google_oauth_callback_general_error(self, client, mock_google_oauth_service, mock_auth_service):
        """Test Google OAuth callback with general error"""
        mock_google_oauth_service.exchange_code_for_tokens.side_effect = Exception("Network error")
        
        with patch('app.api.v1.endpoints.auth.get_google_oauth_service', return_value=mock_google_oauth_service), \
             patch('app.api.v1.endpoints.auth.get_auth_service', return_value=mock_auth_service):
            
            response = client.post(
                "/api/v1/auth/google/callback",
                json={
                    "code": "auth_code_123",
                    "state": "test_state",
                    "redirect_uri": "http://localhost:3000/auth/callback"
                }
            )
        
        assert response.status_code == 500
        assert "Google OAuth authentication failed" in response.json()["detail"]
    
    def test_google_oauth_login_success(self, client, mock_auth_service, sample_oauth_response):
        """Test successful Google OAuth login with ID token"""
        mock_auth_service.authenticate_google_oauth.return_value = sample_oauth_response
        
        with patch('app.api.v1.endpoints.auth.get_auth_service', return_value=mock_auth_service):
            response = client.post(
                "/api/v1/auth/google/login",
                json={
                    "id_token": "valid_google_id_token",
                    "access_token": "google_access_token"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "jwt_access_token"
        assert data["user"]["email"] == "test@example.com"
        assert data["is_new_user"] is False
    
    def test_google_oauth_login_without_access_token(self, client, mock_auth_service, sample_oauth_response):
        """Test Google OAuth login without access token"""
        mock_auth_service.authenticate_google_oauth.return_value = sample_oauth_response
        
        with patch('app.api.v1.endpoints.auth.get_auth_service', return_value=mock_auth_service):
            response = client.post(
                "/api/v1/auth/google/login",
                json={
                    "id_token": "valid_google_id_token"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "jwt_access_token"
    
    def test_google_oauth_login_invalid_token(self, client, mock_auth_service):
        """Test Google OAuth login with invalid ID token"""
        mock_auth_service.authenticate_google_oauth.side_effect = HTTPException(
            status_code=400, detail="Invalid Google token"
        )
        
        with patch('app.api.v1.endpoints.auth.get_auth_service', return_value=mock_auth_service):
            response = client.post(
                "/api/v1/auth/google/login",
                json={
                    "id_token": "invalid_google_id_token"
                }
            )
        
        assert response.status_code == 400
        assert "Invalid Google token" in response.json()["detail"]
    
    def test_google_oauth_login_general_error(self, client, mock_auth_service):
        """Test Google OAuth login with general error"""
        mock_auth_service.authenticate_google_oauth.side_effect = Exception("Service error")
        
        with patch('app.api.v1.endpoints.auth.get_auth_service', return_value=mock_auth_service):
            response = client.post(
                "/api/v1/auth/google/login",
                json={
                    "id_token": "valid_google_id_token"
                }
            )
        
        assert response.status_code == 500
        assert "Google OAuth login failed" in response.json()["detail"]
    
    def test_google_oauth_endpoints_validation(self, client):
        """Test request validation for Google OAuth endpoints"""
        # Test missing required fields
        response = client.post("/api/v1/auth/google/auth-url", json={})
        assert response.status_code == 422  # Validation error
        
        response = client.post("/api/v1/auth/google/callback", json={})
        assert response.status_code == 422  # Validation error
        
        response = client.post("/api/v1/auth/google/login", json={})
        assert response.status_code == 422  # Validation error
    
    def test_google_oauth_endpoints_invalid_json(self, client):
        """Test Google OAuth endpoints with invalid JSON"""
        response = client.post(
            "/api/v1/auth/google/auth-url",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_google_oauth_new_user_flow(self, client, mock_google_oauth_service, mock_auth_service):
        """Test Google OAuth flow for new user creation"""
        # Create response for new user
        new_user_response = GoogleOAuthResponse(
            access_token="jwt_access_token",
            refresh_token="jwt_refresh_token",
            token_type="bearer",
            user=UserResponse(
                id=1,
                email="newuser@example.com",
                first_name="New",
                last_name="User",
                phone=None,
                is_active=True,
                is_verified=True,
                email_verified=True,
                phone_verified=False,
                created_at="2024-01-01T00:00:00Z"
            ),
            is_new_user=True
        )
        
        mock_auth_service.authenticate_google_oauth.return_value = new_user_response
        
        with patch('app.api.v1.endpoints.auth.get_auth_service', return_value=mock_auth_service):
            response = client.post(
                "/api/v1/auth/google/login",
                json={
                    "id_token": "valid_google_id_token"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_new_user"] is True
        assert data["user"]["email"] == "newuser@example.com" 