"""
Permission validation tests for Men's Circle Management Platform project structure.

This test suite validates that all directories and files have proper permissions
for secure development and deployment of the men's circle management platform.

Following TDD principles: These tests ensure the project structure maintains
appropriate security permissions across all components.
"""

import os
import stat
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import pytest


class TestProjectPermissions:
    """Test class for validating project directory and file permissions."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def core_directories(self, project_root: Path) -> List[Path]:
        """Get all core project directories that should exist."""
        return [
            project_root / 'backend',
            project_root / 'frontend', 
            project_root / 'docker',
            project_root / 'tests',
            project_root / 'docs',
            project_root / 'scripts',
            project_root / '.github',
            project_root / '.github' / 'workflows',
            project_root / 'project-documents'
        ]

    @pytest.fixture
    def script_files(self, project_root: Path) -> List[Path]:
        """Get all script files that should be executable."""
        scripts_dir = project_root / 'scripts'
        return [f for f in scripts_dir.glob('*.sh') if f.is_file()]

    @pytest.mark.structure
    @pytest.mark.security
    def test_directory_permissions_are_readable_writable(self, core_directories: List[Path]):
        """Test that all core directories are readable and writable by owner."""
        for directory in core_directories:
            if not directory.exists():
                pytest.skip(f"Directory {directory} does not exist yet")
            
            # Get directory permissions
            dir_stat = directory.stat()
            dir_mode = stat.filemode(dir_stat.st_mode)
            permissions = stat.S_IMODE(dir_stat.st_mode)
            
            # Check owner read permission (400)
            assert permissions & stat.S_IRUSR, f"Directory {directory} must be readable by owner. Current: {dir_mode}"
            
            # Check owner write permission (200)
            assert permissions & stat.S_IWUSR, f"Directory {directory} must be writable by owner. Current: {dir_mode}"
            
            # Check owner execute permission (100) - needed to access directory
            assert permissions & stat.S_IXUSR, f"Directory {directory} must be executable by owner. Current: {dir_mode}"

    @pytest.mark.structure
    @pytest.mark.security
    def test_directory_permissions_not_world_writable(self, core_directories: List[Path]):
        """Test that directories are not world-writable for security."""
        for directory in core_directories:
            if not directory.exists():
                pytest.skip(f"Directory {directory} does not exist yet")
            
            dir_stat = directory.stat()
            permissions = stat.S_IMODE(dir_stat.st_mode)
            dir_mode = stat.filemode(dir_stat.st_mode)
            
            # Check that directory is NOT world-writable (002)
            assert not (permissions & stat.S_IWOTH), f"Directory {directory} must not be world-writable for security. Current: {dir_mode}"

    @pytest.mark.structure
    @pytest.mark.security
    def test_scripts_are_executable(self, script_files: List[Path]):
        """Test that all shell scripts are executable."""
        assert len(script_files) > 0, "Should have at least one script file"
        
        for script_file in script_files:
            # Check if file is executable by owner
            assert os.access(script_file, os.X_OK), f"Script {script_file.name} must be executable"
            
            # Get detailed permissions
            script_stat = script_file.stat()
            permissions = stat.S_IMODE(script_stat.st_mode)
            file_mode = stat.filemode(script_stat.st_mode)
            
            # Check owner execute permission (100)
            assert permissions & stat.S_IXUSR, f"Script {script_file.name} must be executable by owner. Current: {file_mode}"

    @pytest.mark.structure
    @pytest.mark.security
    def test_script_permissions_not_world_writable(self, script_files: List[Path]):
        """Test that script files are not world-writable for security."""
        for script_file in script_files:
            script_stat = script_file.stat()
            permissions = stat.S_IMODE(script_stat.st_mode)
            file_mode = stat.filemode(script_stat.st_mode)
            
            # Check that script is NOT world-writable (002)
            assert not (permissions & stat.S_IWOTH), f"Script {script_file.name} must not be world-writable for security. Current: {file_mode}"

    @pytest.mark.structure
    @pytest.mark.security
    def test_regular_files_not_executable(self, project_root: Path):
        """Test that regular files (non-scripts) are not executable."""
        # Files that should NOT be executable
        regular_files = [
            project_root / 'README.md',
            project_root / '.gitignore',
            project_root / 'pytest.ini',
            project_root / 'backend' / '__init__.py',
            project_root / 'frontend' / 'package.json',
            project_root / 'tests' / 'conftest.py'
        ]
        
        for file_path in regular_files:
            if not file_path.exists():
                continue  # Skip files that don't exist yet
            
            file_stat = file_path.stat()
            permissions = stat.S_IMODE(file_stat.st_mode)
            file_mode = stat.filemode(file_stat.st_mode)
            
            # Regular files should not be executable
            assert not (permissions & stat.S_IXUSR), f"Regular file {file_path.name} should not be executable. Current: {file_mode}"
            assert not (permissions & stat.S_IXGRP), f"Regular file {file_path.name} should not be executable by group. Current: {file_mode}"
            assert not (permissions & stat.S_IXOTH), f"Regular file {file_path.name} should not be executable by others. Current: {file_mode}"

    @pytest.mark.structure
    @pytest.mark.security
    def test_configuration_files_readable(self, project_root: Path):
        """Test that configuration files are readable."""
        config_files = [
            project_root / 'pytest.ini',
            project_root / '.gitignore',
            project_root / 'tests' / 'conftest.py'
        ]
        
        for config_file in config_files:
            if not config_file.exists():
                continue  # Skip files that don't exist yet
            
            # Test that file is readable
            assert os.access(config_file, os.R_OK), f"Configuration file {config_file.name} must be readable"
            
            # Get detailed permissions
            file_stat = config_file.stat()
            permissions = stat.S_IMODE(file_stat.st_mode)
            file_mode = stat.filemode(file_stat.st_mode)
            
            # Check owner read permission (400)
            assert permissions & stat.S_IRUSR, f"Configuration file {config_file.name} must be readable by owner. Current: {file_mode}"

    @pytest.mark.structure
    @pytest.mark.security
    def test_test_files_permissions(self, project_root: Path):
        """Test that test files have appropriate permissions."""
        test_files = list((project_root / 'tests').rglob('*.py'))
        
        assert len(test_files) > 0, "Should have at least one test file"
        
        for test_file in test_files:
            # Test files should be readable
            assert os.access(test_file, os.R_OK), f"Test file {test_file.name} must be readable"
            
            # Test files should be writable by owner
            assert os.access(test_file, os.W_OK), f"Test file {test_file.name} must be writable by owner"
            
            # Test files should NOT be executable (they're modules, not scripts)
            file_stat = test_file.stat()
            permissions = stat.S_IMODE(file_stat.st_mode)
            file_mode = stat.filemode(file_stat.st_mode)
            
            assert not (permissions & stat.S_IXUSR), f"Test file {test_file.name} should not be executable. Current: {file_mode}"

    @pytest.mark.structure
    @pytest.mark.security
    def test_hidden_directories_permissions(self, project_root: Path):
        """Test that hidden directories have proper permissions."""
        hidden_dirs = [
            project_root / '.github',
            project_root / '.github' / 'workflows'
        ]
        
        for hidden_dir in hidden_dirs:
            if not hidden_dir.exists():
                continue  # Skip directories that don't exist yet
            
            # Hidden directories should be readable and writable by owner
            assert os.access(hidden_dir, os.R_OK), f"Hidden directory {hidden_dir.name} must be readable"
            assert os.access(hidden_dir, os.W_OK), f"Hidden directory {hidden_dir.name} must be writable by owner"
            
            # Get detailed permissions
            dir_stat = hidden_dir.stat()
            permissions = stat.S_IMODE(dir_stat.st_mode)
            dir_mode = stat.filemode(dir_stat.st_mode)
            
            # Check standard directory permissions
            assert permissions & stat.S_IRUSR, f"Hidden directory {hidden_dir.name} must be readable by owner. Current: {dir_mode}"
            assert permissions & stat.S_IWUSR, f"Hidden directory {hidden_dir.name} must be writable by owner. Current: {dir_mode}"
            assert permissions & stat.S_IXUSR, f"Hidden directory {hidden_dir.name} must be executable by owner. Current: {dir_mode}"

    @pytest.mark.structure
    @pytest.mark.platform
    def test_project_permissions_compliance(self, project_root: Path):
        """Test that project permissions comply with men's circle platform security requirements."""
        
        # Security-sensitive directories
        security_dirs = [
            project_root / 'scripts',    # Contains setup and validation scripts
            project_root / 'tests',      # Contains test code
            project_root / '.github'     # Contains CI/CD configurations
        ]
        
        for security_dir in security_dirs:
            if not security_dir.exists():
                continue
            
            dir_stat = security_dir.stat()
            permissions = stat.S_IMODE(dir_stat.st_mode)
            dir_mode = stat.filemode(dir_stat.st_mode)
            
            # Security-sensitive directories should not be world-writable
            assert not (permissions & stat.S_IWOTH), f"Security directory {security_dir.name} must not be world-writable. Current: {dir_mode}"
            
            # Should be readable and executable by owner and group for collaboration
            assert permissions & stat.S_IRUSR, f"Security directory {security_dir.name} must be readable by owner"
            assert permissions & stat.S_IXUSR, f"Security directory {security_dir.name} must be accessible by owner"

    @pytest.mark.structure
    @pytest.mark.performance
    def test_permission_check_performance(self, core_directories: List[Path], script_files: List[Path]):
        """Test that permission checks complete quickly for CI/CD integration."""
        import time
        
        start_time = time.time()
        
        # Check all directory permissions
        for directory in core_directories:
            if directory.exists():
                os.access(directory, os.R_OK)
                os.access(directory, os.W_OK)
                os.access(directory, os.X_OK)
        
        # Check all script permissions
        for script_file in script_files:
            os.access(script_file, os.R_OK)
            os.access(script_file, os.W_OK)
            os.access(script_file, os.X_OK)
        
        end_time = time.time()
        permission_check_time = end_time - start_time
        
        # Permission checks should complete quickly
        assert permission_check_time < 1.0, f"Permission checks too slow: {permission_check_time:.3f}s"

    @pytest.mark.structure
    @pytest.mark.comprehensive
    def test_comprehensive_permission_audit(self, project_root: Path):
        """Comprehensive audit of all project permissions."""
        
        # Collect permission audit results
        audit_results = {
            'directories': {},
            'scripts': {},
            'config_files': {},
            'test_files': {},
            'security_issues': []
        }
        
        # Audit all directories
        for item in project_root.rglob('*'):
            if item.is_dir() and not any(part.startswith('.') for part in item.parts if part != '.github'):
                relative_path = item.relative_to(project_root)
                item_stat = item.stat()
                permissions = stat.S_IMODE(item_stat.st_mode)
                
                audit_results['directories'][str(relative_path)] = {
                    'permissions': oct(permissions),
                    'mode': stat.filemode(item_stat.st_mode),
                    'readable': bool(permissions & stat.S_IRUSR),
                    'writable': bool(permissions & stat.S_IWUSR),
                    'executable': bool(permissions & stat.S_IXUSR),
                    'world_writable': bool(permissions & stat.S_IWOTH)
                }
                
                # Flag security issues
                if permissions & stat.S_IWOTH:
                    audit_results['security_issues'].append(f"Directory {relative_path} is world-writable")
        
        # Audit script files
        for script_file in (project_root / 'scripts').glob('*.sh'):
            if script_file.is_file():
                script_stat = script_file.stat()
                permissions = stat.S_IMODE(script_stat.st_mode)
                
                audit_results['scripts'][script_file.name] = {
                    'permissions': oct(permissions),
                    'mode': stat.filemode(script_stat.st_mode),
                    'executable': bool(permissions & stat.S_IXUSR),
                    'world_writable': bool(permissions & stat.S_IWOTH)
                }
                
                # Flag security issues
                if permissions & stat.S_IWOTH:
                    audit_results['security_issues'].append(f"Script {script_file.name} is world-writable")
                if not (permissions & stat.S_IXUSR):
                    audit_results['security_issues'].append(f"Script {script_file.name} is not executable")
        
        # Audit configuration files
        config_files = ['pytest.ini', '.gitignore', 'README.md']
        for config_name in config_files:
            config_file = project_root / config_name
            if config_file.exists():
                config_stat = config_file.stat()
                permissions = stat.S_IMODE(config_stat.st_mode)
                
                audit_results['config_files'][config_name] = {
                    'permissions': oct(permissions),
                    'mode': stat.filemode(config_stat.st_mode),
                    'readable': bool(permissions & stat.S_IRUSR),
                    'executable': bool(permissions & stat.S_IXUSR),
                    'world_writable': bool(permissions & stat.S_IWOTH)
                }
                
                # Flag security issues
                if permissions & stat.S_IWOTH:
                    audit_results['security_issues'].append(f"Config file {config_name} is world-writable")
                if permissions & stat.S_IXUSR:
                    audit_results['security_issues'].append(f"Config file {config_name} should not be executable")
        
        # Assert no critical security issues
        critical_issues = [issue for issue in audit_results['security_issues'] if 'world-writable' in issue]
        assert not critical_issues, f"Critical security issues found: {critical_issues}"
        
        # Validate minimum security standards
        total_directories = len(audit_results['directories'])
        secure_directories = sum(1 for d in audit_results['directories'].values() if not d['world_writable'])
        
        if total_directories > 0:
            security_percentage = (secure_directories / total_directories) * 100
            assert security_percentage >= 100.0, f"All directories must be secure. Security: {security_percentage:.1f}%"
        
        # Validate script executability
        total_scripts = len(audit_results['scripts'])
        executable_scripts = sum(1 for s in audit_results['scripts'].values() if s['executable'])
        
        if total_scripts > 0:
            executable_percentage = (executable_scripts / total_scripts) * 100
            assert executable_percentage >= 100.0, f"All scripts must be executable. Executable: {executable_percentage:.1f}%"


