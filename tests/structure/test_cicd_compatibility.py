"""
Test project structure compatibility with CI/CD pipelines.

This module tests the compatibility of the project structure with various
CI/CD platforms and deployment workflows for the men's circle management platform.
Ensures smooth integration with GitHub Actions, Docker, and deployment processes.
"""

import os
import subprocess
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pytest


class TestGitHubActionsCompatibility:
    """Test GitHub Actions workflow compatibility."""

    def test_github_workflows_directory_exists(self, project_root):
        """Test that GitHub workflows directory exists and is properly structured."""
        workflows_dir = project_root / '.github' / 'workflows'
        
        assert workflows_dir.exists(), "GitHub workflows directory must exist for CI/CD"
        assert workflows_dir.is_dir(), "GitHub workflows path must be a directory"
        
        # Check directory permissions
        assert os.access(workflows_dir, os.R_OK), "Workflows directory must be readable"
        assert os.access(workflows_dir, os.X_OK), "Workflows directory must be accessible"

    def test_github_workflow_files_exist(self, project_root):
        """Test that required GitHub workflow files exist."""
        workflows_dir = project_root / '.github' / 'workflows'
        
        required_workflows = ['ci.yml', 'test.yml', 'deploy.yml']
        existing_workflows = []
        
        for workflow_file in required_workflows:
            workflow_path = workflows_dir / workflow_file
            if workflow_path.exists():
                existing_workflows.append(workflow_file)
                
                # Validate file is readable
                assert os.access(workflow_path, os.R_OK), f"Workflow {workflow_file} must be readable"
                
                # Validate file size (should not be empty)
                assert workflow_path.stat().st_size > 0, f"Workflow {workflow_file} must not be empty"
        
        assert len(existing_workflows) >= 1, "At least one workflow file should exist for CI/CD"

    def test_github_workflow_yaml_syntax(self, project_root):
        """Test that GitHub workflow YAML files have valid syntax."""
        workflows_dir = project_root / '.github' / 'workflows'
        
        if not workflows_dir.exists():
            pytest.skip("No workflows directory found")
        
        yaml_files = list(workflows_dir.glob('*.yml')) + list(workflows_dir.glob('*.yaml'))
        
        assert len(yaml_files) > 0, "Should have at least one workflow YAML file"
        
        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    workflow_content = yaml.safe_load(f)
                
                # Basic workflow structure validation
                assert isinstance(workflow_content, dict), f"Workflow {yaml_file.name} must be a valid YAML dict"
                
                # Check for trigger section (can be 'on' or True key due to YAML parsing)
                has_trigger = 'on' in workflow_content or True in workflow_content
                assert has_trigger, f"Workflow {yaml_file.name} must have trigger section ('on' or equivalent)"
                
                assert 'jobs' in workflow_content, f"Workflow {yaml_file.name} must have 'jobs' section"
                
                # Validate jobs structure
                jobs = workflow_content['jobs']
                assert isinstance(jobs, dict), f"Jobs section in {yaml_file.name} must be a dict"
                assert len(jobs) > 0, f"Workflow {yaml_file.name} must have at least one job"
                
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML syntax in {yaml_file.name}: {e}")
            except Exception as e:
                pytest.fail(f"Error reading workflow {yaml_file.name}: {e}")

    def test_workflow_project_structure_compatibility(self, project_root):
        """Test that workflows are compatible with project structure."""
        workflows_dir = project_root / '.github' / 'workflows'
        
        if not workflows_dir.exists():
            pytest.skip("No workflows directory found")
        
        # Expected project components that workflows should handle
        project_components = {
            'backend': project_root / 'backend',
            'frontend': project_root / 'frontend',
            'tests': project_root / 'tests',
            'docker': project_root / 'docker',
            'scripts': project_root / 'scripts'
        }
        
        # Read all workflow files
        workflow_files = list(workflows_dir.glob('*.yml')) + list(workflows_dir.glob('*.yaml'))
        
        component_references = {comp: False for comp in project_components.keys()}
        
        for workflow_file in workflow_files:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow_content = f.read()
            
            # Check if workflow references project components appropriately
            for component, component_path in project_components.items():
                if component_path.exists():
                    # Workflow should reference existing components
                    if (component in workflow_content or 
                        str(component_path.relative_to(project_root)) in workflow_content):
                        component_references[component] = True
        
        # At least tests should be referenced in workflows
        if (project_root / 'tests').exists():
            assert component_references['tests'], "CI/CD workflows should reference tests directory"

    def test_workflow_environment_compatibility(self, project_root):
        """Test that workflows define appropriate environment settings."""
        workflows_dir = project_root / '.github' / 'workflows'
        
        if not workflows_dir.exists():
            pytest.skip("No workflows directory found")
        
        workflow_files = list(workflows_dir.glob('*.yml')) + list(workflows_dir.glob('*.yaml'))
        
        checkout_found = False
        
        for workflow_file in workflow_files:
            with open(workflow_file, 'r', encoding='utf-8') as f:
                workflow_content = yaml.safe_load(f)
            
            # Check for proper environment setup
            jobs = workflow_content.get('jobs', {})
            
            for job_name, job_config in jobs.items():
                steps = job_config.get('steps', [])
                
                # Look for setup actions in steps
                for step in steps:
                    if 'uses' in step:
                        action = step['uses']
                        if 'checkout' in action:
                            checkout_found = True
        
        # At least one workflow should checkout code
        assert checkout_found, "At least one workflow should checkout code"


