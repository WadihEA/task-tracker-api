# docs/decisions/comments-feature-plan.md

## 1. Data Model

Comments should be added as new Pydantic models in `app/models.py`, alongside the existing `TaskCreate`/`TaskUpdate`/`TaskResponse` (`app/models.py:59-165`), following the same three-model split (create / update / response) that's already established there — though "update" may not be needed (see §6).

Concrete mapping to existing patterns:
- `model_config = ConfigDict(extra="forbid")` — every existing model uses this (`app/models.py:60,94,141`); a `CommentCreate` should too, so an unexpected field (e.g. a client-supplied `id`) is rejected the same way `test_create_task_unknown_field_returns_422` covers for tasks.
- `author`: `str = Field(..., min_length=1, max_length=100)` mirrors `title: str = Field(..., min_length=1, max_length=200)` (`app/models.py:62`). It should also get a `@field_validator("author", mode="before")` that trims and rejects blank-after-strip, matching `validate_title` (`app/models.py:70-83`) — plain `min_length=1` alone doesn't catch a whitespace-only string, which is exactly why `validate_title` exists.
- `body`: same pattern, `max_length=2000`, trimmed, blank rejected.
- `id`: **not** on `CommentCreate` — server-generated, so it's naturally rejected by `extra="forbid"` if a client sends it, same as `TaskCreate` never exposes `id`.
- `created_at`: same — server-generated in `CommentResponse` only, never client-settable, matching `TaskResponse.created_at`/`updated_at` (`app/models.py:151-152`).
- `task_id`: on `CommentResponse` (and implicitly known from the URL path on create — see §2), matching the existing string-id convention `storage.py` uses (`task_id: str`).

One real deviation from existing convention: the spec calls for `id: string UUID`, but `app/storage.py:12-18` currently assigns task ids from a **monotonic int counter stringified** (`_next_id`), specifically to avoid id recycling after deletes. Comments would need a different id-generation strategy (`uuid.uuid4()`) since a monotonic counter isn't what's specified. This means the repo would have two different id schemes for two sibling resources — flagged as an open question in §6, not silently resolved here.

`CommentResponse` has no `updated_at` in the given schema (unlike `TaskResponse`, which has both `created_at` and `updated_at` — `app/models.py:151-152`). That's a real signal the schema intends comments to be immutable after creation; see §6.

## 2. API Routes

Task routes currently live directly in `app/main.py` (`app/main.py:34-77`), not behind a separate router — `app/api/` only holds `health.py`, included via `app.include_router(health_router)` (`app/main.py:26`). Comments could go either way; see §6 for that as an open decision rather than an assumption.

Proposed routes, modeled on the existing task routes' status codes and 404 conventions:

| Method | Path | Request body | Response body | Errors |
|---|---|---|---|---|
| `POST` | `/tasks/{task_id}/comments` | `{author, body}` (`CommentCreate`) | `CommentResponse` (201) | 404 if `task_id` doesn't exist (mirrors `app/main.py:51-56`'s `get_task_by_id` 404 check, reused before insert); 422 on validation (blank/oversized `author`/`body`, unknown field) |
| `GET` | `/tasks/{task_id}/comments` | — | `list[CommentResponse]` (200) | 404 if `task_id` doesn't exist — **different** from `GET /tasks`, which never 404s on an empty result (`app/main.py:39-48`); this endpoint is scoped to a specific parent, so it should behave like `GET /tasks/{id}` (404-capable), not like the flat collection endpoint |
| `DELETE` | `/tasks/{task_id}/comments/{comment_id}` | — | 204, empty body | 404 if either the task or the comment doesn't exist, or if the comment exists but doesn't belong to `task_id` (mirrors the empty-body-204 pattern at `app/main.py:73-77` and the 204-body assertion style in tests) |

Not proposed, pending §6: `PATCH /tasks/{task_id}/comments/{comment_id}` and `GET /tasks/{task_id}/comments/{comment_id}` (single-comment fetch) — the given schema doesn't include an `updated_at` field, so an edit endpoint isn't clearly in scope, and no requirement calls for fetching a single comment by id.

404 detail string should follow the existing format exactly, e.g. `f"Task with id {task_id} not found"` (`app/main.py:55`) and an equivalent `f"Comment with id {comment_id} not found"` for the comment-not-found case, for consistency with `docs/security-review.md`'s note that error details are already stable/non-verbose.

