# Men's Circle Management Platform - Launch-Focused Punchlist

## COMPLETED TASKS (DEPRECATED - Infrastructure Setup)

### Project Structure (DEPRECATED - COMPLETED)

- [x] **DEPRECATED** 1.1.2 Write test for project directory structure validation (tests/structure/test_directories.py)
- [x] **DEPRECATED** 1.1.3 Create project root directory 'mens-circle-platform'
- [x] **DEPRECATED** 1.1.4 Create backend/ subdirectory with **init**.py
- [x] **DEPRECATED** 1.1.5 Create frontend/ subdirectory with package.json placeholder
- [x] **DEPRECATED** 1.1.6 Create docker/ subdirectory with README.md
- [x] **DEPRECATED** 1.1.7 Create tests/ subdirectory with conftest.py and structure/ subfolder
- [x] **DEPRECATED** 1.1.8 Create docs/ subdirectory with initial README.md
- [x] **DEPRECATED** 1.1.9 Create scripts/ subdirectory with setup-dev.sh template
- [x] **DEPRECATED** 1.1.10 Create .github/workflows/ directory for CI/CD (already exists, add workflow files)
- [x] **DEPRECATED** 1.1.11 Create comprehensive .gitignore for Python/Node.js/Docker
- [x] **DEPRECATED** 1.1.12 Create project README.md with setup instructions
- [x] **DEPRECATED** 1.1.13 Write validation script (scripts/validate-structure.sh) to verify directory structure
- [x] **DEPRECATED** 1.1.14 Run structure tests - verify all pass
- [x] **DEPRECATED** 1.1.15 Execute validation script - confirm no errors
- [x] **DEPRECATED** 1.1.16 Create pytest.ini configuration in project root for global test settings
- [x] **DEPRECATED** 1.1.17 Write integration test for complete project structure (tests/integration/test_project_integration.py)
- [x] **DEPRECATED** 1.1.18 Test that all created directories have proper permissions
- [x] **DEPRECATED** 1.1.19 Validate that conftest.py fixtures load properly across all test modules
- [x] **DEPRECATED** 1.1.20 Create .editorconfig for consistent coding standards
- [x] **DEPRECATED** 1.1.21 Test project structure compatibility with Docker volume mounts

---

## LAUNCH-CRITICAL TASKS (MVP)

### Phase 1: Core Foundation (Weeks 1-2)

#### 1. Environment & Docker Setup [Priority: Critical]

- [ ] 1.1 Set up basic development environment
- [ ] 1.2 Create .env.example with required variables (DATABASE_URL, REDIS_URL, JWT_SECRET, STRIPE_API_KEY)
- [ ] 1.3 Create docker-compose.yml with PostgreSQL, Redis, backend, and frontend services
- [ ] 1.4 Create simple Dockerfiles for backend (Python 3.11) and frontend (Node 18)
- [ ] 1.5 Test full stack starts with `docker-compose up`

#### 2. Backend Foundation [Priority: Critical]

- [ ] 2.1 Set up FastAPI application structure in backend/app/
- [ ] 2.2 Create requirements.txt with core dependencies: FastAPI, SQLAlchemy, psycopg2, redis, stripe, python-jose
- [ ] 2.3 Configure SQLAlchemy with async support for main and credentials databases
- [ ] 2.4 Set up Alembic for database migrations
- [ ] 2.5 Create health check endpoint (`/health`)
- [ ] 2.6 Add CORS middleware for frontend access

#### 3. Frontend Foundation [Priority: Critical]

- [ ] 3.1 Set up React TypeScript project with Vite
- [ ] 3.2 Configure Material-UI theme and basic components
- [ ] 3.3 Set up Redux Toolkit with RTK Query
- [ ] 3.4 Create basic routing with react-router-dom
- [ ] 3.5 Create responsive layout components

### Phase 2: Authentication System (Weeks 3-4)

#### 4. User Authentication [Priority: Critical]

- [ ] 4.1 Create User and Credential models (separate databases as per tech spec)
- [ ] 4.2 Implement JWT-based authentication service
- [ ] 4.3 Create registration API endpoint with email validation
- [ ] 4.4 Create login API endpoint with password hashing (bcrypt)
- [ ] 4.5 Add phone verification with SMS (Twilio integration)
- [ ] 4.6 Implement Google OAuth integration
- [ ] 4.7 Create password reset functionality

#### 5. Role-Based Access Control [Priority: Critical]

- [ ] 5.1 Define six user roles as per product brief: Member, Facilitator, PTM, Manager, Director, Admin
- [ ] 5.2 Create Role and Permission models with many-to-many relationships
- [ ] 5.3 Implement permission checking middleware
- [ ] 5.4 Create role assignment and context switching
- [ ] 5.5 Add audit logging for permission changes

#### 6. Frontend Authentication [Priority: Critical]

- [ ] 6.1 Create login/registration forms with validation
- [ ] 6.2 Implement Redux authentication state management
- [ ] 6.3 Create protected routes based on user roles
- [ ] 6.4 Add phone verification UI workflow
- [ ] 6.5 Implement Google OAuth button and flow

### Phase 3: Circle Management (Weeks 5-6)

#### 7. Circle Core Features [Priority: Critical]

- [ ] 7.1 Create Circle model with capacity constraints (2-10 members)
- [ ] 7.2 Create CircleMembership model with payment status tracking
- [ ] 7.3 Implement circle creation API with facilitator assignment
- [ ] 7.4 Create member management API (add/remove/transfer)
- [ ] 7.5 Add meeting tracking and attendance recording
- [ ] 7.6 Implement circle search and filtering

#### 8. Circle Frontend [Priority: Critical]

- [ ] 8.1 Create circle dashboard for facilitators
- [ ] 8.2 Build member management interface
- [ ] 8.3 Create circle member view with meeting history
- [ ] 8.4 Add circle creation and editing forms
- [ ] 8.5 Implement member transfer requests

### Phase 4: Payment Integration (Weeks 7-8)

#### 9. Stripe Payment System [Priority: Critical]

- [ ] 9.1 Set up Stripe customer creation linked to users
- [ ] 9.2 Implement subscription management for circle dues
- [ ] 9.3 Create webhook endpoints for payment events
- [ ] 9.4 Add payment plan support for events
- [ ] 9.5 Implement manual payment intervention workflow
- [ ] 9.6 Create payment status tracking and notifications

#### 10. Frontend Payment Integration [Priority: Critical]

- [ ] 10.1 Integrate Stripe Elements for secure payment collection
- [ ] 10.2 Create subscription management interface
- [ ] 10.3 Build payment history and invoice views
- [ ] 10.4 Add payment method management
- [ ] 10.5 Implement payment failure handling with retry options