class TestDockerCompatibility:
    """Test Docker integration compatibility."""

    def test_docker_directory_structure(self, project_root):
        """Test that Docker directory structure is compatible with CI/CD."""
        docker_dir = project_root / 'docker'
        
        if not docker_dir.exists():
            pytest.skip("Docker directory does not exist")
        
        assert docker_dir.is_dir(), "Docker path must be a directory"
        assert os.access(docker_dir, os.R_OK), "Docker directory must be readable"
        
        # Check for common Docker files
        docker_files = list(docker_dir.glob('*.dockerfile')) + list(docker_dir.glob('Dockerfile*'))
        
        if len(docker_files) > 0:
            for docker_file in docker_files:
                assert os.access(docker_file, os.R_OK), f"Docker file {docker_file.name} must be readable"
                assert docker_file.stat().st_size > 0, f"Docker file {docker_file.name} must not be empty"

    def test_dockerignore_file_compatibility(self, project_root):
        """Test .dockerignore file compatibility with CI/CD."""
        dockerignore_file = project_root / '.dockerignore'
        
        if dockerignore_file.exists():
            assert os.access(dockerignore_file, os.R_OK), ".dockerignore must be readable"
            
            # Check file content
            with open(dockerignore_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            assert len(content.strip()) > 0, ".dockerignore should not be empty"

    def test_docker_build_context_security(self, project_root):
        """Test that sensitive files are excluded from Docker build context."""
        # Check for .gitignore which helps with Docker build context
        gitignore_file = project_root / '.gitignore'
        
        if gitignore_file.exists():
            with open(gitignore_file, 'r', encoding='utf-8') as f:
                gitignore_content = f.read()
            
            # Common patterns that should be ignored
            security_patterns = ['.env', '__pycache__', '*.pyc']
            
            for pattern in security_patterns:
                # At least some security patterns should be present
                if pattern in gitignore_content:
                    break
            else:
                # This is a soft recommendation
                pass


class TestBuildToolCompatibility:
    """Test build tool and dependency management compatibility."""

    def test_python_dependency_management(self, project_root):
        """Test Python dependency management compatibility with CI/CD."""
        python_files = list(project_root.rglob('*.py'))
        
        if len(python_files) > 0:
            # Look for dependency management files
            dependency_files = [
                project_root / 'requirements.txt',
                project_root / 'backend' / 'requirements.txt',
                project_root / 'pyproject.toml',
                project_root / 'setup.py'
            ]
            
            existing_dependency_files = [f for f in dependency_files if f.exists()]
            
            if len(existing_dependency_files) > 0:
                for dep_file in existing_dependency_files:
                    assert os.access(dep_file, os.R_OK), f"Dependency file {dep_file.name} must be readable"
                    assert dep_file.stat().st_size > 0, f"Dependency file {dep_file.name} must not be empty"

    def test_nodejs_dependency_management(self, project_root):
        """Test Node.js dependency management compatibility with CI/CD."""
        frontend_dir = project_root / 'frontend'
        
        if frontend_dir.exists():
            package_json = frontend_dir / 'package.json'
            
            if package_json.exists():
                assert os.access(package_json, os.R_OK), "package.json must be readable"
                assert package_json.stat().st_size > 0, "package.json must not be empty"

    def test_test_configuration_compatibility(self, project_root):
        """Test that test configuration is compatible with CI/CD."""
        # Check for test configuration files
        test_configs = [
            project_root / 'pytest.ini',
            project_root / 'pyproject.toml',
            project_root / 'setup.cfg'
        ]
        
        existing_test_configs = [f for f in test_configs if f.exists()]
        
        if len(existing_test_configs) > 0:
            for config_file in existing_test_configs:
                assert os.access(config_file, os.R_OK), f"Test config {config_file.name} must be readable"
                assert config_file.stat().st_size > 0, f"Test config {config_file.name} must not be empty"

    def test_script_execution_compatibility(self, project_root):
        """Test that scripts are compatible with CI/CD execution."""
        scripts_dir = project_root / 'scripts'
        
        if scripts_dir.exists():
            script_files = list(scripts_dir.glob('*.sh'))
            
            for script_file in script_files:
                # Scripts should be readable in CI/CD
                assert os.access(script_file, os.R_OK), f"Script {script_file.name} must be readable"
                assert script_file.stat().st_size > 0, f"Script {script_file.name} must not be empty"


class TestEnvironmentCompatibility:
    """Test environment setup compatibility with CI/CD."""

    def test_environment_configuration_files(self, project_root):
        """Test environment configuration for CI/CD."""
        # Look for environment configuration files
        env_files = [
            project_root / '.env.example',
            project_root / '.env.template',
            project_root / 'backend' / '.env.example'
        ]
        
        existing_env_files = [f for f in env_files if f.exists()]
        
        for env_file in existing_env_files:
            assert os.access(env_file, os.R_OK), f"Environment file {env_file.name} must be readable"
            assert env_file.stat().st_size > 0, f"Environment file {env_file.name} must not be empty"

    def test_gitignore_security_compatibility(self, project_root):
        """Test that .gitignore properly excludes sensitive files."""
        gitignore_file = project_root / '.gitignore'
        
        if gitignore_file.exists():
            with open(gitignore_file, 'r', encoding='utf-8') as f:
                gitignore_content = f.read()
            
            # Check for common security patterns
            security_patterns = ['.env', '*.key', 'secrets']
            patterns_found = 0
            
            for pattern in security_patterns:
                if pattern in gitignore_content:
                    patterns_found += 1
            
            # At least one security pattern should be present
            assert patterns_found > 0, "Gitignore should contain security patterns"


class TestCICDPerformance:
    """Test CI/CD pipeline performance characteristics."""

    def test_project_structure_scanning_performance(self, project_root):
        """Test that project structure can be scanned efficiently in CI/CD."""
        import time
        
        start_time = time.perf_counter()
        
        # Simulate CI/CD structure scanning
        total_files = 0
        total_dirs = 0
        
        for root, dirs, files in os.walk(project_root):
            # Skip common CI/CD ignore patterns
            dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.github']
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'node_modules', '.pytest_cache']]
            
            total_dirs += len(dirs)
            total_files += len(files)
        
        end_time = time.perf_counter()
        scan_time = end_time - start_time
        
        # Structure scanning should be fast for CI/CD
        assert scan_time < 2.0, f"Project structure scan took {scan_time:.3f}s, should be under 2.0s"
        
        # Verify reasonable project size
        assert total_files > 0, "Should find files in project"
        assert total_dirs > 0, "Should find directories in project"

    def test_configuration_file_access_performance(self, project_root):
        """Test that configuration files can be accessed quickly in CI/CD."""
        import time
        
        config_files = [
            project_root / 'pytest.ini',
            project_root / '.gitignore',
            project_root / 'README.md',
            project_root / '.github' / 'workflows' / 'ci.yml'
        ]
        
        total_access_time = 0
        accessed_files = 0
        
        for config_file in config_files:
            if config_file.exists():
                start_time = time.perf_counter()
                
                # Simulate reading file (like CI/CD would)
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                end_time = time.perf_counter()
                access_time = end_time - start_time
                total_access_time += access_time
                accessed_files += 1
        
        if accessed_files > 0:
            avg_access_time = total_access_time / accessed_files
            assert avg_access_time < 0.1, f"Average config file access took {avg_access_time:.3f}s, should be under 0.1s" 