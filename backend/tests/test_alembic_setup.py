"""
Test suite for Alembic database migration setup

This test suite verifies that:
1. Alembic configuration files are properly set up
2. Both main and credentials databases can be migrated
3. Migration scripts work correctly
4. Database schemas are created as expected
"""
import os
import subprocess
import pytest
from pathlib import Path


class TestAlembicSetup:
    """Test Alembic migration setup and functionality"""
    
    @pytest.fixture
    def backend_dir(self):
        """Get the backend directory path"""
        return Path(__file__).parent.parent
    
    @pytest.fixture
    def env_vars(self):
        """Set up test environment variables"""
        return {
            "DATABASE_URL": "postgresql+asyncpg://postgres:development_password@localhost:5432/mens_circle_main",
            "CREDS_DATABASE_URL": "postgresql+asyncpg://postgres:development_creds_password@localhost:5433/mens_circle_creds",
            "REDIS_URL": "redis://localhost:6379",
            "JWT_SECRET_KEY": "test_secret_key",
            "STRIPE_SECRET_KEY": "sk_test_fake_key"
        }
    
    def test_alembic_config_files_exist(self, backend_dir):
        """Test that Alembic configuration files exist"""
        # Main database config
        alembic_ini = backend_dir / "alembic.ini"
        assert alembic_ini.exists(), "alembic.ini should exist"
        
        # Credentials database config
        alembic_creds_ini = backend_dir / "alembic-credentials.ini"
        assert alembic_creds_ini.exists(), "alembic-credentials.ini should exist"
        
        # Main database env.py
        main_env = backend_dir / "alembic" / "env.py"
        assert main_env.exists(), "alembic/env.py should exist"
        
        # Credentials database env.py
        creds_env = backend_dir / "alembic-credentials" / "env.py"
        assert creds_env.exists(), "alembic-credentials/env.py should exist"
    
    def test_migration_script_exists(self, backend_dir):
        """Test that the migration management script exists and is executable"""
        migrate_script = backend_dir / "migrate.py"
        assert migrate_script.exists(), "migrate.py should exist"
        assert os.access(migrate_script, os.X_OK), "migrate.py should be executable"
    
    def test_alembic_current_command(self, backend_dir, env_vars):
        """Test that alembic current command works for both databases"""
        # Test main database
        result = subprocess.run(
            ["alembic", "current"],
            cwd=backend_dir,
            env={**os.environ, **env_vars},
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Main database alembic current failed: {result.stderr}"
        
        # Test credentials database
        result = subprocess.run(
            ["alembic", "-c", "alembic-credentials.ini", "current"],
            cwd=backend_dir,
            env={**os.environ, **env_vars},
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Credentials database alembic current failed: {result.stderr}"
    
    def test_migration_script_current_command(self, backend_dir, env_vars):
        """Test that the migration script current command works"""
        result = subprocess.run(
            ["python", "migrate.py", "current"],
            cwd=backend_dir,
            env={**os.environ, **env_vars},
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Migration script current failed: {result.stderr}"
        assert "Main database current revision" in result.stdout
        assert "Credentials database current revision" in result.stdout
    
    def test_model_imports_work(self, backend_dir):
        """Test that model imports work correctly in Alembic env files"""
        # Test main database models import
        try:
            import sys
            sys.path.append(str(backend_dir))
            from app.models.user import User
            assert hasattr(User, '__tablename__')
            assert User.__tablename__ == 'users'
        except ImportError as e:
            pytest.fail(f"Failed to import User model: {e}")
        
        # Test credentials database models import
        try:
            from app.models.credentials import UserCredentials
            assert hasattr(UserCredentials, '__tablename__')
            assert UserCredentials.__tablename__ == 'user_credentials'
        except ImportError as e:
            pytest.fail(f"Failed to import UserCredentials model: {e}")
    
    def test_alembic_config_content(self, backend_dir):
        """Test that Alembic configuration files have correct content"""
        # Check main database config
        alembic_ini = backend_dir / "alembic.ini"
        content = alembic_ini.read_text()
        assert "script_location = alembic" in content
        assert "# sqlalchemy.url is now loaded from environment variables" in content
        
        # Check credentials database config
        alembic_creds_ini = backend_dir / "alembic-credentials.ini"
        content = alembic_creds_ini.read_text()
        assert "script_location = alembic-credentials" in content
        assert "# See CREDS_DATABASE_URL in .env file" in content
    
    def test_env_files_have_async_support(self, backend_dir):
        """Test that env.py files are configured for async support"""
        # Check main database env.py
        main_env = backend_dir / "alembic" / "env.py"
        content = main_env.read_text()
        assert "import asyncio" in content
        assert "create_async_engine" in content
        assert "run_async_migrations" in content
        assert "from app.models.user import User" in content
        
        # Check credentials database env.py
        creds_env = backend_dir / "alembic-credentials" / "env.py"
        content = creds_env.read_text()
        assert "import asyncio" in content
        assert "create_async_engine" in content
        assert "run_async_migrations" in content
        assert "from app.models.credentials import UserCredentials" in content
    
    def test_migration_directories_exist(self, backend_dir):
        """Test that migration version directories exist"""
        main_versions = backend_dir / "alembic" / "versions"
        assert main_versions.exists(), "alembic/versions directory should exist"
        assert main_versions.is_dir(), "alembic/versions should be a directory"
        
        creds_versions = backend_dir / "alembic-credentials" / "versions"
        assert creds_versions.exists(), "alembic-credentials/versions directory should exist"
        assert creds_versions.is_dir(), "alembic-credentials/versions should be a directory"
    
    def test_migration_files_exist(self, backend_dir):
        """Test that initial migration files were created"""
        main_versions = backend_dir / "alembic" / "versions"
        main_migrations = list(main_versions.glob("*.py"))
        assert len(main_migrations) > 0, "Main database should have at least one migration file"
        
        # Check that the migration file contains expected content
        migration_content = main_migrations[0].read_text()
        assert "create_table('users'" in migration_content
        assert "Initial user model" in migration_content
        
        creds_versions = backend_dir / "alembic-credentials" / "versions"
        creds_migrations = list(creds_versions.glob("*.py"))
        assert len(creds_migrations) > 0, "Credentials database should have at least one migration file"
        
        # Check that the migration file contains expected content
        migration_content = creds_migrations[0].read_text()
        assert "create_table('user_credentials'" in migration_content
        assert "Initial user credentials model" in migration_content 