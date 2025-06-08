# Technical Specification: Men's Circle Management Platform

## 1. Introduction

### 1.1 Purpose

This document provides the technical specification for a comprehensive management platform designed to support a men's personal development organization. The platform will manage member circles, events, payments, and communications while maintaining strict security and privacy standards.

### 1.2 Scope

The system will support six distinct user roles with overlapping permissions, handle recurring and one-time payments through Stripe, provide real-time messaging capabilities, and operate as a Progressive Web Application (PWA) for mobile accessibility.

### 1.3 Definitions and Acronyms

- **Circle**: A small group of 2-10 men who meet regularly for personal development
- **Event**: Organized gatherings ranging from casual meetups to multi-day retreats
- **PTM**: Production Team Manager (event staff role)
- **PWA**: Progressive Web Application
- **RBAC**: Role-Based Access Control

## 2. System Architecture

### 2.1 Overview

The platform follows a microservices-inspired architecture with clear separation of concerns:

- **Presentation Layer**: React-based PWA with offline capabilities
- **API Layer**: RESTful API built with FastAPI, supplemented by WebSocket connections
- **Business Logic Layer**: Service-oriented architecture with domain-specific modules
- **Data Access Layer**: Repository pattern with PostgreSQL as primary storage
- **External Services Layer**: Integrations with Stripe, SMS, and email providers

### 2.2 Technology Stack

#### Backend Technologies

- **Language**: Python 3.11+ for type safety and performance
- **Framework**: FastAPI chosen for async support, automatic API documentation, and performance
- **Database**: PostgreSQL 15 with PostGIS for geospatial features and separate encrypted credentials database
- **Cache**: Redis 7 for session management and response caching
- **Task Queue**: Celery for background job processing
- **WebSockets**: Native FastAPI WebSocket support for real-time features

#### Frontend Technologies

- **Framework**: React 18 with TypeScript for type safety
- **State Management**: Redux Toolkit with RTK Query for efficient data fetching
- **UI Framework**: Material-UI v5 for consistent, accessible components
- **Build System**: Vite for fast development and optimized production builds
- **PWA Support**: Workbox for service worker management

#### Infrastructure

- **Containerization**: Docker for consistent deployment environments
- **Orchestration**: AWS ECS Fargate or DigitalOcean App Platform
- **Monitoring**: Prometheus/Grafana for metrics, ELK stack for logging
- **CI/CD**: GitHub Actions for automated testing and deployment

### 2.4 Development Methodology

#### Test-Driven Development Approach

All components are built using TDD methodology:

1. **Test First**: Write failing tests that specify desired behavior
2. **Implementation**: Write minimal code to pass tests
3. **Refactoring**: Improve design while maintaining passing tests

This approach influences architecture by:

- Promoting loose coupling for testability
- Encouraging interface-based design
- Driving modular, composable components
- Ensuring all code has a purpose (no speculative features)

#### Authentication Service

Handles user authentication, authorization, and session management. Implements JWT-based authentication with refresh tokens, supporting multiple authentication methods including email/password, SMS verification, and Google OAuth.

#### User Management Service

Manages user profiles, roles, and permissions. Implements flexible RBAC system where users can hold multiple roles simultaneously with additive permissions.

#### Circle Management Service

Handles all circle-related operations including member management, meeting tracking, and goal setting. Enforces capacity constraints and manages payment status for members.

#### Event Management Service

Provides flexible event creation and management, supporting various event types from simple gatherings to complex multi-day retreats with custom requirements.

#### Payment Service

Integrates with Stripe to handle subscriptions for circles and payment plans for events. Supports manual intervention for payment issues while maintaining automated tracking.

#### Communication Service

Manages in-platform messaging, email, and SMS notifications. Implements hierarchical message routing based on user roles and relationships.

#### Real-time Service

WebSocket-based service providing live updates for messages, notifications, and system events.

## 3. Data Architecture

### 3.1 Database Design Philosophy

The system uses two separate PostgreSQL databases:

1. **Main Application Database**: Contains all business data
2. **Credentials Database**: Encrypted storage for sensitive authentication data

This separation allows for enhanced security measures on credential data while maintaining performance for general application queries.

### 3.2 Key Entities and Relationships

#### User Model

Central to the system, the User entity is split between credentials (authentication) and profile (application data). This separation enables:

- Independent scaling of authentication services
- Enhanced security for credential storage
- Easier compliance with data privacy regulations

#### Role-Based Access Control

The permission system uses a many-to-many relationship between users and roles, with each role having specific permissions. Key features:

- Additive permissions across multiple roles
- Context switching for users with multiple roles
- Audit trail for all permission changes

#### Circle Membership