### Phase 5: Event Management (Weeks 9-10)

#### 11. Event System [Priority: Critical]

- [ ] 11.1 Create flexible Event model supporting various event types
- [ ] 11.2 Implement event registration with capacity management
- [ ] 11.3 Add waitlist functionality with automatic promotion
- [ ] 11.4 Create staff assignment system (facilitators, PTMs, care team)
- [ ] 11.5 Implement event requirement templates (age, experience, etc.)
- [ ] 11.6 Add event cancellation and refund processing

#### 12. Event Frontend [Priority: Critical]

- [ ] 12.1 Create event listing and filtering interface
- [ ] 12.2 Build event registration flow with requirement checking
- [ ] 12.3 Create event management dashboard for staff
- [ ] 12.4 Add waitlist management interface
- [ ] 12.5 Implement event creation and editing forms

### Phase 6: Communication System (Weeks 11-12)

#### 13. Messaging Infrastructure [Priority: High]

- [ ] 13.1 Create Message model with hierarchical routing
- [ ] 13.2 Implement WebSocket connections for real-time messaging
- [ ] 13.3 Add role-based message broadcasting
- [ ] 13.4 Create notification system with email/SMS integration
- [ ] 13.5 Implement message threading and replies

#### 14. Communication Frontend [Priority: High]

- [ ] 14.1 Create messaging interface with real-time updates
- [ ] 14.2 Build notification center and preferences
- [ ] 14.3 Add broadcast messaging for leadership roles
- [ ] 14.4 Implement message search and filtering

### Phase 7: Launch Preparation (Weeks 13-14)

#### 15. Security & Compliance [Priority: Critical]

- [ ] 15.1 Implement field-level encryption for sensitive data
- [ ] 15.2 Add rate limiting and security headers
- [ ] 15.3 Configure HTTPS and SSL certificates
- [ ] 15.4 Implement GDPR compliance features (data export/deletion)
- [ ] 15.5 Add security audit logging

#### 16. Testing & Quality Assurance [Priority: Critical]

- [ ] 16.1 Write unit tests for core business logic (80% coverage minimum)
- [ ] 16.2 Create integration tests for API endpoints
- [ ] 16.3 Add end-to-end tests for critical user flows
- [ ] 16.4 Perform load testing for performance requirements (<200ms API response)
- [ ] 16.5 Security penetration testing

#### 17. Deployment & Monitoring [Priority: Critical]

- [ ] 17.1 Set up production Docker configuration
- [ ] 17.2 Configure CI/CD pipeline with GitHub Actions
- [ ] 17.3 Set up basic monitoring (health checks, error tracking)
- [ ] 17.4 Configure automated database backups
- [ ] 17.5 Create deployment runbook and rollback procedures

#### 18. Launch Checklist [Priority: Critical]

- [ ] 18.1 User acceptance testing with stakeholders
- [ ] 18.2 Data migration preparation and validation
- [ ] 18.3 User training documentation and sessions
- [ ] 18.4 Performance optimization and final testing
- [ ] 18.5 Go-live execution and post-launch monitoring

---

## POST-LAUNCH ENHANCEMENTS (Future Phases)

### Phase 8: Mobile & PWA Features [Priority: Medium]

- [ ] 19.1 Implement Progressive Web App features
- [ ] 19.2 Add offline functionality for critical features
- [ ] 19.3 Optimize mobile responsiveness
- [ ] 19.4 Add push notifications

### Phase 9: Advanced Features [Priority: Low]

- [ ] 20.1 Advanced reporting and analytics
- [ ] 20.2 Goal tracking and progress monitoring
- [ ] 20.3 Archive system for historical data
- [ ] 20.4 Advanced search and filtering capabilities
- [ ] 20.5 Integration with external calendar systems

---

## SUCCESS METRICS (from Product Brief)

- **User Adoption**: 90% active usage within 60 days of launch
- **Payment Success Rate**: Increase on-time payments by 40%
- **Administrative Time Savings**: Reduce manual tasks by 70%
- **System Reliability**: 99.9% uptime with <200ms response times
- **Member Engagement**: 80% weekly goal completion rate

## CORE FUNCTIONALITY PRESERVED

✅ **Six user roles with flexible, additive permissions**
✅ **Circle management for 2-10 member groups**
✅ **Flexible event system (movie nights to multi-day retreats)**
✅ **Stripe payment integration with manual intervention**
✅ **Secure messaging with hierarchical routing**
✅ **Mobile-first PWA design**
✅ **Separate credential storage with encryption**
✅ **Real-time features via WebSocket**
✅ **GDPR compliance and data privacy**
✅ **Test-driven development approach**

## ELIMINATED OVER-ENGINEERING

❌ **Excessive validation layers** (5+ structure validation approaches → 1 simple validation)
❌ **Premature optimization** (performance testing → wait for real load)
❌ **Complex CI/CD infrastructure** (25 docker test items → basic CI/CD)
❌ **Over-specified testing** (770+ tasks → focus on business logic)
❌ **Analysis paralysis items** (follow-up enhancement tasks → post-launch)

**Total Tasks Reduced**: From 770+ to ~85 focused, launch-critical tasks
**Timeline**: 14 weeks instead of 20-22 weeks
**Focus**: Building working software that delivers business value

**TDD Approach: Test data persistence and cleanup in containers**

- [ ] 1.2.2.1 Write tests for test data management (tests/docker/test_data_management.py)
- [ ] 1.2.2.2 Create test database initialization scripts in docker/init-test-db.sql
- [ ] 1.2.2.3 Test database seeding for consistent test environments
- [ ] 1.2.2.4 Create factory data fixtures that work in containers
- [ ] 1.2.2.5 Test data cleanup between test container runs
- [ ] 1.2.2.6 Verify test database state isolation
- [ ] 1.2.2.7 Test fixture loading in containerized pytest
- [ ] 1.2.2.8 Create volume mounts for test artifacts and reports
- [ ] 1.2.2.9 Test coverage report generation in containers
- [ ] 1.2.2.10 Verify test logs are accessible from host system

### 1.2.3 Container Development Workflow [Priority: High]

**TDD Approach: Test development workflow efficiency in containerized environment**

- [ ] 1.2.3.1 Write tests for development workflow performance (tests/docker/test_dev_workflow.py)
- [ ] 1.2.3.2 Test hot reload performance with volume mounts
- [ ] 1.2.3.3 Create docker-compose.dev.yml for optimized development
- [ ] 1.2.3.4 Test file synchronization between host and containers
- [ ] 1.2.3.5 Validate debugging capabilities in containerized environment
- [ ] 1.2.3.6 Test IDE integration with containerized development
- [ ] 1.2.3.7 Create development workflow documentation
- [ ] 1.2.3.8 Test container startup time optimization
- [ ] 1.2.3.9 Validate resource usage efficiency
- [ ] 1.2.3.10 Test multi-platform development support (Intel/ARM)

