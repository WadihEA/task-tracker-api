# Mini-ADR — Due Dates & Tags

Status: Accepted · Scope: Module 4 mid-course · Branch: `mid-course-project`

## Context
Extend the Task Tracker with two small end-to-end features without disturbing the
existing CRUD contract (40 passing tests) or the Kanban frontend. Storage stays
in-memory; models stay Pydantic with `extra="forbid"`.

## Decision 1 — `due_date` is a `date`, and `overdue` is computed, not stored
- **Chosen:** `due_date: Optional[date]`; `overdue` is a `@computed_field` on
  `TaskResponse` (`due_date < today and status != Done`).
- **AI alternatives considered / rejected:**
  - *Full `datetime` with time-of-day* — rejected; a due *date* has no meaningful
    clock time and it complicates input/validation.
  - *Store `overdue` as a boolean at write time* — rejected; it silently goes stale
    when the day rolls over. Computing on read is always correct and costs nothing
    at this scale.
- **Consequence:** invalid date strings are rejected by Pydantic's native parser
  (`422`) with no custom code.

## Decision 2 — Tags are a real `list[str]` with one shared validator
- **Chosen:** `tags: list[str]`, normalized by `_normalize_tags()` (trim, drop
  blanks, de-dupe, cap `MAX_TAGS=10` / `MAX_TAG_LENGTH=30`). The same helper backs
  both `TaskCreate` and `TaskUpdate`.
- **AI alternatives considered / rejected:**
  - *Comma-separated string column* — rejected; leaks parsing/escaping to every
    consumer and makes filtering brittle.
  - *A separate `/tasks/{id}/tags` sub-resource with its own endpoints* — rejected
    as over-scoped for a labeling feature; tags ride along on the task payload.
- **Consequence:** tag filtering is a simple case-insensitive membership check in
  `storage.get_all_tasks`.

## Decision 3 — View filters live client-side; API filters are authoritative
- **Chosen:** the frontend "Overdue only" / "Filter by tag" controls filter the
  already-loaded list (`applyFilters` over a `currentTasks` cache) — instant, no
  refetch. The backend independently supports `?overdue=` and `?tag=` and is the
  tested source of truth.
- **Rejected:** round-tripping to the API on every keystroke — unnecessary latency
  for an in-memory board of this size, and it would fight the drag-drop re-render.
- **Consequence:** the two filter paths are intentionally parallel; the pytest
  suite covers the server-side filters so they can't silently drift.

## Explicitly out of scope (rejected as too big for this checkpoint)
- Text **search + combined filter bar** as a third feature — the tag/overdue
  filters already exercise the same idea at the right size.
- **Persistence** (tasks.json / DB) — orthogonal to these features.
- Bulk operations, saved views/presets — flagged "easy to overbuild" by the brief.
