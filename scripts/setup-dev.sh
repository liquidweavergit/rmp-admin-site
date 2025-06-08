#!/bin/bash

# Men's Circle Management Platform - Development Environment Setup
# This script automates the complete setup of the development environment
# including dependencies, databases, Docker containers, and testing infrastructure.

set -e  # Exit on any error
set -u  # Exit on undefined variables

# Color codes for output formatting
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# Configuration variables
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
readonly PYTHON_VERSION="3.11"
readonly NODE_VERSION="18"
readonly POSTGRES_VERSION="15"
readonly REDIS_VERSION="7"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

log_substep() {
    echo -e "${CYAN}  → ${NC}$1"
}

# Error handling
handle_error() {
    log_error "Setup failed at line $1. Exiting..."
    exit 1
}

trap 'handle_error $LINENO' ERR

# Utility functions
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

check_python_version() {
    if command_exists python3; then
        local python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
        if [[ "$python_version" == "$PYTHON_VERSION" ]]; then
            return 0
        fi
    fi
    return 1
}

check_node_version() {
    if command_exists node; then
        local node_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        if [[ "$node_version" == "$NODE_VERSION" ]]; then
            return 0
        fi
    fi
    return 1
}

# Platform detection
detect_platform() {
    case "$(uname -s)" in
        Darwin*)
            echo "macOS"
            ;;
        Linux*)
            echo "Linux"
            ;;
        CYGWIN*|MINGW32*|MSYS*|MINGW*)
            echo "Windows"
            ;;
        *)
            echo "Unknown"
            ;;
    esac
}

# Main setup functions
print_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                                                                  ║"
    echo "║        Men's Circle Management Platform - Dev Setup             ║"
    echo "║                                                                  ║"
    echo "║  This script will set up your complete development environment  ║"
    echo "║  including Python, Node.js, Docker, databases, and testing.     ║"
    echo "║                                                                  ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
}

check_prerequisites() {
    log_step "Checking system prerequisites..."
    
    local platform=$(detect_platform)
    log_substep "Detected platform: $platform"
    
    # Check for required system tools
    local required_tools=("git" "curl" "tar" "unzip")
    for tool in "${required_tools[@]}"; do
        if ! command_exists "$tool"; then
            log_error "Required tool '$tool' is not installed. Please install it and run this script again."
            exit 1
        fi
        log_substep "✓ $tool found"
    done
    
    # Check for Docker
    if ! command_exists docker; then
        log_warning "Docker not found. Please install Docker Desktop and run this script again."
        log_info "Docker installation: https://docs.docker.com/get-docker/"
        exit 1
    fi
    log_substep "✓ Docker found"
    
    # Check for Docker Compose
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        log_warning "Docker Compose not found. Please install Docker Compose and run this script again."
        exit 1
    fi
    log_substep "✓ Docker Compose found"
    
    log_success "All prerequisites checked"
}

setup_python_environment() {
    log_step "Setting up Python environment..."
    
    # Check Python version
    if ! check_python_version; then
        log_warning "Python $PYTHON_VERSION not found. Please install Python $PYTHON_VERSION first."
        case $(detect_platform) in
            "macOS")
                log_info "Install Python via Homebrew: brew install python@$PYTHON_VERSION"
                ;;
            "Linux")
                log_info "Install Python via package manager: apt-get install python$PYTHON_VERSION python$PYTHON_VERSION-venv"
                ;;
        esac
        exit 1
    fi
    log_substep "✓ Python $PYTHON_VERSION found"
    
    # Create virtual environment
    cd "$PROJECT_ROOT"
    if [[ ! -d "venv" ]]; then
        log_substep "Creating Python virtual environment..."
        python3 -m venv venv
        log_substep "✓ Virtual environment created"
    else
        log_substep "✓ Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    log_substep "✓ Virtual environment activated"
    
    # Upgrade pip
    log_substep "Upgrading pip..."
    pip install --upgrade pip
    
    # Install backend dependencies
    if [[ -f "backend/requirements.txt" ]]; then
        log_substep "Installing backend production dependencies..."
        pip install -r backend/requirements.txt
    fi
    
    if [[ -f "backend/requirements-dev.txt" ]]; then
        log_substep "Installing backend development dependencies..."
        pip install -r backend/requirements-dev.txt
    fi
    
    log_success "Python environment setup complete"
}

