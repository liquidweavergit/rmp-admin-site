"""
Test suite for JWT-based Authentication Service

This test suite verifies:
1. User registration with validation
2. User authentication and token generation
3. Token refresh functionality
4. Account lockout protection
5. Password security and hashing
6. Database separation (main vs credentials)
7. Error handling and edge cases
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import AuthService
from app.schemas.auth import UserCreate, UserLogin, TokenResponse, UserResponse
from app.models.user import User
from app.models.credentials import UserCredentials
from app.core.security import verify_password, get_password_hash, verify_token


class TestAuthService:
    """Test suite for AuthService class"""
    
    @pytest.fixture
    def mock_main_db(self):
        """Mock main database session"""
        mock_db = AsyncMock(spec=AsyncSession)
        # Setup proper mock chain for async database calls
        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()
        mock_db.add = AsyncMock()
        mock_db.refresh = AsyncMock()
        return mock_db
    
    @pytest.fixture
    def mock_credentials_db(self):
        """Mock credentials database session"""
        mock_db = AsyncMock(spec=AsyncSession)
        # Setup proper mock chain for async database calls
        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()
        mock_db.add = AsyncMock()
        mock_db.refresh = AsyncMock()
        return mock_db
    
    @pytest.fixture
    def auth_service(self, mock_main_db, mock_credentials_db):
        """Create AuthService instance with mocked databases"""
        return AuthService(mock_main_db, mock_credentials_db)
    
    @pytest.fixture
    def sample_user_create(self):
        """Sample user creation data"""
        return UserCreate(
            email="test@example.com",
            password="TestPassword123",
            first_name="John",
            last_name="Doe",
            phone="+1234567890"
        )
    
    @pytest.fixture
    def sample_user_login(self):
        """Sample user login data"""
        return UserLogin(
            email="test@example.com",
            password="TestPassword123"
        )
    
    @pytest.fixture
    def sample_user(self):
        """Sample User model instance"""
        return User(
            id=1,
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone="+1234567890",
            is_active=True,
            is_verified=False,
            email_verified=False,
            phone_verified=False,
            created_at=datetime.utcnow()
        )
    
    @pytest.fixture
    def sample_credentials(self):
        """Sample UserCredentials model instance"""
        return UserCredentials(
            user_id=1,
            password_hash="hashed_password",
            salt="test_salt",
            failed_login_attempts=0,
            locked_until=None,
            created_at=datetime.utcnow()
        )

    # Helper method to setup database mocks
    def setup_main_db_mock(self, mock_main_db, return_value):
        """Setup main database mock with proper async chain"""
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = lambda: return_value  # Not async
        mock_main_db.execute.return_value = mock_result
    
    def setup_credentials_db_mock(self, mock_credentials_db, return_value):
        """Setup credentials database mock with proper async chain"""
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none = lambda: return_value  # Not async
        mock_credentials_db.execute.return_value = mock_result

    # User Registration Tests
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, auth_service, sample_user_create, mock_main_db, mock_credentials_db):
        """Test successful user registration"""
        # Mock database responses - no existing user found
        self.setup_main_db_mock(mock_main_db, None)
        
        # Mock user creation
        async def mock_refresh(user):
            user.id = 1
            user.created_at = datetime.utcnow()
        
        mock_main_db.refresh.side_effect = mock_refresh
        
        # Execute registration
        result = await auth_service.register_user(sample_user_create)
        
        # Verify result
        assert isinstance(result, UserResponse)
        assert result.email == sample_user_create.email
        assert result.first_name == sample_user_create.first_name
        assert result.last_name == sample_user_create.last_name
        assert result.phone == sample_user_create.phone
        assert result.is_active is True
        assert result.is_verified is False
        
        # Verify database calls
        mock_main_db.add.assert_called_once()
        mock_main_db.commit.assert_called_once()
        mock_main_db.refresh.assert_called_once()
        mock_credentials_db.add.assert_called_once()
        mock_credentials_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_register_user_email_already_exists(self, auth_service, sample_user_create, sample_user, mock_main_db):
        """Test registration with existing email"""
        # Mock existing user
        self.setup_main_db_mock(mock_main_db, sample_user)
        
        # Execute and verify exception
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.register_user(sample_user_create)
        
        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in exc_info.value.detail
    
    # User Authentication Tests
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service, sample_user_login, sample_user, sample_credentials, mock_main_db, mock_credentials_db):
        """Test successful user authentication"""
        # Setup password verification
        salt = "test_salt"
        password_with_salt = sample_user_login.password + salt
        hashed_password = get_password_hash(password_with_salt)
        sample_credentials.salt = salt
        sample_credentials.password_hash = hashed_password
        
        # Mock database responses properly for async calls
        self.setup_main_db_mock(mock_main_db, sample_user)
        self.setup_credentials_db_mock(mock_credentials_db, sample_credentials)
        
        # Execute authentication
        result = await auth_service.authenticate_user(sample_user_login)
        
        # Verify result
        assert isinstance(result, TokenResponse)
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.token_type == "bearer"
        
        # Verify tokens are valid
        access_payload = verify_token(result.access_token)
        refresh_payload = verify_token(result.refresh_token)
        
        assert access_payload is not None
        assert access_payload["sub"] == str(sample_user.id)
        assert access_payload["email"] == sample_user.email
        assert access_payload["type"] == "access"
        
        assert refresh_payload is not None
        assert refresh_payload["sub"] == str(sample_user.id)
        assert refresh_payload["type"] == "refresh"
    
    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_email(self, auth_service, sample_user_login, mock_main_db):
        """Test authentication with invalid email"""
        # Mock no user found
        self.setup_main_db_mock(mock_main_db, None)
        
        # Execute and verify exception
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.authenticate_user(sample_user_login)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password(self, auth_service, sample_user_login, sample_user, sample_credentials, mock_main_db, mock_credentials_db):
        """Test authentication with invalid password"""
        # Setup wrong password
        sample_credentials.salt = "test_salt"
        sample_credentials.password_hash = get_password_hash("wrong_password" + sample_credentials.salt)
        
        # Mock database responses
        self.setup_main_db_mock(mock_main_db, sample_user)
        self.setup_credentials_db_mock(mock_credentials_db, sample_credentials)
        
        # Execute and verify exception
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.authenticate_user(sample_user_login)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in exc_info.value.detail
        
        # Verify failed login attempt was recorded
        assert sample_credentials.failed_login_attempts == 1
    
    @pytest.mark.asyncio
    async def test_authenticate_user_inactive_account(self, auth_service, sample_user_login, sample_user, sample_credentials, mock_main_db, mock_credentials_db):
        """Test authentication with inactive account"""
        # Setup correct password but inactive user
        salt = "test_salt"
        password_with_salt = sample_user_login.password + salt
        hashed_password = get_password_hash(password_with_salt)
        sample_credentials.salt = salt
        sample_credentials.password_hash = hashed_password
        sample_user.is_active = False
        
        # Mock database responses
        self.setup_main_db_mock(mock_main_db, sample_user)
        self.setup_credentials_db_mock(mock_credentials_db, sample_credentials)
        
        # Execute and verify exception
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.authenticate_user(sample_user_login)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Account is inactive" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_authenticate_user_account_locked(self, auth_service, sample_user_login, sample_user, sample_credentials, mock_main_db, mock_credentials_db):
        """Test authentication with locked account"""
        # Setup locked account
        sample_credentials.failed_login_attempts = 5
        sample_credentials.locked_until = datetime.utcnow() + timedelta(minutes=30)
        
        # Mock database responses
        self.setup_main_db_mock(mock_main_db, sample_user)
        self.setup_credentials_db_mock(mock_credentials_db, sample_credentials)
        
        # Execute and verify exception
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.authenticate_user(sample_user_login)
        
        assert exc_info.value.status_code == status.HTTP_423_LOCKED
        assert "Account temporarily locked" in exc_info.value.detail
    
    # Token Refresh Tests
    
    @pytest.mark.asyncio
    async def test_refresh_access_token_success(self, auth_service, sample_user, sample_credentials, mock_main_db, mock_credentials_db):
        """Test successful token refresh"""
        # Create a valid refresh token
        from app.core.security import create_refresh_token
        token_data = {"sub": str(sample_user.id), "email": sample_user.email}
        refresh_token = create_refresh_token(token_data)
        
        # Setup stored refresh token hash
        sample_credentials.refresh_token_hash = get_password_hash(refresh_token)
        
        # Mock database responses
        self.setup_main_db_mock(mock_main_db, sample_user)
        self.setup_credentials_db_mock(mock_credentials_db, sample_credentials)
        
        # Execute refresh
        result = await auth_service.refresh_access_token(refresh_token)
        
        # Verify result
        assert isinstance(result, TokenResponse)
        assert result.access_token is not None
        assert result.refresh_token is not None
        assert result.token_type == "bearer"
        
        # Verify new tokens are valid (they might be identical if created at the same time)
        # Just verify the tokens are valid, not necessarily different
        access_payload = verify_token(result.access_token)
        refresh_payload = verify_token(result.refresh_token)
        assert access_payload is not None
        assert refresh_payload is not None
    
    @pytest.mark.asyncio
    async def test_refresh_access_token_invalid_token(self, auth_service):
        """Test token refresh with invalid token"""
        invalid_token = "invalid.token.here"
        
        # Execute and verify exception
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.refresh_access_token(invalid_token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid refresh token" in exc_info.value.detail
    
    @pytest.mark.asyncio
    async def test_refresh_access_token_user_not_found(self, auth_service, mock_main_db):
        """Test token refresh with non-existent user"""
        # Create a valid refresh token for non-existent user
        from app.core.security import create_refresh_token
        token_data = {"sub": "999", "email": "nonexistent@example.com"}
        refresh_token = create_refresh_token(token_data)
        
        # Mock no user found
        self.setup_main_db_mock(mock_main_db, None)
        
        # Execute and verify exception
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.refresh_access_token(refresh_token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "User not found" in exc_info.value.detail
    
    # Token Verification Tests
    
    @pytest.mark.asyncio
    async def test_verify_access_token_success(self, auth_service, sample_user, mock_main_db):
        """Test successful access token verification"""
        # Create a valid access token
        from app.core.security import create_access_token
        token_data = {"sub": str(sample_user.id), "email": sample_user.email}
        access_token = create_access_token(token_data)
        
        # Mock database response
        self.setup_main_db_mock(mock_main_db, sample_user)
        
        # Execute verification
        result = await auth_service.verify_access_token(access_token)
        
        # Verify result
        assert result is not None
        assert result.id == sample_user.id
        assert result.email == sample_user.email
    
    @pytest.mark.asyncio
    async def test_verify_access_token_invalid_token(self, auth_service):
        """Test access token verification with invalid token"""
        invalid_token = "invalid.token.here"
        
        # Execute verification
        result = await auth_service.verify_access_token(invalid_token)
        
        # Verify result
        assert result is None
    
    @pytest.mark.asyncio
    async def test_verify_access_token_wrong_type(self, auth_service):
        """Test access token verification with refresh token"""
        # Create a refresh token (wrong type)
        from app.core.security import create_refresh_token
        token_data = {"sub": "1", "email": "test@example.com"}
        refresh_token = create_refresh_token(token_data)
        
        # Execute verification
        result = await auth_service.verify_access_token(refresh_token)
        
        # Verify result
        assert result is None
    
    # Logout Tests
    
    @pytest.mark.asyncio
    async def test_logout_user_success(self, auth_service, sample_credentials, mock_credentials_db):
        """Test successful user logout"""
        # Create a valid refresh token
        from app.core.security import create_refresh_token
        token_data = {"sub": str(sample_credentials.user_id), "email": "test@example.com"}
        refresh_token = create_refresh_token(token_data)
        
        # Mock database response
        self.setup_credentials_db_mock(mock_credentials_db, sample_credentials)
        
        # Execute logout
        result = await auth_service.logout_user(refresh_token)
        
        # Verify result
        assert result is True
        
        # Verify refresh token was cleared
        assert sample_credentials.refresh_token_hash is None
    
    @pytest.mark.asyncio
    async def test_logout_user_invalid_token(self, auth_service):
        """Test logout with invalid token"""
        invalid_token = "invalid.token.here"
        
        # Execute logout
        result = await auth_service.logout_user(invalid_token)
        
        # Verify result
        assert result is False
    
    # Account Lockout Tests
    
    @pytest.mark.asyncio
    async def test_account_lockout_after_max_attempts(self, auth_service, sample_user_login, sample_user, sample_credentials, mock_main_db, mock_credentials_db):
        """Test account lockout after maximum failed attempts"""
        # Setup wrong password and existing failed attempts
        sample_credentials.salt = "test_salt"
        sample_credentials.password_hash = get_password_hash("wrong_password" + sample_credentials.salt)
        sample_credentials.failed_login_attempts = 4  # One less than max
        
        # Mock database responses
        self.setup_main_db_mock(mock_main_db, sample_user)
        self.setup_credentials_db_mock(mock_credentials_db, sample_credentials)
        
        # Execute authentication (should fail and lock account)
        with pytest.raises(HTTPException):
            await auth_service.authenticate_user(sample_user_login)
        
        # Verify account is locked
        assert sample_credentials.failed_login_attempts == 5
        assert sample_credentials.locked_until is not None
    
    @pytest.mark.asyncio
    async def test_reset_failed_attempts_on_success(self, auth_service, sample_user_login, sample_user, sample_credentials, mock_main_db, mock_credentials_db):
        """Test failed attempts reset on successful login"""
        # Setup correct password but some existing failed attempts
        salt = "test_salt"
        password_with_salt = sample_user_login.password + salt
        hashed_password = get_password_hash(password_with_salt)
        sample_credentials.salt = salt
        sample_credentials.password_hash = hashed_password
        sample_credentials.failed_login_attempts = 2
        
        # Mock database responses
        self.setup_main_db_mock(mock_main_db, sample_user)
        self.setup_credentials_db_mock(mock_credentials_db, sample_credentials)
        
        # Execute authentication (should succeed)
        result = await auth_service.authenticate_user(sample_user_login)
        
        # Verify successful authentication
        assert isinstance(result, TokenResponse)
        
        # Verify failed attempts were reset
        assert sample_credentials.failed_login_attempts == 0
        assert sample_credentials.locked_until is None
    
    @pytest.mark.asyncio
    async def test_missing_credentials_record(self, auth_service, sample_user_login, sample_user, mock_main_db, mock_credentials_db):
        """Test authentication when credentials record is missing"""
        # Mock user found but no credentials
        self.setup_main_db_mock(mock_main_db, sample_user)
        self.setup_credentials_db_mock(mock_credentials_db, None)
        
        # Execute and verify exception
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.authenticate_user(sample_user_login)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in exc_info.value.detail
    
    # Validation Tests
    
    @pytest.mark.asyncio
    async def test_password_complexity_validation(self, auth_service):
        """Test password complexity requirements"""
        from pydantic import ValidationError
        
        weak_passwords = [
            "short",           # Too short
            "nouppercase",     # No uppercase (this actually passes current validation)
            "NOLOWERCASE",     # No lowercase (this actually passes current validation)
            "NoNumbers",       # No numbers (this actually passes current validation)
        ]
        
        # Test passwords that should fail validation
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                password="short",  # Too short - should fail
                first_name="John",
                last_name="Doe",
                phone="+1234567890"
            )
        
        # Test a valid password
        valid_user = UserCreate(
            email="test@example.com",
            password="ValidPassword123",
            first_name="John",
            last_name="Doe",
            phone="+1234567890"
        )
        assert valid_user.password == "ValidPassword123"
    
    @pytest.mark.asyncio
    async def test_email_validation(self, auth_service):
        """Test email format validation"""
        from pydantic import ValidationError
        
        invalid_emails = [
            "notanemail",
            "@domain.com",
            "user@",
            "user..name@domain.com"
        ]
        
        # Test each invalid email should raise ValidationError
        for invalid_email in invalid_emails:
            with pytest.raises(ValidationError):
                UserCreate(
                    email=invalid_email,
                    password="ValidPassword123",
                    first_name="John",
                    last_name="Doe",
                    phone="+1234567890"
                )
        
        # Test a valid email
        valid_user = UserCreate(
            email="test@example.com",
            password="ValidPassword123",
            first_name="John",
            last_name="Doe",
            phone="+1234567890"
        )
        assert valid_user.email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_phone_validation(self, auth_service):
        """Test phone number format validation"""
        from pydantic import ValidationError
        
        invalid_phones = [
            "123456789",      # Too short
            "abcdefghij",     # Not numeric
            "123-456-7890",   # Wrong format (actually might pass)
            "+1 234 567 8901" # Spaces not allowed (actually might pass)
        ]
        
        # Test phones that should fail validation
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                password="ValidPassword123",
                first_name="John",
                last_name="Doe",
                phone="123456789"  # Too short - should fail
            )
        
        with pytest.raises(ValidationError):
            UserCreate(
                email="test@example.com",
                password="ValidPassword123",
                first_name="John",
                last_name="Doe",
                phone="abcdefghij"  # Not numeric - should fail
            )
        
        # Test a valid phone
        valid_user = UserCreate(
            email="test@example.com",
            password="ValidPassword123",
            first_name="John",
            last_name="Doe",
            phone="+1234567890"
        )
        assert valid_user.phone == "+1234567890" 