# TDD PHILOSOPHY (TEST-DRIVEN DEVELOPMENT)

- Strict Cycle: RED (Test fails) -> GREEN (Minimum code to pass) -> REFACTOR (Improve without changing behavior).
- Golden Rule: NEVER write implementation code without first having a failing test that proves its absence.
- Testing Pyramid: Prioritize fast, isolated unit tests, then integration tests

# LANGUAGE AND COMMUNICATION

- Agent: Communicates exclusively in ENGLISH.
- Project: All code, variable names, comments, and docstrings, must be in SPANISH.

# TOOLS AND VERSION CONTROL

- Package Manager: Use EXCLUSIVELY uv.
  - Add dep: uv add <package>
  - Sync: uv sync
- GIT (Mandatory):
  - Atomic and frequent commits (ideally one per TDD step).
  - Clear messages: "test(products): add test for creation", "feat(products): implement POST endpoint".
- Docker: Use multi-stage Dockerfile for lightweight builds.

# ARCHITECTURE AND BEST PRACTICES

- Backend (FastAPI):
  - Separation of Concerns (SoC): Strict layers (API -> Service/CRUD -> Models).
  - Dependency Injection: Use Depends() for DB and complex logic.
  - Error Handling: Use custom exceptions in business logic and HTTPException only in the API layer.
- Frontend (Dash):
  - Modular Structure: Separate app (entrypoint), layouts (view), callbacks (logic).
  - Testing: ALWAYS mock API calls (requests) to isolate the frontend.
- Code Quality:
  - Type Hints in 100% of functions.
  - Robust Logging: DEBUG for trace, INFO for events, WARNING for client errors, ERROR for internal failures.