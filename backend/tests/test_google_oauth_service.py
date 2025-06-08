"""
Tests for Google OAuth Service

This module tests the Google OAuth service functionality including:
- Authorization URL generation
- Token exchange
- ID token verification
- User profile retrieval
- Mock mode functionality
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
import httpx

from app.services.google_oauth_service import GoogleOAuthService


class TestGoogleOAuthService:
    """Test cases for Google OAuth Service"""
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing"""
        settings = MagicMock()
        settings.google_client_id = "test_client_id"
        settings.google_client_secret = "test_client_secret"
        return settings
    
    @pytest.fixture
    def mock_settings_no_oauth(self):
        """Mock settings without OAuth credentials (mock mode)"""
        settings = MagicMock()
        settings.google_client_id = None
        settings.google_client_secret = None
        return settings
    
    @pytest.fixture
    def oauth_service(self, mock_settings):
        """Create OAuth service with mocked settings"""
        with patch('app.services.google_oauth_service.get_settings', return_value=mock_settings):
            return GoogleOAuthService()
    
    @pytest.fixture
    def oauth_service_mock_mode(self, mock_settings_no_oauth):
        """Create OAuth service in mock mode"""
        with patch('app.services.google_oauth_service.get_settings', return_value=mock_settings_no_oauth):
            return GoogleOAuthService()
    
    def test_init_with_credentials(self, oauth_service):
        """Test service initialization with OAuth credentials"""
        assert oauth_service.client_id == "test_client_id"
        assert oauth_service.client_secret == "test_client_secret"
        assert oauth_service.mock_mode is False
    
    def test_init_mock_mode(self, oauth_service_mock_mode):
        """Test service initialization in mock mode"""
        assert oauth_service_mock_mode.mock_mode is True
    
    def test_get_authorization_url_with_state(self, oauth_service):
        """Test authorization URL generation with provided state"""
        redirect_uri = "http://localhost:3000/auth/callback"
        state = "test_state_123"
        
        url = oauth_service.get_authorization_url(redirect_uri, state)
        
        assert "accounts.google.com/o/oauth2/auth" in url
        assert f"client_id={oauth_service.client_id}" in url
        assert f"redirect_uri={redirect_uri}" in url
        assert f"state={state}" in url
        assert "scope=openid email profile" in url
        assert "response_type=code" in url
    
    def test_get_authorization_url_without_state(self, oauth_service):
        """Test authorization URL generation without provided state"""
        redirect_uri = "http://localhost:3000/auth/callback"
        
        url = oauth_service.get_authorization_url(redirect_uri)
        
        assert "accounts.google.com/o/oauth2/auth" in url
        assert "state=" in url  # State should be generated
    
    def test_get_authorization_url_mock_mode(self, oauth_service_mock_mode):
        """Test authorization URL generation in mock mode"""
        redirect_uri = "http://localhost:3000/auth/callback"
        state = "test_state"
        
        url = oauth_service_mock_mode.get_authorization_url(redirect_uri, state)
        
        assert url == f"https://accounts.google.com/oauth/authorize?mock=true&state={state}"
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_tokens_success(self, oauth_service):
        """Test successful token exchange"""
        code = "test_auth_code"
        redirect_uri = "http://localhost:3000/auth/callback"
        
        mock_response = {
            "access_token": "test_access_token",
            "id_token": "test_id_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "test_refresh_token"
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            
            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response_obj
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await oauth_service.exchange_code_for_tokens(code, redirect_uri)
            
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_tokens_mock_mode(self, oauth_service_mock_mode):
        """Test token exchange in mock mode"""
        code = "test_auth_code"
        redirect_uri = "http://localhost:3000/auth/callback"
        
        result = await oauth_service_mock_mode.exchange_code_for_tokens(code, redirect_uri)
        
        assert result["access_token"] == "mock_access_token"
        assert result["id_token"] == "mock_id_token"
        assert result["token_type"] == "Bearer"
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_tokens_http_error(self, oauth_service):
        """Test token exchange with HTTP error"""
        code = "invalid_code"
        redirect_uri = "http://localhost:3000/auth/callback"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response_obj = MagicMock()
            mock_response_obj.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Bad Request", request=MagicMock(), response=MagicMock()
            )
            mock_response_obj.response.text = "Invalid authorization code"
            
            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response_obj
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            with pytest.raises(HTTPException) as exc_info:
                await oauth_service.exchange_code_for_tokens(code, redirect_uri)
            
            assert exc_info.value.status_code == 400
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_tokens_general_error(self, oauth_service):
        """Test token exchange with general error"""
        code = "test_code"
        redirect_uri = "http://localhost:3000/auth/callback"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.side_effect = Exception("Network error")
            
            with pytest.raises(HTTPException) as exc_info:
                await oauth_service.exchange_code_for_tokens(code, redirect_uri)
            
            assert exc_info.value.status_code == 503
    
    @pytest.mark.asyncio
    async def test_verify_id_token_success(self, oauth_service):
        """Test successful ID token verification"""
        id_token = "valid_id_token"
        
        mock_idinfo = {
            "sub": "google_user_123",
            "email": "test@example.com",
            "email_verified": True,
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "iss": "accounts.google.com"
        }
        
        with patch('app.services.google_oauth_service.id_token.verify_oauth2_token', return_value=mock_idinfo):
            result = await oauth_service.verify_id_token(id_token)
            
            assert result == mock_idinfo
    
    @pytest.mark.asyncio
    async def test_verify_id_token_mock_mode(self, oauth_service_mock_mode):
        """Test ID token verification in mock mode"""
        id_token = "mock_id_token"
        
        result = await oauth_service_mock_mode.verify_id_token(id_token)
        
        assert result["sub"] == "mock_google_user_id"
        assert result["email"] == "test@example.com"
        assert result["email_verified"] is True
    
    @pytest.mark.asyncio
    async def test_verify_id_token_invalid_issuer(self, oauth_service):
        """Test ID token verification with invalid issuer"""
        id_token = "invalid_token"
        
        mock_idinfo = {
            "sub": "google_user_123",
            "email": "test@example.com",
            "iss": "invalid.issuer.com"
        }
        
        with patch('app.services.google_oauth_service.id_token.verify_oauth2_token', return_value=mock_idinfo):
            with pytest.raises(HTTPException) as exc_info:
                await oauth_service.verify_id_token(id_token)
            
            assert exc_info.value.status_code == 400
            assert "Invalid ID token" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_verify_id_token_value_error(self, oauth_service):
        """Test ID token verification with ValueError"""
        id_token = "malformed_token"
        
        with patch('app.services.google_oauth_service.id_token.verify_oauth2_token', side_effect=ValueError("Invalid token")):
            with pytest.raises(HTTPException) as exc_info:
                await oauth_service.verify_id_token(id_token)
            
            assert exc_info.value.status_code == 400
    
    @pytest.mark.asyncio
    async def test_verify_id_token_general_error(self, oauth_service):
        """Test ID token verification with general error"""
        id_token = "test_token"
        
        with patch('app.services.google_oauth_service.id_token.verify_oauth2_token', side_effect=Exception("Service error")):
            with pytest.raises(HTTPException) as exc_info:
                await oauth_service.verify_id_token(id_token)
            
            assert exc_info.value.status_code == 503
    
    @pytest.mark.asyncio
    async def test_get_user_profile_success(self, oauth_service):
        """Test successful user profile retrieval"""
        access_token = "valid_access_token"
        
        mock_profile = {
            "id": "google_user_123",
            "email": "test@example.com",
            "verified_email": True,
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "picture": "https://example.com/avatar.jpg"
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_profile
            mock_response_obj.raise_for_status.return_value = None
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response_obj
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            result = await oauth_service.get_user_profile(access_token)
            
            assert result == mock_profile
    
    @pytest.mark.asyncio
    async def test_get_user_profile_mock_mode(self, oauth_service_mock_mode):
        """Test user profile retrieval in mock mode"""
        access_token = "mock_access_token"
        
        result = await oauth_service_mock_mode.get_user_profile(access_token)
        
        assert result["id"] == "mock_google_user_id"
        assert result["email"] == "test@example.com"
        assert result["verified_email"] is True
    
    @pytest.mark.asyncio
    async def test_get_user_profile_http_error(self, oauth_service):
        """Test user profile retrieval with HTTP error"""
        access_token = "invalid_token"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response_obj = MagicMock()
            mock_response_obj.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Unauthorized", request=MagicMock(), response=MagicMock()
            )
            mock_response_obj.response.text = "Invalid access token"
            
            mock_client_instance = AsyncMock()
            mock_client_instance.get.return_value = mock_response_obj
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            
            with pytest.raises(HTTPException) as exc_info:
                await oauth_service.get_user_profile(access_token)
            
            assert exc_info.value.status_code == 400
    
    @pytest.mark.asyncio
    async def test_get_user_profile_general_error(self, oauth_service):
        """Test user profile retrieval with general error"""
        access_token = "test_token"
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Network error")
            
            with pytest.raises(HTTPException) as exc_info:
                await oauth_service.get_user_profile(access_token)
            
            assert exc_info.value.status_code == 503
    
    def test_validate_email_domain_no_restrictions(self, oauth_service):
        """Test email domain validation with no restrictions"""
        email = "test@anydomain.com"
        
        result = oauth_service.validate_email_domain(email)
        
        assert result is True
    
    def test_validate_email_domain_allowed(self, oauth_service):
        """Test email domain validation with allowed domain"""
        email = "test@example.com"
        allowed_domains = ["example.com", "test.org"]
        
        result = oauth_service.validate_email_domain(email, allowed_domains)
        
        assert result is True
    
    def test_validate_email_domain_not_allowed(self, oauth_service):
        """Test email domain validation with disallowed domain"""
        email = "test@forbidden.com"
        allowed_domains = ["example.com", "test.org"]
        
        result = oauth_service.validate_email_domain(email, allowed_domains)
        
        assert result is False
    
    def test_validate_email_domain_case_insensitive(self, oauth_service):
        """Test email domain validation is case insensitive"""
        email = "test@EXAMPLE.COM"
        allowed_domains = ["example.com"]
        
        result = oauth_service.validate_email_domain(email, allowed_domains)
        
        assert result is True


def test_get_google_oauth_service():
    """Test the dependency function"""
    from app.services.google_oauth_service import get_google_oauth_service
    
    service = get_google_oauth_service()
    assert isinstance(service, GoogleOAuthService) 