# Database Management

This document explains how to manage the PostgreSQL database with Alembic migrations.

## Database Schema

### Products Table

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key (auto-generated) |
| name | String(255) | Product name (indexed) |
| category | String(100) | Product category (indexed) |
| orig_price | Numeric(10,2) | Original price |
| selling_price | Numeric(10,2) | Actual selling price |
| platform | String(100) | Sales platform (indexed) |
| date_of_selling | DateTime(TZ) | Date and time of sale (indexed) |
| country_of_selling | String(100) | Country of sale (indexed) |
| created_at | DateTime(TZ) | Record creation timestamp |
| updated_at | DateTime(TZ) | Record update timestamp |

## Initial Setup

### 1. Start PostgreSQL Database

**Using Podman/Docker:**
```bash
# Start the database container
./start-podman.sh  # or .\start-podman.ps1 on Windows

# The database will be available at:
# - Host: localhost
# - Port: 5432
# - Database: product_distribution
# - User: user
# - Password: password
```

**Using Local PostgreSQL:**
```bash
# Make sure PostgreSQL is running and create the database
psql -U postgres
CREATE DATABASE product_distribution;
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update the database URL:

```env
# For local PostgreSQL
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/product_distribution

# For Docker/Podman (when running app in container)
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/product_distribution
```

### 3. Run Migrations

**Option A: Using the init script (Recommended):**
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\Activate.ps1  # Windows PowerShell

# Run initialization script
python init_db.py
```

**Option B: Using Alembic directly:**
```bash
# Apply all migrations
alembic upgrade head

# Check current migration version
alembic current

# View migration history
alembic history
```

## Common Migration Commands

### Create a New Migration

After modifying models in `app/models/`, generate a new migration:

```bash
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Upgrade to specific version
alembic upgrade <revision_id>
```

### Rollback Migrations

```bash
# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

### View Migration Info

```bash
# Show current version
alembic current

# Show migration history
alembic history --verbose

# Show pending migrations
alembic current
alembic heads
```

## Database Connection in Code

### Using Dependency Injection (Recommended)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models import Product

router = APIRouter()

@router.get("/products")
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return products
```

### Direct Session Usage

```python
from app.core.database import AsyncSessionLocal
from app.models import Product

async def some_function():
    async with AsyncSessionLocal() as session:
        try:
            # Your database operations
            result = await session.execute(select(Product))
            products = result.scalars().all()
            await session.commit()
            return products
        except Exception:
            await session.rollback()
            raise
```

## Troubleshooting

### Connection Refused

If you get "connection refused" errors:

1. Check if PostgreSQL is running:
   ```bash
   # For Podman/Docker
   podman ps  # or docker ps

   # For local PostgreSQL
   pg_isready -h localhost -p 5432
   ```

2. Verify the DATABASE_URL in `.env` matches your setup

3. Check firewall settings allow connections to port 5432

### Migration Conflicts

If migrations get out of sync:

```bash
# Check current state
alembic current

# If needed, manually set to a specific version
alembic stamp <revision_id>

# Then upgrade as normal
alembic upgrade head
```

### Reset Database (DESTRUCTIVE)

**Warning: This will delete all data!**

```bash
# Stop containers
./start-podman.sh --down

# Remove volumes (deletes all data)
podman compose down -v  # or docker compose down -v

# Start fresh
./start-podman.sh --build
python init_db.py
```

## Best Practices

1. **Always review generated migrations** before applying them
2. **Test migrations** on development/staging before production
3. **Backup production database** before running migrations
4. **Never edit applied migrations** - create new ones instead
5. **Use transactions** for data migrations
6. **Keep migrations small** and focused on one change
7. **Add descriptive comments** in migration messages

## Production Deployment

For production environments:

1. Backup the database first
2. Run migrations in a maintenance window if possible
3. Test rollback procedure
4. Monitor application logs during and after migration
5. Have a rollback plan ready

```bash
# Production migration workflow
pg_dump production_db > backup_$(date +%Y%m%d).sql
alembic upgrade head
# Monitor application
# If issues: alembic downgrade -1
```