### 1.3 Environment Configuration [Priority: Critical]

**TDD Approach: Test environment variable loading and validation before use**

- [ ] 1.3.1 Write tests for environment configuration validation (tests/config/test_env_config.py)
- [ ] 1.3.2 Create .env.example with all required environment variables
- [ ] 1.3.3 Add DATABASE_URL for main PostgreSQL database connection
- [ ] 1.3.4 Add CREDS_DATABASE_URL for credentials database (separate instance)
- [ ] 1.3.5 Add REDIS_URL for cache and session storage
- [ ] 1.3.6 Add JWT_SECRET_KEY with secure random generation example
- [ ] 1.3.7 Add ENCRYPTION_KEY for field-level encryption (32-byte base64)
- [ ] 1.3.8 Add STRIPE_API_KEY placeholder with development/production notes
- [ ] 1.3.9 Add STRIPE_WEBHOOK_SECRET placeholder for payment webhooks
- [ ] 1.3.10 Add TWILIO_ACCOUNT_SID placeholder for SMS functionality
- [ ] 1.3.11 Add TWILIO_AUTH_TOKEN placeholder for SMS authentication
- [ ] 1.3.12 Add SENDGRID_API_KEY placeholder for email delivery
- [ ] 1.3.13 Add GOOGLE_CLIENT_ID placeholder for OAuth integration
- [ ] 1.3.14 Add GOOGLE_CLIENT_SECRET placeholder for OAuth
- [ ] 1.3.15 Add CORS_ORIGINS for frontend domain whitelist
- [ ] 1.3.16 Add DEBUG flag for development/production mode
- [ ] 1.3.17 Add LOG_LEVEL configuration (DEBUG, INFO, WARNING, ERROR)
- [ ] 1.3.18 Create scripts/generate-secrets.sh for secure key generation
- [ ] 1.3.19 Copy .env.example to .env with generated values
- [ ] 1.3.20 Test environment variable loading in both backend and Docker
- [ ] 1.3.21 Verify sensitive variables are properly excluded from git
- [ ] 1.3.22 Test configuration validation catches missing required variables

## 2. Backend Foundation [Priority: Critical]

### 2.1 Python Project Setup [Priority: Critical]

**TDD Approach: Test dependency installation and compatibility before proceeding**

- [ ] 2.1.1 Write tests for Python environment setup (tests/backend/test_dependencies.py)
- [ ] 2.1.2 Create backend/requirements.txt with core production dependencies
- [ ] 2.1.3 Add FastAPI==0.104.1 (async web framework)
- [ ] 2.1.4 Add SQLAlchemy==2.0.23 (async ORM with type hints)
- [ ] 2.1.5 Add alembic==1.12.1 (database migrations)
- [ ] 2.1.6 Add psycopg2-binary==2.9.9 (PostgreSQL async adapter)
- [ ] 2.1.7 Add redis==5.0.1 (cache and session storage)
- [ ] 2.1.8 Add celery==5.3.4 (background task processing)
- [ ] 2.1.9 Add python-jose[cryptography]==3.3.0 (JWT token handling)
- [ ] 2.1.10 Add passlib[bcrypt]==1.7.4 (password hashing)
- [ ] 2.1.11 Add python-multipart==0.0.6 (form data parsing)
- [ ] 2.1.12 Add email-validator==2.1.0 (email validation)
- [ ] 2.1.13 Add stripe==7.5.0 (payment processing)
- [ ] 2.1.14 Add twilio==8.10.0 (SMS notifications)
- [ ] 2.1.15 Add sendgrid==6.11.0 (email delivery)
- [ ] 2.1.16 Add uvicorn[standard]==0.24.0 (ASGI server)
- [ ] 2.1.17 Add pydantic[email]==2.5.0 (data validation)
- [ ] 2.1.18 Test production requirements installation
- [ ] 2.1.19 Create backend/requirements-dev.txt with development/testing dependencies
- [ ] 2.1.20 Add pytest==7.4.3 (testing framework)
- [ ] 2.1.21 Add pytest-asyncio==0.21.1 (async test support)
- [ ] 2.1.22 Add pytest-cov==4.1.0 (coverage reporting)
- [ ] 2.1.23 Add factory-boy==3.3.0 (test data generation)
- [ ] 2.1.24 Add black==23.11.0 (code formatting)
- [ ] 2.1.25 Add isort==5.12.0 (import sorting)
- [ ] 2.1.26 Add mypy==1.7.1 (type checking)
- [ ] 2.1.27 Add flake8==6.1.0 (linting)
- [ ] 2.1.28 Add pre-commit==3.6.0 (git hooks)
- [ ] 2.1.29 Test development requirements installation
- [ ] 2.1.30 Verify all dependencies are compatible and importable

### 2.2 FastAPI Application Structure [Priority: Critical]

**TDD Approach: Test application structure and endpoints before expanding functionality**

