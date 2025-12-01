

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

### Bugfix: API Error 500 on Alerts Dash Tab

- Added `joinedload(LoteModel.producto)` to `check_lotes_por_vencer_and_manage_alerts` in `backend/app/services/alerts.py` to ensure eager loading of related product data, preventing potential `None` errors.
- Implemented defensive checks for `lote.producto.nombre` and `lote.producto.sku` to handle cases where related product might be missing.
- Wrapped alert management functions (`check_stock_minimo`, `check_lotes_por_vencer_and_manage_alerts`) with `try-except` blocks in `backend/app/services/alerts.py` for robust error logging without re-raising.
- Added a `try-except` block to `get_alertas_activas_read` in `backend/app/services/alerts.py` to catch unexpected errors and raise an `HTTPException(500)`.
- Implemented `try-except` blocks in API endpoints (`get_low_stock_alerts`, `get_expiring_lotes_alert`) in `backend/app/api/endpoints/alerts.py` to catch and re-raise `HTTPException` or raise a generic `HTTPException(500)` for other errors.

### Module 8: Frontend (UI) and Reports (Dash)

#### Task 8.9: Dark Theme Toggle (Frontend)

- Added a `dbc.Switch` component for theme toggling to `frontend/layouts.py` (sidebar).
- Modified `frontend/app.py` to include `dcc.Store` for theme preference and `html.Link` for dynamic stylesheet loading, along with a `THEMES` dictionary.
- Implemented `toggle_theme` callback in `frontend/callbacks.py` to switch between light and dark themes using `dcc.Store` and updating the stylesheet link.
- Corrected import path for `THEMES` in `frontend/callbacks.py` to `from frontend.app import THEMES`.

#### Task 8.10: Lotes Table UI

- Added a `dash_table.DataTable` component for displaying lots to `inventory_layout` in `frontend/layouts.py`.
- Defined `columnas_lotes` for the lot table columns (ID, Product SKU, Received Quantity, Current Quantity, Expiration Date).
- Implemented `update_lotes_table` callback in `frontend/callbacks.py` to fetch lot data from the backend API (`/lotes`), process it to include `producto_sku`, and populate the table.
- Added `dcc.Interval` and `dbc.Button` to `inventory_layout` for auto and manual refresh of the lot table.

#### Task 8.11: UX Improvement: Product dropdown for inventory entry

- Replaced the "Producto ID" `dbc.Input` with a `dcc.Dropdown` (`entry-product-dropdown`) in `frontend/layouts.py`.
- Added a hidden `dcc.Input` (`entry-product-id`) to store the selected product ID.
- Implemented `update_product_dropdown_options` callback in `frontend/callbacks.py` to fetch products from `/productos` API and populate the dropdown.
- Implemented `update_selected_product_id` callback in `frontend/callbacks.py` to update the hidden input with the dropdown's selection.
- Modified `register_inventory_entry` callback to use the value from the hidden `entry-product-id` input.

#### Task 8.12: UX Improvement: Smart dispatch (FEFO) from UI

- Replaced the "Producto ID" `dbc.Input` with a `dcc.Dropdown` (`dispatch-fefo-product-dropdown`) in `frontend/layouts.py` for the FEFO dispatch section.
- Added a hidden `dcc.Input` (`dispatch-fefo-product-id`) to store the selected product ID for FEFO dispatch.
- Implemented `update_fefo_product_dropdown_options` callback in `frontend/callbacks.py` to fetch products from `/productos` API and populate the FEFO dispatch dropdown.
- Implemented `update_fefo_selected_product_id` callback in `frontend/callbacks.py` to update the hidden input with the dropdown's selection for FEFO dispatch.
- Modified `register_fefo_dispatch` callback to use the value from the hidden `dispatch-fefo-product-id` input.

## Module 11: Reporting

### Task 11.1: Basic Inventory Report (current stock per product)

