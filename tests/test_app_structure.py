"""
Test suite for validating the FastAPI application structure
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os


def test_directory_structure():
    """Test that all required directories and files exist"""
    import os
    from pathlib import Path
    
    base_path = Path(__file__).parent.parent / "backend" / "app"
    
    # Check main directories exist
    required_dirs = [
        "api",
        "api/v1",
        "api/v1/endpoints",
        "core",
        "models",
        "schemas", 
        "services",
        "utils"
    ]
    
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        assert full_path.exists(), f"Directory {dir_path} does not exist"
        assert (full_path / "__init__.py").exists(), f"__init__.py missing in {dir_path}"
    
    # Check key files exist
    required_files = [
        "config.py",
        "main.py",
        "core/database.py",
        "core/security.py",
        "api/v1/router.py",
        "api/v1/endpoints/health.py"
    ]
    
    for file_path in required_files:
        full_path = base_path / file_path
        assert full_path.exists(), f"File {file_path} does not exist"


@patch.dict(os.environ, {
    'DATABASE_URL': 'postgresql+asyncpg://test:test@localhost/test_main',
    'CREDS_DATABASE_URL': 'postgresql+asyncpg://test:test@localhost/test_creds',
    'REDIS_URL': 'redis://localhost:6379/0',
    'JWT_SECRET_KEY': 'test-secret-key',
    'STRIPE_SECRET_KEY': 'sk_test_123',
    'REACT_APP_STRIPE_PUBLISHABLE_KEY': 'pk_test_123',
    'STRIPE_WEBHOOK_SECRET': 'whsec_test_123',
    'ENVIRONMENT': 'development'
}, clear=True)
def test_config_loading():
    """Test that configuration loads correctly with environment variables"""
    # Clear the settings cache to ensure fresh load
    from backend.app.config import get_settings
    get_settings.cache_clear()
    
    settings = get_settings()
    assert settings.database_url == 'postgresql+asyncpg://test:test@localhost/test_main'
    assert settings.credentials_database_url == 'postgresql+asyncpg://test:test@localhost/test_creds'
    assert settings.redis_url == 'redis://localhost:6379/0'
    assert settings.jwt_secret_key == 'test-secret-key'
    assert settings.environment == 'development'
    assert settings.debug == True


@patch.dict(os.environ, {
    'DATABASE_URL': 'postgresql+asyncpg://test:test@localhost/test_main',
    'CREDS_DATABASE_URL': 'postgresql+asyncpg://test:test@localhost/test_creds',
    'REDIS_URL': 'redis://localhost:6379/0',
    'JWT_SECRET_KEY': 'test-secret-key',
    'STRIPE_SECRET_KEY': 'sk_test_123',
    'REACT_APP_STRIPE_PUBLISHABLE_KEY': 'pk_test_123',
    'STRIPE_WEBHOOK_SECRET': 'whsec_test_123'
}, clear=True)
def test_security_functions():
    """Test that security functions work correctly"""
    # Clear the settings cache to ensure fresh load
    from backend.app.config import get_settings
    get_settings.cache_clear()
    
    from backend.app.core.security import (
        get_password_hash, 
        verify_password, 
        generate_reset_token, 
        generate_verification_code
    )
    
    # Test password hashing
    password = "test_password_123"
    hashed = get_password_hash(password)
    
    assert hashed != password  # Should be hashed
    assert verify_password(password, hashed) == True
    assert verify_password("wrong_password", hashed) == False
    
    # Test token generation
    reset_token = generate_reset_token()
    assert len(reset_token) > 20  # Should be a substantial token
    
    verification_code = generate_verification_code()
    assert len(verification_code) == 6  # Should be 6 digits
    assert verification_code.isdigit()  # Should be all digits


@patch.dict(os.environ, {
    'DATABASE_URL': 'postgresql+asyncpg://test:test@localhost/test_main',
    'CREDS_DATABASE_URL': 'postgresql+asyncpg://test:test@localhost/test_creds',
    'REDIS_URL': 'redis://localhost:6379/0',
    'JWT_SECRET_KEY': 'test-secret-key',
    'STRIPE_SECRET_KEY': 'sk_test_123',
    'REACT_APP_STRIPE_PUBLISHABLE_KEY': 'pk_test_123',  
    'STRIPE_WEBHOOK_SECRET': 'whsec_test_123'
}, clear=True)
def test_app_initialization():
    """Test that the FastAPI app initializes correctly with mocked dependencies"""
    
    # Clear the settings cache to ensure fresh load
    from backend.app.config import get_settings
    get_settings.cache_clear()
    
    # Mock database initialization to avoid actual database connections
    with patch('backend.app.core.database.init_db') as mock_init_db, \
         patch('backend.app.core.database.close_db') as mock_close_db, \
         patch('backend.app.core.database.create_async_engine') as mock_engine:
        
        mock_init_db.return_value = None
        mock_close_db.return_value = None
        mock_engine.return_value = MagicMock()
        
        from backend.app.main import app
        
        # Create test client
        client = TestClient(app)
        
        # Test root endpoint
        response = client.get("/")
        assert response.status_code == 200
        assert "Men's Circle Management Platform" in response.json()["message"]


def test_application_imports():
    """Test that core modules can be imported with mocked database"""
    with patch.dict(os.environ, {
        'DATABASE_URL': 'postgresql+asyncpg://test:test@localhost/test_main',
        'CREDS_DATABASE_URL': 'postgresql+asyncpg://test:test@localhost/test_creds',
        'REDIS_URL': 'redis://localhost:6379/0',
        'JWT_SECRET_KEY': 'test-secret-key',
        'STRIPE_SECRET_KEY': 'sk_test_123',
        'REACT_APP_STRIPE_PUBLISHABLE_KEY': 'pk_test_123',
        'STRIPE_WEBHOOK_SECRET': 'whsec_test_123'
    }, clear=True):
        # Clear the settings cache
        from backend.app.config import get_settings
        get_settings.cache_clear()
        
        # Mock database engine creation to avoid connection issues
        with patch('backend.app.core.database.create_async_engine') as mock_engine:
            mock_engine.return_value = MagicMock()
            
            # Test core imports
            from backend.app.config import get_settings
            from backend.app.core import database, security
            from backend.app.api.v1.router import router
            from backend.app.main import app
            
            # Verify settings can be instantiated
            settings = get_settings()
            assert settings.app_name == "Men's Circle Management Platform"
            assert settings.app_version == "0.1.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 