- [ ] 2.2.1 Write tests for FastAPI application startup (tests/backend/test_app_structure.py)
- [ ] 2.2.2 Create backend/app/**init**.py (empty package file)
- [ ] 2.2.3 Create backend/app/main.py with FastAPI() instance and metadata
- [ ] 2.2.4 Test FastAPI app instantiation and basic properties
- [ ] 2.2.5 Create backend/app/core/**init**.py
- [ ] 2.2.6 Create backend/app/core/config.py with Pydantic Settings class
- [ ] 2.2.7 Add environment variable validation and type hints to Settings
- [ ] 2.2.8 Test configuration loading and validation
- [ ] 2.2.9 Create backend/app/api/**init**.py
- [ ] 2.2.10 Create backend/app/api/v1/**init**.py
- [ ] 2.2.11 Create backend/app/models/**init**.py
- [ ] 2.2.12 Create backend/app/schemas/**init**.py
- [ ] 2.2.13 Create backend/app/services/**init**.py
- [ ] 2.2.14 Create backend/app/repositories/**init**.py
- [ ] 2.2.15 Write tests for health check endpoint (tests/backend/test_health.py)
- [ ] 2.2.16 Add basic health check endpoint to main.py (/health)
- [ ] 2.2.17 Test health endpoint returns correct status and response time
- [ ] 2.2.18 Add CORS middleware configuration to main.py with proper origins
- [ ] 2.2.19 Add security headers middleware (X-Frame-Options, etc.)
- [ ] 2.2.20 Test CORS configuration allows frontend requests
- [ ] 2.2.21 Start FastAPI app with uvicorn and verify startup logs
- [ ] 2.2.22 Test health endpoint via HTTP GET request
- [ ] 2.2.23 Verify API documentation available at /docs
- [ ] 2.2.24 Verify OpenAPI schema available at /openapi.json
- [ ] 2.2.25 Test application shutdown gracefully handles connections

### 2.3 Database Configuration [Priority: Critical]

- [ ] 2.3.1 Create backend/app/core/database.py
- [ ] 2.3.2 Define async SQLAlchemy engine for main database
- [ ] 2.3.3 Define async SQLAlchemy engine for credentials database
- [ ] 2.3.4 Create AsyncSession factory
- [ ] 2.3.5 Create get_db dependency function
- [ ] 2.3.6 Create backend/alembic.ini configuration
- [ ] 2.3.7 Create backend/alembic/env.py with multi-database support
- [ ] 2.3.8 Create backend/app/models/base.py with Base declarative class
- [ ] 2.3.9 Test database connection with health check
- [ ] 2.3.10 Verify both database connections work

### 2.4 Testing Infrastructure [Priority: Critical]

- [ ] 2.4.1 Create backend/tests/**init**.py
- [ ] 2.4.2 Create backend/tests/conftest.py with pytest fixtures
- [ ] 2.4.3 Create async test database fixture
- [ ] 2.4.4 Create async client fixture for API testing
- [ ] 2.4.5 Create backend/pytest.ini with configuration
- [ ] 2.4.6 Set minimum coverage to 80% in pytest.ini
- [ ] 2.4.7 Create backend/tests/unit/**init**.py
- [ ] 2.4.8 Create backend/tests/integration/**init**.py
- [ ] 2.4.9 Create backend/tests/factories/**init**.py
- [ ] 2.4.10 Write test for health check endpoint
- [ ] 2.4.11 Verify pytest runs successfully
- [ ] 2.4.12 Verify coverage report generates

### 2.5 Advanced Testing Infrastructure [Priority: High]

**TDD Approach: Enhance testing capabilities for comprehensive platform coverage**

- [ ] 2.5.1 Write tests for test infrastructure quality (tests/meta/test_testing_infrastructure.py)
- [ ] 2.5.2 Create backend/tests/performance/ directory for performance testing
- [ ] 2.5.3 Add pytest-benchmark for performance regression testing
- [ ] 2.5.4 Create backend/tests/security/ directory for security testing
- [ ] 2.5.5 Add pytest-xdist for parallel test execution
- [ ] 2.5.6 Create test data management utilities (tests/utils/data_manager.py)
- [ ] 2.5.7 Add mutation testing with mutmut for test quality validation
- [ ] 2.5.8 Create backend/tests/e2e/ directory for end-to-end testing
- [ ] 2.5.9 Implement test reporting dashboard integration
- [ ] 2.5.10 Add property-based testing with Hypothesis
- [ ] 2.5.11 Create test environment isolation validators
- [ ] 2.5.12 Add API contract testing with pact-python
- [ ] 2.5.13 Implement test data factory validation
- [ ] 2.5.14 Create performance baseline tests for response times
- [ ] 2.5.15 Add database query performance testing

## 3. Frontend Foundation [Priority: Critical]

### 3.1 React Project Setup [Priority: Critical]

- [ ] 3.1.1 Create frontend/package.json with name and version
- [ ] 3.1.2 Add React 18.2.0 dependencies to package.json
- [ ] 3.1.3 Add TypeScript 5.3.2 to package.json
- [ ] 3.1.4 Add Vite 5.0.4 to package.json
- [ ] 3.1.5 Add @reduxjs/toolkit 2.0.1 to package.json
- [ ] 3.1.6 Add react-redux 9.0.4 to package.json
- [ ] 3.1.7 Add @mui/material 5.14.20 to package.json
- [ ] 3.1.8 Add react-router-dom 6.20.1 to package.json
- [ ] 3.1.9 Create frontend/tsconfig.json with strict mode
- [ ] 3.1.10 Create frontend/vite.config.ts
- [ ] 3.1.11 Create frontend/index.html entry point
- [ ] 3.1.12 Create frontend/.eslintrc.json configuration
- [ ] 3.1.13 Create frontend/.prettierrc configuration
- [ ] 3.1.14 Run npm install to verify dependencies
- [ ] 3.1.15 Test npm run dev starts development server

### 3.2 React Application Structure [Priority: Critical]

- [ ] 3.2.1 Create frontend/src/main.tsx entry point
- [ ] 3.2.2 Create frontend/src/App.tsx root component
- [ ] 3.2.3 Create frontend/src/components/ directory
- [ ] 3.2.4 Create frontend/src/features/ directory
- [ ] 3.2.5 Create frontend/src/services/ directory
- [ ] 3.2.6 Create frontend/src/hooks/ directory
- [ ] 3.2.7 Create frontend/src/utils/ directory
- [ ] 3.2.8 Create frontend/src/types/ directory
- [ ] 3.2.9 Create frontend/src/store/ directory
- [ ] 3.2.10 Create frontend/src/store/index.ts with Redux store
- [ ] 3.2.11 Wrap App with Redux Provider
- [ ] 3.2.12 Add basic routing with react-router-dom
- [ ] 3.2.13 Create frontend/src/theme.ts with MUI theme
- [ ] 3.2.14 Verify app renders without errors
- [ ] 3.2.15 Test hot module replacement works

### 3.3 Frontend Testing Setup [Priority: Critical]

- [ ] 3.3.1 Add jest 29.7.0 to package.json devDependencies
- [ ] 3.3.2 Add @testing-library/react 14.1.2 to devDependencies
- [ ] 3.3.3 Add @testing-library/jest-dom 6.1.5 to devDependencies
- [ ] 3.3.4 Add @testing-library/user-event 14.5.1 to devDependencies
- [ ] 3.3.5 Create frontend/jest.config.js
- [ ] 3.3.6 Create frontend/src/setupTests.ts
- [ ] 3.3.7 Create frontend/src/**tests**/ directory
- [ ] 3.3.8 Write test for App component rendering
- [ ] 3.3.9 Verify npm test runs successfully
- [ ] 3.3.10 Set up coverage threshold at 80%

## 4. Authentication System [Priority: Critical]

### 4.1 Authentication Models [Priority: Critical]

**TDD Approach: Test model validation and database operations before implementation**

