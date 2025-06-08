# Docker Configuration for Men's Circle Management Platform

## Overview

This directory contains Docker configuration files for containerizing the Men's Circle Management Platform. The platform uses a microservices architecture with separate containers for backend, frontend, databases, and supporting services.

## Architecture

### Container Services

- **Backend**: Python 3.11 FastAPI application
- **Frontend**: Node.js 18 React TypeScript PWA
- **Main Database**: PostgreSQL 15 for application data
- **Credentials Database**: Separate PostgreSQL 15 for authentication data
- **Cache/Sessions**: Redis 7 for caching and session storage
- **Message Queue**: Celery with Redis for background tasks
- **Reverse Proxy**: Nginx for routing and static file serving

### Security Architecture

The platform implements a dual-database security model:

- **Main Database**: Circle data, events, payments, messaging
- **Credentials Database**: User authentication, passwords, sensitive credentials
- **Separation Benefits**: Enhanced security, compliance, data isolation

## File Structure

```
docker/
├── README.md                 # This documentation
├── backend.Dockerfile        # Python FastAPI container
├── frontend.Dockerfile       # React TypeScript PWA container
├── test.Dockerfile          # Testing environment container
├── nginx.conf               # Nginx reverse proxy configuration
├── .dockerignore            # Docker build context exclusions
├── init-test-db.sql         # Test database initialization
└── docker-compose.yml       # Development services (root level)
```

## Environment Configurations

### Development Environment

- Hot reload for both backend and frontend
- Volume mounts for live code changes
- Debug logging enabled
- Test database with seeded data

### Testing Environment

- Isolated test databases (ephemeral)
- Containerized test execution
- Coverage report generation
- Parallel test execution support

### Production Environment

- Optimized multi-stage builds
- Health checks and monitoring
- Resource limits and security policies
- Automated backups and scaling

## Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum
- 20GB disk space

### Development Setup

```bash
# Clone repository and navigate to project root
cd mens-circle-platform

# Copy environment template
cp .env.example .env

# Generate secure secrets
./scripts/generate-secrets.sh

# Start all services
docker-compose up -d

# Verify services are healthy
docker-compose ps
```

### Testing Setup

```bash
# Run tests in containers
docker-compose -f docker-compose.test.yml up --build

# Or use the test script
./scripts/test-in-docker.sh

# Run specific test suites
docker-compose exec backend-test pytest tests/auth/
docker-compose exec frontend-test npm test
```

## Service Details

### Backend Container (FastAPI)

- **Base Image**: python:3.11-alpine
- **Port**: 8000
- **Health Check**: GET /health
- **Dependencies**: PostgreSQL, Redis
- **Environment**: Async SQLAlchemy, Celery workers

### Frontend Container (React PWA)

- **Base Image**: node:18-alpine
- **Port**: 3000
- **Build Tool**: Vite with HMR
- **Dependencies**: Backend API
- **Environment**: TypeScript, Material-UI, Redux

### Database Containers

- **Main DB**: PostgreSQL 15 (port 5432)
- **Credentials DB**: PostgreSQL 15 (port 5433)
- **Persistence**: Named volumes with backup support
- **Initialization**: Automated schema migration

### Cache Container (Redis)

- **Version**: Redis 7
- **Port**: 6379
- **Persistence**: RDB + AOF
- **Memory Limit**: 512MB default
- **Use Cases**: Sessions, caching, Celery broker

## Docker Compose Services

### Main Application Stack

```yaml
services:
  backend: # FastAPI application
  frontend: # React TypeScript PWA
  main-db: # PostgreSQL main database
  creds-db: # PostgreSQL credentials database
  redis: # Redis cache and message broker
  nginx: # Reverse proxy and load balancer
  celery-worker: # Background task processor
  celery-beat: # Scheduled task scheduler
```

### Testing Stack

```yaml
services:
  backend-test: # Backend test execution
  frontend-test: # Frontend test execution
  test-db: # Ephemeral test database
  test-redis: # Test cache instance
```

## Volume Management

### Persistent Volumes

- `main_db_data`: Main database persistence
- `creds_db_data`: Credentials database persistence
- `redis_data`: Redis cache persistence
- `nginx_logs`: Nginx access and error logs

### Development Volumes

- `./backend:/app`: Backend live reload
- `./frontend:/app`: Frontend live reload
- `./docker/nginx.conf:/etc/nginx/nginx.conf`: Nginx config

## Network Configuration

### Internal Networks

- `platform-network`: Main application network
- `db-network`: Database isolation network
- `test-network`: Testing environment network

### Port Mapping

- **3000**: Frontend development server
- **8000**: Backend API server
- **80/443**: Nginx reverse proxy
- **5432**: Main database (development only)
- **6379**: Redis (development only)

## Health Checks

All services include comprehensive health checks:

- **Backend**: API endpoint validation
- **Frontend**: HTTP response check
- **Databases**: Connection and query validation
- **Redis**: Ping command validation
- **Nginx**: Configuration and upstream checks

## Performance Optimization

### Build Optimization

- Multi-stage Docker builds
- Layer caching strategies
- Minimal base images (Alpine Linux)
- Build context optimization with .dockerignore

### Runtime Optimization

- Resource limits and reservations
- Connection pooling
- Caching strategies
- Horizontal scaling preparation

## Security Considerations

### Container Security

- Non-root user execution
- Read-only filesystems where possible
- Security scanning in CI/CD
- Regular base image updates

### Network Security

- Internal service communication
- Firewall rules for external access
- TLS encryption for production
- Secrets management through Docker secrets

## Monitoring and Logging

### Health Monitoring

- Container health checks
- Service dependency validation
- Resource usage monitoring
- Performance metrics collection

### Logging Strategy

- Centralized log aggregation
- Structured JSON logging
- Log retention policies
- Error tracking and alerting

## Development Workflow

### Code Changes

1. Edit code in host filesystem
2. Changes reflected immediately via volumes
3. Hot reload triggers automatic rebuild
4. Tests run automatically on changes

### Database Changes

1. Create Alembic migration
2. Apply migration in development container
3. Test migration in isolated test container
4. Validate changes across all environments

### Testing Workflow

1. Write tests following TDD principles
2. Run tests in containerized environment
3. Validate test isolation and cleanup
4. Generate coverage reports

## Troubleshooting

### Common Issues

**Services won't start:**

```bash
docker-compose logs [service-name]
docker-compose ps
```

**Database connection errors:**

```bash
docker-compose exec main-db pg_isready
docker-compose exec backend nc -z main-db 5432
```

**Port conflicts:**

```bash
docker-compose down
lsof -i :3000  # Check port usage
```

**Build failures:**

```bash
docker-compose build --no-cache
docker system prune -f
```

### Debug Commands

```bash
# Access container shell
docker-compose exec backend sh
docker-compose exec frontend sh

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Check resource usage
docker stats

# Inspect networks
docker network ls
docker network inspect platform-network
```

## Production Deployment

See `docs/deployment.md` for complete production deployment guide including:

- Infrastructure requirements
- SSL certificate setup
- Load balancer configuration
- Database backup strategies
- Monitoring and alerting setup

## Contributing

When adding new Docker configurations:

1. Test in development environment
2. Validate in testing environment
3. Document configuration changes
4. Update this README
5. Ensure security best practices

## Support

For Docker-related issues:

- Check service logs: `docker-compose logs [service]`
- Validate configuration: `docker-compose config`
- Review health checks: `docker-compose ps`
- Consult troubleshooting section above

---

**Note**: This Docker configuration supports the complete Men's Circle Management Platform including circle management, event orchestration, payment processing, and secure messaging capabilities.
