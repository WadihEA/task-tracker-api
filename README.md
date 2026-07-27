# Task Tracker API

FastAPI + Pydantic Task Tracker with a vanilla-JS Kanban frontend (in-memory
storage). Built across Modules 1–3 and extended in the mid-course project.

Health check, full task CRUD, status-transition rules (Done is terminal), and a
drag-and-drop Kanban board. Authentication, a real database, Docker, and
deployment remain out of scope.

## Mid-Course features (branch `mid-course-project`)

- **Due dates + overdue** — optional `due_date` (`YYYY-MM-DD`); the API returns a
  computed `overdue` flag (past due **and** not Done). Filter with
  `GET /tasks?overdue=true`. Cards show a red ⚠ overdue pill / neutral 📅 date pill;
  the board has an "Overdue only" toggle.
- **Tags / labels** — validated `tags: list[str]` (trimmed, de-duped, ≤10 tags,
  ≤30 chars each). Filter with `GET /tasks?tag=<name>` (case-insensitive). Cards
  render tag chips; the board has a "Filter by tag…" box.

See [`docs/midcourse/`](docs/midcourse/) for user stories, the mini-ADR, the prompt
log, verification (incl. Break Tests), and the reflection.

## Structure

    app/
      api/              health route
      core/             configuration and shared settings
      main.py           FastAPI app + task routes
      models.py         Pydantic models (Task create/update/response, enums)
      business_rules.py status-transition rules
      storage.py        in-memory task store
    frontend/
      index.html        self-contained Kanban board (no build step)
    tests/              pytest suite
    docs/midcourse/     mid-course project documentation

## Setup

    cd C:\Users\wadih\OneDrive\Desktop\AUB\proj\task-tracker-api
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    Copy-Item .env.example .env

## Run the backend

    python -m uvicorn app.main:app --reload --port 8000

Swagger UI: http://127.0.0.1:8000/docs · Health: http://127.0.0.1:8000/health

## Open the frontend

With the backend running, open `frontend/index.html` in a browser (double-click,
or `start frontend/index.html` on Windows). It talks to the API at
`http://localhost:8000`; CORS is enabled for local use.

## Run the tests

    python -m pytest            # full suite (61 tests)
    python -m pytest -q         # quiet

Tests use FastAPI's `TestClient`; storage is reset between tests by an autouse
fixture in `tests/conftest.py`.
