"""
Simple integration test for authentication system
"""
import pytest
import asyncio
from unittest.mock import AsyncMock
from app.services.auth_service import AuthService
from app.schemas.auth import UserCreate, UserLogin
from app.models.user import User
from app.models.credentials import UserCredentials
from app.core.security import get_password_hash, verify_password


@pytest.mark.asyncio
async def test_auth_service_basic_functionality():
    """Test basic auth service functionality with mocked databases"""
    # Create mock database sessions
    mock_main_db = AsyncMock()
    mock_credentials_db = AsyncMock()
    
    # Create auth service
    auth_service = AuthService(mock_main_db, mock_credentials_db)
    
    # Test password hashing
    password = "TestPassword123"
    salt = "test_salt"
    hashed = get_password_hash(password + salt)
    assert verify_password(password + salt, hashed)
    
    # Test token creation
    from app.core.security import create_access_token, create_refresh_token, verify_token
    token_data = {"sub": "1", "email": "test@example.com"}
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Verify tokens
    access_payload = verify_token(access_token)
    refresh_payload = verify_token(refresh_token)
    
    assert access_payload is not None
    assert access_payload["sub"] == "1"
    assert access_payload["email"] == "test@example.com"
    assert access_payload["type"] == "access"
    
    assert refresh_payload is not None
    assert refresh_payload["sub"] == "1"
    assert refresh_payload["type"] == "refresh"
    
    print("✅ Authentication service basic functionality test passed!")


def test_schema_validation():
    """Test Pydantic schema validation"""
    # Test valid user creation
    valid_user = UserCreate(
        email="test@example.com",
        password="ValidPassword123",
        first_name="John",
        last_name="Doe",
        phone="+1234567890"
    )
    assert valid_user.email == "test@example.com"
    assert valid_user.first_name == "John"
    
    # Test password validation
    with pytest.raises(ValueError, match="Password must contain"):
        UserCreate(
            email="test@example.com",
            password="weakpassword",  # No uppercase or digits
            first_name="John",
            last_name="Doe"
        )
    
    # Test email validation
    with pytest.raises(ValueError):
        UserCreate(
            email="not-an-email",
            password="ValidPassword123",
            first_name="John",
            last_name="Doe"
        )
    
    print("✅ Schema validation test passed!")


if __name__ == "__main__":
    # Run the async test
    asyncio.run(test_auth_service_basic_functionality())
    test_schema_validation()
    print("🎉 All authentication tests passed!") 