- [ ] 4.1.1 Write comprehensive tests for Credential model (tests/models/test_credential.py)
- [ ] 4.1.2 Test email validation and uniqueness constraints
- [ ] 4.1.3 Test password hashing and verification
- [ ] 4.1.4 Test phone number validation and formatting
- [ ] 4.1.5 Create backend/app/models/auth.py with SQLAlchemy models
- [ ] 4.1.6 Define Credential model with email field (unique, indexed)
- [ ] 4.1.7 Add password_hash field with proper length constraints
- [ ] 4.1.8 Add phone field with international format validation
- [ ] 4.1.9 Add phone_verified boolean field (default False)
- [ ] 4.1.10 Add google_id field for OAuth integration (unique, nullable)
- [ ] 4.1.11 Add mfa_secret field for two-factor authentication
- [ ] 4.1.12 Add is_active boolean field for account status
- [ ] 4.1.13 Add email_verified boolean field (default False)
- [ ] 4.1.14 Add created_at and updated_at timestamp fields
- [ ] 4.1.15 Add last_login timestamp field
- [ ] 4.1.16 Implement model validation methods and constraints
- [ ] 4.1.17 Create credential table migration with proper indexes
- [ ] 4.1.18 Run migration on credentials database
- [ ] 4.1.19 Test credential creation with valid data
- [ ] 4.1.20 Test constraint violations (duplicate email, etc.)
- [ ] 4.1.21 Verify credential table schema matches model definition
- [ ] 4.1.22 Test credential model CRUD operations

### 4.2 User Profile Models [Priority: Critical]

- [ ] 4.2.1 Write test for Profile model
- [ ] 4.2.2 Create backend/app/models/user.py
- [ ] 4.2.3 Define Profile model with credential_id foreign key
- [ ] 4.2.4 Add first_name and last_name fields
- [ ] 4.2.5 Add display_name field
- [ ] 4.2.6 Add address as JSONB field
- [ ] 4.2.7 Add location as PostGIS geography point
- [ ] 4.2.8 Add notification_preferences as JSONB
- [ ] 4.2.9 Create profile table migration
- [ ] 4.2.10 Run migration and verify table structure

### 4.3 JWT Authentication Service [Priority: Critical]

- [ ] 4.3.1 Write tests for password hashing functions
- [ ] 4.3.2 Create backend/app/core/security.py
- [ ] 4.3.3 Implement get_password_hash function
- [ ] 4.3.4 Implement verify_password function
- [ ] 4.3.5 Write tests for JWT token creation
- [ ] 4.3.6 Implement create_access_token function
- [ ] 4.3.7 Implement create_refresh_token function
- [ ] 4.3.8 Write tests for token validation
- [ ] 4.3.9 Implement decode_token function
- [ ] 4.3.10 Create get_current_user dependency
- [ ] 4.3.11 Test token expiration handling
- [ ] 4.3.12 Verify all security tests pass

### 4.4 Authentication API Endpoints [Priority: Critical]

- [ ] 4.4.1 Write tests for user registration endpoint
- [ ] 4.4.2 Create backend/app/api/v1/auth.py router
- [ ] 4.4.3 Create UserCreate schema in schemas/auth.py
- [ ] 4.4.4 Create UserResponse schema
- [ ] 4.4.5 Implement POST /register endpoint
- [ ] 4.4.6 Write tests for login endpoint
- [ ] 4.4.7 Create LoginRequest schema
- [ ] 4.4.8 Create TokenResponse schema
- [ ] 4.4.9 Implement POST /login endpoint
- [ ] 4.4.10 Write tests for token refresh
- [ ] 4.4.11 Implement POST /refresh endpoint
- [ ] 4.4.12 Write tests for logout
- [ ] 4.4.13 Implement POST /logout endpoint
- [ ] 4.4.14 Add auth router to main app
- [ ] 4.4.15 Verify all auth endpoints work via API docs

### 4.5 Frontend Authentication [Priority: High]

- [ ] 4.5.1 Write tests for auth slice
- [ ] 4.5.2 Create frontend/src/features/auth/authSlice.ts
- [ ] 4.5.3 Define AuthState interface
- [ ] 4.5.4 Create login async thunk
- [ ] 4.5.5 Create register async thunk
- [ ] 4.5.6 Create logout async thunk
- [ ] 4.5.7 Add auth reducers
- [ ] 4.5.8 Write tests for auth API service
- [ ] 4.5.9 Create frontend/src/services/auth.service.ts
- [ ] 4.5.10 Implement login API call
- [ ] 4.5.11 Implement register API call
- [ ] 4.5.12 Implement token refresh logic
- [ ] 4.5.13 Create AuthContext provider
- [ ] 4.5.14 Create useAuth hook
- [ ] 4.5.15 Test auth flow end-to-end

## 5. Role-Based Access Control [Priority: Critical]

### 5.0 User Role Definitions [Priority: Critical]

**TDD Approach: Test role permissions and capabilities before implementation**

- [ ] 5.0.1 Write tests for six distinct user role definitions (tests/auth/test_user_roles.py)
- [ ] 5.0.2 Define Member role: Basic circle participation, event registration, profile management
- [ ] 5.0.3 Define Facilitator role: Circle creation/management, member addition, meeting tracking
- [ ] 5.0.4 Define Admin role: System administration, user management, global settings
- [ ] 5.0.5 Define Leadership role: Financial oversight, organizational reporting, strategic access
- [ ] 5.0.6 Define PTM (Production Team Manager) role: Event production, logistics, staff coordination
- [ ] 5.0.7 Define Support role: Member assistance, payment issue resolution, basic troubleshooting
- [ ] 5.0.8 Test role hierarchy and permission inheritance (additive permissions)
- [ ] 5.0.9 Test multiple role assignment per user with context switching
- [ ] 5.0.10 Create role enumeration in backend/app/models/role.py
- [ ] 5.0.11 Seed database with six system roles and their permissions
- [ ] 5.0.12 Test role assignment and permission validation
- [ ] 5.0.13 Verify overlapping responsibilities work correctly (as per product brief)

### 5.1 Permission Models [Priority: Critical]

