#!/bin/bash
set -e

# Add backend directory to PYTHONPATH so imports like 'from app.main' work
export PYTHONPATH=$PYTHONPATH:/app/backend

# Run database migrations/initialization
echo "Running database initialization..."
/app/.venv/bin/python /app/backend/app/db/init_db.py

# Start Gunicorn
echo "Starting Gunicorn..."
# exec replaces the shell with the gunicorn process, allowing it to receive signals (like SIGTERM) correctly
exec /app/.venv/bin/gunicorn -c /app/backend/gunicorn.conf.py backend.main:app
