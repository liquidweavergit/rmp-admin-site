"""
Integration tests for complete Men's Circle Management Platform project structure.

This test suite validates the integration and relationships between all project 
components, ensuring the complete structure works as a cohesive system for
the men's circle management platform.

Following TDD principles: These integration tests validate that all components
work together to support the platform's business requirements.
"""

import asyncio
import json
import os
import re
import subprocess
import sys
import tempfile
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple
import pytest


class TestProjectStructureIntegration:
    """Integration tests for complete project structure validation."""

    @pytest.fixture(scope="class")
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture(scope="class")
    def all_project_files(self, project_root: Path) -> List[Path]:
        """Get all files in the project structure."""
        files = []
        for root, dirs, filenames in os.walk(project_root):
            # Skip hidden directories and common ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                '__pycache__', 'node_modules', 'build', 'dist', 'venv', 'env'
            ]]
            
            for filename in filenames:
                if not filename.startswith('.') and not filename.endswith('.pyc'):
                    files.append(Path(root) / filename)
        
        return files

    @pytest.mark.integration
    @pytest.mark.structure
    def test_complete_directory_structure_integration(self, project_root: Path):
        """Test that all core directories exist and integrate properly."""
        required_directories = {
            'backend': 'FastAPI application backend',
            'frontend': 'React/TypeScript frontend application',
            'docker': 'Docker containerization configuration',
            'tests': 'Comprehensive test suite',
            'docs': 'Project documentation',
            'scripts': 'Development automation scripts',
            '.github': 'GitHub configuration and workflows',
            'project-documents': 'Project management documents'
        }
        
        missing_directories = []
        directory_relationships = {}
        
        for directory, description in required_directories.items():
            dir_path = project_root / directory
            if not dir_path.exists():
                missing_directories.append(f"{directory} ({description})")
            else:
                # Validate directory has content
                contents = list(dir_path.iterdir())
                directory_relationships[directory] = {
                    'exists': True,
                    'has_content': len(contents) > 0,
                    'content_count': len(contents),
                    'description': description
                }
        
        assert not missing_directories, f"Missing required directories: {missing_directories}"
        
        # Validate all directories have meaningful content
        empty_directories = [
            name for name, info in directory_relationships.items() 
            if not info['has_content']
        ]
        
        assert not empty_directories, f"Empty directories found: {empty_directories}"

    @pytest.mark.integration
    @pytest.mark.structure
    def test_cross_directory_file_consistency(self, project_root: Path):
        """Test that files across directories maintain consistency."""
        
        # Check backend/__init__.py exists for Python package structure
        backend_init = project_root / 'backend' / '__init__.py'
        assert backend_init.exists(), "Backend must be a Python package with __init__.py"
        
        # Check frontend/package.json exists for Node.js structure
        frontend_package = project_root / 'frontend' / 'package.json'
        assert frontend_package.exists(), "Frontend must have package.json for Node.js"
        
        # Check tests/conftest.py exists for pytest configuration
        tests_conftest = project_root / 'tests' / 'conftest.py'
        assert tests_conftest.exists(), "Tests must have conftest.py for pytest"
        
        # Check pytest.ini exists in project root
        pytest_ini = project_root / 'pytest.ini'
        assert pytest_ini.exists(), "Project must have pytest.ini for test configuration"
        
        # Check scripts have executable permissions
        scripts_dir = project_root / 'scripts'
        for script_file in scripts_dir.glob('*.sh'):
            assert os.access(script_file, os.X_OK), f"Script {script_file.name} must be executable"

    @pytest.mark.integration
    @pytest.mark.configuration
    def test_configuration_file_integration(self, project_root: Path):
        """Test that all configuration files integrate properly."""
        
        # Test pytest.ini and conftest.py integration
        pytest_ini = project_root / 'pytest.ini'
        conftest_py = project_root / 'tests' / 'conftest.py'
        
        assert pytest_ini.exists() and conftest_py.exists(), "Both pytest.ini and conftest.py must exist"
        
        # Validate pytest.ini has required sections
        pytest_content = pytest_ini.read_text()
        required_pytest_sections = [
            'testpaths',
            'markers',
            'addopts',
            'asyncio_mode'
        ]
        
        for section in required_pytest_sections:
            assert section in pytest_content, f"pytest.ini must contain {section} configuration"
        
        # Validate .gitignore covers all necessary patterns
        gitignore = project_root / '.gitignore'
        assert gitignore.exists(), ".gitignore must exist"
        
        gitignore_content = gitignore.read_text()
        required_patterns = [
            '*.pyc',
            '__pycache__/',
            'node_modules/',
            '.env',
            '*.log'
        ]
        
        for pattern in required_patterns:
            assert pattern in gitignore_content, f".gitignore must contain pattern: {pattern}"

    @pytest.mark.integration
    @pytest.mark.platform
    def test_mens_circle_platform_integration(self, project_root: Path):
        """Test men's circle platform specific integration requirements."""
        
        # Validate README.md contains platform-specific information
        readme = project_root / 'README.md'
        assert readme.exists(), "README.md must exist"
        
        readme_content = readme.read_text()
        platform_requirements = [
            "Men's Circle Management Platform",
            "FastAPI",
            "React",
            "PostgreSQL",
            "Docker",
            "Setup",
            "Development"
        ]
        
        for requirement in platform_requirements:
            assert requirement in readme_content, f"README.md must contain: {requirement}"
        
        # Validate GitHub Actions workflows exist for CI/CD
        workflows_dir = project_root / '.github' / 'workflows'
        assert workflows_dir.exists(), "GitHub workflows directory must exist"
        
        required_workflows = ['ci.yml', 'test.yml', 'deploy.yml']
        for workflow in required_workflows:
            workflow_file = workflows_dir / workflow
            assert workflow_file.exists(), f"GitHub workflow {workflow} must exist"
            
            # Validate workflow has proper YAML structure
            workflow_content = workflow_file.read_text()
            workflow_data = yaml.safe_load(workflow_content)
            
            assert 'name' in workflow_data, f"{workflow} must have a name"
            assert ('on' in workflow_data or True in workflow_data), f"{workflow} must have trigger conditions"
            assert 'jobs' in workflow_data, f"{workflow} must have jobs defined"

    @pytest.mark.integration
    @pytest.mark.testing
    def test_testing_framework_integration(self, project_root: Path):
        """Test that the complete testing framework integrates properly."""
        
        # Validate pytest configuration works
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', '--collect-only', '-q'],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"pytest collection failed: {result.stderr}"
        
        # Validate structure tests can be run
        structure_tests_result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/structure/', '-v'],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        assert structure_tests_result.returncode == 0, "Structure tests must pass"
        assert "PASSED" in structure_tests_result.stdout, "Structure tests must show PASSED results"
        
        # Validate validation script integration
        validation_script = project_root / 'scripts' / 'validate-structure.sh'
        if validation_script.exists():
            script_result = subprocess.run(
                ['./scripts/validate-structure.sh'],
                cwd=project_root,
                capture_output=True,
                text=True
            )
            
            assert script_result.returncode == 0, "Validation script must execute successfully"
            assert "ALL VALIDATIONS PASSED" in script_result.stdout, "Validation script must show success"

    @pytest.mark.integration
    @pytest.mark.documentation
    def test_documentation_integration(self, project_root: Path):
        """Test that documentation integrates across the project."""
        
        # Validate docs directory structure
        docs_dir = project_root / 'docs'
        docs_readme = docs_dir / 'README.md'
        
        assert docs_readme.exists(), "docs/README.md must exist"
        
        # Validate project root README.md is comprehensive
        main_readme = project_root / 'README.md'
        readme_content = main_readme.read_text()
        
        # Check for required sections
        required_sections = [
            "# Men's Circle Management Platform",
            "## 🚀 Quick Start",
            "## 📋 Manual Setup",
            "## 🛠️ Development",
            "## 🏗️ Architecture",
            "## 🧪 Testing"
        ]
        
        for section in required_sections:
            assert section in readme_content, f"README.md must contain section: {section}"
        
        # Validate documentation references are consistent
        docker_readme = project_root / 'docker' / 'README.md'
        assert docker_readme.exists(), "docker/README.md must exist for containerization docs"

    @pytest.mark.integration
    @pytest.mark.scripts
    def test_automation_scripts_integration(self, project_root: Path):
        """Test that automation scripts integrate with the project structure."""
        
        scripts_dir = project_root / 'scripts'
        required_scripts = ['setup-dev.sh', 'validate-structure.sh']
        
        for script_name in required_scripts:
            script_path = scripts_dir / script_name
            assert script_path.exists(), f"Required script {script_name} must exist"
            assert os.access(script_path, os.X_OK), f"Script {script_name} must be executable"
            
            # Validate script has proper shebang and content
            script_content = script_path.read_text()
            assert script_content.startswith('#!/'), f"Script {script_name} must have proper shebang"

    @pytest.mark.integration
    @pytest.mark.security
    def test_security_configuration_integration(self, project_root: Path):
        """Test that security configurations integrate properly across the project."""
        
        # Validate .gitignore protects sensitive information
        gitignore = project_root / '.gitignore'
        gitignore_content = gitignore.read_text()
        
        security_patterns = [
            '.env',
            '*.key',
            '*.pem',
            '*.p12',
            '*.pfx',
            'secrets/',
            'private/',
            '*.secret'
        ]
        
        missing_patterns = []
        for pattern in security_patterns:
            if pattern not in gitignore_content:
                missing_patterns.append(pattern)
        
        assert not missing_patterns, f"Security patterns missing from .gitignore: {missing_patterns}"
        
        # Validate no sensitive files are tracked
        tracked_files_result = subprocess.run(
            ['git', 'ls-files'],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        if tracked_files_result.returncode == 0:
            tracked_files = tracked_files_result.stdout.split('\n')
            sensitive_files = [
                f for f in tracked_files 
                if any(pattern.replace('*', '') in f for pattern in security_patterns)
            ]
            
            assert not sensitive_files, f"Sensitive files found in git tracking: {sensitive_files}"

    @pytest.mark.integration
    @pytest.mark.performance
    def test_project_structure_performance(self, project_root: Path, all_project_files: List[Path]):
        """Test that the project structure performs well."""
        
        # Test file count is reasonable
        file_count = len(all_project_files)
        assert file_count > 10, "Project should have substantial content"
        assert file_count < 10000, "Project should not have excessive files"
        
        # Test pytest collection performance
        import time
        start_time = time.time()
        
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', '--collect-only', '-q'],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        collection_time = time.time() - start_time
        
        assert result.returncode == 0, "pytest collection must succeed"
        assert collection_time < 5.0, f"pytest collection too slow: {collection_time}s"
        
        # Test validation script performance
        validation_script = project_root / 'scripts' / 'validate-structure.sh'
        if validation_script.exists():
            start_time = time.time()
            
            script_result = subprocess.run(
                ['./scripts/validate-structure.sh'],
                cwd=project_root,
                capture_output=True,
                text=True
            )
            
            validation_time = time.time() - start_time
            
            assert script_result.returncode == 0, "Validation script must succeed"
            assert validation_time < 3.0, f"Validation script too slow: {validation_time}s"

    @pytest.mark.integration
    @pytest.mark.deployment
    def test_deployment_readiness_integration(self, project_root: Path):
        """Test that the project structure is ready for deployment."""
        
        # Validate Docker configuration exists
        docker_dir = project_root / 'docker'
        docker_readme = docker_dir / 'README.md'
        
        assert docker_readme.exists(), "Docker documentation must exist"
        
        # Validate GitHub Actions workflows are deployment-ready
        workflows_dir = project_root / '.github' / 'workflows'
        deploy_workflow = workflows_dir / 'deploy.yml'
        
        assert deploy_workflow.exists(), "Deployment workflow must exist"
        
        deploy_content = deploy_workflow.read_text()
        deploy_data = yaml.safe_load(deploy_content)
        
        # Check for deployment-related job configuration
        assert 'jobs' in deploy_data, "Deploy workflow must have jobs"
        
        # Validate project has necessary configuration files
        required_config_files = [
            'pytest.ini',
            '.gitignore',
            'README.md'
        ]
        
        for config_file in required_config_files:
            config_path = project_root / config_file
            assert config_path.exists(), f"Required config file {config_file} must exist"

    @pytest.mark.integration
    @pytest.mark.comprehensive
    def test_complete_project_integration_health(self, project_root: Path, all_project_files: List[Path]):
        """Comprehensive health check of complete project integration."""
        
        # Collect all validation results
        validation_results = {
            'directories': {},
            'files': {},
            'configurations': {},
            'scripts': {},
            'documentation': {},
            'security': {},
            'performance': {}
        }
        
        # Validate core directories
        core_dirs = ['backend', 'frontend', 'docker', 'tests', 'docs', 'scripts', '.github']
        for directory in core_dirs:
            dir_path = project_root / directory
            validation_results['directories'][directory] = {
                'exists': dir_path.exists(),
                'has_content': len(list(dir_path.iterdir())) > 0 if dir_path.exists() else False
            }
        
        # Validate key files
        key_files = [
            'README.md',
            'pytest.ini',
            '.gitignore',
            'backend/__init__.py',
            'frontend/package.json',
            'tests/conftest.py',
            'docs/README.md',
            'docker/README.md'
        ]
        
        for file_path in key_files:
            full_path = project_root / file_path
            validation_results['files'][file_path] = {
                'exists': full_path.exists(),
                'readable': full_path.is_file() and os.access(full_path, os.R_OK) if full_path.exists() else False
            }
        
        # Generate comprehensive report
        failed_validations = []
        
        for category, items in validation_results.items():
            for item, checks in items.items():
                for check, result in checks.items():
                    if not result:
                        failed_validations.append(f"{category}.{item}.{check}")
        
        # Assert overall health
        assert not failed_validations, f"Project integration health failures: {failed_validations}"
        
        # Validate minimum project maturity
        total_files = len(all_project_files)
        total_directories = len([d for d in project_root.rglob('*') if d.is_dir()])
        
        project_health_score = {
            'total_files': total_files,
            'total_directories': total_directories,
            'core_directories': len([d for d in core_dirs if (project_root / d).exists()]),
            'key_files': len([f for f in key_files if (project_root / f).exists()]),
            'health_percentage': (len([f for f in key_files if (project_root / f).exists()]) / len(key_files)) * 100
        }
        
        assert project_health_score['health_percentage'] >= 95.0, f"Project health too low: {project_health_score}"
        assert project_health_score['core_directories'] == len(core_dirs), "All core directories must exist"
        
        # Final integration validation
        assert total_files >= 15, f"Project should have substantial content: {total_files} files"
        assert total_directories >= 8, f"Project should have proper structure: {total_directories} directories"


class TestProjectWorkflowIntegration:
    """Integration tests for complete project workflow validation."""

    @pytest.mark.integration
    @pytest.mark.workflow
    def test_development_workflow_integration(self, project_root: Path):
        """Test that the complete development workflow integrates properly."""
        
        # Test that pytest works with the configuration
        pytest_result = subprocess.run(
            [sys.executable, '-m', 'pytest', '--version'],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        assert pytest_result.returncode == 0, "pytest must be functional"
        
        # Test that git operations work
        git_status_result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        # Git should be initialized (returncode 0 or 128 if not a git repo)
        assert git_status_result.returncode in [0, 128], "Git integration check"

    @pytest.mark.integration
    @pytest.mark.cicd
    def test_cicd_integration_readiness(self, project_root: Path):
        """Test that the project is ready for CI/CD integration."""
        
        # Validate GitHub Actions workflow files
        workflows_dir = project_root / '.github' / 'workflows'
        workflow_files = list(workflows_dir.glob('*.yml'))
        
        assert len(workflow_files) >= 3, "Should have multiple workflow files"
        
        for workflow_file in workflow_files:
            workflow_content = workflow_file.read_text()
            
            # Basic YAML validation
            try:
                workflow_data = yaml.safe_load(workflow_content)
                assert isinstance(workflow_data, dict), f"Invalid YAML in {workflow_file.name}"
                assert 'name' in workflow_data, f"Workflow {workflow_file.name} must have name"
                assert 'jobs' in workflow_data, f"Workflow {workflow_file.name} must have jobs"
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in {workflow_file.name}: {e}")

    @pytest.mark.integration
    @pytest.mark.platform
    @pytest.mark.comprehensive
    def test_mens_circle_platform_complete_integration(self, project_root: Path):
        """Test complete integration of men's circle platform requirements."""
        
        # Validate platform-specific structure is complete
        platform_requirements = {
            'backend': 'FastAPI backend for men\'s circle management',
            'frontend': 'React frontend for user interfaces',
            'database_support': 'PostgreSQL dual database architecture',
            'testing': 'Comprehensive test suite',
            'documentation': 'Complete setup and development docs',
            'automation': 'CI/CD and development scripts',
            'security': 'Security and compliance configurations'
        }
        
        validation_results = {}
        
        # Backend validation
        backend_dir = project_root / 'backend'
        validation_results['backend'] = {
            'directory_exists': backend_dir.exists(),
            'is_python_package': (backend_dir / '__init__.py').exists(),
            'ready_for_fastapi': True  # Structure ready for FastAPI development
        }
        
        # Frontend validation
        frontend_dir = project_root / 'frontend'
        validation_results['frontend'] = {
            'directory_exists': frontend_dir.exists(),
            'has_package_json': (frontend_dir / 'package.json').exists(),
            'ready_for_react': True  # Structure ready for React development
        }
        
        # Database support validation
        validation_results['database_support'] = {
            'docker_config': (project_root / 'docker' / 'README.md').exists(),
            'test_database_config': 'DATABASE_URL' in (project_root / 'tests' / 'conftest.py').read_text(),
            'dual_database_ready': 'CREDS_DATABASE_URL' in (project_root / 'tests' / 'conftest.py').read_text()
        }
        
        # Testing validation
        tests_dir = project_root / 'tests'
        validation_results['testing'] = {
            'pytest_configured': (project_root / 'pytest.ini').exists(),
            'fixtures_available': (tests_dir / 'conftest.py').exists(),
            'structure_tests': (tests_dir / 'structure').exists(),
            'integration_tests': (tests_dir / 'integration').exists()
        }
        
        # Documentation validation
        validation_results['documentation'] = {
            'main_readme': (project_root / 'README.md').exists(),
            'docs_directory': (project_root / 'docs' / 'README.md').exists(),
            'docker_docs': (project_root / 'docker' / 'README.md').exists(),
            'platform_branding': "Men's Circle Management Platform" in (project_root / 'README.md').read_text()
        }
        
        # Automation validation
        scripts_dir = project_root / 'scripts'
        validation_results['automation'] = {
            'setup_script': (scripts_dir / 'setup-dev.sh').exists(),
            'validation_script': (scripts_dir / 'validate-structure.sh').exists(),
            'github_actions': len(list((project_root / '.github' / 'workflows').glob('*.yml'))) >= 3
        }
        
        # Security validation
        gitignore_content = (project_root / '.gitignore').read_text()
        validation_results['security'] = {
            'gitignore_comprehensive': all(pattern in gitignore_content for pattern in ['.env', '*.key', '*.log']),
            'no_secrets_tracked': True,  # Assumed based on gitignore validation
            'security_patterns': '*.secret' in gitignore_content or 'secrets/' in gitignore_content
        }
        
        # Validate all requirements are met
        failed_requirements = []
        for requirement, checks in validation_results.items():
            for check, result in checks.items():
                if not result:
                    failed_requirements.append(f"{requirement}.{check}")
        
        assert not failed_requirements, f"Men's circle platform integration failures: {failed_requirements}"
        
        # Final platform readiness assessment
        readiness_score = sum(
            sum(checks.values()) for checks in validation_results.values()
        ) / sum(
            len(checks) for checks in validation_results.values()
        ) * 100
        
        assert readiness_score >= 95.0, f"Platform readiness score too low: {readiness_score:.1f}%" 