- [ ] 5.1.1 Write tests for Permission model
- [ ] 5.1.2 Create Permission model with name field
- [ ] 5.1.3 Add resource and action fields
- [ ] 5.1.4 Add description field
- [ ] 5.1.5 Write tests for Role model
- [ ] 5.1.6 Create Role model with name
- [ ] 5.1.7 Add is_system boolean field
- [ ] 5.1.8 Create RolePermission association table
- [ ] 5.1.9 Write tests for UserRole model
- [ ] 5.1.10 Create UserRole model with user_id and role_id
- [ ] 5.1.11 Add is_primary field
- [ ] 5.1.12 Add assigned_by and assigned_at fields
- [ ] 5.1.13 Create migrations for all RBAC tables
- [ ] 5.1.14 Run migrations and verify schema
- [ ] 5.2.1 Write tests for permission checking
- [ ] 5.2.2 Create backend/app/core/permissions.py
- [ ] 5.2.3 Implement get_user_permissions function
- [ ] 5.2.4 Create PermissionChecker dependency class
- [ ] 5.2.5 Implement require_permission decorator
- [ ] 5.2.6 Write tests for role-based access
- [ ] 5.2.7 Create role assignment service
- [ ] 5.2.8 Implement add_user_role function
- [ ] 5.2.9 Implement remove_user_role function
- [ ] 5.2.10 Test permission inheritance

### 5.3 Frontend Role Management [Priority: High]

- [ ] 5.3.1 Create ProtectedRoute component
- [ ] 5.3.2 Add permission checking to ProtectedRoute
- [ ] 5.3.3 Create RoleContext provider
- [ ] 5.3.4 Implement usePermission hook
- [ ] 5.3.5 Create role switching UI component
- [ ] 5.3.6 Test role-based UI rendering

## 6. Circle Management System [Priority: High]

### 6.1 Circle Models [Priority: High]

**TDD Approach: Test circle business rules and membership logic before implementation**

- [ ] 6.1.1 Write comprehensive tests for Circle model (tests/models/test_circle.py)
- [ ] 6.1.2 Test circle name validation and uniqueness per facilitator
- [ ] 6.1.3 Test capacity constraints (min 2, max 10 members)
- [ ] 6.1.4 Test location validation and PostGIS integration
- [ ] 6.1.5 Test meeting schedule validation and JSON structure
- [ ] 6.1.6 Create backend/app/models/circle.py with SQLAlchemy models
- [ ] 6.1.7 Define Circle model with name field (required, 100 chars max)
- [ ] 6.1.8 Add description field (optional, 1000 chars max)
- [ ] 6.1.9 Add location_name field for display purposes
- [ ] 6.1.10 Add location_address field for meetup locations
- [ ] 6.1.11 Add location_point PostGIS geography field for proximity searches
- [ ] 6.1.12 Add facilitator_id foreign key to User profile
- [ ] 6.1.13 Add capacity_min integer field (default 2, min 2)
- [ ] 6.1.14 Add capacity_max integer field (default 8, max 10)
- [ ] 6.1.15 Add meeting_schedule JSONB field (day, time, frequency)
- [ ] 6.1.16 Add status enum field (FORMING, ACTIVE, PAUSED, CLOSED)
- [ ] 6.1.17 Add created_at and updated_at timestamps
- [ ] 6.1.18 Add circle-specific validation constraints
- [ ] 6.1.19 Write tests for CircleMembership model (tests/models/test_circle_membership.py)
- [ ] 6.1.20 Test membership uniqueness per circle
- [ ] 6.1.21 Test payment status tracking and transitions
- [ ] 6.1.22 Test member capacity enforcement
- [ ] 6.1.23 Create CircleMembership model with composite primary key
- [ ] 6.1.24 Add circle_id and user_id foreign keys
- [ ] 6.1.25 Add joined_at timestamp field
- [ ] 6.1.26 Add payment_status enum (PENDING, CURRENT, OVERDUE, PAUSED)
- [ ] 6.1.27 Add stripe_subscription_id field for payment tracking
- [ ] 6.1.28 Add next_payment_due date field
- [ ] 6.1.29 Add is_active boolean field for membership status
- [ ] 6.1.30 Add transfer_request_id for circle transfers
- [ ] 6.1.31 Create circle table migrations with proper constraints
- [ ] 6.1.32 Create circle_membership table migration
- [ ] 6.1.33 Run migrations on main database
- [ ] 6.1.34 Test circle creation with valid data
- [ ] 6.1.35 Test membership addition and capacity enforcement
- [ ] 6.1.36 Verify circle tables schema and constraints

### 6.2 Circle Repository [Priority: High]

- [ ] 6.2.1 Write tests for base repository pattern
- [ ] 6.2.2 Create backend/app/repositories/base.py
- [ ] 6.2.3 Implement generic get method
- [ ] 6.2.4 Implement generic get_multi method
- [ ] 6.2.5 Implement generic create method
- [ ] 6.2.6 Implement generic update method
- [ ] 6.2.7 Implement generic delete method
- [ ] 6.2.8 Write tests for CircleRepository
- [ ] 6.2.9 Create backend/app/repositories/circle.py
- [ ] 6.2.10 Implement get_by_facilitator method
- [ ] 6.2.11 Implement get_with_members method
- [ ] 6.2.12 Implement add_member method
- [ ] 6.2.13 Test capacity validation
- [ ] 6.2.14 Test member uniqueness
- [ ] 6.2.15 Verify all repository tests pass

### 6.3 Circle API Endpoints [Priority: High]

- [ ] 6.3.1 Write tests for circle list endpoint
- [ ] 6.3.2 Create backend/app/api/v1/circles.py
- [ ] 6.3.3 Create CircleCreate schema
- [ ] 6.3.4 Create CircleResponse schema
- [ ] 6.3.5 Implement GET /circles endpoint
- [ ] 6.3.6 Write tests for circle creation
- [ ] 6.3.7 Implement POST /circles endpoint
- [ ] 6.3.8 Write tests for circle details
- [ ] 6.3.9 Implement GET /circles/{id} endpoint
- [ ] 6.3.10 Write tests for adding members
- [ ] 6.3.11 Create MemberAdd schema
- [ ] 6.3.12 Implement POST /circles/{id}/members
- [ ] 6.3.13 Test permission requirements
- [ ] 6.3.14 Add circle router to app
- [ ] 6.3.15 Verify endpoints via API docs

### 6.4 Circle Frontend Components [Priority: High]

- [ ] 6.4.1 Write tests for circle list component
- [ ] 6.4.2 Create CircleList.tsx component
- [ ] 6.4.3 Create CircleCard.tsx component
- [ ] 6.4.4 Write tests for circle creation form
- [ ] 6.4.5 Create CircleCreateForm.tsx
- [ ] 6.4.6 Add form validation
- [ ] 6.4.7 Write tests for circle detail view
- [ ] 6.4.8 Create CircleDetail.tsx component
- [ ] 6.4.9 Create MemberList.tsx component
- [ ] 6.4.10 Create AddMemberDialog.tsx
- [ ] 6.4.11 Implement circle API service
- [ ] 6.4.12 Create circle Redux slice
- [ ] 6.4.13 Add circle routes to router
- [ ] 6.4.14 Test circle CRUD operations
- [ ] 6.4.15 Verify member management works

