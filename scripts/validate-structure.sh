#!/bin/bash

# Men's Circle Management Platform - Project Structure Validation Script
# File: scripts/validate-structure-final.sh
# Purpose: Comprehensive validation of project directory structure and requirements

set -e

# Color codes for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Global counters
PASSED_CHECKS=0
FAILED_CHECKS=0
TOTAL_CHECKS=0

# Auto-detect project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}[INFO]${NC} Men's Circle Management Platform - Structure Validation"
echo -e "${BLUE}[INFO]${NC} Project root: $PROJECT_ROOT"
echo

# Test tracking functions
run_test() {
    local description="$1"
    local test_command="$2"
    
    ((TOTAL_CHECKS++))
    
    if eval "$test_command" >/dev/null 2>&1; then
        ((PASSED_CHECKS++))
        echo -e "${GREEN}[PASS]${NC} $description"
        return 0
    else
        ((FAILED_CHECKS++))
        echo -e "${RED}[FAIL]${NC} $description"
        return 1
    fi
}

# Core directory structure validation
echo -e "${BLUE}[INFO]${NC} Validating core directory structure..."

run_test "Backend directory exists" "[[ -d '$PROJECT_ROOT/backend' ]]"
run_test "Frontend directory exists" "[[ -d '$PROJECT_ROOT/frontend' ]]"
run_test "Docker directory exists" "[[ -d '$PROJECT_ROOT/docker' ]]"
run_test "Tests directory exists" "[[ -d '$PROJECT_ROOT/tests' ]]"
run_test "Docs directory exists" "[[ -d '$PROJECT_ROOT/docs' ]]"
run_test "Scripts directory exists" "[[ -d '$PROJECT_ROOT/scripts' ]]"
run_test "GitHub workflows directory exists" "[[ -d '$PROJECT_ROOT/.github/workflows' ]]"

# Required files validation
echo -e "${BLUE}[INFO]${NC} Validating required files..."

run_test "Backend __init__.py exists" "[[ -f '$PROJECT_ROOT/backend/__init__.py' ]]"
run_test "Frontend package.json exists" "[[ -f '$PROJECT_ROOT/frontend/package.json' ]]"
run_test "Docker README.md exists" "[[ -f '$PROJECT_ROOT/docker/README.md' ]]"
run_test "Tests conftest.py exists" "[[ -f '$PROJECT_ROOT/tests/conftest.py' ]]"
run_test "Tests structure directory exists" "[[ -d '$PROJECT_ROOT/tests/structure' ]]"
run_test "Docs README.md exists" "[[ -f '$PROJECT_ROOT/docs/README.md' ]]"
run_test "Scripts setup-dev.sh exists" "[[ -f '$PROJECT_ROOT/scripts/setup-dev.sh' ]]"
run_test "Project .gitignore exists" "[[ -f '$PROJECT_ROOT/.gitignore' ]]"
run_test "Project README.md exists" "[[ -f '$PROJECT_ROOT/README.md' ]]"

# GitHub workflow files
echo -e "${BLUE}[INFO]${NC} Validating GitHub Actions workflows..."

run_test "CI workflow exists" "[[ -f '$PROJECT_ROOT/.github/workflows/ci.yml' ]]"
run_test "Test workflow exists" "[[ -f '$PROJECT_ROOT/.github/workflows/test.yml' ]]"
run_test "Deploy workflow exists" "[[ -f '$PROJECT_ROOT/.github/workflows/deploy.yml' ]]"

# File permissions validation
echo -e "${BLUE}[INFO]${NC} Validating file permissions..."

run_test "Scripts directory is accessible" "[[ -r '$PROJECT_ROOT/scripts' && -x '$PROJECT_ROOT/scripts' ]]"
run_test "Setup script is executable" "[[ -x '$PROJECT_ROOT/scripts/setup-dev.sh' ]]"

# Content validation for critical files
echo -e "${BLUE}[INFO]${NC} Validating file contents..."

run_test ".gitignore contains *.pyc pattern" "grep -q '*.pyc' '$PROJECT_ROOT/.gitignore'"
run_test ".gitignore contains __pycache__/ pattern" "grep -q '__pycache__/' '$PROJECT_ROOT/.gitignore'"
run_test ".gitignore contains node_modules/ pattern" "grep -q 'node_modules/' '$PROJECT_ROOT/.gitignore'"
run_test ".gitignore contains .env pattern" "grep -q '.env' '$PROJECT_ROOT/.gitignore'"
run_test ".gitignore contains *.log pattern" "grep -q '*.log' '$PROJECT_ROOT/.gitignore'"

run_test "README.md contains platform branding" "grep -q \"Men's Circle Management Platform\" '$PROJECT_ROOT/README.md'"
run_test "README.md contains Setup section" "grep -q 'Setup' '$PROJECT_ROOT/README.md'"
run_test "README.md contains Development section" "grep -q 'Development' '$PROJECT_ROOT/README.md'"

# Workflow content validation
run_test "CI workflow has proper structure" "grep -q 'name:' '$PROJECT_ROOT/.github/workflows/ci.yml' && grep -q 'on:' '$PROJECT_ROOT/.github/workflows/ci.yml' && grep -q 'jobs:' '$PROJECT_ROOT/.github/workflows/ci.yml'"
run_test "Test workflow has proper structure" "grep -q 'name:' '$PROJECT_ROOT/.github/workflows/test.yml' && grep -q 'on:' '$PROJECT_ROOT/.github/workflows/test.yml' && grep -q 'jobs:' '$PROJECT_ROOT/.github/workflows/test.yml'"
run_test "Deploy workflow has proper structure" "grep -q 'name:' '$PROJECT_ROOT/.github/workflows/deploy.yml' && grep -q 'on:' '$PROJECT_ROOT/.github/workflows/deploy.yml' && grep -q 'jobs:' '$PROJECT_ROOT/.github/workflows/deploy.yml'"

# Summary
echo
echo "========================================"
echo "   VALIDATION SUMMARY"
echo "========================================"
echo "Total checks performed: $TOTAL_CHECKS"
echo -e "Passed: ${GREEN}$PASSED_CHECKS${NC}"
echo -e "Failed: ${RED}$FAILED_CHECKS${NC}"
echo

if [[ $FAILED_CHECKS -eq 0 ]]; then
    echo -e "${GREEN}✅ ALL VALIDATIONS PASSED!${NC}"
    echo "The men's circle management platform project structure is complete and valid."
    exit 0
else
    echo -e "${RED}❌ VALIDATION FAILURES DETECTED!${NC}"
    echo "Please address the failed checks above before proceeding."
    exit 1
fi 