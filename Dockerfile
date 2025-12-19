FROM python:3.11-slim

# Install PostgreSQL client for health checks
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies first (for Docker layer caching)
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the geminiGenerator package and install it in editable mode
# This allows the package to be imported as 'gemini_pkg' throughout the project
COPY ./geminiGenerator /app/geminiGenerator
RUN pip install -e ./geminiGenerator

# Copy application code (new structure)
COPY ./src /app/src

# Copy data files for seeding
COPY ./data /app/data

# Copy seeds
COPY ./seeds /app/seeds

# Copy alembic for migrations
COPY ./alembic /app/alembic
COPY ./alembic.ini /app/alembic.ini

# Copy seed database script
COPY ./seed_database.py /app/seed_database.py

# Copy and make entrypoint script executable
COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# Use entrypoint script that waits for DB and runs population
CMD ["/app/entrypoint.sh"]