## 3. Tests

Following `tests/test_tasks.py`'s naming convention (`test_<action>_<condition>_returns_<code>`, grouped with a `# METHOD /path` comment header, e.g. `tests/test_tasks.py:7,42,67,82,118`) and its `client`/`created_task` fixtures (`tests/conftest.py:15-24`):

**Happy path**
- `test_create_comment_valid_returns_201_with_full_body`
- `test_list_comments_empty_returns_200_and_empty_list`
- `test_list_comments_returns_in_created_order`
- `test_delete_comment_returns_204_no_body`

**Validation**
- `test_create_comment_missing_author_returns_422`
- `test_create_comment_blank_author_returns_422`
- `test_create_comment_author_over_100_chars_returns_422`
- `test_create_comment_missing_body_returns_422`
- `test_create_comment_blank_body_returns_422`
- `test_create_comment_body_over_2000_chars_returns_422`
- `test_create_comment_unknown_field_returns_422`
- `test_create_comment_client_supplied_id_returns_422` (relies on `extra="forbid"`, same mechanism as `test_create_task_unknown_field_returns_422` at `tests/test_tasks.py:37-39`)

**Edge cases**
- `test_create_comment_on_nonexistent_task_returns_404`
- `test_list_comments_on_nonexistent_task_returns_404`
- `test_delete_comment_not_found_returns_404`
- `test_delete_comment_belonging_to_different_task_returns_404`
- `test_create_comment_author_exactly_100_chars_returns_201` (boundary)
- `test_create_comment_body_exactly_2000_chars_returns_201` (boundary)
- `test_created_at_is_server_generated_and_not_client_settable`
- `test_delete_task_with_comments_behavior` — outcome depends on the cascade decision in §6; the test should exist regardless of which way that's decided, asserting whatever the chosen behavior is.

## 4. Frontend Changes

Only `frontend/index.html` would change — it's the single self-contained file for the whole UI (no build step, per `README.md`).

Current card rendering (`renderView`, `frontend/index.html:465-493`) has no room for a comment thread — cards are compact, list title/description/priority/assignee/due-date/tags plus move/edit/delete buttons. Concretely:
- Add a "Comments" affordance to each card (e.g. a count badge and a "View" button, similar in style to the existing `badge`/`chip` elements at `frontend/index.html:220-243`), since inlining a full thread into a Kanban card would break the compact-card layout.
- A comment view/add surface is most consistent with the existing pattern of the `<dialog id="task-dialog">` (`frontend/index.html:305-349`) used for "New Task" — a second `<dialog>` (or a reused one) listing existing comments and a small add-comment form (`author`, `body`).
- New calls through the existing `api()` helper (`frontend/index.html:426-437`): `GET /tasks/{id}/comments` on open, `POST /tasks/{id}/comments` on submit — following the same `try { await api(...); load()/refreshComments(); } catch (e) { toast(e.message); }` pattern already used by `moveTask`/`deleteTask`/the new-task form (`frontend/index.html:596-641`).
- Any rendered `author`/`body` text **must** go through the existing `esc()` helper (`frontend/index.html:439-441`) before insertion into the DOM — this is the same escaping already applied to `title`/`description`/`assignee`/`tags`, and `docs/security-review.md` explicitly notes the frontend currently has no XSS issue because of it; a comment feature that skips this would reintroduce one.
- No changes needed to `COLUMNS`/`MOVES`/drag-and-drop logic (`frontend/index.html:365-383`) — comments aren't a board-level entity, they attach to an existing card.

## 5. Migration Notes

- Storage is entirely in-memory (`app/storage.py:8`, a module-level dict) and is wiped on every process restart and reset between every test via the autouse `_reset_storage` fixture (`tests/conftest.py:8-11`, which calls `storage._reset()` at `app/storage.py:80-83`). There is no persisted data to migrate in the traditional sense.
- `storage._reset()` currently only clears `_tasks` and `_next_id` (`app/storage.py:81-83`). Adding a comments store means this reset function would need to also clear the new comments dict (and any id/counter state it uses) — otherwise tests would leak comment data across test functions, breaking the isolation the current suite relies on.
- No change is required to the existing `TaskResponse` shape unless the team decides to embed comments or a comment count directly on the task payload (see §6) — as scoped here, comments are a fully separate collection referencing `task_id`, so existing task tests and the task schema are unaffected.
- `docs/midcourse/` and `README.md`'s documented test count (64 passing, per `AGENTS.md:32`) would need updating once comment tests are added — not a data migration, but a doc that will go stale.