Tracks the relationship between users and circles with temporal data, supporting:

- Historical membership tracking
- Payment status per member
- Transfer requests between circles

#### Event Participation

Complex relationship tracking participant status, payment plans, and staff assignments:

- Waitlist management with automatic promotion
- Care team assignments for participant support
- Sponsor tracking for referrals

### 3.3 Data Integrity and Constraints

- Foreign key constraints ensure referential integrity
- Check constraints validate business rules at the database level
- Unique constraints prevent duplicate memberships and registrations
- Temporal constraints track membership and participation history

## 4. API Design

### 4.1 RESTful API Principles

The API follows REST principles with:

- Resource-based URLs
- HTTP methods for operations (GET, POST, PUT, DELETE)
- Consistent response formats
- Comprehensive error handling

### 4.2 API Versioning

APIs are versioned using URL path versioning (`/api/v1/`) to ensure backward compatibility while allowing evolution.

### 4.3 API Development with TDD

#### API Contract Testing First

Before implementing any endpoint, contract tests are written to define:

1. **Request validation**: What constitutes a valid request
2. **Response structure**: Expected response format
3. **Error scenarios**: All possible error conditions
4. **Authorization rules**: Who can access what

Example workflow for creating a new endpoint:

1. Write OpenAPI specification for the endpoint
2. Generate contract tests from specification
3. Write integration tests for business scenarios
4. Implement endpoint to satisfy tests
5. Refactor for code quality

#### Test-First Error Handling

All error conditions are defined through tests before implementation:

- Validation errors (400)
- Authentication errors (401)
- Authorization errors (403)
- Not found errors (404)
- Business rule violations (422)
- Server errors (500)

### 4.4 Key API Endpoints

#### Authentication

- `POST /api/v1/auth/register` - New user registration
- `POST /api/v1/auth/login` - User authentication
- `POST /api/v1/auth/refresh` - Token refresh
- `POST /api/v1/auth/verify-phone` - SMS verification

#### Circle Management

- `GET /api/v1/circles` - List circles (filtered by permissions)
- `POST /api/v1/circles` - Create new circle
- `GET /api/v1/circles/{id}` - Get circle details
- `POST /api/v1/circles/{id}/members` - Add member to circle
- `POST /api/v1/circles/{id}/meetings` - Record meeting

#### Event Management

- `POST /api/v1/events` - Create event with flexible configuration
- `POST /api/v1/events/{id}/register` - Register for event
- `POST /api/v1/events/{id}/staff` - Assign staff roles

### 4.5 WebSocket Communication

WebSocket connections support real-time features:

- Personal notifications
- Circle-wide broadcasts
- Role-based announcements
- Typing indicators and presence

Connection management includes automatic reconnection, message queuing during disconnection, and efficient routing based on user context.

## 5. Security Architecture

### 5.1 Security Layers

#### Network Security

- HTTPS everywhere with TLS 1.3
- Web Application Firewall (WAF) for common attack prevention
- Rate limiting per user and IP address
- CORS configuration restricting origins

#### Application Security

- Input validation on all endpoints
- SQL injection prevention through parameterized queries
- XSS prevention with content security policies
- CSRF protection for state-changing operations

#### Data Security

- Encryption at rest for sensitive data
- Encryption in transit for all communications
- Separate encrypted database for credentials
- Field-level encryption for PII

### 5.2 Authentication & Authorization

#### Multi-Factor Authentication

- SMS-based verification for sensitive operations
- Optional TOTP support for enhanced security
- Device fingerprinting for anomaly detection

#### Permission System

- Fine-grained permissions mapped to API endpoints
- Role-based access with inheritance
- Audit logging for all permission checks
- Time-based permission expiry support

### 5.3 Privacy & Compliance

- GDPR-compliant data handling
- Right to erasure implementation
- Data minimization principles
- Consent management for communications

## 6. Integration Architecture

### 6.1 Stripe Payment Integration

#### Architecture

The system integrates with Stripe using webhook-based event processing:

1. Client-side Stripe Elements for secure payment collection
2. Server-side API calls for subscription and payment management
3. Webhook endpoints for asynchronous event processing
4. Idempotent request handling to prevent duplicate charges

#### Key Features

- Customer creation linked to user profiles
- Subscription management for circle memberships
- Payment plan creation for events
- Automated retry logic for failed payments
- Manual intervention workflow for payment issues

### 6.2 Communication Integrations

#### Email Service (SendGrid)

- Transactional email for system notifications
- Bulk email capabilities for announcements
- Template management for consistent branding
- Bounce and complaint handling

#### SMS Service (Twilio)

- Phone number verification
- Payment reminders
- Emergency notifications
- Opt-in/opt-out management

