"""
Test suite for project directory structure validation.

This test module validates that the men's circle management platform
has the correct directory structure as specified in the project requirements.

Following TDD principles: This test will initially fail and drive the
creation of the proper directory structure.
"""

import os
import pytest
from pathlib import Path


class TestProjectDirectoryStructure:
    """Test cases for validating the project directory structure."""
    
    @pytest.fixture
    def project_root(self):
        """Get the project root directory."""
        # Navigate up from tests/structure/ to project root
        current_dir = Path(__file__).parent
        return current_dir.parent.parent
    
    def test_backend_directory_exists(self, project_root):
        """Test that backend/ directory exists."""
        backend_dir = project_root / "backend"
        assert backend_dir.exists(), "backend/ directory must exist"
        assert backend_dir.is_dir(), "backend/ must be a directory"
    
    def test_frontend_directory_exists(self, project_root):
        """Test that frontend/ directory exists."""
        frontend_dir = project_root / "frontend"
        assert frontend_dir.exists(), "frontend/ directory must exist"
        assert frontend_dir.is_dir(), "frontend/ must be a directory"
    
    def test_docker_directory_exists(self, project_root):
        """Test that docker/ directory exists."""
        docker_dir = project_root / "docker"
        assert docker_dir.exists(), "docker/ directory must exist"
        assert docker_dir.is_dir(), "docker/ must be a directory"
    
    def test_tests_directory_exists(self, project_root):
        """Test that tests/ directory exists."""
        tests_dir = project_root / "tests"
        assert tests_dir.exists(), "tests/ directory must exist"
        assert tests_dir.is_dir(), "tests/ must be a directory"
    
    def test_docs_directory_exists(self, project_root):
        """Test that docs/ directory exists."""
        docs_dir = project_root / "docs"
        assert docs_dir.exists(), "docs/ directory must exist"
        assert docs_dir.is_dir(), "docs/ must be a directory"
    
    def test_scripts_directory_exists(self, project_root):
        """Test that scripts/ directory exists."""
        scripts_dir = project_root / "scripts"
        assert scripts_dir.exists(), "scripts/ directory must exist"
        assert scripts_dir.is_dir(), "scripts/ must be a directory"
    
    def test_github_workflows_directory_exists(self, project_root):
        """Test that .github/workflows/ directory exists."""
        github_workflows_dir = project_root / ".github" / "workflows"
        assert github_workflows_dir.exists(), ".github/workflows/ directory must exist"
        assert github_workflows_dir.is_dir(), ".github/workflows/ must be a directory"
    
    def test_backend_has_init_file(self, project_root):
        """Test that backend/ contains __init__.py file."""
        backend_init = project_root / "backend" / "__init__.py"
        assert backend_init.exists(), "backend/__init__.py file must exist"
        assert backend_init.is_file(), "backend/__init__.py must be a file"
    
    def test_frontend_has_package_json_placeholder(self, project_root):
        """Test that frontend/ contains package.json placeholder."""
        frontend_package = project_root / "frontend" / "package.json"
        assert frontend_package.exists(), "frontend/package.json placeholder must exist"
        assert frontend_package.is_file(), "frontend/package.json must be a file"
    
    def test_docker_has_readme(self, project_root):
        """Test that docker/ contains README.md."""
        docker_readme = project_root / "docker" / "README.md"
        assert docker_readme.exists(), "docker/README.md must exist"
        assert docker_readme.is_file(), "docker/README.md must be a file"
    
    def test_tests_has_conftest(self, project_root):
        """Test that tests/ contains conftest.py."""
        tests_conftest = project_root / "tests" / "conftest.py"
        assert tests_conftest.exists(), "tests/conftest.py must exist"
        assert tests_conftest.is_file(), "tests/conftest.py must be a file"
    
    def test_tests_structure_subdirectory_exists(self, project_root):
        """Test that tests/structure/ subdirectory exists."""
        tests_structure_dir = project_root / "tests" / "structure"
        assert tests_structure_dir.exists(), "tests/structure/ directory must exist"
        assert tests_structure_dir.is_dir(), "tests/structure/ must be a directory"
    
    def test_docs_has_initial_readme(self, project_root):
        """Test that docs/ contains initial README.md."""
        docs_readme = project_root / "docs" / "README.md"
        assert docs_readme.exists(), "docs/README.md must exist"
        assert docs_readme.is_file(), "docs/README.md must be a file"
    
    def test_scripts_has_setup_dev_template(self, project_root):
        """Test that scripts/ contains setup-dev.sh template."""
        setup_script = project_root / "scripts" / "setup-dev.sh"
        assert setup_script.exists(), "scripts/setup-dev.sh template must exist"
        assert setup_script.is_file(), "scripts/setup-dev.sh must be a file"
    
    def test_gitignore_exists(self, project_root):
        """Test that comprehensive .gitignore exists."""
        gitignore_file = project_root / ".gitignore"
        assert gitignore_file.exists(), ".gitignore file must exist"
        assert gitignore_file.is_file(), ".gitignore must be a file"
        
        # Check that .gitignore contains essential exclusions
        with open(gitignore_file, 'r') as f:
            gitignore_content = f.read()
        
        essential_patterns = [
            "*.pyc",  # Python bytecode
            "__pycache__/",  # Python cache
            "node_modules/",  # Node.js dependencies
            ".env",  # Environment variables
            "*.log",  # Log files
        ]
        
        for pattern in essential_patterns:
            assert pattern in gitignore_content, f".gitignore must contain '{pattern}' pattern"
    
    def test_project_readme_exists(self, project_root):
        """Test that project README.md exists with setup instructions."""
        readme_file = project_root / "README.md"
        assert readme_file.exists(), "README.md file must exist"
        assert readme_file.is_file(), "README.md must be a file"
        
        # Check that README contains essential sections
        with open(readme_file, 'r') as f:
            readme_content = f.read()
        
        essential_sections = [
            "Men's Circle Management Platform",
            "Setup",
            "Development",
        ]
        
        for section in essential_sections:
            assert section in readme_content, f"README.md must contain '{section}' section"
    
    def test_all_core_directories_present(self, project_root):
        """Test that all core directories are present together."""
        required_directories = [
            "backend",
            "frontend", 
            "docker",
            "tests",
            "docs",
            "scripts",
            ".github"
        ]
        
        for directory in required_directories:
            dir_path = project_root / directory
            assert dir_path.exists(), f"Required directory '{directory}' must exist"
            assert dir_path.is_dir(), f"'{directory}' must be a directory"
    
    def test_directory_structure_completeness(self, project_root):
        """Test overall directory structure completeness."""
        # This test ensures the minimum viable directory structure
        # is complete for the men's circle management platform
        
        structure_requirements = {
            "backend": ["__init__.py"],
            "frontend": ["package.json"],
            "docker": ["README.md"],
            "tests": ["conftest.py", "structure"],
            "docs": ["README.md"],
            "scripts": ["setup-dev.sh"],
            ".github": ["workflows"]
        }
        
        for directory, required_items in structure_requirements.items():
            base_dir = project_root / directory
            assert base_dir.exists(), f"Directory '{directory}' must exist"
            
            for item in required_items:
                item_path = base_dir / item
                assert item_path.exists(), f"Required item '{directory}/{item}' must exist"


class TestDirectoryPermissions:
    """Test cases for directory permissions and access."""
    
    @pytest.fixture
    def project_root(self):
        """Get the project root directory."""
        current_dir = Path(__file__).parent
        return current_dir.parent.parent
    
    def test_scripts_directory_executable_permissions(self, project_root):
        """Test that scripts directory has proper permissions."""
        scripts_dir = project_root / "scripts"
        if scripts_dir.exists():
            # Check if directory is readable and executable
            assert os.access(scripts_dir, os.R_OK), "scripts/ directory must be readable"
            assert os.access(scripts_dir, os.X_OK), "scripts/ directory must be executable"
    
    def test_setup_script_executable(self, project_root):
        """Test that setup-dev.sh script is executable."""
        setup_script = project_root / "scripts" / "setup-dev.sh"
        if setup_script.exists():
            # Check if script is executable
            assert os.access(setup_script, os.X_OK), "setup-dev.sh must be executable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 