## 6. Open Questions

1. **404 scoping for the list/create routes**: should `POST`/`GET /tasks/{task_id}/comments` 404 when the parent task doesn't exist (matching `GET /tasks/{id}`'s behavior), or should they behave like the collection-style `GET /tasks` endpoint that never 404s? This directly changes several test outcomes in §3 and isn't decidable from the given schema alone.
2. **Are comments immutable?** The given schema has no `updated_at` field (unlike `Task`, which has both `created_at`/`updated_at`), and no update semantics were requested. Should there be a `PATCH` for comments at all, or is create + delete (+ maybe never delete) the full intended surface?
3. **Cascade behavior on task deletion**: `DELETE /tasks/{id}` (`app/main.py:73-77`) currently has zero awareness of any child resource. When a task with comments is deleted, should its comments cascade-delete, should deletion be blocked while comments exist, or should comments simply become orphaned/unreachable in storage? This needs an explicit product decision before implementation.
4. **Route organization**: task routes are inline in `app/main.py`, while `health` uses a dedicated `APIRouter` in `app/api/health.py` included via `app.include_router`. Should comments follow the file-per-resource `app/api/` pattern (cleaner, but inconsistent with how tasks are actually built today), or go inline in `app/main.py` to match the task routes' current style?
5. **Id scheme consistency**: the spec requires UUID ids for comments, while tasks use a monotonic-counter string id specifically chosen to avoid recycling (`app/storage.py:9-11`). Is it acceptable to have two different id-generation strategies side by side, or should this prompt reconsidering task ids too (out of scope for this feature, but worth surfacing)?

---

## Files read
`AGENTS.md`, `app/models.py` (full), `app/main.py` (full), `app/storage.py` (full), `app/business_rules.py` (full), `app/api/health.py` (full), `app/core/config.py`, `README.md`, `tests/conftest.py` (full), `tests/test_tasks.py` (first ~120 lines), `frontend/index.html` (full), directory listing confirming `app/api/` contains only `health.py`.

## Assumptions to verify
- I assumed comments attach to exactly one task via `task_id` as a simple reference, with no additional relational fields (e.g. no parent-comment/threading) — the given schema supports only that, but it's worth confirming threading is genuinely out of scope.
- I assumed the nested-path style `/tasks/{task_id}/comments` is preferred over a flat `/comments?task_id=` style; the existing repo has no precedent for nested resource routes (tasks are the only top-level resource so far), so this is a design choice, not something observed in the code.
- I did not re-open `docs/midcourse/*.md` or `docs/security-review.md`/`docs/governance-worksheet.md` in this pass — if either documents prior decisions about extending the schema, they weren't checked this turn.
- `tests/test_tasks.py` was only read through line ~120 of 463; later sections (tags/due-date/overdue tests, the PATCH null-title tests) weren't re-verified this turn, though their existence and behavior were confirmed earlier in this session and referenced in `AGENTS.md`.

## Generic vs Repo-Grounded Codex Comparison

**Biggest difference:** The generic plan could describe a reasonable comments feature in abstract terms, but the repo-grounded plan must tie every recommendation to the Task Tracker's actual models, routes, persistence approach, tests, frontend structure, and documented conventions.

**Plan I would hand to a teammate:** The repo-grounded plan, because it should identify the exact files and existing patterns to follow for the comment model, task relationship, API routes, validation, persistence changes, tests, frontend behavior, and any migration concerns. It should also clearly identify anything that could not be determined from the repository.

**Where the generic plan was still useful:** It provided a baseline checklist for the feature: a comment data model with UUID, task reference, validated author and body fields, server-generated UTC timestamp, API considerations, validation and edge-case tests, frontend integration, and storage or migration concerns.

**Where repo grounding mattered most:** Determining how comments should actually be persisted and associated with tasks, which existing model and route conventions should be reused, how missing tasks and validation errors are currently represented, how tests are named and structured, which frontend files and UI patterns should change, and whether the existing storage shape requires a migration or compatibility strategy.
