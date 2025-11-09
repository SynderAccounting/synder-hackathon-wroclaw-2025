#!/bin/bash
# Docker/Podman entrypoint script with database migrations

set -e

echo "========================================"
echo "Product Distribution System - Backend"
echo "Container Startup"
echo "========================================"
echo ""

# Wait for database to be ready
echo "Waiting for database to be ready..."
max_retries=30
retry_count=0
wait_time=2

# Extract database connection details from DATABASE_URL
DB_HOST=$(echo $DATABASE_URL | sed -E 's|.*@([^:]+):.*|\1|')
DB_PORT=$(echo $DATABASE_URL | sed -E 's|.*:([0-9]+)/.*|\1|')
DB_USER=$(echo $DATABASE_URL | sed -E 's|.*://([^:]+):.*|\1|')
DB_NAME=$(echo $DATABASE_URL | sed -E 's|.*/([^?]+).*|\1|')

echo "Database host: $DB_HOST:$DB_PORT"
echo "Database name: $DB_NAME"
echo ""

# Simple approach: just use pg_isready which is more reliable
while [ $retry_count -lt $max_retries ]; do
    if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; then
        echo "✓ Database is ready (pg_isready check passed)"
        # Give it one more second to be absolutely sure
        sleep 1
        break
    fi

    retry_count=$((retry_count + 1))
    if [ $retry_count -eq $max_retries ]; then
        echo "✗ Could not connect to database after $max_retries attempts"
        echo "⚠ Starting application anyway (it may fail if database is not ready)..."
        break
    fi

    echo "Database not ready yet, waiting... (attempt $retry_count/$max_retries)"
    sleep $wait_time
done

# Run database migrations
echo ""
echo "Running database migrations..."
if python -m alembic upgrade head 2>&1; then
    echo "✓ Database migrations completed successfully!"
else
    echo "⚠ Warning: Migration encountered issues"
    echo "Continuing with application startup..."
fi

echo ""
echo "========================================"
echo "Starting application..."
echo "========================================"
echo ""

# Execute the main command (passed as arguments to this script)
exec "$@"
