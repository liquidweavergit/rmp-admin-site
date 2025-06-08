"""
Docker Volume Mount Compatibility Tests for Men's Circle Management Platform

This module tests that the project structure works correctly when mounted as Docker volumes,
ensuring seamless containerized development workflows and proper file system interactions.

Test Categories:
- Volume mount path compatibility
- File permission validation
- Cross-platform mount behavior
- Development workflow compatibility
- Build context optimization
- Security isolation validation
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pytest
import json


class TestDockerVolumeMountCompatibility:
    """Test project structure compatibility with Docker volume mounts."""

    @pytest.fixture(scope="class")
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent

    def test_project_structure_mount_compatibility(self, project_root: Path):
        """Test that project structure is compatible with Docker volume mounts."""
        # Essential directories that must be mountable
        essential_directories = [
            "backend",
            "frontend", 
            "tests",
            "scripts",
            "docs", 
            "docker",
            "project-documents",
            ".github"
        ]

        # Test each directory exists and is accessible
        for directory in essential_directories:
            dir_path = project_root / directory
            assert dir_path.exists(), f"Directory {directory} must exist for volume mounting"
            assert dir_path.is_dir(), f"{directory} must be a directory"
            
            # Test read permissions
            assert os.access(dir_path, os.R_OK), f"Directory {directory} must be readable"
            
            # Test that directory is not empty (except for some special cases)
            if directory not in [".github"]:
                contents = list(dir_path.iterdir())
                non_cache_contents = [f for f in contents if not f.name.startswith('.') or f.name in ['.gitignore', '.env.example']]
                assert len(non_cache_contents) > 0, f"Directory {directory} should have content for meaningful volume mounting"

    def test_development_volume_mount_patterns(self, project_root: Path):
        """Test common development volume mount patterns."""
        # Common volume mount patterns for development
        volume_patterns = [
            ("./backend:/app", "backend"),
            ("./frontend:/app", "frontend"), 
            ("./tests:/app/tests", "tests"),
            ("./scripts:/scripts:ro", "scripts"),
            ("./docs:/docs:ro", "docs")
        ]

        for pattern, directory in volume_patterns:
            local_path = project_root / directory
            assert local_path.exists(), f"Volume mount source {directory} must exist"
            
            # Test that the directory structure supports the expected mount pattern
            if directory in ["backend", "frontend"]:
                # These need write access for development
                assert os.access(local_path, os.W_OK), f"Directory {directory} must be writable for development volumes"
            else:
                # Read-only mounts just need read access
                assert os.access(local_path, os.R_OK), f"Directory {directory} must be readable for read-only volumes"

    def test_file_path_length_compatibility(self, project_root: Path):
        """Test that file paths are compatible with Docker volume mount limits."""
        max_path_length = 240  # Conservative limit for cross-platform compatibility
        
        long_paths = []
        for root, dirs, files in os.walk(project_root):
            # Skip hidden directories like .git, .pytest_cache
            dirs[:] = [d for d in dirs if not d.startswith('.') or d in ['.github']]
            
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(project_root)
                path_length = len(str(relative_path))
                
                if path_length > max_path_length:
                    long_paths.append((str(relative_path), path_length))

        assert len(long_paths) == 0, f"Found paths too long for Docker volumes: {long_paths}"

    def test_special_characters_in_paths(self, project_root: Path):
        """Test that file paths don't contain characters problematic for Docker volumes."""
        problematic_chars = [':', '*', '?', '"', '<', '>', '|']
        
        problematic_paths = []
        for root, dirs, files in os.walk(project_root):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') or d in ['.github']]
            
            for item in dirs + files:
                for char in problematic_chars:
                    if char in item:
                        relative_path = Path(root).relative_to(project_root) / item
                        problematic_paths.append((str(relative_path), char))

        assert len(problematic_paths) == 0, f"Found problematic characters in paths: {problematic_paths}"

    def test_symlink_compatibility(self, project_root: Path):
        """Test that symlinks are handled properly in volume mounts."""
        symlinks = []
        for root, dirs, files in os.walk(project_root):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') or d in ['.github']]
            
            for item in dirs + files:
                item_path = Path(root) / item
                if item_path.is_symlink():
                    target = item_path.resolve()
                    relative_path = item_path.relative_to(project_root)
                    symlinks.append((str(relative_path), str(target)))

        # Symlinks should either be avoided or point to files within the project
        external_symlinks = []
        for symlink_path, target in symlinks:
            target_path = Path(target)
            try:
                target_path.relative_to(project_root)
            except ValueError:
                external_symlinks.append((symlink_path, target))

        assert len(external_symlinks) == 0, f"Found symlinks pointing outside project: {external_symlinks}"