## 7. Event Management System [Priority: High]

### 7.1 Event Models [Priority: High]

**TDD Approach: Test event types and flexible configurations before implementation**

- [ ] 7.1.1 Write comprehensive tests for Event model (tests/models/test_event.py)
- [ ] 7.1.2 Test event type validation and specific configurations
- [ ] 7.1.3 Test event capacity management and waitlist functionality
- [ ] 7.1.4 Create backend/app/models/event.py with flexible event schema
- [ ] 7.1.5 Define Event model with name, description, and event_type enum
- [ ] 7.1.6 Add event_type enum: MOVIE_NIGHT, WORKSHOP, DAY_RETREAT, MULTI_DAY_RETREAT, SOCIAL_GATHERING, TRAINING
- [ ] 7.1.7 Add start_date and end_date datetime fields
- [ ] 7.1.8 Add location_name and location_address fields
- [ ] 7.1.9 Add location_point PostGIS field for proximity searches
- [ ] 7.1.10 Add capacity_min and capacity_max integer fields
- [ ] 7.1.11 Add config JSONB field for event-specific settings
- [ ] 7.1.12 Add requirements JSONB field for participant prerequisites
- [ ] 7.1.13 Add pricing JSONB field for tiered pricing options
- [ ] 7.1.14 Add registration_deadline datetime field
- [ ] 7.1.15 Add status enum field (DRAFT, OPEN, FULL, CANCELLED, COMPLETED)
- [ ] 7.1.16 Write tests for EventStaff model (tests/models/test_event_staff.py)
- [ ] 7.1.17 Test PTM role assignments and conflict detection
- [ ] 7.1.18 Create EventStaff model with event_id and user_id
- [ ] 7.1.19 Add role enum field (PTM1, PTM2, PTM3, FACILITATOR, SUPPORT)
- [ ] 7.1.20 Add responsibilities JSONB field for role-specific duties
- [ ] 7.1.21 Write tests for EventParticipant model (tests/models/test_event_participant.py)
- [ ] 7.1.22 Test participant status transitions and waitlist management
- [ ] 7.1.23 Create EventParticipant model with event_id and user_id
- [ ] 7.1.24 Add status enum (REGISTERED, WAITLISTED, CONFIRMED, CANCELLED, ATTENDED)
- [ ] 7.1.25 Add application_data JSONB for event-specific participant information
- [ ] 7.1.26 Add care_team_member_id field for participant support assignment
- [ ] 7.1.27 Add sponsor_id field for referral tracking
- [ ] 7.1.28 Add registration_date and confirmation_date timestamps
- [ ] 7.1.29 Create event table migrations with proper constraints
- [ ] 7.1.30 Create event_staff and event_participant table migrations
- [ ] 7.1.31 Test event creation for different event types
- [ ] 7.1.32 Test event capacity enforcement and waitlist promotion
- [ ] 7.1.33 Verify event table schema supports all event types from product brief

### 7.2 Event Services [Priority: High]

- [ ] 7.2.1 Write tests for event creation
- [ ] 7.2.2 Create backend/app/services/event.py
- [ ] 7.2.3 Implement create_event function
- [ ] 7.2.4 Write tests for event registration
- [ ] 7.2.5 Implement register_for_event function
- [ ] 7.2.6 Add waitlist logic
- [ ] 7.2.7 Write tests for staff assignment
- [ ] 7.2.8 Implement assign_event_staff function
- [ ] 7.2.9 Add conflict checking
- [ ] 7.2.10 Test capacity enforcement

### 7.3 Event API Endpoints [Priority: High]

- [ ] 7.3.1 Write tests for event creation endpoint
- [ ] 7.3.2 Create backend/app/api/v1/events.py
- [ ] 7.3.3 Create EventCreate schema
- [ ] 7.3.4 Implement POST /events endpoint
- [ ] 7.3.5 Write tests for event registration
- [ ] 7.3.6 Create EventRegistration schema
- [ ] 7.3.7 Implement POST /events/{id}/register
- [ ] 7.3.8 Write tests for staff assignment
- [ ] 7.3.9 Create StaffAssignment schema
- [ ] 7.3.10 Implement POST /events/{id}/staff
- [ ] 7.3.11 Add event router to app
- [ ] 7.3.12 Test all event endpoints

### 7.4 Event Frontend Components [Priority: High]

- [ ] 7.4.1 Create EventList.tsx component
- [ ] 7.4.2 Create EventCard.tsx component
- [ ] 7.4.3 Create EventCreateWizard.tsx
- [ ] 7.4.4 Add dynamic form builder
- [ ] 7.4.5 Create EventDetail.tsx
- [ ] 7.4.6 Create RegistrationForm.tsx
- [ ] 7.4.7 Create StaffAssignment.tsx
- [ ] 7.4.8 Create ParticipantList.tsx
- [ ] 7.4.9 Implement event API service
- [ ] 7.4.10 Create event Redux slice
- [ ] 7.4.11 Test event workflows

## 8. Payment Integration [Priority: Critical]

### 8.1 Payment Models [Priority: Critical]

**TDD Approach: Test payment flows and financial calculations before implementation**

- [ ] 8.1.1 Write comprehensive tests for PaymentPlan model (tests/models/test_payment_plan.py)
- [ ] 8.1.2 Test installment calculation and scheduling logic
- [ ] 8.1.3 Test payment plan validation and constraints
- [ ] 8.1.4 Test payment plan status transitions
- [ ] 8.1.5 Create backend/app/models/payment.py with financial models
- [ ] 8.1.6 Define PaymentPlan model with total_amount and currency
- [ ] 8.1.7 Add installment_count field (1-12 allowed)
- [ ] 8.1.8 Add installment_amount calculated field
- [ ] 8.1.9 Add payment_schedule JSONB field for due dates
- [ ] 8.1.10 Add reference_type enum (CIRCLE_MEMBERSHIP, EVENT_REGISTRATION)
- [ ] 8.1.11 Add reference_id for linking to circles or events
- [ ] 8.1.12 Add stripe_product_id and stripe_price_id fields
- [ ] 8.1.13 Add status enum (PENDING, ACTIVE, COMPLETED, CANCELLED)
- [ ] 8.1.14 Add created_at and updated_at timestamps
- [ ] 8.1.15 Write tests for PaymentTransaction model (tests/models/test_payment_transaction.py)
- [ ] 8.1.16 Test transaction status tracking and idempotency
- [ ] 8.1.17 Test payment failure handling and retry logic
- [ ] 8.1.18 Test refund transaction creation and tracking
- [ ] 8.1.19 Create PaymentTransaction model with amount and currency
- [ ] 8.1.20 Add stripe_payment_intent_id field (unique, indexed)
- [ ] 8.1.21 Add stripe_charge_id field for successful payments
- [ ] 8.1.22 Add transaction_type enum (PAYMENT, REFUND, PARTIAL_REFUND)
- [ ] 8.1.23 Add status enum (PENDING, SUCCEEDED, FAILED, CANCELLED)
- [ ] 8.1.24 Add failure_reason field for failed transactions
- [ ] 8.1.25 Add processed_at timestamp for completion tracking
- [ ] 8.1.26 Add payment_plan_id foreign key relationship
- [ ] 8.1.27 Add metadata JSONB field for Stripe webhook data
- [ ] 8.1.28 Add idempotency_key field for duplicate prevention
- [ ] 8.1.29 Create payment_plans table migration
- [ ] 8.1.30 Create payment_transactions table migration
- [ ] 8.1.31 Run payment migrations on main database
- [ ] 8.1.32 Test payment plan creation and validation
- [ ] 8.1.33 Test transaction creation and status updates
- [ ] 8.1.34 Verify payment table schema and constraints
- [ ] 8.1.35 Test payment plan installment calculations

