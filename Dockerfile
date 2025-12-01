# Stage 1: Builder - Installs dependencies
FROM python:3.10-slim-buster AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install uv and create virtual environment
RUN pip install uv && uv venv "$VIRTUAL_ENV"

# Set the working directory
WORKDIR /app

# Copy dependency definition files
COPY pyproject.toml uv.lock ./

# Install dependencies into the virtual environment using uv
RUN uv pip install --system --no-cache-dir --requirement pyproject.toml

# Stage 2: Final - Runs the application
FROM python:3.10-slim-buster

# Set the working directory
WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Activate the virtual environment
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy the backend application code
COPY ./backend /app/backend

# Copy the gunicorn configuration into the backend directory
COPY ./backend/gunicorn.conf.py /app/backend/gunicorn.conf.py

# Copy the frontend application code
COPY ./frontend /app/frontend

# Command to run the application using Gunicorn
CMD ["gunicorn", "-c", "backend/gunicorn.conf.py", "backend.main:app"]