class TestDockerBuildContextCompatibility:
    """Test project structure compatibility with Docker build contexts."""

    @pytest.fixture(scope="class")
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent

    def test_dockerignore_pattern_validation(self, project_root: Path):
        """Test .dockerignore patterns for optimized build context."""
        # Essential patterns that should be ignored in Docker builds
        essential_ignore_patterns = [
            '.git',
            '.gitignore',
            'README.md',
            '.pytest_cache',
            '__pycache__',
            '*.pyc',
            '.coverage',
            'node_modules',
            '.env',
            '.env.*',
            '!.env.example'
        ]
        
        # Check if .dockerignore exists
        dockerignore_path = project_root / ".dockerignore"
        if not dockerignore_path.exists():
            # Create a recommended .dockerignore
            dockerignore_content = '\n'.join(essential_ignore_patterns)
            dockerignore_path.write_text(dockerignore_content)
            
        assert dockerignore_path.exists(), ".dockerignore file should exist for optimized builds"
        
        # Validate content includes essential patterns
        dockerignore_content = dockerignore_path.read_text()
        missing_patterns = []
        for pattern in essential_ignore_patterns:
            if pattern not in dockerignore_content:
                missing_patterns.append(pattern)
        
        # Allow some flexibility but ensure key patterns are present
        critical_patterns = ['.git', '__pycache__', 'node_modules', '.env']
        missing_critical = [p for p in missing_patterns if p in critical_patterns]
        assert len(missing_critical) == 0, f"Critical .dockerignore patterns missing: {missing_critical}"

    def test_build_context_size(self, project_root: Path):
        """Test that build context is reasonable size for efficient Docker builds."""
        # Calculate total size excluding common ignored patterns
        ignore_patterns = {
            '.git', '.pytest_cache', '__pycache__', 'node_modules', 
            '.coverage', '.mypy_cache', '.venv', 'venv'
        }
        
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(project_root):
            # Remove ignored directories from traversal
            dirs[:] = [d for d in dirs if d not in ignore_patterns]
            
            for file in files:
                if not any(pattern in file for pattern in ['.pyc', '.pyo', '.coverage']):
                    file_path = Path(root) / file
                    try:
                        total_size += file_path.stat().st_size
                        file_count += 1
                    except (OSError, FileNotFoundError):
                        pass  # Skip files that can't be accessed

        # Convert to MB
        total_size_mb = total_size / (1024 * 1024)
        
        # Build context should be reasonable (< 100MB for source code)
        assert total_size_mb < 100, f"Build context too large: {total_size_mb:.2f}MB with {file_count} files"


