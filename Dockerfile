# Stage 1: Builder
FROM python:3.10-slim-bookworm AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Environment variables for uv
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy dependency files first (better layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies into .venv
# --frozen: Sync strictly from uv.lock
# --no-install-project: We only want dependencies, not the app itself yet
RUN uv sync --frozen --no-install-project

# Stage 2: Final
FROM python:3.10-slim-bookworm

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY ./backend /app/backend
COPY ./frontend /app/frontend

# Ensure start script is executable
RUN chmod +x /app/backend/start.sh

# Command to run the application
CMD ["/app/backend/start.sh"]