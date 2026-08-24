# Task Tracker API

FastAPI + Pydantic Task Tracker with a vanilla-JS Kanban frontend (in-memory
storage). Built across Modules 1–3 and extended in the mid-course project.

Health check, full task CRUD, status-transition rules (Done is terminal), and a
drag-and-drop Kanban board. Authentication and a real database remain out of
scope; Docker and CI are covered below and in the Final Project section.

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

    python -m pytest            # full suite (76 tests)
    python -m pytest -q         # quiet

Tests use FastAPI's `TestClient`; storage is reset between tests by an autouse
fixture in `tests/conftest.py`.

## Run with Docker

    docker build -t task-tracker-api .
    docker run -d --name task-tracker-api -p 8000:8000 task-tracker-api
    curl http://127.0.0.1:8000/health

The image runs as a non-root user and only copies `app/` into the final layer
(no `.env`, tests, or docs). See `Dockerfile` and `.dockerignore`.

## Final Project

Branch reviewed: `final-project`

### What this submission demonstrates

- Existing Task Tracker app still runs inside the intended course scope.
- CI runs the pytest suite on push and/or pull request.
- Docker image builds and runs with `/health` returning 200.
- AI review, security, and ownership evidence is in `docs/`.

### How to run locally

    python -m venv venv
    .\venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    Copy-Item .env.example .env
    python -m uvicorn app.main:app --port 8000

### How to run tests

    python -m pytest -q

### How to run with Docker

    docker build -t task-tracker-api:final-project .
    docker run -d --name task-tracker-api-check -p 8000:8000 task-tracker-api:final-project
    curl http://127.0.0.1:8000/health

### Evidence files

- [`docs/release-evidence.md`](docs/release-evidence.md)
- [`docs/final-ai-review.md`](docs/final-ai-review.md)
- [`docs/ai-playbook.md`](docs/ai-playbook.md)

### AI assistance summary

AI helped draft or review: CI/Docker verification steps, docs, security review grading, and this
hardening pass (field-length caps, dependency pinning, test coverage).

I verified the work by: running the full pytest suite (76 passing), building and running the
Docker image and checking `/health` and the container's runtime user directly, opening the
frontend against a live API and exercising the create flow, and checking the latest GitHub
Actions run for `final-project`.

One AI suggestion I rejected or corrected: an earlier `TaskUpdate` implementation allowed
`{"title": null}` to silently blank a task's title; corrected with an explicit
`model_validator` that rejects that case while still allowing `title` to be omitted. See
`docs/final-ai-review.md` for the full write-up.
