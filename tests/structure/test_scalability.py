"""
Test project structure scalability with large file counts.

This module tests the scalability characteristics of the men's circle management platform
project structure when dealing with large numbers of files. Ensures performance and
maintainability under high file count scenarios for future growth.
"""

import os
import tempfile
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import pytest
import random
import string


class TestDirectoryScalability:
    """Test directory structure scalability with large file counts."""

    def test_directory_traversal_performance_current_structure(self, project_root):
        """Test that current project structure traversal is performant."""
        start_time = time.perf_counter()
        
        # Count all files and directories in current structure
        total_files = 0
        total_dirs = 0
        
        for root, dirs, files in os.walk(project_root):
            # Skip problematic directories
            dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.github']
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'node_modules', '.pytest_cache']]
            
            total_dirs += len(dirs)
            total_files += len(files)
        
        end_time = time.perf_counter()
        traversal_time = end_time - start_time
        
        # Current structure should be traversable quickly
        assert traversal_time < 2.0, f"Directory traversal took {traversal_time:.3f}s, should be under 2.0s"
        assert total_files > 0, "Should find files in project"
        assert total_dirs > 0, "Should find directories in project"
        
        # Log current structure size for baseline
        print(f"Current structure: {total_files} files, {total_dirs} directories, {traversal_time:.3f}s")

    def test_large_file_count_simulation(self, project_root):
        """Test project structure behavior with simulated large file counts."""
        # Create temporary test directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Simulate project structure with many files
            start_time = time.perf_counter()
            
            # Create directory structure similar to our project
            directories = [
                temp_path / 'backend' / 'app' / 'models',
                temp_path / 'backend' / 'app' / 'api',
                temp_path / 'backend' / 'app' / 'services',
                temp_path / 'frontend' / 'src' / 'components',
                temp_path / 'frontend' / 'src' / 'pages',
                temp_path / 'tests' / 'unit',
                temp_path / 'tests' / 'integration',
                temp_path / 'docs' / 'api',
                temp_path / 'scripts' / 'deployment'
            ]
            
            for directory in directories:
                directory.mkdir(parents=True, exist_ok=True)
            
            # Create many files in each directory (simulate growth)
            files_per_dir = 50  # Reasonable number for scalability test
            
            for directory in directories:
                for i in range(files_per_dir):
                    if 'backend' in str(directory):
                        file_ext = '.py'
                    elif 'frontend' in str(directory):
                        file_ext = '.tsx' if 'components' in str(directory) else '.ts'
                    elif 'tests' in str(directory):
                        file_ext = '.py'
                    elif 'docs' in str(directory):
                        file_ext = '.md'
                    else:
                        file_ext = '.sh'
                    
                    test_file = directory / f"test_file_{i:03d}{file_ext}"
                    test_file.write_text(f"# Test file {i}\n")
            
            creation_time = time.perf_counter() - start_time
            
            # Test traversal performance
            start_time = time.perf_counter()
            
            file_count = 0
            dir_count = 0
            
            for root, dirs, files in os.walk(temp_path):
                dir_count += len(dirs)
                file_count += len(files)
            
            traversal_time = time.perf_counter() - start_time
            
            # Scalability assertions
            assert creation_time < 5.0, f"File creation took {creation_time:.3f}s, should be under 5.0s"
            assert traversal_time < 1.0, f"Traversal of {file_count} files took {traversal_time:.3f}s, should be under 1.0s"
            assert file_count == len(directories) * files_per_dir, f"Expected {len(directories) * files_per_dir} files, found {file_count}"

    def test_directory_depth_scalability(self, project_root):
        """Test project structure behavior with deep directory hierarchies."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create deep directory structure (simulate nested modules)
            max_depth = 10  # Reasonable depth for most projects
            current_path = temp_path
            
            start_time = time.perf_counter()
            
            for depth in range(max_depth):
                current_path = current_path / f"level_{depth}"
                current_path.mkdir(exist_ok=True)
                
                # Add a file at each level
                test_file = current_path / f"module_{depth}.py"
                test_file.write_text(f"# Module at depth {depth}\n")
            
            creation_time = time.perf_counter() - start_time
            
            # Test access to deep files
            start_time = time.perf_counter()
            
            # Access the deepest file
            deepest_file = temp_path
            for depth in range(max_depth):
                deepest_file = deepest_file / f"level_{depth}"
            deepest_file = deepest_file / f"module_{max_depth-1}.py"
            
            assert deepest_file.exists(), "Deep file should be accessible"
            content = deepest_file.read_text()
            assert f"depth {max_depth-1}" in content, "Deep file should have correct content"
            
            access_time = time.perf_counter() - start_time
            
            # Depth scalability assertions
            assert creation_time < 1.0, f"Deep directory creation took {creation_time:.3f}s, should be under 1.0s"
            assert access_time < 0.1, f"Deep file access took {access_time:.3f}s, should be under 0.1s"

    def test_mixed_file_size_scalability(self, project_root):
        """Test project structure with mixed file sizes."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create files of different sizes
            start_time = time.perf_counter()
            
            # Small files (typical source files)
            small_files_dir = temp_path / 'small_files'
            small_files_dir.mkdir()
            
            for i in range(100):
                small_file = small_files_dir / f"small_{i}.py"
                small_file.write_text(f"# Small file {i}\nprint('Hello World')\n")
            
            # Medium files (typical modules)
            medium_files_dir = temp_path / 'medium_files'
            medium_files_dir.mkdir()
            
            for i in range(20):
                medium_file = medium_files_dir / f"medium_{i}.py"
                content = f"# Medium file {i}\n" + "# " + "x" * 1000 + "\n" * 50
                medium_file.write_text(content)
            
            # Large files (documentation, configs)
            large_files_dir = temp_path / 'large_files'
            large_files_dir.mkdir()
            
            for i in range(5):
                large_file = large_files_dir / f"large_{i}.md"
                content = f"# Large file {i}\n" + "Content line\n" * 1000
                large_file.write_text(content)
            
            creation_time = time.perf_counter() - start_time
            
            # Test directory operations on mixed sizes
            start_time = time.perf_counter()
            
            total_files = 0
            total_size = 0
            
            for root, dirs, files in os.walk(temp_path):
                for file in files:
                    file_path = Path(root) / file
                    total_files += 1
                    total_size += file_path.stat().st_size
            
            analysis_time = time.perf_counter() - start_time
            
            # Mixed size scalability assertions
            assert creation_time < 2.0, f"Mixed file creation took {creation_time:.3f}s, should be under 2.0s"
            assert analysis_time < 1.0, f"Mixed file analysis took {analysis_time:.3f}s, should be under 1.0s"
            assert total_files == 125, f"Expected 125 files, found {total_files}"
            assert total_size > 0, "Should calculate total size correctly"


