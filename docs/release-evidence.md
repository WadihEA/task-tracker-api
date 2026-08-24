# Release Evidence

## Baseline

- Branch: `final-project`
- Date: 2026-08-24
- Local app run command: `python -m uvicorn app.main:app --port 8000` (venv active)
- `/health` result: `HTTP 200` — `{"status":"ok","timestamp":"2026-08-24T20:13:56.157315+00:00"}`
- Frontend check: served `frontend/index.html` locally with `python -m http.server 8080` from
  the `frontend/` directory (API running on `:8000`), opened it in a browser tab. Header showed
  "connected · 0 tasks", confirming a live fetch against the API. Used "+ New Task" to create a
  task titled "Final project baseline check" — it appeared immediately in the To Do column with
  its priority chip and Start/Edit/Delete controls, confirming the create flow still works. Task
  was deleted afterward to leave storage clean.
- Test command: `python -m pytest -q`
- Test result: **76 passed, 0 failed** (0.79s). No pre-existing or newly-introduced failures.

## CI evidence

- Workflow file: `.github/workflows/ci.yml`
- Latest run: success — https://github.com/WadihEA/task-tracker-api/actions/runs/32773887086
  (triggered by the push of this final-project-evidence commit; the prior push also ran green:
  https://github.com/WadihEA/task-tracker-api/actions/runs/32772281272)
- Test command used by CI: `pytest -v --tb=short`
- Shortcut check (read `.github/workflows/ci.yml` directly): no `continue-on-error`, no `|| true`,
  pytest step is not skipped or conditional, Python version is explicitly pinned (`"3.11"`, not a
  floating tag), and `pip install -r requirements.txt` runs before tests. No shortcuts found.

## Docker evidence

- Build command: `docker build -t task-tracker-api:final-project .`
- Run command: `docker run -d --name task-tracker-api-check -p 8000:8000 task-tracker-api:final-project`
- `/health` check: `HTTP 200` — `{"status":"ok","timestamp":"2026-08-24T20:20:29.267291+00:00"}`
  (checked from the host with `curl` against the mapped port)
- Non-root check: `docker exec task-tracker-api-check whoami` → `app`;
  `docker exec ... id` → `uid=1000(app) gid=1000(app) groups=1000(app)`. The Dockerfile's
  `USER app` (line 48) is in effect at runtime, not just declared.
- No-baked-secrets check: `docker exec task-tracker-api-check sh -c "find / -maxdepth 3 -iname '.env*'"`
  → no matches. `.dockerignore` excludes `.env`, `.env.*`, `tests/`, `docs/`, and `.claude/`; the
  runtime image only `COPY`s `app/` (Dockerfile line 37), not the full build context.

## Documentation claim-vs-reality log

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| `GET /health` returns `HTTP 200` (README/AGENTS.md) | Ran the app locally and in Docker, `curl`'d `/health` both times | Confirmed true | None |
| CORS is fully open (`allow_origins=["*"]`) for local use only (AGENTS.md) | Read `app/main.py:19-24` directly | Confirmed true | None — already tracked as an open, accepted tradeoff in `docs/security-review.md`'s backlog |
| "64 tests currently pass" (AGENTS.md, pre-existing claim from before this session) | Ran `pytest -q` | **False when checked** — was stale; this session's hardening pass (field-length caps, `verify_a.py` fix) brought it to 72, and the boundary tests added while writing `docs/final-ai-review.md` brought it to 76 | Updated `AGENTS.md`'s test count to 76 and the file list to include `tests/test_verify_a.py` |
| Dockerfile runs the container as a non-root user (Dockerfile `USER app` line, never previously verified against a running container) | `docker exec ... whoami` / `id` against the built image | Confirmed true | None |