class TestPlatformSpecificPermissions:
    """Test class for men's circle platform-specific permission requirements."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent

    @pytest.mark.platform
    @pytest.mark.security
    def test_backend_directory_permissions(self, project_root: Path):
        """Test backend directory permissions for FastAPI deployment."""
        backend_dir = project_root / 'backend'
        
        if not backend_dir.exists():
            pytest.skip("Backend directory does not exist yet")
        
        # Backend should be readable and writable for development
        assert os.access(backend_dir, os.R_OK), "Backend directory must be readable"
        assert os.access(backend_dir, os.W_OK), "Backend directory must be writable"
        assert os.access(backend_dir, os.X_OK), "Backend directory must be accessible"
        
        # Check for __init__.py permissions
        init_file = backend_dir / '__init__.py'
        if init_file.exists():
            assert os.access(init_file, os.R_OK), "Backend __init__.py must be readable"
            
            # Should not be executable (it's a module, not a script)
            init_stat = init_file.stat()
            permissions = stat.S_IMODE(init_stat.st_mode)
            assert not (permissions & stat.S_IXUSR), "Backend __init__.py should not be executable"

    @pytest.mark.platform
    @pytest.mark.security
    def test_frontend_directory_permissions(self, project_root: Path):
        """Test frontend directory permissions for React development."""
        frontend_dir = project_root / 'frontend'
        
        if not frontend_dir.exists():
            pytest.skip("Frontend directory does not exist yet")
        
        # Frontend should be readable and writable for development
        assert os.access(frontend_dir, os.R_OK), "Frontend directory must be readable"
        assert os.access(frontend_dir, os.W_OK), "Frontend directory must be writable"
        assert os.access(frontend_dir, os.X_OK), "Frontend directory must be accessible"
        
        # Check for package.json permissions
        package_json = frontend_dir / 'package.json'
        if package_json.exists():
            assert os.access(package_json, os.R_OK), "Frontend package.json must be readable"
            
            # Should not be executable
            package_stat = package_json.stat()
            permissions = stat.S_IMODE(package_stat.st_mode)
            assert not (permissions & stat.S_IXUSR), "Frontend package.json should not be executable"

    @pytest.mark.platform
    @pytest.mark.security
    def test_docker_directory_permissions(self, project_root: Path):
        """Test Docker directory permissions for containerization."""
        docker_dir = project_root / 'docker'
        
        if not docker_dir.exists():
            pytest.skip("Docker directory does not exist yet")
        
        # Docker directory should be readable and accessible
        assert os.access(docker_dir, os.R_OK), "Docker directory must be readable"
        assert os.access(docker_dir, os.W_OK), "Docker directory must be writable"
        assert os.access(docker_dir, os.X_OK), "Docker directory must be accessible"
        
        # Docker files should not be executable
        for docker_file in docker_dir.glob('*'):
            if docker_file.is_file() and not docker_file.name.endswith('.sh'):
                docker_stat = docker_file.stat()
                permissions = stat.S_IMODE(docker_stat.st_mode)
                assert not (permissions & stat.S_IXUSR), f"Docker file {docker_file.name} should not be executable"

    @pytest.mark.platform
    @pytest.mark.cicd
    def test_github_workflows_permissions(self, project_root: Path):
        """Test GitHub workflows directory permissions for CI/CD."""
        workflows_dir = project_root / '.github' / 'workflows'
        
        if not workflows_dir.exists():
            pytest.skip("GitHub workflows directory does not exist yet")
        
        # Workflows directory should be accessible
        assert os.access(workflows_dir, os.R_OK), "Workflows directory must be readable"
        assert os.access(workflows_dir, os.X_OK), "Workflows directory must be accessible"
        
        # Workflow files should be readable but not executable
        for workflow_file in workflows_dir.glob('*.yml'):
            assert os.access(workflow_file, os.R_OK), f"Workflow {workflow_file.name} must be readable"
            
            workflow_stat = workflow_file.stat()
            permissions = stat.S_IMODE(workflow_stat.st_mode)
            assert not (permissions & stat.S_IXUSR), f"Workflow {workflow_file.name} should not be executable"

    @pytest.mark.platform
    @pytest.mark.deployment
    def test_deployment_ready_permissions(self, project_root: Path):
        """Test that permissions are appropriate for deployment."""
        
        # Key deployment files and directories
        deployment_items = [
            project_root / 'README.md',
            project_root / '.gitignore',
            project_root / 'pytest.ini',
            project_root / 'backend',
            project_root / 'frontend',
            project_root / 'docker'
        ]
        
        for item in deployment_items:
            if not item.exists():
                continue
            
            if item.is_dir():
                # Directories should be readable and accessible
                assert os.access(item, os.R_OK), f"Deployment directory {item.name} must be readable"
                assert os.access(item, os.X_OK), f"Deployment directory {item.name} must be accessible"
                
                # Should not be world-writable
                item_stat = item.stat()
                permissions = stat.S_IMODE(item_stat.st_mode)
                assert not (permissions & stat.S_IWOTH), f"Deployment directory {item.name} must not be world-writable"
            
            else:
                # Files should be readable
                assert os.access(item, os.R_OK), f"Deployment file {item.name} must be readable"
                
                # Regular files should not be executable (except scripts)
                if not item.suffix == '.sh':
                    item_stat = item.stat()
                    permissions = stat.S_IMODE(item_stat.st_mode)
                    assert not (permissions & stat.S_IXUSR), f"Deployment file {item.name} should not be executable"

    @pytest.mark.platform
    @pytest.mark.comprehensive
    def test_mens_circle_platform_permission_compliance(self, project_root: Path):
        """Test comprehensive permission compliance for men's circle platform."""
        
        # Platform-specific permission requirements
        platform_requirements = {
            'security': {
                'no_world_writable_files': True,
                'scripts_executable': True,
                'configs_readable': True
            },
            'development': {
                'source_dirs_writable': True,
                'test_dirs_accessible': True,
                'docs_readable': True
            },
            'deployment': {
                'no_executable_configs': True,
                'proper_script_permissions': True,
                'secure_directory_permissions': True
            }
        }
        
        validation_results = {}
        
        # Security validation
        validation_results['security'] = {}
        
        # Check no world-writable files
        world_writable_items = []
        for item in project_root.rglob('*'):
            if item.is_file() or item.is_dir():
                try:
                    item_stat = item.stat()
                    permissions = stat.S_IMODE(item_stat.st_mode)
                    if permissions & stat.S_IWOTH:
                        world_writable_items.append(str(item.relative_to(project_root)))
                except (OSError, PermissionError):
                    continue
        
        validation_results['security']['no_world_writable_files'] = len(world_writable_items) == 0
        
        # Check scripts are executable
        scripts_dir = project_root / 'scripts'
        executable_scripts = 0
        total_scripts = 0
        
        if scripts_dir.exists():
            for script_file in scripts_dir.glob('*.sh'):
                total_scripts += 1
                if os.access(script_file, os.X_OK):
                    executable_scripts += 1
        
        validation_results['security']['scripts_executable'] = (
            total_scripts == 0 or executable_scripts == total_scripts
        )
        
        # Check configs are readable
        config_files = ['pytest.ini', '.gitignore', 'README.md']
        readable_configs = 0
        existing_configs = 0
        
        for config_name in config_files:
            config_file = project_root / config_name
            if config_file.exists():
                existing_configs += 1
                if os.access(config_file, os.R_OK):
                    readable_configs += 1
        
        validation_results['security']['configs_readable'] = (
            existing_configs == 0 or readable_configs == existing_configs
        )
        
        # Development validation
        validation_results['development'] = {}
        
        # Check source directories are writable
        source_dirs = ['backend', 'frontend', 'tests', 'docs']
        writable_source_dirs = 0
        existing_source_dirs = 0
        
        for dir_name in source_dirs:
            source_dir = project_root / dir_name
            if source_dir.exists():
                existing_source_dirs += 1
                if os.access(source_dir, os.W_OK):
                    writable_source_dirs += 1
        
        validation_results['development']['source_dirs_writable'] = (
            existing_source_dirs == 0 or writable_source_dirs == existing_source_dirs
        )
        
        # Check test directories are accessible
        test_dirs = ['tests']
        accessible_test_dirs = 0
        existing_test_dirs = 0
        
        for dir_name in test_dirs:
            test_dir = project_root / dir_name
            if test_dir.exists():
                existing_test_dirs += 1
                if os.access(test_dir, os.R_OK) and os.access(test_dir, os.X_OK):
                    accessible_test_dirs += 1
        
        validation_results['development']['test_dirs_accessible'] = (
            existing_test_dirs == 0 or accessible_test_dirs == existing_test_dirs
        )
        
        # Check docs are readable
        docs_dirs = ['docs']
        readable_docs_dirs = 0
        existing_docs_dirs = 0
        
        for dir_name in docs_dirs:
            docs_dir = project_root / dir_name
            if docs_dir.exists():
                existing_docs_dirs += 1
                if os.access(docs_dir, os.R_OK):
                    readable_docs_dirs += 1
        
        validation_results['development']['docs_readable'] = (
            existing_docs_dirs == 0 or readable_docs_dirs == existing_docs_dirs
        )
        
        # Deployment validation
        validation_results['deployment'] = {}
        
        # Check no executable configs
        non_executable_configs = 0
        for config_name in config_files:
            config_file = project_root / config_name
            if config_file.exists():
                config_stat = config_file.stat()
                permissions = stat.S_IMODE(config_stat.st_mode)
                if not (permissions & stat.S_IXUSR):
                    non_executable_configs += 1
        
        validation_results['deployment']['no_executable_configs'] = (
            existing_configs == 0 or non_executable_configs == existing_configs
        )
        
        # Check proper script permissions
        proper_script_perms = 0
        for script_file in (project_root / 'scripts').glob('*.sh'):
            if script_file.exists():
                script_stat = script_file.stat()
                permissions = stat.S_IMODE(script_stat.st_mode)
                # Script should be executable by owner and not world-writable
                if (permissions & stat.S_IXUSR) and not (permissions & stat.S_IWOTH):
                    proper_script_perms += 1
        
        validation_results['deployment']['proper_script_permissions'] = (
            total_scripts == 0 or proper_script_perms == total_scripts
        )
        
        # Check secure directory permissions
        secure_dirs = 0
        total_dirs = 0
        core_dirs = ['backend', 'frontend', 'docker', 'tests', 'docs', 'scripts']
        
        for dir_name in core_dirs:
            dir_path = project_root / dir_name
            if dir_path.exists():
                total_dirs += 1
                dir_stat = dir_path.stat()
                permissions = stat.S_IMODE(dir_stat.st_mode)
                # Directory should not be world-writable
                if not (permissions & stat.S_IWOTH):
                    secure_dirs += 1
        
        validation_results['deployment']['secure_directory_permissions'] = (
            total_dirs == 0 or secure_dirs == total_dirs
        )
        
        # Assert all platform requirements are met
        failed_requirements = []
        for category, requirements in platform_requirements.items():
            for requirement, expected in requirements.items():
                actual = validation_results.get(category, {}).get(requirement, False)
                if actual != expected:
                    failed_requirements.append(f"{category}.{requirement}")
        
        assert not failed_requirements, f"Platform permission requirements failed: {failed_requirements}"
        
        # Additional validation messages
        if world_writable_items:
            pytest.fail(f"World-writable items found (security risk): {world_writable_items}")
        
        if total_scripts > 0 and executable_scripts < total_scripts:
            pytest.fail(f"Non-executable scripts found: {total_scripts - executable_scripts}/{total_scripts}")
        
        # Platform compliance score
        total_checks = sum(len(reqs) for reqs in platform_requirements.values())
        passed_checks = sum(
            sum(results.values()) for results in validation_results.values()
        )
        
        compliance_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 100
        
        assert compliance_score >= 100.0, f"Platform permission compliance: {compliance_score:.1f}%" 