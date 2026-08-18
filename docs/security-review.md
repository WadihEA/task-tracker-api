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

## Reconciliation

### Agreement

### AI-only

### You-only

## Top 3 Unfixed Backlog

| Rank | Finding | Severity | Owner | Next Step |
|------|---------|----------|-------|-----------|
