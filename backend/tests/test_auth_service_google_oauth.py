"""
Tests for AuthService Google OAuth functionality

This module tests the Google OAuth integration in the AuthService including:
- Google OAuth authentication
- User creation from Google profile
- Account linking
- Error handling
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from fastapi import HTTPException

from app.services.auth_service import AuthService
from app.models.user import User
from app.models.credentials import UserCredentials
from app.schemas.auth import GoogleOAuthLoginRequest, GoogleOAuthResponse


class TestAuthServiceGoogleOAuth:
    """Test cases for AuthService Google OAuth functionality"""
    
    @pytest.fixture
    def mock_main_db(self):
        """Mock main database session"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_credentials_db(self):
        """Mock credentials database session"""
        return AsyncMock()
    
    @pytest.fixture
    def mock_google_oauth_service(self):
        """Mock Google OAuth service"""
        return AsyncMock()
    
    @pytest.fixture
    def auth_service(self, mock_main_db, mock_credentials_db, mock_google_oauth_service):
        """Create AuthService with mocked dependencies"""
        return AuthService(
            main_db=mock_main_db,
            credentials_db=mock_credentials_db,
            google_oauth_service=mock_google_oauth_service
        )
    
    @pytest.fixture
    def google_user_info(self):
        """Sample Google user information"""
        return {
            "sub": "google_user_123",
            "email": "test@example.com",
            "email_verified": True,
            "name": "Test User",
            "given_name": "Test",
            "family_name": "User",
            "picture": "https://example.com/avatar.jpg"
        }
    
    @pytest.fixture
    def existing_user(self):
        """Sample existing user"""
        return User(
            id=1,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            phone=None,
            is_active=True,
            is_verified=True,
            email_verified=True,
            phone_verified=False,
            created_at=datetime.utcnow()
        )
    
    @pytest.fixture
    def user_credentials(self):
        """Sample user credentials"""
        return UserCredentials(
            user_id=1,
            password_hash="",
            salt="",
            failed_login_attempts=0
        )
    
    @pytest.mark.asyncio
    async def test_authenticate_google_oauth_existing_user_by_google_id(
        self, auth_service, google_user_info, existing_user, user_credentials
    ):
        """Test Google OAuth authentication with existing user found by Google ID"""
        request = GoogleOAuthLoginRequest(
            id_token="valid_id_token",
            access_token="valid_access_token"
        )
        
        # Mock Google OAuth service
        auth_service.google_oauth_service.verify_id_token.return_value = google_user_info
        
        # Mock finding existing user by Google ID
        auth_service._get_user_by_google_id = AsyncMock(return_value=existing_user)
        auth_service._update_last_login = AsyncMock()
        auth_service._get_user_credentials = AsyncMock(return_value=user_credentials)
        auth_service._store_refresh_token = AsyncMock()
        
        # Mock token creation
        with patch('app.services.auth_service.create_access_token', return_value="access_token"), \
             patch('app.services.auth_service.create_refresh_token', return_value="refresh_token"):
            
            result = await auth_service.authenticate_google_oauth(request)
        
        assert isinstance(result, GoogleOAuthResponse)
        assert result.access_token == "access_token"
        assert result.refresh_token == "refresh_token"
        assert result.user.email == "test@example.com"
        assert result.is_new_user is False
    
    @pytest.mark.asyncio
    async def test_authenticate_google_oauth_existing_user_by_email(
        self, auth_service, google_user_info, existing_user, user_credentials
    ):
        """Test Google OAuth authentication with existing user found by email"""
        request = GoogleOAuthLoginRequest(
            id_token="valid_id_token",
            access_token="valid_access_token"
        )
        
        # Mock Google OAuth service
        auth_service.google_oauth_service.verify_id_token.return_value = google_user_info
        
        # Mock not finding user by Google ID, but finding by email
        auth_service._get_user_by_google_id = AsyncMock(return_value=None)
        auth_service._get_user_by_email = AsyncMock(return_value=existing_user)
        auth_service._link_google_account = AsyncMock()
        auth_service._update_last_login = AsyncMock()
        auth_service._get_user_credentials = AsyncMock(return_value=user_credentials)
        auth_service._store_refresh_token = AsyncMock()
        
        # Mock token creation
        with patch('app.services.auth_service.create_access_token', return_value="access_token"), \
             patch('app.services.auth_service.create_refresh_token', return_value="refresh_token"):
            
            result = await auth_service.authenticate_google_oauth(request)
        
        assert isinstance(result, GoogleOAuthResponse)
        assert result.is_new_user is False
        auth_service._link_google_account.assert_called_once_with(
            existing_user.id, "google_user_123", "valid_access_token"
        )
    
    @pytest.mark.asyncio
    async def test_authenticate_google_oauth_new_user(
        self, auth_service, google_user_info, existing_user, user_credentials
    ):
        """Test Google OAuth authentication with new user creation"""
        request = GoogleOAuthLoginRequest(
            id_token="valid_id_token",
            access_token="valid_access_token"
        )
        
        # Mock Google OAuth service
        auth_service.google_oauth_service.verify_id_token.return_value = google_user_info
        
        # Mock not finding any existing user
        auth_service._get_user_by_google_id = AsyncMock(return_value=None)
        auth_service._get_user_by_email = AsyncMock(return_value=None)
        auth_service._create_google_user = AsyncMock(return_value=existing_user)
        auth_service._link_google_account = AsyncMock()
        auth_service._update_last_login = AsyncMock()
        auth_service._get_user_credentials = AsyncMock(return_value=user_credentials)
        auth_service._store_refresh_token = AsyncMock()
        
        # Mock token creation
        with patch('app.services.auth_service.create_access_token', return_value="access_token"), \
             patch('app.services.auth_service.create_refresh_token', return_value="refresh_token"):
            
            result = await auth_service.authenticate_google_oauth(request)
        
        assert isinstance(result, GoogleOAuthResponse)
        assert result.is_new_user is True
        auth_service._create_google_user.assert_called_once_with(google_user_info)
        auth_service._link_google_account.assert_called_once_with(
            existing_user.id, "google_user_123", "valid_access_token"
        )
    
    @pytest.mark.asyncio
    async def test_authenticate_google_oauth_missing_user_info(self, auth_service):
        """Test Google OAuth authentication with missing user information"""
        request = GoogleOAuthLoginRequest(id_token="invalid_token")
        
        # Mock Google OAuth service returning incomplete info
        incomplete_info = {"email": "test@example.com"}  # Missing 'sub'
        auth_service.google_oauth_service.verify_id_token.return_value = incomplete_info
        
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.authenticate_google_oauth(request)
        
        assert exc_info.value.status_code == 400
        assert "missing required user information" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_authenticate_google_oauth_unverified_email(self, auth_service):
        """Test Google OAuth authentication with unverified email"""
        request = GoogleOAuthLoginRequest(id_token="invalid_token")
        
        # Mock Google OAuth service returning unverified email
        unverified_info = {
            "sub": "google_user_123",
            "email": "test@example.com",
            "email_verified": False
        }
        auth_service.google_oauth_service.verify_id_token.return_value = unverified_info
        
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.authenticate_google_oauth(request)
        
        assert exc_info.value.status_code == 400
        assert "Google email not verified" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_get_user_by_google_id_found(self, auth_service, existing_user, user_credentials):
        """Test finding user by Google ID"""
        google_user_id = "google_user_123"
        
        # Mock credentials database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user_credentials
        auth_service.credentials_db.execute = AsyncMock(return_value=mock_result)
        
        # Mock getting user by ID
        auth_service._get_user_by_id = AsyncMock(return_value=existing_user)
        
        result = await auth_service._get_user_by_google_id(google_user_id)
        
        assert result == existing_user
        auth_service._get_user_by_id.assert_called_once_with(user_credentials.user_id)
    
    @pytest.mark.asyncio
    async def test_get_user_by_google_id_not_found(self, auth_service):
        """Test not finding user by Google ID"""
        google_user_id = "nonexistent_google_user"
        
        # Mock credentials database query returning None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        auth_service.credentials_db.execute = AsyncMock(return_value=mock_result)
        
        result = await auth_service._get_user_by_google_id(google_user_id)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_create_google_user(self, auth_service, google_user_info):
        """Test creating a new user from Google information"""
        # Mock user creation
        new_user = User(
            id=1,
            email="test@example.com",
            first_name="Test",
            last_name="User",
            phone=None,
            is_active=True,
            is_verified=True,
            email_verified=True,
            phone_verified=False
        )
        
        auth_service.main_db.add = MagicMock()
        auth_service.main_db.commit = AsyncMock()
        auth_service.main_db.refresh = AsyncMock()
        
        auth_service.credentials_db.add = MagicMock()
        auth_service.credentials_db.commit = AsyncMock()
        
        # Mock the user creation process
        with patch('app.services.auth_service.User', return_value=new_user):
            result = await auth_service._create_google_user(google_user_info)
        
        assert result == new_user
        auth_service.main_db.add.assert_called_once()
        auth_service.main_db.commit.assert_called_once()
        auth_service.credentials_db.add.assert_called_once()
        auth_service.credentials_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_link_google_account_success(self, auth_service, user_credentials):
        """Test linking Google account to existing user"""
        user_id = 1
        google_user_id = "google_user_123"
        access_token = "access_token"
        
        auth_service._get_user_credentials = AsyncMock(return_value=user_credentials)
        auth_service.credentials_db.commit = AsyncMock()
        
        await auth_service._link_google_account(user_id, google_user_id, access_token)
        
        assert user_credentials.google_user_id == google_user_id
        assert user_credentials.google_access_token == access_token.encode('utf-8')
        auth_service.credentials_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_link_google_account_no_credentials(self, auth_service):
        """Test linking Google account when credentials not found"""
        user_id = 1
        google_user_id = "google_user_123"
        
        auth_service._get_user_credentials = AsyncMock(return_value=None)
        
        with pytest.raises(HTTPException) as exc_info:
            await auth_service._link_google_account(user_id, google_user_id)
        
        assert exc_info.value.status_code == 404
        assert "User credentials not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_link_google_account_without_access_token(self, auth_service, user_credentials):
        """Test linking Google account without access token"""
        user_id = 1
        google_user_id = "google_user_123"
        
        auth_service._get_user_credentials = AsyncMock(return_value=user_credentials)
        auth_service.credentials_db.commit = AsyncMock()
        
        await auth_service._link_google_account(user_id, google_user_id)
        
        assert user_credentials.google_user_id == google_user_id
        assert user_credentials.google_access_token is None
        auth_service.credentials_db.commit.assert_called_once()


class TestAuthServiceGoogleOAuthIntegration:
    """Integration tests for Google OAuth functionality"""
    
    @pytest.mark.asyncio
    async def test_full_google_oauth_flow_new_user(self):
        """Test complete Google OAuth flow for new user"""
        # This would be an integration test that tests the full flow
        # For now, we'll keep it as a placeholder for future implementation
        pass
    
    @pytest.mark.asyncio
    async def test_full_google_oauth_flow_existing_user(self):
        """Test complete Google OAuth flow for existing user"""
        # This would be an integration test that tests the full flow
        # For now, we'll keep it as a placeholder for future implementation
        pass 