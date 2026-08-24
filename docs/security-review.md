# Security Review

## AI Findings

| ID | Severity | File / location | Finding | Evidence | Suggested next step | Confidence | Grade | Reason |
|----|----------|------------------|---------|----------|----------------------|------------|-------|--------|
| F1 | Medium | `app/models.py:63,66,96,100` (`TaskCreate`/`TaskUpdate`) | `description` and `assignee` accept unbounded-length strings — only `title` (`max_length=200`) and `tags` (`MAX_TAG_LENGTH=30`) are capped. | `title: str = Field(..., min_length=1, max_length=200)` vs. `description: Optional[str] = ""` and `assignee: Optional[str] = None` — neither has a `Field(max_length=...)` or validator. | Add a `max_length` (Field or validator) to `description`/`assignee`, mirroring the pattern already used for `title`. | High | Accurate | Confirmed directly in the model code; severity is correctly scoped as Medium since real impact only materializes combined with F2/F3, not as a standalone critical. |
| F2 | Medium | `app/storage.py:8` (`_tasks` dict); no request-size config in `app/main.py` | No cap on total stored tasks and no request-body size limit at the app/server level. Combined with F1, an unauthenticated client could grow process memory unbounded by repeated large `POST /tasks`. | `_tasks: dict[str, TaskResponse] = {}` has no size guard; uvicorn is started with no `--limit-*` flags in README/Dockerfile `CMD`. | If ever exposed beyond a local/course machine, add a body-size limit (proxy or Starlette middleware) and/or a max-task-count guard. | Medium | Accurate | The gap is real, but the "Medium" confidence already hedges that exploitability is low for a single-user local/course tool — didn't overstate it as a standalone production-grade DoS. |
| F3 | Info | `app/main.py` (all routes) | No authentication/authorization on any endpoint — every task can be created/read/updated/deleted by anyone who can reach the port. | No auth dependency/middleware anywhere in `app/main.py`; `README.md:7-8` explicitly states "Authentication… remain out of scope." | None required for course scope; call out explicitly before any deployment beyond localhost. | High | Accurate | Correctly identified as an intentional, documented course-scope decision rather than a bug, per the rubric's explicit instruction not to flag this as a flaw. |
| F4 | Medium | `app/main.py:19-24` (`CORSMiddleware`) | CORS is fully open: `allow_origins=["*"]`, `allow_methods=["*"]`, `allow_headers=["*"]` (no `allow_credentials`, defaults `False`). | The middleware block and its own comment about tightening before real deployment. | Keep as-is for local/course use; restrict `allow_origins` before any non-local deployment. | High | Accurate | Directly verifiable in code, and the code's own comment already acknowledges the same tradeoff, so this isn't a surprising or invented finding. |
| F5 | Low | `requirements.txt:1-6` | Dependencies are unpinned (`fastapi`, `uvicorn[standard]`, `pydantic`, `python-dotenv`, `pytest`, `httpx` — no version specifiers). | Full file contents. | Pin versions or add a lockfile for reproducible CI/Docker builds. | High | Accurate | Straightforward, unambiguous fact from the file contents; Low severity is appropriate since it's a reproducibility/supply-chain hygiene issue, not an active vulnerability. |
| F6 | Low | `app/models.py` (`assignee` field, `TaskCreate`/`TaskUpdate`) | `assignee` has no validator at all (unlike `title`/`tags`), so whitespace-only or arbitrarily long values are silently accepted. | No `@field_validator("assignee", ...)` exists in either model. | Apply the same strip/blank-check pattern used for `title` if `assignee` is meant to be a meaningful identifier. | Medium | Overstated as a separate row | Accurate as a fact, but overlaps with F1 (same field, same underlying "no constraints on `assignee`" gap) — should have been folded into F1 rather than listed as a distinct finding. |

## My Manual Findings

| Severity | File:Line | Finding | Suggested Fix | Reason |
|----------|-----------|---------|----------------|--------|
| Low | `tests/verify_a.py` (whole file) | The file isn't collected by pytest (its name doesn't match `test_*.py`/`*_test.py`), so its 8 assertions never run automatically via `pytest -q` or in CI (`.github/workflows/ci.yml:27` just runs `pytest -v --tb=short`). | Rename to `test_verify_a.py` so it's collected, fold its checks into `tests/test_tasks.py`, or delete it if superseded. | A file that reads like a validation suite but silently never executes creates false confidence that those checks are enforced. |
| Low | `Dockerfile:4,19` | The base image `python:3.11-slim` is pinned by tag only, not by digest, so `docker build` isn't fully reproducible over time as the tag gets rebuilt upstream. | Pin to a specific digest (`python:3.11-slim@sha256:...`) or explicitly accept the tradeoff, same as the unpinned-`requirements.txt` tradeoff already noted in F5. | Same reproducibility gap as F5, just at the Docker base-image layer instead of the Python dependency layer — worth tracking together. |
| Medium | `Dockerfile:50` + `app/main.py:19-24` | The container binds `0.0.0.0:8000` with no auth (F3) and CORS wide open to `*` (F4) — nothing in the Docker artifact itself adds access control, so the image is "deploy-ready" to expose a fully open, unauthenticated task API on any network it's run on. | Add an explicit "LOCAL/DEV ONLY — do not expose publicly" warning in the Dockerfile/README so the risk travels with the deployable artifact, not just the source. | F3 and F4 were reported as separate, per-file findings; connecting them to the concrete deployment artifact (the container) shows where they'd actually bite if someone `docker run -p 8000:8000`'d this on a public host. |

## Fixed (final-project hardening pass)

| Finding | Fix |
|---------|-----|
| F1 / F6 — `description`/`assignee` unbounded | Added `max_length` (`MAX_DESCRIPTION_LENGTH=2000`, `MAX_ASSIGNEE_LENGTH=100`) to both fields in `TaskCreate`/`TaskUpdate` (`app/models.py`). |
| F5 — unpinned dependencies | `requirements.txt` pinned to the exact versions verified in the project venv (fastapi==0.140.0, uvicorn==0.51.0, pydantic==2.13.4, python-dotenv==1.2.2, pytest==9.1.1, httpx==0.28.1). |
| Manual — `verify_a.py` never collected by pytest | Replaced with `tests/test_verify_a.py`: same checks, rewritten as real `pytest.raises` assertions instead of print-based pass/fail. Suite grew from 64 to 72 passing tests. |

## Reconciliation

### Agreement

### AI-only

### You-only

## Top 3 Unfixed Backlog

| Rank | Finding | Severity | Owner | Next Step |
|------|---------|----------|-------|-----------|
| 1 | F2 — no cap on stored tasks / no request-body size limit | Medium | TBD | Add a max-task-count guard or body-size limit before any deployment beyond localhost. |
| 2 | F4 — CORS fully open (`allow_origins=["*"]`) | Medium | TBD | Restrict `allow_origins` before any non-local deployment. |
| 3 | Manual — `Dockerfile` base image pinned by tag only, not digest | Low | TBD | Pin `python:3.11-slim` to a specific `sha256` digest, or explicitly accept the tradeoff. |
