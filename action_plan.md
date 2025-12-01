# Module 1: Configuration (Setup, DB, Models) - [COMPLETED]

[X] Task 1.1: Professional backend folder structure.

[X] Task 1.2: Pytest configuration and Test DB (SQLite).

[X] Task 1.3: Smoke test.

[X] Task 1.4: ORM Models (Producto, Lote, Movimiento) and Pydantic Schemas.

[X] Task 1.5: Initialization script (init_db.py).

# Module 2: Product CRUD (API) - [COMPLETED]

[X] Task 2.1-2.3: POST /productos (Create).

[X] Task 2.4-2.6: GET /productos/{id} (Read One) and GET /productos (List).

[X] Task 2.7-2.9: PUT /productos/{id} (Update).

[X] Task 2.10-2.12: DELETE /productos/{id} (Delete).

# Module 3: Inventory Logic (Entries, Exits, FEFO) - [COMPLETED]

[X] Task 3.1-3.3: Register entry (Lote + Movimiento).

[X] Task 3.4-3.6: Register simple exit (by lote_id) + stock validation.

[X] Task 3.7-3.9: GET /lotes/{id}.

[X] Task 3.10-3.12: Smart Dispatch FEFO (First Expired, First Out).

# Module 4: Alert Services (Logic & API) - [COMPLETED]

[X] Task 4.1-4.3: Service and API for "Out of Stock" (Minimum Stock).

[X] Task 4.4-4.6: Service and API for "Expiring Soon" (Lotes near expiration).

# Module 5: Deployment (Docker) - [COMPLETED]

[X] Task 5.1: Multi-stage Dockerfile (python:3.10-slim).

[X] Task 5.2: Build optimization with cache.

# Module 6: Logging Configuration - [COMPLETED]

[X] Task 6.1: Centralized configuration (logging_setup.py).

[X] Task 6.2: Configurable levels per environment (.env).

# Module 7: Logging Integration Refactor - [COMPLETED]

[X] Task 7.1: Full instrumentation of CRUDs and Services.

[X] Task 7.2: Robust error handling (try/except) in endpoints.

# Module 8: Frontend (UI) and Reports (Dash) - [COMPLETED]

[X] Task 8.1: Frontend Structure (app/dashboard/layouts/callbacks).

[X] Task 8.2: Smoke Test (Import).

[X] Task 8.3: Layout and Navigation Callbacks.

[X] Task 8.4: Products Table (Mocking API).

[X] Task 8.5: Products Table Auto-refresh.

[X] Task 8.6 (REFACTOR): Create fixtures for frontend tests (DRY) - HIGH PRIORITY.

[X] Task 8.7 (RED): Alerts Dashboard UI (Layout + Callbacks to connect with Alerts API).

[X] Task 8.8: Inventory Management UI (Forms for Entries and Dispatches).

[X] Task 8.9: Dark Theme Toggle (Frontend).
[X] Task 8.10: Lotes Table UI.
[X] Task 8.11: UX Improvement: Product dropdown for inventory entry.
[X] Task 8.12: UX Improvement: Smart dispatch (FEFO) from UI.

# Module 9: Production Deployment - [COMPLETED] (Revisited and Improved)

[X] Task 9.1: Gunicorn configuration.

[X] Task 9.2: PostgreSQL Configuration (Prod).

[X] Task 9.3: Migration/Initialization script for Prod.

[X] Task 9.4: Deployment Configuration (Render + Supabase).

# Module 10: Optimization and Caching - [PENDING]

[X] Task 10.1: Implement Caching for alerts (invalidation by events).

[X] Task 10.2: Refactor to CQRS pattern (Dedicated Alerts Table for fast reads).

# Module 11: Reporting - [PENDING]

[X] Task 11.1: Basic Inventory Report (current stock per product).
[X] Task 11.2: Expiration Report (lotes nearing expiration).
[X] Task 11.3: Movement Report (ins and outs in a date range).