### 8.2 Stripe Service [Priority: Critical]

- [ ] 8.2.1 Write tests for Stripe customer creation
- [ ] 8.2.2 Create backend/app/services/stripe.py
- [ ] 8.2.3 Implement create_customer function
- [ ] 8.2.4 Write tests for subscription creation
- [ ] 8.2.5 Implement create_circle_subscription
- [ ] 8.2.6 Write tests for payment plans
- [ ] 8.2.7 Implement create_event_payment_plan
- [ ] 8.2.8 Write tests for refunds
- [ ] 8.2.9 Implement process_refund function
- [ ] 8.2.10 Add webhook signature validation
- [ ] 8.2.11 Test idempotent request handling

### 8.3 Payment API Endpoints [Priority: Critical]

- [ ] 8.3.1 Write tests for webhook endpoint
- [ ] 8.3.2 Create backend/app/api/v1/payments.py
- [ ] 8.3.3 Implement POST /webhooks/stripe
- [ ] 8.3.4 Handle payment_intent.succeeded
- [ ] 8.3.5 Handle payment_intent.failed
- [ ] 8.3.6 Handle subscription.deleted
- [ ] 8.3.7 Write tests for payment methods
- [ ] 8.3.8 Implement payment method endpoints
- [ ] 8.3.9 Test webhook security
- [ ] 8.3.10 Verify payment flow

### 8.4 Payment Frontend [Priority: Critical]

- [ ] 8.4.1 Install @stripe/stripe-js
- [ ] 8.4.2 Install @stripe/react-stripe-js
- [ ] 8.4.3 Create PaymentForm.tsx component
- [ ] 8.4.4 Implement Stripe Elements
- [ ] 8.4.5 Create SubscriptionManager.tsx
- [ ] 8.4.6 Create PaymentHistory.tsx
- [ ] 8.4.7 Create RefundDialog.tsx
- [ ] 8.4.8 Test payment flow
- [ ] 8.4.9 Test subscription management
- [ ] 8.4.10 Verify PCI compliance

## 9. Messaging System [Priority: Medium]

### 9.1 Message Models [Priority: Medium]

- [ ] 9.1.1 Write tests for Message model
- [ ] 9.1.2 Create backend/app/models/message.py
- [ ] 9.1.3 Define Message model with type field
- [ ] 9.1.4 Add recipient_type and recipient_id
- [ ] 9.1.5 Add thread_id for conversations
- [ ] 9.1.6 Create MessageRecipient model
- [ ] 9.1.7 Add read_at tracking
- [ ] 9.1.8 Create message migrations
- [ ] 9.1.9 Test message creation
- [ ] 9.1.10 Test recipient tracking

### 9.2 WebSocket Implementation [Priority: Medium]

- [ ] 9.2.1 Write tests for connection manager
- [ ] 9.2.2 Create backend/app/core/websocket.py
- [ ] 9.2.3 Implement ConnectionManager class
- [ ] 9.2.4 Add user connection tracking
- [ ] 9.2.5 Add circle-based routing
- [ ] 9.2.6 Add role-based routing
- [ ] 9.2.7 Write tests for message broadcasting
- [ ] 9.2.8 Implement broadcast methods
- [ ] 9.2.9 Add WebSocket endpoint to app
- [ ] 9.2.10 Test real-time delivery

### 9.3 Messaging API [Priority: Medium]

- [ ] 9.3.1 Write tests for message sending
- [ ] 9.3.2 Create backend/app/api/v1/messages.py
- [ ] 9.3.3 Create MessageCreate schema
- [ ] 9.3.4 Implement POST /messages endpoint
- [ ] 9.3.5 Write tests for message history
- [ ] 9.3.6 Implement GET /messages endpoint
- [ ] 9.3.7 Add pagination support
- [ ] 9.3.8 Test permission-based filtering and hierarchical routing
- [ ] 9.3.9 Test role-based message routing (as specified in tech spec)
- [ ] 9.3.10 Add message router to app
- [ ] 9.3.11 Test message response time tracking (secondary metric from product brief)
- [ ] 9.3.12 Verify secure messaging maintains confidential nature of organization
- [ ] 9.3.13 Verify messaging flow supports broadcast and direct messaging

### 9.4 Messaging Frontend [Priority: Medium]

- [ ] 9.4.1 Create MessageComposer.tsx
- [ ] 9.4.2 Create MessageThread.tsx
- [ ] 9.4.3 Create MessageList.tsx
- [ ] 9.4.4 Implement WebSocket connection
- [ ] 9.4.5 Create useWebSocket hook
- [ ] 9.4.6 Add real-time message updates
- [ ] 9.4.7 Create NotificationBell.tsx
- [ ] 9.4.8 Add unread count tracking
- [ ] 9.4.9 Test messaging UI
- [ ] 9.4.10 Test real-time updates

## 10. Notification System [Priority: Medium]

### 10.1 Email Integration [Priority: Medium]

- [ ] 10.1.1 Write tests for email service
- [ ] 10.1.2 Create backend/app/services/email.py
- [ ] 10.1.3 Implement SendGrid client setup
- [ ] 10.1.4 Create email template system
- [ ] 10.1.9 Test email delivery
- [ ] 10.1.10 Test template rendering

**Section Completion Strategy:**

- Each major section (1.1, 1.2, etc.) represents a complete, committable unit
- Tests must pass at 100% before section completion
- Enhancement documentation created after each section
- Commit messages follow Husky-style conventions
