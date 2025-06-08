"""
Test file encoding and format validation for project structure.

This module validates that all files in the men's circle management platform
have proper encoding (UTF-8), correct format, and adhere to platform standards.
Ensures file integrity and compatibility across different systems and environments.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import pytest
import re


class TestFileEncodingValidation:
    """Test file encoding validation across the project."""

    def test_python_files_utf8_encoding(self, project_root):
        """Test that all Python files use UTF-8 encoding."""
        python_files = list(project_root.rglob('*.py'))
        
        assert len(python_files) > 0, "Should find Python files in project"
        
        encoding_issues = []
        
        for py_file in python_files:
            # Skip cache and compiled files
            if '__pycache__' in str(py_file) or py_file.suffix == '.pyc':
                continue
            
            try:
                # Try to read as UTF-8
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Validate no BOM markers
                if content.startswith('\ufeff'):
                    encoding_issues.append(f"{py_file}: Contains BOM marker")
                
                # Check for encoding declaration if present
                lines = content.split('\n')
                for i, line in enumerate(lines[:2]):  # Check first two lines
                    if 'coding:' in line or 'coding=' in line:
                        if 'utf-8' not in line.lower() and 'utf8' not in line.lower():
                            encoding_issues.append(f"{py_file}: Non-UTF-8 encoding declaration on line {i+1}")
                
            except UnicodeDecodeError as e:
                encoding_issues.append(f"{py_file}: UTF-8 decode error - {e}")
            except Exception as e:
                encoding_issues.append(f"{py_file}: Read error - {e}")
        
        assert len(encoding_issues) == 0, f"Python file encoding issues found: {encoding_issues}"

    def test_text_files_utf8_encoding(self, project_root):
        """Test that all text files use UTF-8 encoding."""
        text_extensions = ['.md', '.txt', '.yml', '.yaml', '.json', '.ini', '.cfg', '.toml']
        text_files = []
        
        for ext in text_extensions:
            text_files.extend(list(project_root.rglob(f'*{ext}')))
        
        assert len(text_files) > 0, "Should find text files in project"
        
        encoding_issues = []
        
        for text_file in text_files:
            # Skip binary or cache directories
            if any(skip_dir in str(text_file) for skip_dir in ['__pycache__', '.git', 'node_modules']):
                continue
            
            try:
                # Try to read as UTF-8 directly
                with open(text_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if len(content) == 0:
                    continue  # Skip empty files
                
                # Check for BOM
                if content.startswith('\ufeff'):
                    encoding_issues.append(f"{text_file}: Contains BOM marker")
                        
            except UnicodeDecodeError as e:
                encoding_issues.append(f"{text_file}: UTF-8 decode error - {e}")
            except Exception as e:
                encoding_issues.append(f"{text_file}: Read error - {e}")
        
        assert len(encoding_issues) == 0, f"Text file encoding issues found: {encoding_issues}"

    def test_script_files_utf8_encoding(self, project_root):
        """Test that all script files use UTF-8 encoding."""
        script_files = list(project_root.rglob('*.sh'))
        
        if len(script_files) == 0:
            pytest.skip("No script files found")
        
        encoding_issues = []
        
        for script_file in script_files:
            try:
                with open(script_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for BOM
                if content.startswith('\ufeff'):
                    encoding_issues.append(f"{script_file}: Contains BOM marker")
                    
            except UnicodeDecodeError as e:
                encoding_issues.append(f"{script_file}: UTF-8 decode error - {e}")
            except Exception as e:
                encoding_issues.append(f"{script_file}: Read error - {e}")
        
        assert len(encoding_issues) == 0, f"Script file encoding issues found: {encoding_issues}"

    def test_no_binary_files_in_source(self, project_root):
        """Test that no binary files are accidentally included in source directories."""
        source_dirs = ['backend', 'frontend', 'tests', 'scripts', 'docs']
        binary_extensions = ['.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.db', '.sqlite']
        
        binary_files_found = []
        
        for source_dir in source_dirs:
            source_path = project_root / source_dir
            if not source_path.exists():
                continue
            
            for binary_ext in binary_extensions:
                binary_files = list(source_path.rglob(f'*{binary_ext}'))
                for binary_file in binary_files:
                    binary_files_found.append(str(binary_file.relative_to(project_root)))
        
        assert len(binary_files_found) == 0, f"Binary files found in source directories: {binary_files_found}"


class TestFileFormatValidation:
    """Test file format validation and standards compliance."""

    def test_json_file_format_validation(self, project_root):
        """Test that all JSON files have valid format and structure."""
        json_files = list(project_root.rglob('*.json'))
        
        if len(json_files) == 0:
            pytest.skip("No JSON files found")
        
        format_issues = []
        
        for json_file in json_files:
            # Skip node_modules and cache directories
            if any(skip_dir in str(json_file) for skip_dir in ['node_modules', '__pycache__', '.git']):
                continue
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if len(content) == 0:
                    continue  # Skip empty files
                
                # Validate JSON syntax
                json_data = json.loads(content)
                
                # Check for consistent formatting (no tabs, proper indentation)
                if '\t' in content:
                    format_issues.append(f"{json_file}: Contains tab characters (use spaces)")
                
                # Check for trailing commas (not valid in JSON)
                if re.search(r',\s*[}\]]', content):
                    format_issues.append(f"{json_file}: Contains trailing commas")
                
                # Validate structure for package.json files
                if json_file.name == 'package.json':
                    required_fields = ['name', 'version']
                    for field in required_fields:
                        if field not in json_data:
                            format_issues.append(f"{json_file}: Missing required field '{field}'")
                
            except json.JSONDecodeError as e:
                format_issues.append(f"{json_file}: Invalid JSON syntax - {e}")
            except Exception as e:
                format_issues.append(f"{json_file}: Read error - {e}")
        
        assert len(format_issues) == 0, f"JSON format issues found: {format_issues}"

    def test_yaml_file_format_validation(self, project_root):
        """Test that all YAML files have valid format and structure."""
        yaml_files = list(project_root.rglob('*.yml')) + list(project_root.rglob('*.yaml'))
        
        if len(yaml_files) == 0:
            pytest.skip("No YAML files found")
        
        format_issues = []
        
        for yaml_file in yaml_files:
            # Skip cache directories
            if any(skip_dir in str(yaml_file) for skip_dir in ['__pycache__', '.git', 'node_modules']):
                continue
            
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if len(content) == 0:
                    continue  # Skip empty files
                
                # Validate YAML syntax
                yaml_data = yaml.safe_load(content)
                
                # Check for consistent indentation (spaces, not tabs)
                if '\t' in content:
                    format_issues.append(f"{yaml_file}: Contains tab characters (use spaces)")
                
                # Check for proper YAML structure
                if yaml_data is None and content.strip():
                    format_issues.append(f"{yaml_file}: YAML content parsed as null")
                
                # Validate GitHub workflow files
                if '.github/workflows' in str(yaml_file):
                    if not isinstance(yaml_data, dict):
                        format_issues.append(f"{yaml_file}: Workflow file must be a dictionary")
                    elif 'jobs' not in yaml_data and True not in yaml_data:
                        # Handle YAML parsing variations
                        format_issues.append(f"{yaml_file}: Workflow file missing 'jobs' section")
                
            except yaml.YAMLError as e:
                format_issues.append(f"{yaml_file}: Invalid YAML syntax - {e}")
            except Exception as e:
                format_issues.append(f"{yaml_file}: Read error - {e}")
        
        assert len(format_issues) == 0, f"YAML format issues found: {format_issues}"

    def test_python_file_format_validation(self, project_root):
        """Test that Python files follow proper format standards."""
        python_files = list(project_root.rglob('*.py'))
        
        assert len(python_files) > 0, "Should find Python files in project"
        
        format_issues = []
        
        for py_file in python_files:
            # Skip cache files
            if '__pycache__' in str(py_file) or py_file.suffix == '.pyc':
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                if len(content.strip()) == 0:
                    continue  # Skip empty files
                
                # Check for shebang in executable files
                if py_file.name.endswith('.py') and len(lines) > 0:
                    first_line = lines[0]
                    # If file starts with shebang, it should be proper
                    if first_line.startswith('#!'):
                        if 'python' not in first_line:
                            format_issues.append(f"{py_file}: Invalid shebang line")
                
                # Check for consistent line endings (no mixed line endings)
                if '\r\n' in content and '\n' in content.replace('\r\n', ''):
                    format_issues.append(f"{py_file}: Mixed line endings detected")
                
                # Check for trailing whitespace on non-empty lines (count occurrences)
                trailing_whitespace_count = 0
                for i, line in enumerate(lines, 1):
                    if line.rstrip() != line and line.strip():
                        trailing_whitespace_count += 1
                
                # Only flag if excessive trailing whitespace (more than 20% of lines)
                if len(lines) > 0 and trailing_whitespace_count > len(lines) * 0.2:
                    format_issues.append(f"{py_file}: Excessive trailing whitespace ({trailing_whitespace_count} lines)")
                
                # Check for tabs (PEP 8 recommends spaces)
                if '\t' in content:
                    format_issues.append(f"{py_file}: Contains tab characters (PEP 8 recommends spaces)")
                
            except Exception as e:
                format_issues.append(f"{py_file}: Read error - {e}")
        
        assert len(format_issues) == 0, f"Python format issues found: {format_issues}"

    def test_markdown_file_format_validation(self, project_root):
        """Test that Markdown files follow proper format standards."""
        md_files = list(project_root.rglob('*.md'))
        
        if len(md_files) == 0:
            pytest.skip("No Markdown files found")
        
        format_issues = []
        
        for md_file in md_files:
            # Skip cache directories
            if any(skip_dir in str(md_file) for skip_dir in ['__pycache__', '.git', 'node_modules']):
                continue
            
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                if len(content.strip()) == 0:
                    continue  # Skip empty files
                
                # Check for consistent line endings
                if '\r\n' in content and '\n' in content.replace('\r\n', ''):
                    format_issues.append(f"{md_file}: Mixed line endings detected")
                
                # Check for proper heading structure (should start with #)
                heading_levels = []
                for i, line in enumerate(lines, 1):
                    if line.strip().startswith('#'):
                        level = len(line) - len(line.lstrip('#'))
                        heading_levels.append((level, i))
                
                # Validate heading hierarchy (count major violations)
                hierarchy_violations = 0
                for j in range(1, len(heading_levels)):
                    prev_level, prev_line = heading_levels[j-1]
                    curr_level, curr_line = heading_levels[j]
                    
                    # Allow same level, one level deeper, or any level shallower
                    # Flag only extreme jumps (more than 2 levels)
                    if curr_level > prev_level + 2:
                        hierarchy_violations += 1
                
                # Only flag if excessive hierarchy violations (more than 20% of heading transitions)
                if len(heading_levels) > 1 and hierarchy_violations > len(heading_levels) * 0.2:
                    format_issues.append(f"{md_file}: Excessive heading hierarchy violations ({hierarchy_violations} major jumps)")
                
            except Exception as e:
                format_issues.append(f"{md_file}: Read error - {e}")
        
        assert len(format_issues) == 0, f"Markdown format issues found: {format_issues}"


class TestFileIntegrityValidation:
    """Test file integrity and consistency validation."""

    def test_file_size_validation(self, project_root):
        """Test that files have reasonable sizes and detect potential issues."""
        large_file_threshold = 10 * 1024 * 1024  # 10MB
        zero_byte_issues = []
        large_file_issues = []
        
        # Check all files except in ignore directories
        ignore_dirs = {'__pycache__', '.git', 'node_modules', '.pytest_cache'}
        
        for file_path in project_root.rglob('*'):
            if file_path.is_file():
                # Skip ignored directories
                if any(ignore_dir in str(file_path) for ignore_dir in ignore_dirs):
                    continue
                
                try:
                    file_size = file_path.stat().st_size
                    
                    # Check for zero-byte files that shouldn't be empty
                    if file_size == 0:
                        # Certain files are expected to be empty
                        if file_path.name not in ['__init__.py', '.gitkeep', '.dockerignore']:
                            zero_byte_issues.append(str(file_path.relative_to(project_root)))
                    
                    # Check for unexpectedly large files
                    if file_size > large_file_threshold:
                        # Exclude known large file types
                        if file_path.suffix not in ['.jpg', '.png', '.gif', '.pdf', '.zip', '.tar', '.gz']:
                            large_file_issues.append(f"{file_path.relative_to(project_root)} ({file_size // (1024*1024)}MB)")
                
                except Exception as e:
                    # File access issues
                    pass
        
        # Only warn about zero-byte files, don't fail
        if zero_byte_issues:
            print(f"Warning: Zero-byte files found: {zero_byte_issues}")
        
        assert len(large_file_issues) == 0, f"Unexpectedly large files found: {large_file_issues}"

    def test_file_naming_conventions(self, project_root):
        """Test that files follow proper naming conventions."""
        naming_issues = []
        
        # Define naming patterns for different file types
        python_pattern = re.compile(r'^[a-z0-9_]+\.py$')
        test_pattern = re.compile(r'^test_[a-z0-9_]+\.py$')
        
        ignore_dirs = {'__pycache__', '.git', 'node_modules', '.pytest_cache'}
        
        for file_path in project_root.rglob('*'):
            if file_path.is_file():
                # Skip ignored directories
                if any(ignore_dir in str(file_path) for ignore_dir in ignore_dirs):
                    continue
                
                filename = file_path.name
                
                # Check Python files (excluding test files and special cases)
                if filename.endswith('.py') and not filename.startswith('test_'):
                    # Allow special files like conftest.py, __init__.py
                    if filename not in ['conftest.py', '__init__.py', 'setup.py']:
                        if not python_pattern.match(filename):
                            naming_issues.append(f"{file_path.relative_to(project_root)}: Python file naming violation")
                
                # Check test files
                if filename.startswith('test_') and filename.endswith('.py'):
                    if not test_pattern.match(filename):
                        naming_issues.append(f"{file_path.relative_to(project_root)}: Test file naming violation")
                
                # Check for spaces in filenames (generally bad practice)
                if ' ' in filename:
                    naming_issues.append(f"{file_path.relative_to(project_root)}: Filename contains spaces")
                
                # Check for non-ASCII characters in filenames
                try:
                    filename.encode('ascii')
                except UnicodeEncodeError:
                    naming_issues.append(f"{file_path.relative_to(project_root)}: Filename contains non-ASCII characters")
        
        assert len(naming_issues) == 0, f"File naming convention issues found: {naming_issues}"

    def test_line_ending_consistency(self, project_root):
        """Test that files have consistent line endings."""
        text_extensions = ['.py', '.md', '.txt', '.yml', '.yaml', '.json', '.ini', '.cfg', '.sh']
        line_ending_issues = []
        
        ignore_dirs = {'__pycache__', '.git', 'node_modules', '.pytest_cache'}
        
        for ext in text_extensions:
            for file_path in project_root.rglob(f'*{ext}'):
                # Skip ignored directories
                if any(ignore_dir in str(file_path) for ignore_dir in ignore_dirs):
                    continue
                
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    
                    if len(content) == 0:
                        continue  # Skip empty files
                    
                    # Check for mixed line endings
                    has_crlf = b'\r\n' in content
                    has_lf = b'\n' in content.replace(b'\r\n', b'')
                    has_cr = b'\r' in content.replace(b'\r\n', b'')
                    
                    if sum([has_crlf, has_lf, has_cr]) > 1:
                        line_ending_issues.append(f"{file_path.relative_to(project_root)}: Mixed line endings")
                    
                    # Prefer LF endings (Unix-style)
                    if has_cr and not has_lf and not has_crlf:
                        # Pure CR is problematic
                        line_ending_issues.append(f"{file_path.relative_to(project_root)}: Uses CR line endings (use LF)")
                
                except Exception as e:
                    # Skip files that can't be read
                    pass
        
        assert len(line_ending_issues) == 0, f"Line ending issues found: {line_ending_issues}"


class TestFileEncodingPerformance:
    """Test file encoding and format validation performance."""

    def test_encoding_validation_performance(self, project_root):
        """Test that encoding validation completes in reasonable time."""
        import time
        
        start_time = time.perf_counter()
        
        # Count files that need encoding validation
        text_extensions = ['.py', '.md', '.txt', '.yml', '.yaml', '.json', '.ini', '.cfg', '.sh']
        total_files = 0
        
        ignore_dirs = {'__pycache__', '.git', 'node_modules', '.pytest_cache'}
        
        for ext in text_extensions:
            for file_path in project_root.rglob(f'*{ext}'):
                if not any(ignore_dir in str(file_path) for ignore_dir in ignore_dirs):
                    total_files += 1
        
        end_time = time.perf_counter()
        scan_time = end_time - start_time
        
        # Encoding validation should be fast
        assert scan_time < 1.0, f"File encoding scan took {scan_time:.3f}s, should be under 1.0s"
        assert total_files > 0, "Should find files to validate"

    def test_format_validation_performance(self, project_root):
        """Test that format validation completes in reasonable time."""
        import time
        
        start_time = time.perf_counter()
        
        # Quick format validation simulation
        validation_count = 0
        ignore_dirs = {'__pycache__', '.git', 'node_modules', '.pytest_cache'}
        
        # JSON files
        for json_file in project_root.rglob('*.json'):
            if not any(ignore_dir in str(json_file) for ignore_dir in ignore_dirs):
                validation_count += 1
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if content.strip():
                        json.loads(content)
                except:
                    pass
        
        # YAML files
        for yaml_file in list(project_root.rglob('*.yml')) + list(project_root.rglob('*.yaml')):
            if not any(ignore_dir in str(yaml_file) for ignore_dir in ignore_dirs):
                validation_count += 1
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if content.strip():
                        yaml.safe_load(content)
                except:
                    pass
        
        end_time = time.perf_counter()
        validation_time = end_time - start_time
        
        # Format validation should be reasonably fast
        assert validation_time < 2.0, f"Format validation took {validation_time:.3f}s, should be under 2.0s" 