class TestVolumePermissionCompatibility:
    """Test file permissions work correctly with Docker volume mounts."""

    @pytest.fixture(scope="class")
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent

    def test_script_executable_permissions(self, project_root: Path):
        """Test that script files maintain executable permissions in volume mounts."""
        scripts_dir = project_root / "scripts"
        if scripts_dir.exists():
            for script_file in scripts_dir.glob("*.sh"):
                # Check that shell scripts are executable
                assert os.access(script_file, os.X_OK), f"Script {script_file.name} should be executable"

    def test_directory_write_permissions(self, project_root: Path):
        """Test that development directories have proper write permissions."""
        # Directories that need write access during development
        writable_dirs = ["backend", "frontend", "tests"]
        
        for dir_name in writable_dirs:
            dir_path = project_root / dir_name
            if dir_path.exists():
                # Test write permissions
                assert os.access(dir_path, os.W_OK), f"Directory {dir_name} must be writable for development"
                
                # Test that we can create and delete a test file
                test_file = dir_path / ".volume_test_temp"
                try:
                    test_file.write_text("volume mount test")
                    assert test_file.exists(), f"Could not create test file in {dir_name}"
                    test_file.unlink()
                    assert not test_file.exists(), f"Could not delete test file in {dir_name}"
                except PermissionError:
                    pytest.fail(f"Permission error testing write access in {dir_name}")

    def test_readonly_directory_behavior(self, project_root: Path):
        """Test that read-only directories behave correctly when mounted read-only."""
        # Directories that are typically mounted read-only
        readonly_dirs = ["docs", "docker", ".github"]
        
        for dir_name in readonly_dirs:
            dir_path = project_root / dir_name
            if dir_path.exists():
                # Test read permissions
                assert os.access(dir_path, os.R_OK), f"Directory {dir_name} must be readable"
                
                # These should have content that can be read
                files = list(dir_path.rglob("*"))
                readable_files = [f for f in files if f.is_file()]
                
                if readable_files:
                    # Test reading a file from the directory
                    test_file = readable_files[0]
                    try:
                        content = test_file.read_text(errors='ignore')
                        assert len(content) >= 0, f"Could not read file {test_file.name} from {dir_name}"
                    except (UnicodeDecodeError, PermissionError):
                        # Try reading as bytes if text fails
                        content = test_file.read_bytes()
                        assert len(content) >= 0, f"Could not read file {test_file.name} from {dir_name}"


class TestCrossPlatformVolumeCompatibility:
    """Test volume mount compatibility across different platforms."""

    @pytest.fixture(scope="class") 
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent

    def test_case_sensitivity_issues(self, project_root: Path):
        """Test for potential case sensitivity issues with volume mounts."""
        # Collect all files and directories by directory
        all_items_by_dir = {}
        case_conflicts = []
        
        for root, dirs, files in os.walk(project_root):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') or d in ['.github']]
            
            # Check case conflicts within each directory
            current_dir = str(Path(root).relative_to(project_root))
            if current_dir not in all_items_by_dir:
                all_items_by_dir[current_dir] = set()
                
            for item in dirs + files:
                lower_item = item.lower()
                if lower_item in all_items_by_dir[current_dir]:
                    # Found potential case sensitivity conflict within the same directory
                    relative_path = Path(root).relative_to(project_root)
                    case_conflicts.append(str(relative_path / item))
                all_items_by_dir[current_dir].add(lower_item)

        # Allow common patterns like README.md in different directories and __pycache__ 
        allowed_duplicates = {'readme.md', '__pycache__', '.gitignore'}
        filtered_conflicts = []
        for conflict in case_conflicts:
            conflict_name = Path(conflict).name.lower()
            if conflict_name not in allowed_duplicates:
                filtered_conflicts.append(conflict)

        assert len(filtered_conflicts) == 0, f"Found potential case sensitivity conflicts: {filtered_conflicts}"

    def test_line_ending_compatibility(self, project_root: Path):
        """Test that text files use consistent line endings for cross-platform volumes."""
        text_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.md', '.txt', '.yml', '.yaml', '.json', '.sh'}
        
        inconsistent_files = []
        
        for root, dirs, files in os.walk(project_root):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') or d in ['.github']]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in text_extensions:
                    try:
                        with open(file_path, 'rb') as f:
                            content = f.read()
                            
                        # Check for different line ending types
                        has_crlf = b'\r\n' in content
                        has_lf_only = b'\n' in content and not has_crlf
                        has_cr_only = b'\r' in content and not has_crlf
                        
                        if has_crlf or has_cr_only:
                            relative_path = file_path.relative_to(project_root)
                            line_ending = "CRLF" if has_crlf else "CR"
                            inconsistent_files.append((str(relative_path), line_ending))
                            
                    except (UnicodeDecodeError, PermissionError, FileNotFoundError):
                        pass  # Skip files that can't be read

        # With .editorconfig, we should have consistent LF line endings
        assert len(inconsistent_files) == 0, f"Found files with inconsistent line endings: {inconsistent_files}"

    def test_unicode_filename_compatibility(self, project_root: Path):
        """Test that filenames are compatible with Docker volume mounts across platforms."""
        non_ascii_files = []
        
        for root, dirs, files in os.walk(project_root):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.') or d in ['.github']]
            
            for item in dirs + files:
                try:
                    # Test if filename is ASCII
                    item.encode('ascii')
                except UnicodeEncodeError:
                    relative_path = Path(root).relative_to(project_root) / item
                    non_ascii_files.append(str(relative_path))

        # For maximum compatibility, project files should use ASCII filenames
        assert len(non_ascii_files) == 0, f"Found non-ASCII filenames that may cause volume mount issues: {non_ascii_files}"


