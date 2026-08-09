# Containerize the Task Tracker API with a Multi-Stage, Non-Root Dockerfile and Gate Merges with CI

## Context

Before this change, `README.md` stated plainly that "Docker, and deployment remain out of scope" (README.md, lines 7–8). The FastAPI app in `app/main.py` already exposed a `/health` route (via `app.include_router(health_router)`) and a full task CRUD surface (`create_task`, `list_tasks`, `get_task`, `update_task`, `delete_task`), and `app/models.py` already enforced request validation through Pydantic (`TaskCreate`, `TaskUpdate`, field and model validators like `reject_explicit_null_title`). The pytest suite (61+ tests per `README.md`, line 59) only ran locally — there was no `Dockerfile`, no `.dockerignore`, and no `.github/workflows/` directory, so there was no reproducible way to package the app for another machine and no automated gate verifying that a push or pull request didn't break the suite.

## Decision

Package the app as a multi-stage Docker image — a `python:3.11-slim` builder stage that installs dependencies into `/opt/venv`, and a `python:3.11-slim` runtime stage that copies only the venv and `app/` source, runs as a fixed-UID non-root user, and health-checks `GET /health` — and add `.github/workflows/ci.yml` to run `pytest -v --tb=short` on every push and every pull request into `main`.

## Alternatives Considered

- **Single-stage Dockerfile** (`FROM python:3.11-slim`, `pip install` directly, run as root): rejected because it leaves pip's build/download cache and the default root user in the final image — unnecessary size and an avoidable privilege escalation surface for a network-facing process (`CMD ["uvicorn", "app.main:app", ...]`).
- **`curl`-based `HEALTHCHECK`** (`CMD curl -f http://127.0.0.1:8000/health || exit 1`): rejected because it requires installing `curl` into the slim runtime image for no functional gain; the stdlib `urllib.request` call in the current `HEALTHCHECK` does the same GET/status check with zero added packages.
- **No CI, rely on manual `pytest` before merge**: rejected because it depends on a contributor remembering to run the suite; a workflow triggered on `push`/`pull_request` makes the check unconditional and visible on GitHub regardless of who forgets.
- **Matrix CI across multiple Python versions/OSes**: rejected as unnecessary scope — the `Dockerfile` pins a single target (`python:3.11-slim`), so testing against other interpreters or OSes would add job time without a corresponding deployment target.

## Trade-offs

- The multi-stage `Dockerfile` is more complex to read and modify than a single-stage one — a contributor changing `requirements.txt` needs to understand that installation happens in the `builder` stage and is copied via `COPY --from=builder /opt/venv /opt/venv`, not installed directly in `runtime`.
- `RUN chown -R app:app /app` only takes ownership of `/app`, not `/opt/venv`; this is fine for the current stateless, in-memory design (`app/storage.py`'s module-level `_tasks` dict), but if the app later needs to write inside `/app` (a log file, an on-disk store) the permission model will need revisiting.
- `ci.yml` only runs `pytest`; it does not `docker build` the image. A syntax error or a bad `COPY` path in the `Dockerfile` will not fail CI — Docker correctness still depends on someone building it manually.
- The `HEALTHCHECK` only proves `/health` responds; it says nothing about `app/main.py`'s task routes. A regression in `storage.add_task` or `validate_status_transition` would not flip the container to `unhealthy`.
- `actions/cache@v4` is keyed only on `hashFiles('requirements.txt')` (`ci.yml`, lines 18–21). Since `requirements.txt` pins no versions, the cache key doesn't change when `pip` resolves a new transitive release — the cache speeds up repeat installs but doesn't make them reproducible.
- Triggering CI on `push` to any branch (`ci.yml`, line 4, no branch filter) means every branch push consumes a CI run, not just work headed toward `main`.

## Consequences

- Any new route added to `app/main.py` or dependency added to `requirements.txt` is exercised by `pytest -v --tb=short` on every push, so regressions surface before merge rather than after.
- The image builds and runs consistently across machines: verified locally, the container transitioned from Docker's `starting` to `healthy` status and served `/health` and `/` correctly under the non-root `app` user (UID 1000).
- `.dockerignore` excludes `tests/`, `docs/`, `.claude/`, `.git`, `.github`, and `venv/`, and the `Dockerfile` never `COPY`s `.env` — secrets and dev-only artifacts are structurally excluded from every image layer, not just from the final `COPY app ./app` step.
- The `app` user's UID (1000) becomes an implicit contract: any future orchestration config (e.g., a Kubernetes `securityContext` or a bind-mounted volume) that assumes a specific UID must match 1000 or ownership will mismatch.

## Open Questions

- Should CI add a `docker build .` step so a broken `Dockerfile` is caught automatically, rather than relying on someone building it by hand before it's needed?
- Should `requirements.txt` be pinned or replaced with a lockfile so the `pip-${{ hashFiles('requirements.txt') }}` cache key and the versions actually installed in CI stay reproducible across runs?
- If `app/storage.py` moves off the in-memory `_tasks` dict to a file-backed or database store, does the current `chown -R app:app /app`-only ownership model still work, or does it need a writable volume with a broader `chown` scope?
- Is a single `HEALTHCHECK` against `/health` sufficient long-term, or will an orchestrator eventually need a separate liveness vs. readiness probe that also exercises the `/tasks` routes?
