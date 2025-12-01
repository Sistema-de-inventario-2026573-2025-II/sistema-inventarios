

## Module 9: Production Deployment

### Task 9.1: Gunicorn Configuration

- Updated `backend/gunicorn.conf.py` to use Spanish comments and variable names, aligning with project rules.
- Added a `timeout` setting for Gunicorn workers to enhance stability in production environments.
- Maintained the use of environment variables (`GUNICORN_PROCESSES`, `GUNICORN_THREADS`, `GUNICORN_BIND`, `GUNICORN_LOGLEVEL`, `GUNICORN_TIMEOUT`) for flexible deployment configuration.

### Task 9.2: PostgreSQL Configuration (Prod)

- Verified that `backend/app/core/config.py` already handles dynamic PostgreSQL connection string construction using environment variables.
- Updated `backend/.env_example` to explicitly include `POSTGRES_SERVER`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` environment variables for clearer configuration by developers.
- Clarified in `backend/.env_example` that `DATABASE_URL` for PostgreSQL is automatically constructed when these variables are set.

## Module 10: Optimization and Caching

### Task 10.1: Implement Caching for Alerts (Invalidation by Events)

- Verified that caching for alerts (`check_stock_minimo` and `check_lotes_por_vencer`) was already implemented in `backend/app/services/alerts.py`.
- Confirmed the use of `app.core.cache.MemoryCache` for in-memory caching.
- Noted that `invalidate_pattern` method in `MemoryCache` provides the mechanism for invalidation by events, as per the task requirements.

### Task 10.2: Refactor to CQRS pattern (Dedicated Alerts Table for fast reads)

- Created `backend/app/models/alerta.py` for the new `Alerta` ORM model.
- Created `backend/app/schemas/alerta.py` for the `Alerta` Pydantic schema.
- Modified `backend/app/models/__init__.py` to include the `Alerta` model.
- Verified that `init_db.py` correctly creates the `alertas` table.
- Created `backend/app/crud/crud_alerta.py` with CRUD operations for the `Alerta` model.
- Refactored `check_stock_minimo` in `backend/app/services/alerts.py` to manage `Alerta` table entries.
- Refactored `check_lotes_por_vencer` into `check_lotes_por_vencer_and_manage_alerts` in `backend/app/services/alerts.py` to manage `Alerta` table entries.
- Added `get_alertas_activas_read` in `backend/app/services/alerts.py` to serve as the read model for active alerts.
- Updated API endpoints in `backend/app/api/endpoints/alerts.py` to use `get_alertas_activas_read` and return `List[AlertaInDB]`.
- Rewrote relevant tests in `backend/tests/test_services.py` and `backend/tests/api/test_alerts.py` to align with the new CQRS-based alert management.
