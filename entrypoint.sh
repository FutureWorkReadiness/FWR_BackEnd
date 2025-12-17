#!/bin/bash
set -e

echo "🚀 Starting Future Work Readiness Backend..."

# Wait for database
echo "⏳ Waiting for database to be ready..."
while ! pg_isready -h ${DB_HOST:-postgres} -p ${DB_PORT:-5432} -U ${DB_USER:-fw_user} > /dev/null 2>&1; do
  echo "  Database is unavailable - sleeping..."
  sleep 2
done
echo "✅ Database is ready!"

# Run migrations
echo "🔄 Running database migrations..."
cd /app && alembic upgrade head || echo "⚠️  Migration skipped (tables may already exist)"

# Create tables using central models registry
echo "📊 Creating tables..."
cd /app && python3 -c "
from src.app.db.session import engine
from src.app.db.base import Base
from src.app.db.models import *  # Import all models from central registry
Base.metadata.create_all(bind=engine)
print('✅ Tables created/verified')
"

# Auto-seed
echo "🌱 Auto-seeding if database is empty..."
cd /app && python3 -c "from seeds.base import auto_seed_if_empty; auto_seed_if_empty()"

# Start server
echo "🚀 Starting FastAPI server..."
exec uvicorn src.app.main:app --host 0.0.0.0 --port ${PORT:-8000} --reload