class TestFileOperationScalability:
    """Test file operation scalability under high file count scenarios."""

    def test_file_search_performance(self, project_root):
        """Test file search performance with current project structure."""
        start_time = time.perf_counter()
        
        # Search for Python files
        python_files = list(project_root.rglob('*.py'))
        
        # Search for YAML files
        yaml_files = list(project_root.rglob('*.yml')) + list(project_root.rglob('*.yaml'))
        
        # Search for Markdown files
        md_files = list(project_root.rglob('*.md'))
        
        search_time = time.perf_counter() - start_time
        
        # Search performance assertions
        assert search_time < 1.0, f"File search took {search_time:.3f}s, should be under 1.0s"
        assert len(python_files) > 0, "Should find Python files"
        
        print(f"Search results: {len(python_files)} .py, {len(yaml_files)} .yml/.yaml, {len(md_files)} .md files")

    def test_concurrent_file_access_simulation(self, project_root):
        """Test simulated concurrent file access scenarios."""
        # Get sample of existing files
        existing_files = list(project_root.rglob('*.py'))[:10]  # Sample 10 files
        
        if len(existing_files) == 0:
            pytest.skip("No Python files found for concurrent access test")
        
        start_time = time.perf_counter()
        
        # Simulate concurrent access by reading multiple files rapidly
        read_results = []
        
        for _ in range(3):  # Simulate 3 concurrent operations
            for file_path in existing_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    read_results.append(len(content))
                except Exception as e:
                    read_results.append(0)
        
        concurrent_time = time.perf_counter() - start_time
        
        # Concurrent access assertions
        assert concurrent_time < 2.0, f"Concurrent file access took {concurrent_time:.3f}s, should be under 2.0s"
        assert len(read_results) == len(existing_files) * 3, "Should complete all reads"
        assert sum(read_results) > 0, "Should read content from files"

    def test_file_modification_detection_scalability(self, project_root):
        """Test file modification detection scalability."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create many files to monitor
            num_files = 100
            test_files = []
            
            start_time = time.perf_counter()
            
            for i in range(num_files):
                test_file = temp_path / f"monitor_{i}.txt"
                test_file.write_text(f"Initial content {i}")
                test_files.append(test_file)
            
            # Get initial modification times
            initial_times = {}
            for file_path in test_files:
                initial_times[file_path] = file_path.stat().st_mtime
            
            # Modify some files
            modification_start = time.perf_counter()
            
            for i in range(0, num_files, 10):  # Modify every 10th file
                test_files[i].write_text(f"Modified content {i}")
            
            # Detect modifications
            modified_files = []
            for file_path in test_files:
                current_time = file_path.stat().st_mtime
                if current_time != initial_times[file_path]:
                    modified_files.append(file_path)
            
            detection_time = time.perf_counter() - modification_start
            total_time = time.perf_counter() - start_time
            
            # Modification detection assertions
            assert total_time < 3.0, f"Total modification test took {total_time:.3f}s, should be under 3.0s"
            assert detection_time < 1.0, f"Modification detection took {detection_time:.3f}s, should be under 1.0s"
            assert len(modified_files) == 10, f"Expected 10 modified files, detected {len(modified_files)}"

    def test_batch_file_operations_performance(self, project_root):
        """Test batch file operations performance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test batch creation
            batch_size = 200
            
            start_time = time.perf_counter()
            
            # Batch create files
            created_files = []
            for i in range(batch_size):
                batch_file = temp_path / f"batch_{i:03d}.txt"
                batch_file.write_text(f"Batch file {i}")
                created_files.append(batch_file)
            
            creation_time = time.perf_counter() - start_time
            
            # Test batch reading
            start_time = time.perf_counter()
            
            total_content_length = 0
            for batch_file in created_files:
                content = batch_file.read_text()
                total_content_length += len(content)
            
            reading_time = time.perf_counter() - start_time
            
            # Test batch deletion
            start_time = time.perf_counter()
            
            for batch_file in created_files:
                batch_file.unlink()
            
            deletion_time = time.perf_counter() - start_time
            
            # Batch operations assertions
            assert creation_time < 2.0, f"Batch creation of {batch_size} files took {creation_time:.3f}s, should be under 2.0s"
            assert reading_time < 1.0, f"Batch reading took {reading_time:.3f}s, should be under 1.0s"
            assert deletion_time < 1.0, f"Batch deletion took {deletion_time:.3f}s, should be under 1.0s"
            assert total_content_length > 0, "Should read content from all files"