setup_node_environment() {
    log_step "Setting up Node.js environment..."
    
    # Check Node.js version
    if ! check_node_version; then
        log_warning "Node.js $NODE_VERSION not found. Please install Node.js $NODE_VERSION first."
        case $(detect_platform) in
            "macOS")
                log_info "Install Node.js via Homebrew: brew install node@$NODE_VERSION"
                ;;
            "Linux")
                log_info "Install Node.js via NodeSource: https://github.com/nodesource/distributions"
                ;;
        esac
        exit 1
    fi
    log_substep "✓ Node.js $NODE_VERSION found"
    
    # Install frontend dependencies
    if [[ -f "frontend/package.json" ]]; then
        log_substep "Installing frontend dependencies..."
        cd "$PROJECT_ROOT/frontend"
        npm install
        cd "$PROJECT_ROOT"
        log_substep "✓ Frontend dependencies installed"
    else
        log_substep "⚠ frontend/package.json not found, skipping npm install"
    fi
    
    log_success "Node.js environment setup complete"
}

setup_environment_files() {
    log_step "Setting up environment configuration..."
    
    cd "$PROJECT_ROOT"
    
    # Copy .env.example to .env if it doesn't exist
    if [[ -f ".env.example" ]] && [[ ! -f ".env" ]]; then
        log_substep "Creating .env file from .env.example..."
        cp .env.example .env
        log_substep "✓ .env file created"
        log_warning "Please review and update .env file with your specific configuration"
    elif [[ ! -f ".env.example" ]]; then
        log_substep "Creating basic .env file..."
        cat > .env << 'EOF'
# Men's Circle Management Platform - Development Environment

# Database Configuration
DATABASE_URL=postgresql://postgres:dev_password@localhost:5432/mens_circles_main
CREDS_DATABASE_URL=postgresql://postgres:dev_password@localhost:5433/mens_circles_creds

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Security Keys (CHANGE THESE FOR PRODUCTION!)
JWT_SECRET_KEY=dev_jwt_secret_key_change_in_production
ENCRYPTION_KEY=dev_encryption_key_32_bytes_change_prod

# External Service Configuration (Development)
STRIPE_API_KEY=sk_test_your_stripe_test_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
SENDGRID_API_KEY=your_sendgrid_api_key_here

# OAuth Configuration (Development)
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# Application Configuration
DEBUG=true
LOG_LEVEL=DEBUG
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Development Configuration
PYTEST_CURRENT_TEST=true
TEST_DATABASE_URL=postgresql://postgres:test_password@localhost:5434/test_mens_circles_main
TEST_CREDS_DATABASE_URL=postgresql://postgres:test_password@localhost:5435/test_mens_circles_creds
EOF
        log_substep "✓ Basic .env file created"
        log_warning "Please update .env file with your actual API keys and configuration"
    else
        log_substep "✓ .env file already exists"
    fi
    
    log_success "Environment configuration setup complete"
}

setup_testing_environment() {
    log_step "Setting up testing environment..."
    
    cd "$PROJECT_ROOT"
    
    # Ensure pytest is installed
    if command_exists pytest; then
        log_substep "✓ pytest found"
    else
        log_substep "Installing pytest..."
        pip install pytest pytest-asyncio pytest-cov
    fi
    
    # Create pytest.ini if it doesn't exist
    if [[ ! -f "pytest.ini" ]]; then
        log_substep "Creating pytest.ini configuration..."
        cat > pytest.ini << 'EOF'
[tool:pytest]
minversion = 6.0
addopts = 
    -ra
    --strict-markers
    --strict-config
    --cov=backend
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    api: marks tests as API tests
    database: marks tests that require database
    redis: marks tests that require Redis
    external: marks tests that require external services
asyncio_mode = auto
filterwarnings =
    ignore::UserWarning
    ignore::DeprecationWarning
EOF
        log_substep "✓ pytest.ini created"
    else
        log_substep "✓ pytest.ini already exists"
    fi
    
    # Basic pytest validation
    log_substep "Validating pytest installation..."
    if pytest --version >/dev/null 2>&1; then
        log_substep "✓ pytest installation validated"
    else
        log_warning "pytest validation failed"
    fi
    
    log_success "Testing environment setup complete"
}