- Created `backend/app/api/endpoints/reports.py` with an endpoint `/api/v1/reportes/inventario-basico` to serve the report data.
- Integrated `reports.router` into the main API router in `backend/app/api/api.py`.
- Created `backend/app/services/reports.py` with `get_current_stock_per_product` service function to fetch product stock data.
- Added a new navigation link "Reportes" to the `sidebar_layout` in `frontend/layouts.py`.
- Defined `columnas_reporte_inventario_basico` and `reports_layout` in `frontend/layouts.py` to display the report table.
- Implemented `update_basic_inventory_report_table` callback in `frontend/callbacks.py` to fetch report data and populate the table.

### Task 11.2: Expiration Report (lotes nearing expiration)

- Added a new API endpoint `/api/v1/reportes/lotes-por-vencer` to `backend/app/api/endpoints/reports.py` to serve the expiration report data.
- Corrected the `response_model` and type hint for `get_expiring_lotes_report` in `backend/app/api/endpoints/reports.py` to use `app.schemas.lote.Lote`.
- Implemented `get_expiring_lotes_report` service function in `backend/app/services/reports.py` to fetch expiring lot data, including product information.
- Defined `columnas_reporte_lotes_por_vencer` in `frontend/layouts.py` and added a `dash_table.DataTable` to `reports_layout` to display the expiration report.
- Implemented `update_expiring_lotes_report_table` callback in `frontend/callbacks.py` to fetch expiration report data and populate the table.

### Task 11.3: Movement Report (ins and outs in a date range)

- Added a new API endpoint `/api/v1/reportes/movimientos-por-rango-fecha` to `backend/app/api/endpoints/reports.py` to serve the movement report data.
- Added missing imports for `date` and `movimiento_schema` in `backend/app/api/endpoints/reports.py`.
- Implemented `get_movement_report_by_date_range` service function in `backend/app/services/reports.py` to fetch movement data within a specified date range, including product and lot information.
- Defined `columnas_reporte_movimientos` in `frontend/layouts.py` and added a `dash_table.DataTable` to `reports_layout` to display the movement report, along with date range pickers.
- Implemented `update_movement_report_table` callback in `frontend/callbacks.py` to fetch movement report data and populate the table.

## Module 9: Production Deployment (Revisited)

- **Dockerfile Improvements:**
    - Refactored dependency management to use a virtual environment (`/opt/venv`) within the builder stage and copied it to the final stage for better isolation and portability.
    - Modified `Dockerfile` to copy `gunicorn.conf.py` into the `backend` directory (`/app/backend/gunicorn.conf.py`) for better organization.
    - Added copying of `frontend` application code (`COPY ./frontend /app/frontend`).
    - Updated `CMD` to reference `gunicorn.conf.py` from its new location (`backend/gunicorn.conf.py`).
- **docker-compose.yml Improvements:**
    - Added a `frontend` service that builds from the same `Dockerfile`, exposes port `8050`, and runs `frontend/app.py`. It depends on the `backend` service and sets `API_BASE_URL` to point to the backend service within the Docker network.
    - Integrated database initialization (`init_db.py`) into the `backend` service's `command` using `bash -c "/opt/venv/bin/python /app/backend/app/db/init_db.py && ..."`, ensuring it runs before Gunicorn starts.
    - Added a `healthcheck` to the `backend` service to ensure it's healthy before the `frontend` starts.

### Task 9.4: Deployment Configuration (Render + Supabase)

- Created `render.yaml` to define Backend and Frontend services for Render's Blueprint system.
- Updated `backend/gunicorn.conf.py` to respect the `PORT` environment variable provided by Render.
- Updated `frontend/app.py` to bind to `0.0.0.0` and use the `PORT` environment variable.
- Enhanced `frontend/ui_config.py` to automatically append `/api/v1` to `API_BASE_URL` if missing (fixing `fromService` injection).
- Created `DEPLOY.md` with step-by-step instructions for setting up Supabase (DB) and Render.