class TestMemoryScalability:
    """Test memory usage scalability with large file counts."""

    def test_directory_traversal_memory_efficiency(self, project_root):
        """Test memory efficiency during directory traversal."""
        import gc
        
        # Force garbage collection before test
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Perform directory traversal
        file_paths = []
        
        for root, dirs, files in os.walk(project_root):
            # Skip problematic directories
            dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.github']
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'node_modules', '.pytest_cache']]
            
            for file in files:
                file_paths.append(Path(root) / file)
        
        # Check memory usage after traversal
        gc.collect()
        final_objects = len(gc.get_objects())
        object_increase = final_objects - initial_objects
        
        # Memory efficiency assertions
        assert object_increase < 10000, f"Object count increased by {object_increase}, should be under 10,000"
        assert len(file_paths) > 0, "Should find file paths"

    def test_large_file_list_memory_usage(self, project_root):
        """Test memory usage when handling large file lists."""
        import gc
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create moderate number of files for memory test
            num_files = 500
            
            # Create files
            for i in range(num_files):
                test_file = temp_path / f"memory_test_{i}.txt"
                test_file.write_text(f"Memory test file {i}")
            
            # Measure memory during file list operations
            gc.collect()
            initial_objects = len(gc.get_objects())
            
            # Create large file list
            all_files = list(temp_path.rglob('*.txt'))
            
            # Process file list
            file_sizes = []
            for file_path in all_files:
                file_sizes.append(file_path.stat().st_size)
            
            gc.collect()
            final_objects = len(gc.get_objects())
            object_increase = final_objects - initial_objects
            
            # Memory usage assertions
            assert object_increase < 20000, f"Object count increased by {object_increase}, should be under 20,000"
            assert len(all_files) == num_files, f"Expected {num_files} files, found {len(all_files)}"
            assert len(file_sizes) == num_files, "Should calculate sizes for all files"

    def test_file_content_streaming_memory(self, project_root):
        """Test memory usage when processing file contents."""
        import gc
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create files with substantial content
            num_files = 50
            
            for i in range(num_files):
                test_file = temp_path / f"content_test_{i}.txt"
                # Create files with moderate content (not too large for test speed)
                content = ''.join(f"Line {j}\n" for j in range(100))
                test_file.write_text(content)
            
            gc.collect()
            initial_objects = len(gc.get_objects())
            
            # Process file contents one by one (streaming approach)
            total_lines = 0
            
            for i in range(num_files):
                test_file = temp_path / f"content_test_{i}.txt"
                with open(test_file, 'r') as f:
                    for line in f:
                        total_lines += 1
            
            gc.collect()
            final_objects = len(gc.get_objects())
            object_increase = final_objects - initial_objects
            
            # Streaming memory assertions
            assert object_increase < 5000, f"Object count increased by {object_increase}, should be under 5,000"
            assert total_lines == num_files * 100, f"Expected {num_files * 100} lines, counted {total_lines}"


