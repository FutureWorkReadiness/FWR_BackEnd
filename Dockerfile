FROM python:3.11-slim

# Install PostgreSQL client for health checks
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY ./app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (use . to copy contents, not directory itself)
COPY ./app/. /app/

# Copy data files for population (must be in Backend/data relative to app directory)
COPY ./data /app/data
COPY ./alembic /app/alembic
COPY ./alembic.ini /app/alembic.ini

# Copy and make entrypoint script executable (ensure it's in the right location)
COPY ./app/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# Use entrypoint script that waits for DB and runs population
CMD ["/app/entrypoint.sh"]