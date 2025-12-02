#!/bin/bash
set -e

# Run database migrations/initialization
echo "Running database initialization..."
/opt/venv/bin/python /app/backend/app/db/init_db.py

# Start Gunicorn
echo "Starting Gunicorn..."
# exec replaces the shell with the gunicorn process, allowing it to receive signals (like SIGTERM) correctly
exec /opt/venv/bin/gunicorn -c /app/backend/gunicorn.conf.py backend.main:app
