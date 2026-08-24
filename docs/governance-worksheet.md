# Governance Retrospective - AI-Assisted Coding

## What I Shared With AI
| Item | Module | Risk Level | Reason |
|---|---|---|---|
| Task Tracker code | 2-5 | Low | Original, non-proprietary course toy-project code with no embedded secrets or real user data; the repo is now public on GitHub. |
| Test output and stack traces | 2-4 | Medium | Output repeatedly included full local Windows file paths (e.g. `C:\Users\wadih\...`) that expose the local OS username tied to a real name — a minor but real personal-information leak beyond the toy-project content itself. |
| Frontend code | 3 | Low | `frontend/index.html` is self-contained client-side code with no API keys, auth tokens, or real user data; it only calls a local, unauthenticated dev API. |
| Dockerfile and CI YAML | 4 | Low | Audited and confirmed secret-free: no credentials, no `.env` copied into the image, and nothing sensitive referenced in the CI workflow. |
| Any real external data I used by mistake | Not confirmed | Cannot classify | No specific incident is recorded — missing whether this happened at all, and if so, what type of data and in which module/session. |

## What I Received From AI
| Generated Thing | Module | Do I Understand It Line by Line? | Action |
|---|---|---|---|
| Backend models and validators | 2 | Yes — including the subtler bits, like why `TaskUpdate` needs a `model_validator(mode="before")` to catch an explicit `{"title": null}` (Optional alone can't distinguish "omitted" from "sent as null"). | Kept as-is; this is the piece I'd be asked to walk through in an interview, so I made sure I could. |
| Frontend board and drag-and-drop logic | 3 | Partial — the fetch calls, state updates, and card rendering, yes. The native HTML5 drag-and-drop event sequence (`dragstart`/`dragover`/`drop`) I can use and modify but wouldn't write from scratch unaided. | Revisit before extending drag-and-drop further; treat as understood-enough-to-maintain, not understood-enough-to-reimplement. |
| CI workflow | 4 | Yes — it's short: checkout, set up Python 3.11, cache pip, install `requirements.txt`, run `pytest -v --tb=short` on every push and on PRs into `main`. | Kept as-is; will need a bump if the Python version or test command ever changes. |
| Dockerfile | 4 | Yes — `python:3.11-slim` base, copies `requirements.txt` first for layer caching, then app code, exposes 8000, runs uvicorn as the `CMD`. | Kept as-is for course scope; base image is pinned by tag only, not digest — logged as an open backlog item in `security-review.md`, not silently accepted. |
| Security findings and plans | 5 | Yes — reviewed each AI-reported finding against the actual code before grading it (see `security-review.md`'s Grade/Reason columns), and fixed the ones scoped as course-appropriate (field length caps, dependency pinning, the dead `verify_a.py` test file). | Acted on: F1/F6, F5, and the `verify_a.py` gap are fixed. F2, F4, and the Docker digest pin remain open and tracked in the Top 3 Unfixed Backlog. |
