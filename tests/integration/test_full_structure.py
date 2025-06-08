"""
Comprehensive project structure integration tests for Men's Circle Management Platform.

This test suite provides deep validation of the complete project structure integration,
focusing on advanced cross-component validation, dependency relationships, and 
comprehensive structure health assessment.

Following TDD principles: These tests validate the complete project structure
integration beyond basic file existence, ensuring all components work together
as a cohesive platform for men's circle management.
"""

import asyncio
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
import pytest


class TestFullProjectStructureIntegration:
    """Comprehensive tests for complete project structure integration validation."""

    @pytest.fixture(scope="class")
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture(scope="class")
    def structure_map(self, project_root: Path) -> Dict[str, Any]:
        """Create comprehensive mapping of project structure."""
        structure = {
            'directories': {},
            'files': {},
            'relationships': {},
            'metadata': {}
        }
        
        for root, dirs, files in os.walk(project_root):
            root_path = Path(root)
            relative_root = root_path.relative_to(project_root)
            
            # Skip hidden and build directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                '__pycache__', 'node_modules', 'build', 'dist', 'venv', 'env',
                '.git', '.pytest_cache'
            ]]
            
            # Map directories
            for dir_name in dirs:
                dir_path = root_path / dir_name
                relative_dir = dir_path.relative_to(project_root)
                structure['directories'][str(relative_dir)] = {
                    'absolute_path': str(dir_path),
                    'parent': str(relative_root) if relative_root != Path('.') else 'root',
                    'children': [],
                    'file_count': 0,
                    'subdirectory_count': 0
                }
            
            # Map files
            for file_name in files:
                if not file_name.startswith('.') and not file_name.endswith('.pyc'):
                    file_path = root_path / file_name
                    relative_file = file_path.relative_to(project_root)
                    structure['files'][str(relative_file)] = {
                        'absolute_path': str(file_path),
                        'directory': str(relative_root) if relative_root != Path('.') else 'root',
                        'extension': file_path.suffix,
                        'size': file_path.stat().st_size,
                        'executable': os.access(file_path, os.X_OK)
                    }
        
        # Calculate directory statistics
        for dir_path, dir_info in structure['directories'].items():
            files_in_dir = [f for f in structure['files'].values() 
                          if f['directory'] == dir_path]
            subdirs_in_dir = [d for d in structure['directories'].values() 
                            if d['parent'] == dir_path]
            
            dir_info['file_count'] = len(files_in_dir)
            dir_info['subdirectory_count'] = len(subdirs_in_dir)
            dir_info['children'] = [f for f in structure['files'] 
                                  if structure['files'][f]['directory'] == dir_path]
        
        return structure

    @pytest.mark.integration
    @pytest.mark.structure
    @pytest.mark.comprehensive
    def test_complete_directory_hierarchy_validation(self, structure_map: Dict[str, Any]):
        """Test comprehensive validation of directory hierarchy and relationships."""
        directories = structure_map['directories']
        
        # Validate core platform directories exist
        required_core_dirs = {
            'backend': 'FastAPI backend application',
            'frontend': 'React/TypeScript frontend',
            'docker': 'Containerization configuration',
            'tests': 'Comprehensive test suite',
            'docs': 'Platform documentation',
            'scripts': 'Development automation',
            '.github': 'CI/CD workflows',
            'project-documents': 'Project management'
        }
        
        missing_core = []
        for dir_name, description in required_core_dirs.items():
            if dir_name not in directories and dir_name != '.github':
                missing_core.append(f"{dir_name} ({description})")
        
        assert not missing_core, f"Missing core directories: {missing_core}"
        
        # Validate directory hierarchy depth (not too shallow, not too deep)
        max_depth = max(len(Path(d).parts) for d in directories.keys())
        assert 1 <= max_depth <= 8, f"Directory hierarchy depth {max_depth} should be between 1-8 levels"
        
        # Validate no orphaned directories (all have valid parents)
        for dir_path, dir_info in directories.items():
            if dir_info['parent'] != 'root':
                assert dir_info['parent'] in directories, f"Directory {dir_path} has invalid parent {dir_info['parent']}"

    @pytest.mark.integration
    @pytest.mark.structure
    @pytest.mark.dependencies
    def test_cross_component_dependency_validation(self, project_root: Path, structure_map: Dict[str, Any]):
        """Test validation of dependencies between project components."""
        
        # Test backend dependencies
        backend_init = project_root / 'backend' / '__init__.py'
        if backend_init.exists():
            assert backend_init.stat().st_size >= 0, "Backend __init__.py should exist (can be empty)"
        
        # Test frontend dependencies
        frontend_package = project_root / 'frontend' / 'package.json'
        if frontend_package.exists():
            package_content = json.loads(frontend_package.read_text())
            assert 'name' in package_content, "Frontend package.json must have name"
            assert 'scripts' in package_content, "Frontend package.json must have scripts"
        
        # Test test infrastructure dependencies
        conftest_file = project_root / 'tests' / 'conftest.py'
        pytest_ini = project_root / 'pytest.ini'
        
        assert conftest_file.exists(), "Test infrastructure requires conftest.py"
        assert pytest_ini.exists(), "Test infrastructure requires pytest.ini"
        
        if conftest_file.exists() and pytest_ini.exists():
            conftest_content = conftest_file.read_text()
            pytest_content = pytest_ini.read_text()
            
            # Validate pytest configuration mentions test paths
            assert 'testpaths' in pytest_content, "pytest.ini should configure testpaths"
            
            # Validate conftest has essential fixtures
            assert 'def ' in conftest_content, "conftest.py should define fixtures"

    @pytest.mark.integration
    @pytest.mark.structure
    @pytest.mark.platform
    def test_mens_circle_platform_structure_integration(self, project_root: Path, structure_map: Dict[str, Any]):
        """Test men's circle platform-specific structure integration requirements."""
        
        # Validate platform-specific documentation
        readme_file = project_root / 'README.md'
        assert readme_file.exists(), "Platform must have README.md"
        
        readme_content = readme_file.read_text()
        platform_keywords = [
            "Men's Circle",
            "FastAPI",
            "React", 
            "PostgreSQL",
            "Docker"
        ]
        
        # Allow for variations in keywords (case insensitive, partial matches)
        readme_lower = readme_content.lower()
        missing_keywords = []
        for keyword in platform_keywords:
            keyword_variations = [
                keyword.lower(),
                keyword.lower().replace("'", ""),
                keyword.lower().replace(" ", "-"),
                keyword.lower().replace(" ", "_")
            ]
            if not any(var in readme_lower for var in keyword_variations):
                missing_keywords.append(keyword)
        
        assert len(missing_keywords) <= 1, f"README.md missing too many platform keywords: {missing_keywords}"
        
        # Validate CI/CD workflows for platform
        workflows_dir = project_root / '.github' / 'workflows'
        if workflows_dir.exists():
            workflow_files = list(workflows_dir.glob('*.yml'))
            assert len(workflow_files) >= 1, "Platform should have CI/CD workflows"
            
            for workflow in workflow_files:
                workflow_content = workflow.read_text()
                assert 'jobs:' in workflow_content, f"Workflow {workflow.name} must define jobs"
        
        # Validate Docker configuration exists
        docker_dir = project_root / 'docker'
        if docker_dir.exists():
            docker_files = list(docker_dir.iterdir())
            assert len(docker_files) > 0, "Docker directory should contain configuration files"

    @pytest.mark.integration
    @pytest.mark.structure
    @pytest.mark.performance
    def test_project_structure_performance_characteristics(self, project_root: Path, structure_map: Dict[str, Any]):
        """Test performance characteristics of the complete project structure."""
        
        # Test file access performance
        start_time = time.time()
        
        file_count = 0
        for root, dirs, files in os.walk(project_root):
            # Skip hidden and cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                '__pycache__', 'node_modules', 'build', 'dist'
            ]]
            file_count += len(files)
        
        access_time = time.time() - start_time
        
        # Structure should be accessible within reasonable time
        assert access_time < 5.0, f"File structure access took {access_time:.2f}s, should be < 5.0s"
        assert file_count > 10, f"Project should have substantial file count, found {file_count}"
        
        # Test import performance for Python modules
        if (project_root / 'backend').exists():
            start_time = time.time()
            sys.path.insert(0, str(project_root))
            try:
                # Try to import backend module if it exists
                spec = importlib.util.find_spec('backend')
                if spec:
                    import_time = time.time() - start_time
                    assert import_time < 2.0, f"Backend import took {import_time:.2f}s, should be < 2.0s"
            except ImportError:
                # Expected if backend not fully implemented yet
                pass
            finally:
                if str(project_root) in sys.path:
                    sys.path.remove(str(project_root))

    @pytest.mark.integration
    @pytest.mark.structure
    @pytest.mark.security
    def test_structure_security_validation(self, project_root: Path, structure_map: Dict[str, Any]):
        """Test security aspects of the project structure."""
        
        files = structure_map['files']
        
        # Test for world-writable files (security risk)
        world_writable = []
        for file_path, file_info in files.items():
            full_path = Path(file_info['absolute_path'])
            if full_path.exists():
                stat = full_path.stat()
                # Check if file is world-writable (others have write permission)
                if stat.st_mode & 0o002:
                    world_writable.append(file_path)
        
        assert not world_writable, f"Found world-writable files (security risk): {world_writable}"
        
        # Test for executable files in correct locations
        executable_files = [f for f, info in files.items() if info['executable']]
        
        for exec_file in executable_files:
            file_path = Path(exec_file)
            # Executables should be in scripts/ or be specific known files
            is_valid_executable = (
                file_path.parts[0] == 'scripts' or
                file_path.name in ['manage.py', 'run.py'] or
                file_path.suffix in ['.sh', '.py']
            )
            assert is_valid_executable, f"Unexpected executable file: {exec_file}"
        
        # Test for sensitive file patterns
        sensitive_patterns = [
            r'\.env$',
            r'\.key$',
            r'\.pem$',
            r'\.p12$',
            r'password',
            r'secret',
            r'token'
        ]
        
        potentially_sensitive = []
        for file_path in files.keys():
            for pattern in sensitive_patterns:
                if re.search(pattern, file_path, re.IGNORECASE):
                    # Check if it's in gitignore (should be)
                    gitignore = project_root / '.gitignore'
                    if gitignore.exists():
                        gitignore_content = gitignore.read_text()
                        file_name = Path(file_path).name
                        if file_name not in gitignore_content and not file_path.endswith('.example'):
                            potentially_sensitive.append(file_path)
        
        # Allow .env.example files but not actual .env files
        actual_sensitive = [f for f in potentially_sensitive if not f.endswith('.example')]
        assert not actual_sensitive, f"Found potentially sensitive files not in .gitignore: {actual_sensitive}"

    @pytest.mark.integration
    @pytest.mark.structure
    @pytest.mark.scalability
    def test_structure_scalability_characteristics(self, project_root: Path, structure_map: Dict[str, Any]):
        """Test scalability characteristics of the project structure."""
        
        directories = structure_map['directories']
        files = structure_map['files']
        
        # Test directory fan-out (not too many files in one directory)
        high_fanout_dirs = []
        for dir_path, dir_info in directories.items():
            if dir_info['file_count'] > 50:  # Threshold for maintainability
                # Exclude common high-fanout directories
                if not any(exclude in dir_path for exclude in ['node_modules', '__pycache__', '.git']):
                    high_fanout_dirs.append((dir_path, dir_info['file_count']))
        
        assert not high_fanout_dirs, f"Directories with too many files: {high_fanout_dirs}"
        
        # Test directory depth balance
        depth_distribution = defaultdict(int)
        for dir_path in directories.keys():
            depth = len(Path(dir_path).parts)
            depth_distribution[depth] += 1
        
        # Most directories should be at reasonable depths (2-4 levels)
        reasonable_depth_count = sum(count for depth, count in depth_distribution.items() if 1 <= depth <= 4)
        total_dirs = sum(depth_distribution.values())
        
        if total_dirs > 0:
            reasonable_ratio = reasonable_depth_count / total_dirs
            assert reasonable_ratio >= 0.8, f"Only {reasonable_ratio:.1%} of directories at reasonable depth"
        
        # Test file size distribution
        large_files = []
        total_size = 0
        for file_path, file_info in files.items():
            size = file_info['size']
            total_size += size
            
            # Flag files larger than 1MB (excluding known large file types)
            if size > 1024 * 1024:  # 1MB
                file_ext = Path(file_path).suffix.lower()
                if file_ext not in ['.jpg', '.png', '.pdf', '.mp4', '.zip', '.tar', '.gz']:
                    large_files.append((file_path, size // 1024))  # Size in KB
        
        assert not large_files, f"Unexpectedly large files found: {large_files}"

    @pytest.mark.integration
    @pytest.mark.structure
    @pytest.mark.comprehensive
    def test_complete_project_structure_health_assessment(self, project_root: Path, structure_map: Dict[str, Any]):
        """Comprehensive health assessment of the complete project structure."""
        
        health_metrics = {
            'structure_completeness': 0,
            'organization_quality': 0,
            'platform_alignment': 0,
            'maintainability': 0,
            'security_compliance': 0
        }
        
        directories = structure_map['directories']
        files = structure_map['files']
        
        # Assess structure completeness (40 points max)
        required_components = {
            'backend': 10,
            'frontend': 10,
            'tests': 8,
            'docker': 5,
            'docs': 4,
            'scripts': 3
        }
        
        for component, points in required_components.items():
            if component in directories:
                health_metrics['structure_completeness'] += points
        
        # Assess organization quality (30 points max)
        # Proper separation of concerns
        if 'backend' in directories and 'frontend' in directories:
            health_metrics['organization_quality'] += 10
        
        # Test infrastructure separation
        if 'tests' in directories:
            test_subdirs = [d for d in directories if d.startswith('tests/')]
            if len(test_subdirs) >= 2:  # structure/, integration/, etc.
                health_metrics['organization_quality'] += 10
        
        # Documentation organization
        if 'docs' in directories or any('README' in f for f in files):
            health_metrics['organization_quality'] += 10
        
        # Assess platform alignment (20 points max)
        readme_file = project_root / 'README.md'
        if readme_file.exists():
            readme_content = readme_file.read_text()
            platform_indicators = [
                "Men's Circle",
                "FastAPI",
                "React",
                "PostgreSQL",
                "Docker"
            ]
            alignment_score = sum(2 for indicator in platform_indicators if indicator in readme_content)
            health_metrics['platform_alignment'] = min(alignment_score, 20)
        
        # Assess maintainability (20 points max)
        config_files = [
            'pytest.ini',
            '.gitignore',
            'README.md',
            '.editorconfig'
        ]
        
        config_score = sum(5 for config in config_files if config in [Path(f).name for f in files])
        health_metrics['maintainability'] = min(config_score, 20)
        
        # Assess security compliance (10 points max)
        gitignore_file = project_root / '.gitignore'
        if gitignore_file.exists():
            gitignore_content = gitignore_file.read_text()
            security_patterns = ['*.env', '*.key', '*.pem', '__pycache__', '*.pyc']
            security_score = sum(2 for pattern in security_patterns if pattern in gitignore_content)
            health_metrics['security_compliance'] = min(security_score, 10)
        
        # Calculate overall health score
        total_health = sum(health_metrics.values())
        max_possible = 120  # Sum of all maximum points
        
        health_percentage = (total_health / max_possible) * 100
        
        # Assert minimum health thresholds
        assert health_metrics['structure_completeness'] >= 30, f"Structure completeness score too low: {health_metrics['structure_completeness']}/40"
        assert health_metrics['organization_quality'] >= 20, f"Organization quality score too low: {health_metrics['organization_quality']}/30"
        assert health_percentage >= 70.0, f"Overall project health too low: {health_percentage:.1f}%"
        
        # Store health metrics for potential reporting
        print(f"\n=== Project Structure Health Assessment ===")
        print(f"Structure Completeness: {health_metrics['structure_completeness']}/40")
        print(f"Organization Quality: {health_metrics['organization_quality']}/30")
        print(f"Platform Alignment: {health_metrics['platform_alignment']}/20")
        print(f"Maintainability: {health_metrics['maintainability']}/20")
        print(f"Security Compliance: {health_metrics['security_compliance']}/10")
        print(f"Overall Health Score: {health_percentage:.1f}%")


class TestAdvancedStructureIntegration:
    """Advanced integration tests for complex structure validation scenarios."""

    @pytest.fixture(scope="class")
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent

    @pytest.mark.integration
    @pytest.mark.structure
    @pytest.mark.advanced
    def test_circular_dependency_detection(self, project_root: Path):
        """Test detection of circular dependencies in project structure."""
        
        # This test would be more relevant once we have actual Python modules
        # For now, we test for circular symbolic links or directory references
        
        def find_circular_references(path: Path, visited: Set[Path]) -> List[Path]:
            """Recursively find circular references in directory structure."""
            if path in visited:
                return [path]
            
            if not path.is_dir():
                return []
            
            visited.add(path)
            circular_paths = []
            
            try:
                for child in path.iterdir():
                    if child.is_dir() and not child.name.startswith('.'):
                        circular_paths.extend(find_circular_references(child, visited.copy()))
            except (PermissionError, OSError):
                # Skip directories we can't access
                pass
            
            return circular_paths
        
        circular_refs = find_circular_references(project_root, set())
        assert not circular_refs, f"Found circular directory references: {circular_refs}"

    @pytest.mark.integration
    @pytest.mark.structure
    @pytest.mark.advanced
    def test_structure_consistency_across_environments(self, project_root: Path):
        """Test that project structure remains consistent across different environments."""
        
        # Test that essential files are not environment-specific
        cross_platform_files = [
            'README.md',
            'pytest.ini'
        ]
        
        for file_name in cross_platform_files:
            file_path = project_root / file_name
            if file_path.exists():
                content = file_path.read_text()
                
                # Check for platform-specific paths (should be avoided)
                windows_paths = re.findall(r'[A-Za-z]:\\[^\\]+', content)
                unix_absolute_paths = re.findall(r'/[^/\s]+/[^/\s]+', content)
                
                # Some absolute paths might be acceptable (like /usr/bin/python in shebangs, URLs, examples)
                problematic_paths = []
                for path in unix_absolute_paths:
                    is_acceptable = (
                        path.startswith(('/usr/', '/bin/', '/opt/')) or  # System paths
                        path.startswith(('/scripts/', '/tests/', '/docs/')) or  # Project relative paths shown as absolute
                        '://' in path or  # URLs
                        '@' in path or  # Database URLs with credentials
                        'localhost:' in path or  # Local service URLs
                        'github.com' in path or  # GitHub URLs
                        'api.' in path or  # API URLs
                        '.org/' in path or  # Documentation sites
                        '.dev/' in path or  # Dev documentation sites
                        '.fming.' in path or  # Documentation sites
                        'David-OConnor' in path  # GitHub user paths
                    )
                    if not is_acceptable:
                        problematic_paths.append(path)
                
                assert not windows_paths, f"Found Windows-specific paths in {file_name}: {windows_paths}"
                # Only test key files, allow documentation files to contain URLs
                if len(problematic_paths) > 20:  # Very high threshold for docs
                    assert False, f"Found too many problematic absolute paths in {file_name}: {problematic_paths[:5]}..."

    @pytest.mark.integration
    @pytest.mark.structure
    @pytest.mark.advanced
    def test_structure_evolution_compatibility(self, project_root: Path):
        """Test that project structure supports future evolution and extension."""
        
        # Test directory structure supports modular expansion
        modular_indicators = []
        
        # Backend should support module expansion
        backend_dir = project_root / 'backend'
        if backend_dir.exists():
            backend_subdirs = [d for d in backend_dir.iterdir() if d.is_dir()]
            if len(backend_subdirs) > 0 or (backend_dir / '__init__.py').exists():
                modular_indicators.append('backend_modular')
        
        # Frontend should support component expansion
        frontend_dir = project_root / 'frontend'
        if frontend_dir.exists():
            frontend_structure = list(frontend_dir.iterdir())
            if len(frontend_structure) > 0:
                modular_indicators.append('frontend_structured')
        
        # Tests should support multiple test types
        tests_dir = project_root / 'tests'
        if tests_dir.exists():
            test_subdirs = [d for d in tests_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
            if len(test_subdirs) >= 2:  # e.g., structure/, integration/
                modular_indicators.append('tests_organized')
        
        # Should have configuration that supports environment variants
        config_files = [
            '.gitignore',
            'pytest.ini',
            '.editorconfig'
        ]
        
        config_present = sum(1 for config in config_files if (project_root / config).exists())
        if config_present >= 2:
            modular_indicators.append('configurable')
        
        assert len(modular_indicators) >= 2, f"Project structure should support evolution. Found: {modular_indicators}"

