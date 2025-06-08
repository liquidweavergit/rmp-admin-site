"""
Test suite for .env.example file validation
Tests that all required environment variables are present in the .env.example file
"""
import os
import pytest
from pathlib import Path


class TestEnvExample:
    """Test suite for .env.example file validation"""
    
    @pytest.fixture
    def env_example_path(self):
        """Fixture to get the path to .env.example file"""
        project_root = Path(__file__).parent.parent
        return project_root / ".env.example"
    
    @pytest.fixture
    def env_example_content(self, env_example_path):
        """Fixture to read .env.example file content"""
        if not env_example_path.exists():
            pytest.fail(f".env.example file not found at {env_example_path}")
        
        with open(env_example_path, 'r') as f:
            return f.read()
    
    def test_env_example_file_exists(self, env_example_path):
        """Test that .env.example file exists in project root"""
        assert env_example_path.exists(), f".env.example file should exist at {env_example_path}"
        assert env_example_path.is_file(), f".env.example should be a file, not a directory"
    
    def test_required_database_variables(self, env_example_content):
        """Test that required database variables are present"""
        required_db_vars = [
            "DATABASE_URL",
            "CREDS_DATABASE_URL", 
            "POSTGRES_PASSWORD",
            "POSTGRES_CREDS_PASSWORD"
        ]
        
        for var in required_db_vars:
            assert f"{var}=" in env_example_content, f"Required database variable {var} not found in .env.example"
    
    def test_required_redis_variables(self, env_example_content):
        """Test that required Redis variables are present"""
        assert "REDIS_URL=" in env_example_content, "Required REDIS_URL variable not found in .env.example"
    
    def test_required_jwt_variables(self, env_example_content):
        """Test that required JWT variables are present"""
        # Task 1.2 specifies JWT_SECRET, but codebase uses JWT_SECRET_KEY
        assert "JWT_SECRET_KEY=" in env_example_content, "Required JWT_SECRET_KEY variable not found in .env.example"
        assert "SECRET_KEY=" in env_example_content, "Required SECRET_KEY variable not found in .env.example"
    
    def test_required_stripe_variables(self, env_example_content):
        """Test that required Stripe variables are present"""
        required_stripe_vars = [
            "STRIPE_SECRET_KEY",
            "STRIPE_WEBHOOK_SECRET",
            "REACT_APP_STRIPE_PUBLISHABLE_KEY"
        ]
        
        for var in required_stripe_vars:
            assert f"{var}=" in env_example_content, f"Required Stripe variable {var} not found in .env.example"
    
    def test_external_service_variables(self, env_example_content):
        """Test that external service variables are present"""
        external_vars = [
            "SENDGRID_API_KEY",
            "TWILIO_ACCOUNT_SID", 
            "TWILIO_AUTH_TOKEN",
            "TWILIO_PHONE_NUMBER"
        ]
        
        for var in external_vars:
            assert f"{var}=" in env_example_content, f"External service variable {var} not found in .env.example"
    
    def test_application_config_variables(self, env_example_content):
        """Test that application configuration variables are present"""
        app_vars = [
            "ENVIRONMENT",
            "REACT_APP_API_URL",
            "REACT_APP_ENVIRONMENT"
        ]
        
        for var in app_vars:
            assert f"{var}=" in env_example_content, f"Application config variable {var} not found in .env.example"
    
    def test_docker_port_variables(self, env_example_content):
        """Test that Docker port configuration variables are present"""
        port_vars = [
            "BACKEND_PORT",
            "FRONTEND_PORT", 
            "POSTGRES_PORT",
            "POSTGRES_CREDS_PORT",
            "REDIS_PORT"
        ]
        
        for var in port_vars:
            assert f"{var}=" in env_example_content, f"Docker port variable {var} not found in .env.example"
    
    def test_security_documentation_present(self, env_example_content):
        """Test that security notes and documentation are present"""
        security_keywords = [
            "Never commit actual secrets",
            "openssl rand -hex 32",
            "production",
            "secrets management"
        ]
        
        for keyword in security_keywords:
            assert keyword in env_example_content, f"Security documentation should mention '{keyword}'"
    
    def test_file_structure_and_comments(self, env_example_content):
        """Test that file has proper structure and comments"""
        # Check for section headers
        assert "DATABASE CONFIGURATION" in env_example_content
        assert "REDIS CONFIGURATION" in env_example_content
        assert "AUTHENTICATION & SECURITY" in env_example_content
        assert "STRIPE PAYMENT PROCESSING" in env_example_content
        assert "EXTERNAL SERVICES" in env_example_content
        assert "APPLICATION CONFIGURATION" in env_example_content
        assert "DOCKER & DEVELOPMENT" in env_example_content
        assert "SECURITY NOTES" in env_example_content
        
        # Check for proper commenting
        lines = env_example_content.split('\n')
        comment_lines = [line for line in lines if line.strip().startswith('#')]
        assert len(comment_lines) > 20, "File should have comprehensive comments and documentation"
    
    def test_no_actual_secrets_present(self, env_example_content):
        """Test that no actual secrets are present in the example file"""
        # Common patterns that might indicate real secrets
        forbidden_patterns = [
            "sk_live_",  # Live Stripe keys
            "pk_live_",  # Live Stripe publishable keys
            "SG.",       # Real SendGrid keys start with SG.
            "=AC",       # Real Twilio Account SIDs start with AC (check for value assignment)
        ]
        
        for pattern in forbidden_patterns:
            assert pattern not in env_example_content, f"Potential real secret pattern '{pattern}' found in .env.example"
    
    def test_placeholder_values_present(self, env_example_content):
        """Test that placeholder values are used instead of real values"""
        placeholder_patterns = [
            "your_password",
            "your_secure_",
            "sk_test_",
            "pk_test_",
            "your_sendgrid_",
            "your_twilio_"
        ]
        
        found_placeholders = 0
        for pattern in placeholder_patterns:
            if pattern in env_example_content:
                found_placeholders += 1
        
        assert found_placeholders >= 3, "File should contain placeholder values, not real secrets" 