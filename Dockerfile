# Stage 1: Builder - Installs dependencies
FROM python:3.10-slim-buster AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install uv
RUN pip install uv

# Set the working directory
WORKDIR /app

# Copy dependency definition files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv pip install --system --no-cache --requirement pyproject.toml

# Stage 2: Final - Runs the application
FROM python:3.10-slim-buster

# Set the working directory
WORKDIR /app

# Copy the installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the backend application code
COPY ./backend /app/backend

# Copy the gunicorn configuration
COPY ./backend/gunicorn.conf.py /app/gunicorn.conf.py

# Command to run the application using Gunicorn
CMD ["gunicorn", "-c", "gunicorn.conf.py", "backend.main:app"]
