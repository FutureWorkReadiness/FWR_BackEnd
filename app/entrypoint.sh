#!/bin/bash
set -e

echo "🚀 Starting Future Work Readiness Backend..."
echo "================================================"

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
if [ -z "$DATABASE_URL" ]; then
  echo "❌ ERROR: DATABASE_URL environment variable is not set!"
  exit 1
fi
until psql "$DATABASE_URL" -c "SELECT 1" > /dev/null 2>&1; do
  echo "  Database is unavailable - sleeping..."
  sleep 2
done

echo "✅ Database is ready!"

# Run database migrations
echo "🔄 Running database migrations..."
cd /app && alembic upgrade head

# Run database population
echo "📊 Running database population..."
python3 -c "from app.db_init import auto_populate_if_empty; auto_populate_if_empty()"

# Start FastAPI server
echo "🚀 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