### 6.3 External Authentication (Google OAuth)

- OAuth 2.0 flow implementation
- Account linking for existing users
- Profile synchronization
- Secure token storage

## 7. Performance & Scalability

### 7.1 Performance Requirements

- API response time: < 200ms (p95)
- Page load time: < 3 seconds
- WebSocket latency: < 100ms
- Database query time: < 50ms (p95)

### 7.2 Caching Strategy

#### Application-Level Caching

- Redis for session storage
- API response caching for read-heavy endpoints
- Database query result caching
- Computed value caching (permissions, statistics)

#### CDN Strategy

- Static asset delivery through CDN
- Geographic distribution for global access
- Image optimization and responsive delivery

### 7.3 Database Optimization

- Materialized views for complex aggregations
- Proper indexing strategy based on query patterns
- Connection pooling for efficient resource usage
- Read replicas for scaling read operations

### 7.4 Scalability Approach

#### Horizontal Scaling

- Stateless application servers
- Load balancing with health checks
- Auto-scaling based on metrics
- Database connection pooling

#### Vertical Scaling

- Resource monitoring and right-sizing
- Performance profiling for bottlenecks
- Query optimization
- Caching layer expansion

## 8. Frontend Architecture

### 8.1 Component Architecture

The frontend follows a component-based architecture with:

- Atomic design principles (atoms, molecules, organisms)
- Shared component library
- Consistent styling through theme system
- Accessibility-first development

### 8.2 State Management

Redux Toolkit provides predictable state management:

- Global state for user context and preferences
- RTK Query for server state and caching
- Local component state for UI interactions
- Persistent state for offline functionality

### 8.3 Progressive Web App Features

#### Offline Functionality

- Service worker for request interception
- Offline page for degraded experience
- Background sync for deferred actions
- Local storage for critical data

#### Mobile Optimization

- Touch-optimized interfaces
- Responsive design system
- Reduced data usage
- Native app-like experience

### 8.4 Performance Optimization

- Code splitting by route
- Lazy loading for components
- Image optimization and lazy loading
- Bundle size optimization
- Tree shaking for unused code

## 9. Test-Driven Development Strategy

### 9.1 TDD Philosophy

The project follows strict Test-Driven Development principles where tests are written before implementation code. This approach ensures:

- **Requirements clarity**: Tests define expected behavior before coding
- **Design emergence**: Better architecture emerges from test constraints
- **Regression prevention**: All functionality is tested from inception
- **Living documentation**: Tests serve as executable specifications

### 9.2 TDD Workflow

1. **Red Phase**: Write a failing test that defines desired functionality
2. **Green Phase**: Write minimal code to make the test pass
3. **Refactor Phase**: Improve code quality while keeping tests green

### 9.3 Test Categories and Priorities

#### Unit Tests (Written First)

- **Coverage Target**: 95% for business logic, 80% overall
- **Execution Time**: < 10 seconds for entire suite
- **Isolation**: No database, network, or file system access
- **Naming Convention**: `test_should_[expected_behavior]_when_[condition]`

Example test structure:

```python
def test_should_reject_circle_member_when_capacity_exceeded():
    # Arrange
    circle = Circle(capacity_max=2)
    circle.add_member(User())
    circle.add_member(User())

    # Act & Assert
    with pytest.raises(CapacityExceeded):
        circle.add_member(User())
```

#### Integration Tests (Written After Units)

- **Coverage Target**: Key user flows and API contracts
- **Database**: Uses test database with transactions rolled back
- **External Services**: Mocked with realistic responses
- **Execution Time**: < 2 minutes for entire suite

#### End-to-End Tests (Written Last)

- **Coverage**: Critical business paths only
- **Environment**: Staging environment mimicking production
- **Data**: Dedicated test accounts and data sets
- **Execution Time**: < 10 minutes for smoke tests

### 9.4 Backend TDD Implementation

#### Repository Pattern Testing

Each repository method has corresponding tests written first:

1. Test defines expected database behavior
2. Repository implementation satisfies test
3. Database migrations support test requirements

#### Service Layer Testing

Business logic tests written before service implementation:

1. Mock dependencies (repositories, external services)
2. Define business rules through tests
3. Implement services to satisfy test specifications

#### API Endpoint Testing

Contract tests written before endpoint implementation:

1. Define request/response schemas
2. Test authorization requirements
3. Test validation rules
4. Test error scenarios

### 9.5 Frontend TDD Implementation

#### Component Testing Strategy

1. **Behavior Tests First**: Define component behavior through tests
2. **Render Tests**: Verify correct rendering based on props
3. **Interaction Tests**: Test user interactions and state changes
4. **Accessibility Tests**: Ensure WCAG compliance from start

