"""
Test project structure performance (import times, file access).

This module tests the performance characteristics of the project structure
for the men's circle management platform, focusing on import times and 
file access patterns that are critical for application startup and runtime.

Test Categories:
1. Import Performance Testing
2. File Access Performance Testing  
3. Directory Structure Performance
4. Module Loading Performance
5. Cross-Directory Access Performance
6. Concurrent Access Performance
7. Memory Usage During Imports
8. Startup Time Performance

TDD Approach:
- Establish performance baselines before optimization
- Test import times meet acceptable thresholds
- Validate file access patterns are efficient
- Ensure scalable performance as project grows
"""

import importlib
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Tuple
import pytest
import gc


class TestImportPerformance:
    """Test import performance across project structure."""

    def test_conftest_import_performance(self):
        """Test that conftest.py imports quickly."""
        start_time = time.perf_counter()
        
        # Import conftest module
        import tests.conftest
        
        end_time = time.perf_counter()
        import_time = end_time - start_time
        
        # Conftest should import quickly (under 0.2 seconds)
        assert import_time < 0.2, \
            f"conftest.py import took {import_time:.3f}s, should be under 0.2s"
        
        # Verify conftest was actually imported
        assert hasattr(tests.conftest, 'project_root'), \
            "conftest should have project_root fixture"

    def test_test_module_import_performance(self):
        """Test that test modules import within acceptable time."""
        test_modules = [
            'tests.structure.test_directories',
            'tests.structure.test_cross_directory_imports',
            'tests.structure.test_conftest_fixture_validation'
        ]
        
        import_times = {}
        
        for module_name in test_modules:
            # Clear any existing import
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            start_time = time.perf_counter()
            
            try:
                importlib.import_module(module_name)
                end_time = time.perf_counter()
                import_time = end_time - start_time
                import_times[module_name] = import_time
                
                # Each test module should import quickly (under 0.5 seconds)
                assert import_time < 0.5, \
                    f"{module_name} import took {import_time:.3f}s, should be under 0.5s"
                    
            except ImportError as e:
                pytest.fail(f"Failed to import {module_name}: {e}")
        
        # Total import time for all test modules should be reasonable
        total_import_time = sum(import_times.values())
        assert total_import_time < 1.0, \
            f"Total test module imports took {total_import_time:.3f}s, should be under 1.0s"

    def test_backend_module_import_performance(self):
        """Test that backend modules import efficiently."""
        start_time = time.perf_counter()
        
        # Import backend package
        import backend
        
        end_time = time.perf_counter()
        import_time = end_time - start_time
        
        # Backend package should import quickly (under 0.1 seconds)
        assert import_time < 0.1, \
            f"backend module import took {import_time:.3f}s, should be under 0.1s"

    def test_repeated_import_performance(self):
        """Test that repeated imports are cached and fast."""
        module_name = 'tests.conftest'
        
        # First import (may be slower due to compilation)
        start_time = time.perf_counter()
        importlib.import_module(module_name)
        first_import_time = time.perf_counter() - start_time
        
        # Subsequent imports should be much faster (cached)
        import_times = []
        for i in range(5):
            start_time = time.perf_counter()
            importlib.import_module(module_name)
            import_time = time.perf_counter() - start_time
            import_times.append(import_time)
        
        avg_cached_import_time = sum(import_times) / len(import_times)
        
        # Cached imports should be very fast (under 0.01 seconds)
        assert avg_cached_import_time < 0.01, \
            f"Cached imports averaged {avg_cached_import_time:.6f}s, should be under 0.01s"

    def test_import_memory_usage(self):
        """Test that imports don't consume excessive memory."""
        # Simple memory usage test using gc
        gc.collect()  # Clear garbage before test
        
        # Count objects before imports
        objects_before = len(gc.get_objects())
        
        # Import test modules
        test_modules = [
            'tests.conftest',
            'tests.structure.test_directories'
        ]
        
        for module_name in test_modules:
            importlib.import_module(module_name)
        
        # Count objects after imports
        gc.collect()  # Clear garbage after imports
        objects_after = len(gc.get_objects())
        
        object_increase = objects_after - objects_before
        
        # Object increase should be reasonable (under 10000 new objects)
        assert object_increase < 10000, \
            f"Test module imports created {object_increase} objects, should be under 10000"


