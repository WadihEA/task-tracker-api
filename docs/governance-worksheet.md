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
| Backend models and validators | 2 | TODO | TODO |
| Frontend board and drag-and-drop logic | 3 | TODO | TODO |
| CI workflow | 4 | TODO | TODO |
| Dockerfile | 4 | TODO | TODO |
| Security findings and plans | 5 | TODO | TODO |