#### State Management Testing

1. **Action Tests**: Define expected action creators
2. **Reducer Tests**: Specify state transformations
3. **Selector Tests**: Define data derivation logic
4. **Effect Tests**: Specify side effect behavior

### 9.6 TDD Tools and Configuration

#### Backend Testing Stack

- **pytest**: Test runner with fixtures and parametrization
- **pytest-asyncio**: Async test support
- **factory_boy**: Test data generation
- **freezegun**: Time mocking
- **responses**: HTTP request mocking
- **pytest-cov**: Coverage reporting

#### Frontend Testing Stack

- **Jest**: Test runner and assertion library
- **React Testing Library**: Component testing
- **MSW**: API mocking for integration tests
- **Cypress**: E2E testing with TDD approach
- **jest-axe**: Accessibility testing

### 9.7 Continuous Testing Pipeline

#### Pre-commit Phase

- Run unit tests for changed files
- Linting and formatting checks
- Type checking (mypy for Python, TypeScript compiler)

#### Pull Request Phase

- Full unit test suite
- Integration tests for affected modules
- Coverage report with minimum thresholds
- Performance benchmarks against baseline

#### Deployment Phase

- Full test suite execution
- E2E smoke tests
- Performance tests
- Security scanning

### 9.8 Test Data Management

#### Test Fixtures

- Factories for consistent test data generation
- Builders for complex object creation
- Fixtures for common test scenarios
- Separate test database with known state

#### Test Isolation

- Each test runs in isolation
- Database transactions rolled back
- No shared mutable state
- Deterministic test execution

### 9.9 TDD Metrics and Monitoring

#### Key Metrics

- **Test Coverage**: Minimum 80%, target 95% for critical paths
- **Test Execution Time**: Track and optimize slow tests
- **Test Flakiness**: Zero tolerance for flaky tests
- **Test/Code Ratio**: Aim for 1.5:1 ratio

#### Test Health Dashboard

- Coverage trends over time
- Test execution time trends
- Flaky test identification
- Test failure patterns

### 9.10 TDD Best Practices

#### Test Quality Standards

- **Single Responsibility**: Each test verifies one behavior
- **Descriptive Names**: Test names clearly state expectations
- **Arrange-Act-Assert**: Consistent test structure
- **No Logic in Tests**: Tests should be simple and obvious

#### Refactoring Guidelines

- Never refactor without passing tests
- Refactor in small increments
- Run tests after each change
- Improve test quality during refactoring

#### Documentation Through Tests

- Tests serve as living documentation
- Example usage in test cases
- Edge cases documented through tests
- Integration patterns demonstrated

## 10. Deployment Architecture

### 10.1 Container Strategy

Multi-stage Docker builds optimize image size:

1. Build stage with development dependencies
2. Production stage with minimal runtime
3. Security scanning in CI pipeline
4. Image versioning and tagging

### 10.2 Orchestration

- Container orchestration via ECS or Kubernetes
- Service discovery and load balancing
- Health checks and auto-recovery
- Rolling deployments with rollback

### 10.3 Infrastructure as Code

- Terraform for infrastructure provisioning
- Environment-specific configurations
- Secret management through AWS Secrets Manager
- Automated backup configuration

### 10.4 Monitoring & Observability

#### Application Monitoring

- Distributed tracing for request flow
- Error tracking with Sentry
- Performance monitoring
- Custom business metrics

#### Infrastructure Monitoring

- Resource utilization tracking
- Availability monitoring
- Log aggregation and analysis
- Alerting and escalation

## 11. Disaster Recovery

### 11.1 Backup Strategy

- Automated daily backups
- Point-in-time recovery capability
- Cross-region backup replication
- Regular restore testing

### 11.2 High Availability

- Multi-AZ deployment
- Automatic failover
- Load balancer health checks
- Circuit breaker patterns

### 11.3 Incident Response

- Runbook documentation
- On-call rotation
- Incident classification
- Post-mortem process

## 12. Future Considerations

### 12.1 Scalability Path

- Microservices migration path
- Event-driven architecture adoption
- GraphQL API layer
- Real-time analytics pipeline

### 12.2 Feature Expansion

- Mobile native apps
- Advanced analytics dashboard
- AI-powered insights
- Third-party integrations

### 12.3 Technical Debt Management

- Regular refactoring cycles
- Dependency updates
- Performance optimization
- Security improvements

## Appendices

### A. API Documentation

Detailed API documentation available via Swagger/OpenAPI at `/api/docs`

### B. Database Schema

Complete ERD and migration scripts in project repository

### C. Security Policies

Detailed security policies and procedures in separate security documentation

### D. Deployment Procedures

Step-by-step deployment guides for each environment