class TestFileAccessPerformance:
    """Test file access performance across project structure."""

    def test_file_read_performance(self, project_root):
        """Test that reading project files is performant."""
        test_files = [
            project_root / 'pytest.ini',
            project_root / 'README.md',
            project_root / '.gitignore',
            project_root / 'tests' / 'conftest.py'
        ]
        
        read_times = {}
        
        for file_path in test_files:
            if file_path.exists():
                start_time = time.perf_counter()
                
                # Read file content
                content = file_path.read_text(encoding='utf-8')
                
                end_time = time.perf_counter()
                read_time = end_time - start_time
                read_times[str(file_path.name)] = read_time
                
                # File reads should be fast (under 0.1 seconds for typical files)
                assert read_time < 0.1, \
                    f"Reading {file_path.name} took {read_time:.3f}s, should be under 0.1s"
                
                # Verify content was actually read
                assert len(content) > 0, f"{file_path.name} should have content"

    def test_directory_traversal_performance(self, project_root):
        """Test that directory traversal is efficient."""
        start_time = time.perf_counter()
        
        # Traverse project directory structure
        file_count = 0
        dir_count = 0
        
        for root, dirs, files in os.walk(project_root):
            # Skip hidden directories and cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            dir_count += len(dirs)
            file_count += len(files)
        
        end_time = time.perf_counter()
        traversal_time = end_time - start_time
        
        # Directory traversal should be efficient (under 0.5 seconds)
        assert traversal_time < 0.5, \
            f"Directory traversal took {traversal_time:.3f}s, should be under 0.5s"
        
        # Verify we found files and directories
        assert file_count > 0, "Should find files in project"
        assert dir_count > 0, "Should find directories in project"

    def test_concurrent_file_access_performance(self, project_root):
        """Test file access performance under concurrent load."""
        test_files = [
            project_root / 'pytest.ini',
            project_root / 'README.md',
            project_root / '.gitignore'
        ]
        
        # Filter to existing files
        existing_files = [f for f in test_files if f.exists()]
        
        def read_file_timed(file_path: Path) -> Tuple[str, float]:
            """Read a file and return its name and read time."""
            start_time = time.perf_counter()
            try:
                content = file_path.read_text(encoding='utf-8')
                end_time = time.perf_counter()
                return file_path.name, end_time - start_time
            except Exception:
                return file_path.name, float('inf')
        
        # Test concurrent file reads
        with ThreadPoolExecutor(max_workers=len(existing_files)) as executor:
            start_time = time.perf_counter()
            
            futures = [executor.submit(read_file_timed, file_path) 
                      for file_path in existing_files]
            
            results = [future.result() for future in futures]
            
            end_time = time.perf_counter()
            total_concurrent_time = end_time - start_time
        
        # Concurrent file access should be efficient
        assert total_concurrent_time < 0.2, \
            f"Concurrent file reads took {total_concurrent_time:.3f}s, should be under 0.2s"
        
        # Individual read times should be reasonable
        for file_name, read_time in results:
            assert read_time < 0.1, \
                f"Concurrent read of {file_name} took {read_time:.3f}s"

    def test_file_stat_performance(self, project_root):
        """Test that file stat operations are fast."""
        test_paths = [
            project_root,
            project_root / 'tests',
            project_root / 'backend',
            project_root / 'frontend',
            project_root / 'pytest.ini',
            project_root / 'README.md'
        ]
        
        stat_times = {}
        
        for path in test_paths:
            if path.exists():
                start_time = time.perf_counter()
                
                # Perform stat operations
                stat_info = path.stat()
                is_file = path.is_file()
                is_dir = path.is_dir()
                
                end_time = time.perf_counter()
                stat_time = end_time - start_time
                stat_times[str(path.name)] = stat_time
                
                # Stat operations should be very fast (under 0.01 seconds)
                assert stat_time < 0.01, \
                    f"Stat operations on {path.name} took {stat_time:.6f}s, should be under 0.01s"

    def test_path_resolution_performance(self, project_root):
        """Test that path resolution operations are efficient."""
        relative_paths = [
            'tests/conftest.py',
            'backend/__init__.py',
            'frontend/',
            'pytest.ini',
            'tests/structure/',
            'project-documents/'
        ]
        
        resolution_times = {}
        
        for rel_path in relative_paths:
            start_time = time.perf_counter()
            
            # Resolve path
            resolved_path = project_root / rel_path
            normalized_path = resolved_path.resolve()
            exists = resolved_path.exists()
            
            end_time = time.perf_counter()
            resolution_time = end_time - start_time
            resolution_times[rel_path] = resolution_time
            
            # Path resolution should be fast (under 0.01 seconds)
            assert resolution_time < 0.01, \
                f"Path resolution for {rel_path} took {resolution_time:.6f}s, should be under 0.01s"


