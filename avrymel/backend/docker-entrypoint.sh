#!/bin/bash
# Database initialization script

echo "🔧 Waiting for PostgreSQL to be ready..."
until pg_isready -h $POSTGRES_HOST -p ${POSTGRES_PORT:-5432} -U $POSTGRES_USER 2>/dev/null; do
  echo "⏳ Waiting for PostgreSQL..."
  sleep 2
done

echo "✅ PostgreSQL is ready!"

echo "🔄 Running database migrations..."
cd /app
alembic upgrade head

echo "👤 Initializing default data..."
python scripts/init_db.py

echo "🚀 Starting application..."
exec python run.py