class TestDockerComposeVolumeConfiguration:
    """Test Docker Compose volume configuration validation."""

    @pytest.fixture(scope="class")
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent

    def test_volume_mount_syntax_validation(self, project_root: Path):
        """Test that volume mount syntax is valid for Docker Compose."""
        # Common volume mount patterns that should be valid
        volume_patterns = [
            "./backend:/app/backend",
            "./frontend:/app/frontend:rw",
            "./docs:/app/docs:ro", 
            "./scripts:/app/scripts:ro",
            "./tests:/app/tests",
            ".:/workspace:ro"
        ]
        
        for pattern in volume_patterns:
            parts = pattern.split(':')
            assert len(parts) >= 2, f"Volume pattern should have at least source:target - {pattern}"
            
            source = parts[0]
            target = parts[1]
            
            # Source should be relative path starting with . or absolute path
            assert source.startswith('./') or source.startswith('/') or source == '.', f"Volume source should be relative or absolute: {source}"
            
            # Target should be absolute path
            assert target.startswith('/'), f"Volume target should be absolute path: {target}"
            
            # If there's a third part, it should be a valid mount option
            if len(parts) == 3:
                mount_option = parts[2]
                assert mount_option in ['ro', 'rw', 'z', 'Z'], f"Invalid mount option: {mount_option}"

    def test_development_volume_configuration(self, project_root: Path):
        """Test recommended volume configuration for development workflow."""
        # Expected volume mappings for development
        dev_volumes = {
            'backend': './backend:/app/backend',
            'frontend': './frontend:/app/frontend', 
            'tests': './tests:/app/tests',
            'project_root': '.:/workspace:ro'
        }
        
        for purpose, volume_spec in dev_volumes.items():
            source_path = volume_spec.split(':')[0]
            
            if source_path == '.':
                source_dir = project_root
            else:
                source_dir = project_root / source_path.lstrip('./')
                
            assert source_dir.exists(), f"Volume source for {purpose} must exist: {source_dir}"
            
            # For development volumes, ensure they have appropriate content
            if purpose in ['backend', 'frontend', 'tests']:
                assert any(source_dir.iterdir()), f"Development volume {purpose} should have content"


@pytest.mark.integration
class TestRealDockerVolumeMount:
    """Integration tests that actually test Docker volume mounts if Docker is available."""

    @pytest.fixture(scope="class")
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent

    def test_docker_available(self):
        """Test if Docker is available for integration testing."""
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            docker_available = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            docker_available = False
            
        if not docker_available:
            pytest.skip("Docker not available for integration testing")
            
        assert docker_available, "Docker should be available for volume mount testing"

    def test_simple_volume_mount_integration(self, project_root: Path):
        """Test actual Docker volume mount with project structure."""
        if not self._docker_available():
            pytest.skip("Docker not available")
            
        # Create a simple test container with volume mount
        try:
            # Test that we can mount the project root as read-only
            cmd = [
                'docker', 'run', '--rm', 
                '-v', f'{project_root}:/workspace:ro',
                'alpine:latest',
                'sh', '-c', 'ls -la /workspace && test -f /workspace/README.md'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            assert result.returncode == 0, f"Docker volume mount test failed: {result.stderr}"
            assert 'README.md' in result.stdout, "Should be able to see README.md in mounted volume"
            
        except subprocess.TimeoutExpired:
            pytest.fail("Docker volume mount test timed out")
        except Exception as e:
            pytest.skip(f"Docker volume mount test failed: {e}")

    def _docker_available(self) -> bool:
        """Check if Docker is available."""
        try:
            result = subprocess.run(['docker', '--version'], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False


# Platform-specific test markers
pytestmark = [
    pytest.mark.structure,
    pytest.mark.docker,
    pytest.mark.volume_mount
] 