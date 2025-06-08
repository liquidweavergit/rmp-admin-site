# Database Migrations with Alembic

This document describes the database migration setup for the Men's Circle Management Platform, which uses Alembic to manage schema changes for both the main application database and the separate credentials database.

## Overview

The platform uses two separate PostgreSQL databases:

1. **Main Database** (`mens_circle_main`) - Stores application data (users, circles, events, etc.)
2. **Credentials Database** (`mens_circle_creds`) - Stores sensitive authentication data (passwords, tokens, etc.)

Each database has its own Alembic configuration and migration history to maintain security separation as specified in the tech spec.

## Configuration Files

### Main Database

- **Config**: `alembic.ini`
- **Environment**: `alembic/env.py`
- **Migrations**: `alembic/versions/`
- **Models**: Imports from `app.models.*` (inheriting from `Base`)

### Credentials Database

- **Config**: `alembic-credentials.ini`
- **Environment**: `alembic-credentials/env.py`
- **Migrations**: `alembic-credentials/versions/`
- **Models**: Imports from `app.models.credentials` (inheriting from `CredentialsBase`)

## Environment Variables

The migration system requires the following environment variables:

```bash
# Main application database (async driver required)
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/mens_circle_main

# Credentials database (async driver required)
CREDS_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5433/mens_circle_creds
```

**Important**: The URLs must use the `postgresql+asyncpg://` driver for async support.

## Migration Management Script

The `migrate.py` script provides convenient commands for managing both databases:

### Available Commands

```bash
# Initialize both databases (run migrations to head)
python migrate.py init

# Upgrade both databases to latest revision
python migrate.py upgrade

# Create new migration for main database
python migrate.py revision "Description of changes"

# Create new migration for credentials database
python migrate.py revision-creds "Description of changes"

# Downgrade both databases by one revision
python migrate.py downgrade

# Show current revision for both databases
python migrate.py current

# Show migration history for both databases
python migrate.py history
```

### Example Usage

```bash
# Set environment variables
export DATABASE_URL="postgresql+asyncpg://postgres:dev_password@localhost:5432/mens_circle_main"
export CREDS_DATABASE_URL="postgresql+asyncpg://postgres:dev_password@localhost:5433/mens_circle_creds"

# Check current status
python migrate.py current

# Create a new migration for main database
python migrate.py revision "Add circle membership table"

# Create a new migration for credentials database
python migrate.py revision-creds "Add OAuth token encryption"

# Apply all pending migrations
python migrate.py upgrade
```

## Direct Alembic Commands

You can also use Alembic directly for more advanced operations:

### Main Database

```bash
# Check current revision
alembic current

# Create new migration
alembic revision --autogenerate -m "Description"

# Upgrade to latest
alembic upgrade head

# Downgrade one revision
alembic downgrade -1

# Show history
alembic history
```

### Credentials Database

```bash
# Check current revision
alembic -c alembic-credentials.ini current

# Create new migration
alembic -c alembic-credentials.ini revision --autogenerate -m "Description"

# Upgrade to latest
alembic -c alembic-credentials.ini upgrade head

# Downgrade one revision
alembic -c alembic-credentials.ini downgrade -1

# Show history
alembic -c alembic-credentials.ini history
```

## Adding New Models

### Main Database Models

1. Create your model in `app/models/` inheriting from `Base`
2. Import the model in `alembic/env.py`
3. Generate migration: `python migrate.py revision "Add new model"`
4. Apply migration: `python migrate.py upgrade`

Example:

```python
# app/models/circle.py
from sqlalchemy import Column, Integer, String
from ..core.database import Base

class Circle(Base):
    __tablename__ = "circles"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
```

Then update `alembic/env.py`:

```python
# Import all models here
from app.models.user import User
from app.models.circle import Circle  # Add this line
```

### Credentials Database Models

1. Create your model in `app/models/` inheriting from `CredentialsBase`
2. Import the model in `alembic-credentials/env.py`
3. Generate migration: `python migrate.py revision-creds "Add new credentials model"`
4. Apply migration: `python migrate.py upgrade`

## Testing

The migration setup includes comprehensive tests in `tests/test_alembic_setup.py`:

```bash
# Run migration tests
python -m pytest tests/test_alembic_setup.py -v
```

Tests verify:

- Configuration files exist and are properly formatted
- Both databases can be migrated successfully
- Model imports work correctly
- Migration files are generated properly
- Async support is configured correctly

## Troubleshooting

### Common Issues

1. **"The asyncio extension requires an async driver"**

   - Ensure your DATABASE_URL uses `postgresql+asyncpg://` not `postgresql://`

2. **"No module named 'app'"**

   - Run migrations from the `backend/` directory
   - Ensure `PYTHONPATH` includes the backend directory

3. **Connection refused**

   - Ensure PostgreSQL containers are running: `docker compose up -d postgres-main postgres-creds`
   - Check database URLs and credentials

4. **Migration conflicts**
   - Use `alembic history` to see migration tree
   - Resolve conflicts manually or create merge migration

### Database Connection Test

```bash
# Test main database connection
docker exec mens-circle-postgres-main psql -U postgres -d mens_circle_main -c "SELECT version();"

# Test credentials database connection
docker exec mens-circle-postgres-creds psql -U postgres -d mens_circle_creds -c "SELECT version();"
```

## Production Deployment

### CI/CD Integration

The GitHub Actions workflow automatically runs migrations:

```yaml
- name: Run database migrations
  run: |
    cd backend
    if [ -f "alembic/env.py" ]; then
      alembic upgrade head
    fi
```

### Manual Production Deployment

1. **Backup databases** before running migrations
2. **Test migrations** on staging environment first
3. **Run migrations** during maintenance window:

```bash
# Production migration commands
python migrate.py current  # Check current state
python migrate.py upgrade  # Apply all pending migrations
```

### Rollback Procedure

```bash
# Rollback both databases by one revision
python migrate.py downgrade

# Or rollback to specific revision
alembic downgrade <revision_id>
alembic -c alembic-credentials.ini downgrade <revision_id>
```

## Security Considerations

1. **Separate Databases**: Credentials are isolated in a separate database
2. **Async Support**: Uses asyncpg driver for better performance and security
3. **Environment Variables**: Database URLs are loaded from environment, not hardcoded
4. **Migration History**: Each database maintains its own migration history
5. **Access Control**: Credentials database can have different access permissions

## Best Practices

1. **Always backup** before running migrations in production
2. **Test migrations** on development/staging first
3. **Use descriptive names** for migration messages
4. **Review generated migrations** before applying
5. **Keep migrations small** and focused on single changes
6. **Don't edit** existing migration files after they've been applied
7. **Use the migration script** for consistency across environments