class TestScalabilityPerformance:
    """Test overall scalability performance characteristics."""

    def test_project_structure_growth_simulation(self, project_root):
        """Test how project structure performs under simulated growth."""
        # Measure current baseline
        start_time = time.perf_counter()
        
        current_file_count = 0
        current_dir_count = 0
        
        for root, dirs, files in os.walk(project_root):
            # Skip problematic directories
            dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.github']
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'node_modules', '.pytest_cache']]
            
            current_dir_count += len(dirs)
            current_file_count += len(files)
        
        baseline_time = time.perf_counter() - start_time
        
        # Simulate project growth scenarios
        growth_scenarios = [
            (current_file_count * 2, "2x growth"),
            (current_file_count * 5, "5x growth"),
            (current_file_count * 10, "10x growth")
        ]
        
        for target_files, scenario_name in growth_scenarios:
            # Estimate performance based on baseline
            estimated_time = baseline_time * (target_files / current_file_count) if current_file_count > 0 else 0
            
            # Growth should remain manageable
            if target_files <= current_file_count * 2:
                assert estimated_time < 5.0, f"{scenario_name}: Estimated time {estimated_time:.3f}s should be under 5.0s"
            elif target_files <= current_file_count * 5:
                assert estimated_time < 15.0, f"{scenario_name}: Estimated time {estimated_time:.3f}s should be under 15.0s"
            else:  # 10x growth
                assert estimated_time < 30.0, f"{scenario_name}: Estimated time {estimated_time:.3f}s should be under 30.0s"
        
        print(f"Baseline: {current_file_count} files, {current_dir_count} dirs, {baseline_time:.3f}s")

    def test_scalability_bottleneck_detection(self, project_root):
        """Test detection of potential scalability bottlenecks."""
        bottlenecks = []
        
        # Check directory fan-out (files per directory)
        dir_file_counts = {}
        
        for root, dirs, files in os.walk(project_root):
            # Skip problematic directories
            dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.github']
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'node_modules', '.pytest_cache']]
            
            dir_path = Path(root)
            file_count = len(files)
            dir_file_counts[dir_path] = file_count
            
            # Flag directories with very high file counts
            if file_count > 100:
                bottlenecks.append(f"High file count in {dir_path}: {file_count} files")
        
        # Check directory depth
        max_depth = 0
        for root, dirs, files in os.walk(project_root):
            current_depth = len(Path(root).relative_to(project_root).parts)
            max_depth = max(max_depth, current_depth)
        
        if max_depth > 15:
            bottlenecks.append(f"Very deep directory structure: {max_depth} levels")
        
        # Check for uneven distribution
        if dir_file_counts:
            avg_files = sum(dir_file_counts.values()) / len(dir_file_counts)
            max_files = max(dir_file_counts.values()) if dir_file_counts.values() else 0
            
            if max_files > avg_files * 10:
                bottlenecks.append(f"Uneven file distribution: max {max_files} vs avg {avg_files:.1f}")
        
        # Bottleneck assertions (warnings, not failures)
        if bottlenecks:
            print(f"Potential scalability bottlenecks detected: {bottlenecks}")
        
        # Basic scalability requirements
        assert max_depth < 20, f"Directory depth {max_depth} should be under 20 levels"
        assert max(dir_file_counts.values()) if dir_file_counts.values() else 0 < 200, "No directory should have more than 200 files"

    def test_scalability_performance_benchmarks(self, project_root):
        """Test scalability performance against established benchmarks."""
        benchmarks = {
            'directory_traversal': 5.0,  # seconds
            'file_search': 2.0,          # seconds  
            'stat_operations': 1.0,      # seconds
        }
        
        results = {}
        
        # Directory traversal benchmark
        start_time = time.perf_counter()
        
        total_items = 0
        for root, dirs, files in os.walk(project_root):
            # Skip problematic directories
            dirs[:] = [d for d in dirs if not d.startswith('.') or d == '.github']
            dirs[:] = [d for d in dirs if d not in ['__pycache__', 'node_modules', '.pytest_cache']]
            
            total_items += len(dirs) + len(files)
        
        results['directory_traversal'] = time.perf_counter() - start_time
        
        # File search benchmark
        start_time = time.perf_counter()
        
        python_files = list(project_root.rglob('*.py'))
        yaml_files = list(project_root.rglob('*.yml'))
        md_files = list(project_root.rglob('*.md'))
        
        results['file_search'] = time.perf_counter() - start_time
        
        # Stat operations benchmark
        start_time = time.perf_counter()
        
        sample_files = python_files[:20]  # Sample for performance
        for file_path in sample_files:
            try:
                stat_info = file_path.stat()
                _ = stat_info.st_size, stat_info.st_mtime
            except:
                pass
        
        results['stat_operations'] = time.perf_counter() - start_time
        
        # Benchmark assertions
        for benchmark_name, threshold in benchmarks.items():
            actual_time = results[benchmark_name]
            assert actual_time < threshold, f"{benchmark_name} took {actual_time:.3f}s, should be under {threshold}s"
        
        print(f"Scalability benchmarks: {results}")
        print(f"Project stats: {total_items} total items, {len(python_files)} .py files") 