validate_setup() {
    log_step "Validating development environment setup..."
    
    cd "$PROJECT_ROOT"
    
    # Check Python environment
    if source venv/bin/activate 2>/dev/null && python --version | grep -q "$PYTHON_VERSION"; then
        log_substep "✓ Python environment validated"
    else
        log_substep "⚠ Python environment validation failed"
    fi
    
    # Check Node.js environment
    if command_exists node && node --version | grep -q "v$NODE_VERSION"; then
        log_substep "✓ Node.js environment validated"
    else
        log_substep "⚠ Node.js environment validation failed"
    fi
    
    # Check environment file
    if [[ -f ".env" ]]; then
        log_substep "✓ Environment configuration validated"
    else
        log_substep "⚠ Environment configuration validation failed"
    fi
    
    # Check testing setup
    if [[ -f "pytest.ini" ]] && command_exists pytest; then
        log_substep "✓ Testing environment validated"
    else
        log_substep "⚠ Testing environment validation failed"
    fi
    
    log_success "Development environment validation complete"
}

print_completion_message() {
    echo
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                                                                  ║"
    echo "║                    🎉 SETUP COMPLETE! 🎉                        ║"
    echo "║                                                                  ║"
    echo "║  Your Men's Circle Management Platform development environment   ║"
    echo "║  is now ready for development!                                   ║"
    echo "║                                                                  ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
    echo -e "${BLUE}Next Steps:${NC}"
    echo -e "${CYAN}1.${NC} Activate Python environment: ${YELLOW}source venv/bin/activate${NC}"
    echo -e "${CYAN}2.${NC} Review and update .env file with your API keys"
    echo -e "${CYAN}3.${NC} Run tests to verify setup: ${YELLOW}pytest tests/ -v${NC}"
    echo -e "${CYAN}4.${NC} Start development servers:"
    echo -e "   ${YELLOW}• Backend:${NC} cd backend && uvicorn app.main:app --reload"
    echo -e "   ${YELLOW}• Frontend:${NC} cd frontend && npm run dev"
    echo -e "${CYAN}5.${NC} Check Docker services: ${YELLOW}docker-compose ps${NC}"
    echo
    echo -e "${BLUE}Important Files Created/Updated:${NC}"
    echo -e "${CYAN}•${NC} .env - Environment variables"
    echo -e "${CYAN}•${NC} pytest.ini - Testing configuration"
    echo -e "${CYAN}•${NC} venv/ - Python virtual environment"
    echo
    echo -e "${BLUE}Useful Commands:${NC}"
    echo -e "${CYAN}•${NC} Run all tests: ${YELLOW}pytest${NC}"
    echo -e "${CYAN}•${NC} Run unit tests: ${YELLOW}pytest tests/ -v${NC}"
    echo -e "${CYAN}•${NC} Format code: ${YELLOW}black backend/${NC}"
    echo
    echo -e "${GREEN}Happy coding! 🚀${NC}"
    echo
}

# Main execution
main() {
    print_banner
    
    # Run setup steps
    check_prerequisites
    setup_python_environment
    setup_node_environment
    setup_environment_files
    setup_testing_environment
    validate_setup
    
    print_completion_message
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Men's Circle Management Platform - Development Setup Script"
        echo
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --validate     Only run validation checks"
        echo
        echo "This script will:"
        echo "• Check system prerequisites"
        echo "• Set up Python virtual environment and dependencies"
        echo "• Set up Node.js environment and dependencies"
        echo "• Create environment configuration files"
        echo "• Configure testing environment"
        echo "• Validate the complete setup"
        echo
        exit 0
        ;;
    --validate)
        log_info "Running validation checks only"
        validate_setup
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac 