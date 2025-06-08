#!/usr/bin/env python3
"""
Men's Circle Management Platform - Automated Health Check Script
File: scripts/health-check.py
Purpose: Comprehensive automated health monitoring and validation system

This script provides automated health checking capabilities for the men's circle
management platform, integrating with existing validation infrastructure while
providing enhanced monitoring and reporting features.
"""

import os
import sys
import json
import time
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import argparse


@dataclass
class HealthMetric:
    """Represents a single health metric with scoring and metadata."""
    name: str
    category: str
    value: Any
    max_score: int
    actual_score: int
    status: str
    message: str
    timestamp: str
    execution_time: float


@dataclass
class HealthReport:
    """Comprehensive health report containing all metrics and summary."""
    timestamp: str
    execution_time: float
    overall_score: float
    max_possible_score: int
    health_percentage: float
    status: str
    categories: Dict[str, Dict[str, Any]]
    metrics: List[HealthMetric]
    recommendations: List[str]
    critical_issues: List[str]


class ProjectHealthChecker:
    """Automated health checking system for the men's circle management platform."""
    
    def __init__(self, project_root: Optional[Path] = None, verbose: bool = False):
        """Initialize the health checker with project configuration."""
        self.project_root = project_root or self._detect_project_root()
        self.verbose = verbose
        self.start_time = time.perf_counter()
        self.metrics: List[HealthMetric] = []
        self.critical_issues: List[str] = []
        self.recommendations: List[str] = []
        
        # Health check categories and their weights
        self.categories = {
            'structure': {'weight': 25, 'max_score': 25},
            'dependencies': {'weight': 20, 'max_score': 20},
            'testing': {'weight': 20, 'max_score': 20},
            'security': {'weight': 15, 'max_score': 15},
            'performance': {'weight': 10, 'max_score': 10},
            'documentation': {'weight': 10, 'max_score': 10}
        }
        
        if self.verbose:
            print(f"🔍 Initializing health check for project: {self.project_root}")
    
    def _detect_project_root(self) -> Path:
        """Detect the project root directory."""
        current_dir = Path(__file__).resolve()
        
        # Walk up from script location to find project root
        while current_dir.parent != current_dir:
            if (current_dir / 'README.md').exists() and (current_dir / 'scripts').exists():
                return current_dir
            current_dir = current_dir.parent
        
        # Fallback to script's parent directory
        return Path(__file__).parent.parent
    
    def _record_metric(self, name: str, category: str, value: Any, 
                      max_score: int, actual_score: int, status: str, 
                      message: str, execution_time: float = 0.0) -> None:
        """Record a health metric with all metadata."""
        metric = HealthMetric(
            name=name,
            category=category,
            value=value,
            max_score=max_score,
            actual_score=actual_score,
            status=status,
            message=message,
            timestamp=datetime.now(timezone.utc).isoformat(),
            execution_time=execution_time
        )
        self.metrics.append(metric)
        
        if self.verbose:
            print(f"  📊 {name}: {status} ({actual_score}/{max_score}) - {message}")
    
    def _run_command(self, command: List[str], timeout: int = 30) -> Tuple[bool, str, str]:
        """Run a command and return success status and output."""
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout}s"
        except Exception as e:
            return False, "", f"Command failed: {str(e)}"
    
    def check_project_structure(self) -> None:
        """Check project structure health."""
        if self.verbose:
            print("🏗️  Checking project structure...")
        
        # Core directories check
        core_dirs = ['backend', 'frontend', 'tests', 'docs', 'scripts', '.github']
        existing_dirs = [d for d in core_dirs if (self.project_root / d).exists()]
        
        structure_score = len(existing_dirs)
        max_structure_score = len(core_dirs)
        
        self._record_metric(
            "Core Directories",
            "structure",
            f"{len(existing_dirs)}/{len(core_dirs)}",
            max_structure_score,
            structure_score,
            "PASS" if structure_score == max_structure_score else "WARN",
            f"Found {len(existing_dirs)} of {len(core_dirs)} core directories"
        )
        
        # Key files check
        key_files = [
            'README.md', 'pytest.ini', '.gitignore', 
            'backend/__init__.py', 'frontend/package.json',
            'tests/conftest.py'
        ]
        existing_files = [f for f in key_files if (self.project_root / f).exists()]
        
        files_score = len(existing_files)
        max_files_score = len(key_files)
        
        self._record_metric(
            "Key Files",
            "structure",
            f"{len(existing_files)}/{len(key_files)}",
            max_files_score,
            files_score,
            "PASS" if files_score >= max_files_score * 0.8 else "FAIL",
            f"Found {len(existing_files)} of {len(key_files)} key files"
        )
        
        # GitHub workflows check
        workflows_dir = self.project_root / '.github' / 'workflows'
        if workflows_dir.exists():
            workflow_files = list(workflows_dir.glob('*.yml'))
            workflow_score = min(len(workflow_files), 3)
            
            self._record_metric(
                "GitHub Workflows",
                "structure",
                f"{len(workflow_files)} workflows",
                3,
                workflow_score,
                "PASS" if len(workflow_files) >= 3 else "WARN",
                f"Found {len(workflow_files)} workflow files"
            )
        else:
            self._record_metric(
                "GitHub Workflows",
                "structure",
                "0 workflows",
                3,
                0,
                "FAIL",
                "No .github/workflows directory found"
            )
            self.critical_issues.append("Missing GitHub Actions workflows")
    
    def check_dependencies(self) -> None:
        """Check dependency management and installation health."""
        if self.verbose:
            print("📦 Checking dependencies...")
        
        # Python dependencies check
        requirements_files = ['backend/requirements.txt', 'backend/requirements-dev.txt']
        python_deps_found = sum(1 for f in requirements_files if (self.project_root / f).exists())
        
        self._record_metric(
            "Python Dependencies",
            "dependencies",
            f"{python_deps_found}/{len(requirements_files)} files",
            5,
            python_deps_found * 2 + (1 if python_deps_found > 0 else 0),
            "PASS" if python_deps_found >= 1 else "FAIL",
            f"Found {python_deps_found} Python requirement files"
        )
        
        # Node.js dependencies check
        package_json = self.project_root / 'frontend' / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    package_data = json.load(f)
                deps_count = len(package_data.get('dependencies', {}))
                dev_deps_count = len(package_data.get('devDependencies', {}))
                
                node_score = min(5, (deps_count + dev_deps_count) // 5)
                
                self._record_metric(
                    "Node.js Dependencies",
                    "dependencies",
                    f"{deps_count} deps, {dev_deps_count} dev deps",
                    5,
                    node_score,
                    "PASS" if deps_count > 0 else "WARN",
                    f"Found {deps_count} dependencies and {dev_deps_count} dev dependencies"
                )
            except Exception as e:
                self._record_metric(
                    "Node.js Dependencies",
                    "dependencies",
                    "Invalid package.json",
                    5,
                    0,
                    "FAIL",
                    f"Could not parse package.json: {str(e)}"
                )
        else:
            self._record_metric(
                "Node.js Dependencies",
                "dependencies",
                "No package.json",
                5,
                0,
                "WARN",
                "No frontend package.json found"
            )
    
    def check_testing_infrastructure(self) -> None:
        """Check testing infrastructure health."""
        if self.verbose:
            print("🧪 Checking testing infrastructure...")
        
        # pytest configuration
        pytest_ini = self.project_root / 'pytest.ini'
        pytest_score = 5 if pytest_ini.exists() else 0
        
        self._record_metric(
            "Pytest Configuration",
            "testing",
            "Configured" if pytest_ini.exists() else "Missing",
            5,
            pytest_score,
            "PASS" if pytest_ini.exists() else "FAIL",
            "pytest.ini found" if pytest_ini.exists() else "No pytest configuration"
        )
        
        # Test discovery
        test_dirs = ['tests', 'backend/tests', 'frontend/tests']
        existing_test_dirs = [d for d in test_dirs if (self.project_root / d).exists()]
        
        test_discovery_score = min(5, len(existing_test_dirs) * 2)
        
        self._record_metric(
            "Test Directories",
            "testing",
            f"{len(existing_test_dirs)} directories",
            5,
            test_discovery_score,
            "PASS" if len(existing_test_dirs) >= 1 else "FAIL",
            f"Found {len(existing_test_dirs)} test directories"
        )
        
        # Test execution check
        test_execution_success, test_output, test_error = self._run_command([
            sys.executable, '-m', 'pytest', '--collect-only', '-q'
        ], timeout=15)
        
        if test_execution_success:
            # Count collected tests
            lines = test_output.split('\n')
            collected_line = [line for line in lines if 'collected' in line.lower()]
            test_count = 0
            if collected_line:
                try:
                    test_count = int(''.join(filter(str.isdigit, collected_line[0])))
                except:
                    pass
            
            execution_score = min(5, test_count // 10)
            
            self._record_metric(
                "Test Collection",
                "testing",
                f"{test_count} tests",
                5,
                execution_score,
                "PASS" if test_count > 0 else "WARN",
                f"Successfully collected {test_count} tests"
            )
        else:
            self._record_metric(
                "Test Collection",
                "testing",
                "Failed",
                5,
                0,
                "FAIL",
                f"Test collection failed: {test_error}"
            )
            self.critical_issues.append("Test collection is failing")
    
    def check_security_compliance(self) -> None:
        """Check security compliance and best practices."""
        if self.verbose:
            print("🔒 Checking security compliance...")
        
        # .gitignore security patterns
        gitignore_file = self.project_root / '.gitignore'
        security_patterns = ['.env', '*.key', '*.pem', '*.log', '__pycache__/', 'node_modules/']
        
        if gitignore_file.exists():
            gitignore_content = gitignore_file.read_text()
            found_patterns = [p for p in security_patterns if p in gitignore_content]
            gitignore_score = min(5, len(found_patterns))
            
            self._record_metric(
                "GitIgnore Security",
                "security",
                f"{len(found_patterns)}/{len(security_patterns)} patterns",
                5,
                gitignore_score,
                "PASS" if len(found_patterns) >= 5 else "WARN",
                f"Found {len(found_patterns)} of {len(security_patterns)} security patterns"
            )
        else:
            self._record_metric(
                "GitIgnore Security",
                "security",
                "No .gitignore",
                5,
                0,
                "FAIL",
                "No .gitignore file found"
            )
            self.critical_issues.append("Missing .gitignore file")
        
        # Sensitive file detection
        sensitive_files = list(self.project_root.rglob('*.env*'))
        sensitive_files.extend(self.project_root.rglob('*.key'))
        sensitive_files.extend(self.project_root.rglob('*.pem'))
        
        if sensitive_files:
            self._record_metric(
                "Sensitive File Detection",
                "security",
                f"{len(sensitive_files)} found",
                5,
                0,
                "FAIL",
                f"Found {len(sensitive_files)} potentially sensitive files"
            )
            self.critical_issues.append(f"Sensitive files detected: {[f.name for f in sensitive_files[:3]]}")
        else:
            self._record_metric(
                "Sensitive File Detection",
                "security",
                "Clean",
                5,
                5,
                "PASS",
                "No sensitive files detected in repository"
            )
    
    def check_performance_characteristics(self) -> None:
        """Check performance-related characteristics."""
        if self.verbose:
            print("⚡ Checking performance characteristics...")
        
        # Project size analysis
        total_size = sum(f.stat().st_size for f in self.project_root.rglob('*') if f.is_file())
        size_mb = total_size / (1024 * 1024)
        
        size_score = 5 if size_mb < 100 else 3 if size_mb < 500 else 1
        
        self._record_metric(
            "Project Size",
            "performance",
            f"{size_mb:.1f} MB",
            5,
            size_score,
            "PASS" if size_mb < 100 else "WARN" if size_mb < 500 else "FAIL",
            f"Total project size: {size_mb:.1f} MB"
        )
        
        # Test execution performance
        start_time = time.perf_counter()
        test_success, _, _ = self._run_command([
            sys.executable, '-m', 'pytest', '--collect-only', '-q'
        ], timeout=10)
        execution_time = time.perf_counter() - start_time
        
        performance_score = 5 if execution_time < 2 else 3 if execution_time < 5 else 1
        
        self._record_metric(
            "Test Performance",
            "performance",
            f"{execution_time:.2f}s",
            5,
            performance_score if test_success else 0,
            "PASS" if test_success and execution_time < 2 else "WARN" if test_success else "FAIL",
            f"Test collection took {execution_time:.2f} seconds"
        )
    
    def check_documentation_quality(self) -> None:
        """Check documentation quality and completeness."""
        if self.verbose:
            print("📚 Checking documentation quality...")
        
        # README.md analysis
        readme_file = self.project_root / 'README.md'
        if readme_file.exists():
            readme_content = readme_file.read_text()
            required_sections = ['setup', 'development', 'installation', 'usage']
            found_sections = sum(1 for section in required_sections 
                               if section.lower() in readme_content.lower())
            
            readme_score = min(5, found_sections + 1)
            
            self._record_metric(
                "README Quality",
                "documentation",
                f"{found_sections}/{len(required_sections)} sections",
                5,
                readme_score,
                "PASS" if found_sections >= 3 else "WARN",
                f"Found {found_sections} of {len(required_sections)} recommended sections"
            )
        else:
            self._record_metric(
                "README Quality",
                "documentation",
                "Missing",
                5,
                0,
                "FAIL",
                "No README.md file found"
            )
            self.critical_issues.append("Missing project README.md")
        
        # Documentation coverage
        doc_files = list(self.project_root.rglob('*.md'))
        doc_dirs = ['docs', 'documentation']
        existing_doc_dirs = [d for d in doc_dirs if (self.project_root / d).exists()]
        
        doc_score = min(5, len(doc_files) // 2 + len(existing_doc_dirs))
        
        self._record_metric(
            "Documentation Coverage",
            "documentation",
            f"{len(doc_files)} files, {len(existing_doc_dirs)} dirs",
            5,
            doc_score,
            "PASS" if len(doc_files) >= 3 else "WARN",
            f"Found {len(doc_files)} documentation files and {len(existing_doc_dirs)} doc directories"
        )
    
    def generate_report(self) -> HealthReport:
        """Generate comprehensive health report."""
        end_time = time.perf_counter()
        total_execution_time = end_time - self.start_time
        
        # Calculate category scores
        category_scores = {}
        for category in self.categories:
            category_metrics = [m for m in self.metrics if m.category == category]
            total_score = sum(m.actual_score for m in category_metrics)
            max_score = sum(m.max_score for m in category_metrics)
            percentage = (total_score / max_score * 100) if max_score > 0 else 0
            
            category_scores[category] = {
                'score': total_score,
                'max_score': max_score,
                'percentage': percentage,
                'metrics_count': len(category_metrics),
                'status': 'PASS' if percentage >= 80 else 'WARN' if percentage >= 60 else 'FAIL'
            }
        
        # Calculate overall health
        total_score = sum(m.actual_score for m in self.metrics)
        max_possible_score = sum(m.max_score for m in self.metrics)
        health_percentage = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0
        
        # Determine overall status
        if health_percentage >= 90:
            overall_status = "EXCELLENT"
        elif health_percentage >= 80:
            overall_status = "GOOD"
        elif health_percentage >= 70:
            overall_status = "FAIR"
        elif health_percentage >= 60:
            overall_status = "POOR"
        else:
            overall_status = "CRITICAL"
        
        return HealthReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            execution_time=total_execution_time,
            overall_score=total_score,
            max_possible_score=max_possible_score,
            health_percentage=health_percentage,
            status=overall_status,
            categories=category_scores,
            metrics=self.metrics,
            recommendations=self.recommendations,
            critical_issues=self.critical_issues
        )
    
    def run_health_check(self) -> HealthReport:
        """Execute complete health check and return report."""
        if self.verbose:
            print("🩺 Starting comprehensive project health check...")
            print(f"📁 Project: {self.project_root}")
            print("=" * 50)
        
        # Execute all health checks
        self.check_project_structure()
        self.check_dependencies()
        self.check_testing_infrastructure()
        self.check_security_compliance()
        self.check_performance_characteristics()
        self.check_documentation_quality()
        
        # Generate and return report
        report = self.generate_report()
        
        if self.verbose:
            print("\n" + "=" * 50)
            print(f"✅ Health check completed in {report.execution_time:.2f}s")
            print(f"📊 Overall Health: {report.health_percentage:.1f}% ({report.status})")
        
        return report


def print_health_report(report: HealthReport, output_format: str = 'console') -> None:
    """Print health report in specified format."""
    if output_format == 'json':
        print(json.dumps(asdict(report), indent=2))
        return
    
    # Console format
    print("\n" + "=" * 70)
    print("🩺 MEN'S CIRCLE MANAGEMENT PLATFORM - HEALTH REPORT")
    print("=" * 70)
    print(f"📅 Generated: {report.timestamp}")
    print(f"⏱️  Execution Time: {report.execution_time:.2f} seconds")
    print(f"📊 Overall Health: {report.health_percentage:.1f}% ({report.status})")
    print(f"🎯 Score: {report.overall_score}/{report.max_possible_score}")
    
    # Category breakdown
    print("\n📋 CATEGORY BREAKDOWN:")
    print("-" * 70)
    for category, data in report.categories.items():
        status_icon = "✅" if data['status'] == 'PASS' else "⚠️ " if data['status'] == 'WARN' else "❌"
        print(f"{status_icon} {category.upper():15} {data['percentage']:6.1f}% ({data['score']}/{data['max_score']}) - {data['metrics_count']} checks")
    
    # Critical issues
    if report.critical_issues:
        print("\n🚨 CRITICAL ISSUES:")
        print("-" * 70)
        for issue in report.critical_issues:
            print(f"❌ {issue}")
    
    # Recommendations
    if report.recommendations:
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 70)
        for rec in report.recommendations:
            print(f"🔧 {rec}")
    
    print("\n" + "=" * 70)


def main():
    """Main entry point for the health check script."""
    parser = argparse.ArgumentParser(
        description="Men's Circle Management Platform - Automated Health Check",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/health-check.py                    # Basic health check
  python scripts/health-check.py --verbose          # Verbose output
  python scripts/health-check.py --format json      # JSON output
        """
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output during health check'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['console', 'json'],
        default='console',
        help='Output format (default: console)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize health checker
        checker = ProjectHealthChecker(verbose=args.verbose)
        
        # Run comprehensive health check
        report = checker.run_health_check()
        
        # Print report
        print_health_report(report, args.format)
        
        # Exit with appropriate code based on health
        if report.health_percentage >= 80:
            sys.exit(0)  # Success
        elif report.health_percentage >= 60:
            sys.exit(1)  # Warning
        else:
            sys.exit(2)  # Critical
            
    except KeyboardInterrupt:
        print("\n❌ Health check interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 