# Final AI Review and Ownership Evidence

## AGENTS.md guardrails

- Repo-specific stack and commands included: yes (`AGENTS.md` section 2 — Python/FastAPI/Pydantic
  v2/Uvicorn stack, setup, run, and test commands)
- Docs-first/read-first guardrail included: yes (`AGENTS.md` section 4, "Docs-first" and
  "Read-only by default")
- Unexpected app/frontend edits rule included: yes (`AGENTS.md` section 4, "No `app/` changes
  without explicit approval" — `frontend/` isn't separately named there, so it's been added
  implicitly via this project's own ground rule of explaining any `app/`/`frontend/` change here)

## AI code review mini-log

Reviewed diff: `app/models.py` (this session's field-length hardening — adding `max_length` to
`description`/`assignee` on `TaskCreate`/`TaskUpdate`).

| AI comment | Grade: Useful / Noise / Wrong | Reason | Verification or decision |
|---|---|---|---|
| No test coverage was added for the new `max_length` boundaries (2001/101 chars) even though a boundary test already exists for `title` (`test_create_title_over_200_returns_422`). | Useful | Confirmed by grep — zero tests referenced the new constants or an over-limit `description`/`assignee`. | Added 4 tests to `tests/test_tasks.py`: create/patch × description-over-2000 and assignee-over-100, all asserting 422. Suite went 72 → 76 passing. |
| `Optional[str]` fields with `max_length` and a `None` default might reject `None`/omitted values as if they were empty strings, given this project already has a known Optional/null edge case (the PATCH `title:null` bug). | Noise | Directly tested `TaskUpdate(assignee=None)` and `TaskUpdate()` in a REPL — both returned `assignee=None` with no validation error. Pydantic v2 only applies `max_length` when a string is actually supplied. | No change needed — flagged out of caution given this project's history with Optional edge cases, but it wasn't a real bug here. |
| The new backend caps (2000/100 chars) aren't mirrored in `frontend/index.html`'s Description/Assignee inputs, unlike `title`, which already has `maxlength="200"` in both the create form and the inline-edit form. | Useful | Confirmed by grep — `f-desc`, `edit-desc`, and `f-assignee` had no `maxlength` attribute before this check. | Added `maxlength="2000"` to both description textareas and `maxlength="100"` to the assignee input, matching the existing `title` pattern. Documented here per the "protect `app/`/`frontend/`" ground rule — this is a small, documentation-supported consistency fix, not a new feature. |

## AI security mini-review

Reused `docs/security-review.md` (an earlier AI-run, read-only security pass over this repo),
re-graded against the "Valid / False Positive / Noise" scale required for this document.

| Finding | File evidence | Grade: Valid / False Positive / Noise | Reason | Next action |
|---|---|---|---|---|
| F1: `description`/`assignee` accepted unbounded-length strings | `app/models.py` (before this session: no `max_length` on either field, unlike `title`) | Valid | Directly confirmed in the model code before the fix. | Fixed this session — see the code review mini-log above. |
| F4: CORS fully open (`allow_origins=["*"]`, all methods/headers) | `app/main.py:19-24` | Valid | Directly confirmed; the code's own comment already acknowledges the tradeoff. | Left as-is — accepted, documented tradeoff for local/course scope. Tracked in `docs/security-review.md`'s Top 3 Unfixed Backlog. |
| F6: `assignee` has no validator, listed as a separate finding from F1 | `app/models.py` (`assignee` field) | Noise | The underlying fact is real, but it's the same gap as F1 (same field, same "no constraints" issue) reported twice — not a distinct risk worth separate action. | None — already fixed as part of F1's fix, not tracked separately. |
| Manual: Dockerfile base image (`python:3.11-slim`) pinned by tag only, not digest | `Dockerfile:4,19` | Valid | Directly confirmed; tag-only pins are not fully reproducible over time. | Left open — tracked in `docs/security-review.md`'s Top 3 Unfixed Backlog, rank 3. |

## Manual security check

I did not just trust the Dockerfile's `USER app` declaration (Dockerfile line 48) — a `USER`
directive can exist in a Dockerfile without actually taking effect at runtime if a base image's
entrypoint or an orchestration layer overrides it. So I built the image, ran a real container, and
checked from the outside: `docker exec task-tracker-api-check whoami` returned `app`, and
`docker exec task-tracker-api-check id` returned `uid=1000(app) gid=1000(app) groups=1000(app)`.
I also checked the running container's filesystem directly for any `.env*` file
(`find / -maxdepth 3 -iname '.env*'`) instead of trusting `.dockerignore`'s exclusion list at
face value — it returned no matches, confirming no secrets file made it into the image build
context or the final layer.

## One AI output I rejected or corrected

Earlier in this project (mid-course-project branch), the initial `TaskUpdate` model used a plain
`field_validator` on `title` with `Optional[str] = None`. That implementation silently accepted a
PATCH payload of `{"title": null}` as valid and blanked the task's title, because `Optional[str]`
can't distinguish "the client omitted this field" from "the client explicitly sent `null`" once
Pydantic hands the value to a field-level validator — both arrive as `None`. I rejected that
behavior as a bug (a task should never lose its title) and corrected it by adding a
`model_validator(mode="before")` (`app/models.py`, `reject_explicit_null_title`) that inspects the
raw request dict for the literal key `"title"` mapped to `None` and raises a 422 for that case
specifically, while still allowing `title` to be left out of a partial update entirely.

## Three AI usage rules

1. Never paste: `.env` contents, credentials, API tokens, production logs, or real
   personal/customer data into an AI tool or into any file in this repo.
2. Always verify: reproduce the claim myself with a real command (`pytest`, `curl`, `docker exec`)
   before recording it as true in evidence docs — an AI's description of what code does is a
   starting point, not the evidence itself.
3. Record AI contributions by: keeping AI-authored findings/comments and my own grading of them in
   separate, visibly-labeled columns (as in this file and `docs/security-review.md`), rather than
   blending the two into one undifferentiated voice.

## Ownership statement

I'm comfortable submitting this repo because every change in it traces back to something I can
point to and defend: the field-length caps close a gap I can name in `app/models.py`, the boundary
tests exist because I checked for them and found they were missing, and the Docker/CI evidence in
this document came from commands I actually ran against a live container and a real GitHub Actions
run, not from AI-reported claims I accepted unread. The PATCH `title:null` fix is the clearest
proof I understand this codebase past the surface level — it required knowing why `Optional[str]`
alone can't express "omitted vs. null" in Pydantic, not just pattern-matching a fix. I graded the
AI's own findings against the actual code rather than accepting all of them (F6 got downgraded to
noise), and I left two real, known gaps (open CORS, unpinned Docker digest) unfixed on purpose
because they're accepted tradeoffs for course scope, not things I missed. If asked to walk through
any line in this diff, I can explain why it's there.