class TestDirectoryStructurePerformance:
    """Test directory structure access performance."""

    def test_deep_directory_access_performance(self, project_root):
        """Test accessing files in nested directory structures."""
        deep_paths = [
            project_root / 'tests' / 'structure' / 'test_directories.py',
            project_root / 'tests' / 'integration' / 'test_full_structure.py',
            project_root / 'project-documents' / 'enhancements' / 'enhancements_1_2.md'
        ]
        
        access_times = {}
        
        for path in deep_paths:
            if path.exists():
                start_time = time.perf_counter()
                
                # Access file properties
                stat_info = path.stat()
                size = stat_info.st_size
                is_readable = os.access(path, os.R_OK)
                
                end_time = time.perf_counter()
                access_time = end_time - start_time
                access_times[str(path.relative_to(project_root))] = access_time
                
                # Deep directory access should be efficient (under 0.01 seconds)
                assert access_time < 0.01, \
                    f"Deep directory access for {path.name} took {access_time:.6f}s, should be under 0.01s"

    def test_directory_listing_performance(self, project_root):
        """Test that directory listing operations are fast."""
        directories_to_list = [
            project_root,
            project_root / 'tests',
            project_root / 'tests' / 'structure',
            project_root / 'project-documents'
        ]
        
        listing_times = {}
        
        for directory in directories_to_list:
            if directory.exists() and directory.is_dir():
                start_time = time.perf_counter()
                
                # List directory contents
                items = list(directory.iterdir())
                file_count = sum(1 for item in items if item.is_file())
                dir_count = sum(1 for item in items if item.is_dir())
                
                end_time = time.perf_counter()
                listing_time = end_time - start_time
                listing_times[str(directory.name)] = listing_time
                
                # Directory listing should be fast (under 0.1 seconds)
                assert listing_time < 0.1, \
                    f"Directory listing for {directory.name} took {listing_time:.3f}s, should be under 0.1s"

    def test_recursive_directory_search_performance(self, project_root):
        """Test recursive directory search performance."""
        start_time = time.perf_counter()
        
        # Search for Python files recursively
        python_files = []
        for path in project_root.rglob('*.py'):
            # Skip hidden directories and cache
            if not any(part.startswith('.') or part == '__pycache__' 
                      for part in path.parts):
                python_files.append(path)
        
        end_time = time.perf_counter()
        search_time = end_time - start_time
        
        # Recursive search should be efficient (under 0.5 seconds)
        assert search_time < 0.5, \
            f"Recursive Python file search took {search_time:.3f}s, should be under 0.5s"
        
        # Verify we found Python files
        assert len(python_files) > 0, "Should find Python files in project"


class TestStartupTimePerformance:
    """Test overall startup time performance."""

    def test_test_suite_startup_performance(self):
        """Test that test suite startup is efficient."""
        start_time = time.perf_counter()
        
        # Simulate test suite startup by importing key modules
        import tests.conftest
        import tests.structure.test_directories
        
        # Access fixture definitions (simulates pytest discovery)
        fixtures = [
            tests.conftest.project_root,
            tests.conftest.temp_directory,
            tests.conftest.mock_env_vars
        ]
        
        end_time = time.perf_counter()
        startup_time = end_time - start_time
        
        # Test suite startup should be fast (under 1.0 seconds)
        assert startup_time < 1.0, \
            f"Test suite startup took {startup_time:.3f}s, should be under 1.0s"

    def test_project_initialization_performance(self, project_root):
        """Test that project initialization steps are performant."""
        start_time = time.perf_counter()
        
        # Simulate project initialization steps
        steps = [
            # Check project structure
            lambda: (project_root / 'tests').exists(),
            lambda: (project_root / 'backend').exists(),
            lambda: (project_root / 'frontend').exists(),
            
            # Read configuration files
            lambda: (project_root / 'pytest.ini').read_text()[:100],
            
            # Import core modules
            lambda: importlib.import_module('tests.conftest'),
            lambda: importlib.import_module('backend'),
        ]
        
        for step in steps:
            step()
        
        end_time = time.perf_counter()
        init_time = end_time - start_time
        
        # Project initialization should be efficient (under 0.5 seconds)
        assert init_time < 0.5, \
            f"Project initialization took {init_time:.3f}s, should be under 0.5s"


class TestPerformanceBenchmarks:
    """Establish performance benchmarks for the project."""

    def test_performance_baseline_documentation(self, project_root):
        """Document performance baselines for future reference."""
        from datetime import datetime
        
        # Collect performance metrics
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'project_structure': {
                'total_directories': 0,
                'total_files': 0,
                'python_files': 0
            },
            'import_times': {},
            'file_access_times': {}
        }
        
        # Count project structure
        for root, dirs, files in os.walk(project_root):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            metrics['project_structure']['total_directories'] += len(dirs)
            metrics['project_structure']['total_files'] += len(files)
            metrics['project_structure']['python_files'] += len([f for f in files if f.endswith('.py')])
        
        # Measure import times
        test_modules = ['tests.conftest', 'backend']
        for module in test_modules:
            start = time.perf_counter()
            importlib.import_module(module)
            metrics['import_times'][module] = time.perf_counter() - start
        
        # Measure file access times
        test_files = ['pytest.ini', 'README.md']
        for filename in test_files:
            file_path = project_root / filename
            if file_path.exists():
                start = time.perf_counter()
                content = file_path.read_text()[:100]
                metrics['file_access_times'][filename] = time.perf_counter() - start
        
        # Verify we collected meaningful metrics
        assert metrics['project_structure']['total_files'] > 0, \
            "Should have collected file count metrics"
        assert len(metrics['import_times']) > 0, \
            "Should have collected import time metrics"
        
        # All measured times should be reasonable
        for module, import_time in metrics['import_times'].items():
            assert import_time < 2.0, f"Import time for {module} should be under 2.0s"
        
        for filename, access_time in metrics['file_access_times'].items():
            assert access_time < 0.5, f"File access time for {filename} should be under 0.5s" 