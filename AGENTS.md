# AGENTS.md — Task Tracker API

## 1. Project summary

A FastAPI + Pydantic REST API for tracking tasks, backed by **in-memory storage**
(no database). It began as a Module 1 learning project and was extended through
a mid-course project on branch `mid-course-project` (due dates/overdue, tags).
A self-contained vanilla-JS Kanban frontend (`frontend/index.html`, no build step)
consumes the API from the browser. Authentication, a real database, and
deployment are explicitly out of scope per `README.md`.

## 2. Tech stack and commands

- **Stack**: Python, FastAPI, Pydantic v2, Uvicorn, `python-dotenv`, pytest,
  httpx (via `requirements.txt` — there is no `pyproject.toml`).
- **Setup**:
  ```
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  python -m pip install -r requirements.txt
  Copy-Item .env.example .env
  ```
- **Run the API**:
  ```
  python -m uvicorn app.main:app --reload --port 8000
  ```
  Swagger UI: `http://127.0.0.1:8000/docs` · Health check: `GET /health`
- **Run tests**:
  ```
  python -m pytest -q
  ```
  76 tests currently pass (`tests/test_tasks.py`, `tests/test_health.py`,
  `tests/test_verify_a.py`).
- **Frontend**: open `frontend/index.html` directly in a browser while the API
  is running; it calls `http://localhost:8000` and CORS is wide open
  (`allow_origins=["*"]`) for local use only.
- Config: `app/core/config.py` reads `APP_ENV` and `PORT` from `.env` via
  `python-dotenv` (see `.env.example`). No other configurable settings found.
- Docker/CI: confirmed present. `Dockerfile` builds from `python:3.11-slim`,
  installs `requirements.txt` (pinned versions), and runs uvicorn on 8000.
  `.github/workflows/ci.yml` installs `requirements.txt` and runs
  `pytest -v --tb=short` on every push and on PRs into `main`.

## 3. Business rules visible in the code

- **Task fields** (`app/models.py`): `title` (required, 1–200 chars, trimmed,
  blank rejected), `description` (optional, defaults to `""`), `status`,
  `priority`, `assignee` (optional), `due_date` (optional `date`), `tags`
  (list of strings). All request models use `extra="forbid"` — unknown fields
  are rejected with 422.
- **`TaskStatus` enum**: `ToDo`, `InProgress`, `Done`.
- **`TaskPriority` enum**: `Low`, `Medium`, `High`.
- **Status transitions** (`app/business_rules.py`, `VALID_TRANSITIONS`): only
  `ToDo → InProgress` and `InProgress → Done` are allowed. Any other pair,
  including same-status and any move out of `Done`, returns 422 — **`Done` is
  terminal**. Transitions are only checked on `PATCH` when `status` is
  included in the payload; `POST /tasks` does not validate transitions, so a
  task can be created directly in any status.
- **Tags** (`_normalize_tags` in `app/models.py`): trimmed, blank tags
  rejected, de-duplicated, max 10 tags, max 30 chars each.
- **`overdue`** (`TaskResponse.overdue`, computed field): `true` only when
  `due_date` is in the past **and** `status != Done`.
- **PATCH null-title guard**: `TaskUpdate` has a `model_validator(mode="before")`
  that rejects an explicit `{"title": null}` with 422 while still allowing
  `title` to be omitted for a partial update.
- **IDs**: assigned by a monotonic counter in `app/storage.py` (`_next_id`,
  stringified), not by list length — ids are never recycled after a delete.
- **Endpoints** (`app/main.py`): `POST /tasks` (201), `GET /tasks` (200,
  optional `status`/`priority`/`tag`/`overdue` filters, empty list is not a
  404), `GET /tasks/{id}` (200/404), `PATCH /tasks/{id}` (200/404/422),
  `DELETE /tasks/{id}` (204, empty body), `GET /health` (200).
- **404 detail format**: `f"Task with id {task_id} not found"`.

## 4. Module 5 guardrails (Codex App)

- **Docs-first**: default to reading and explaining, not changing. Prefer
  producing/updating documentation (like this file) over touching runtime code.
- **Read-only by default**: do not create, edit, or delete any file other than
  `AGENTS.md` unless the user has explicitly approved that specific change in
  this thread.
- **One task per thread**: keep each Codex thread scoped to a single,
  clearly-stated task. Do not pull in unrelated fixes or drive-by refactors.
- **No `app/` changes without explicit approval**: `app/main.py`,
  `app/models.py`, `app/storage.py`, `app/business_rules.py`, `app/core/`, and
  `app/api/` are off-limits for edits unless the user explicitly asks for a
  change in that file, in that thread.

## 5. Security and governance reminders

- **Never paste, log, or expose secrets.** `.env` is gitignored and holds only
  `PORT`/`APP_ENV` today, but treat any future credentials the same way —
  never echo `.env` contents into chat, commits, or generated docs.
- **Do not run destructive commands** (`rm -rf`, `git reset --hard`,
  force-push, dropping/clearing storage in a running instance, etc.) without
  explicit user confirmation for that exact command.
- **Always cite files and line numbers** for claims about behavior (e.g.
  `app/business_rules.py:5-8`) rather than describing code from memory.
- **Do not invent findings.** If a command, dependency, or business rule is
  not directly visible in the inspected files, mark it **"not confirmed"**
  instead of guessing or inferring from similar projects.
