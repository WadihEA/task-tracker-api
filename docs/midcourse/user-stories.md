# User Stories — Mid-Course Features

Two features were added to the Task Tracker: **Due dates + overdue** and
**Tags / labels**. Both are usable from the Kanban frontend.

---

## Feature 1 — Due dates + overdue filter

### US-1.1 — Set a due date when creating a task
**As a** user, **I want** to attach an optional due date to a task **so that** I
know when it needs to be finished.

**Acceptance criteria**
- The New Task modal has a date picker; leaving it empty creates a task with
  `due_date: null`.
- A valid `YYYY-MM-DD` date is stored and returned by the API.
- An invalid date (`31-12-2026`, `2026-13-40`) is rejected with `422`.

### US-1.2 — See at a glance which tasks are overdue
**As a** user, **I want** overdue tasks to stand out **so that** I can act on them
first.

**Acceptance criteria**
- The API returns a computed `overdue` boolean per task.
- A task is overdue only when its due date is in the past **and** it is not `Done`.
- Overdue cards show a red ⚠ pill; non-overdue dated cards show a neutral 📅 pill.

### US-1.3 — Filter the board to only overdue tasks
**As a** user, **I want** an "Overdue only" toggle **so that** I can focus on what
is late.

**Acceptance criteria**
- `GET /tasks?overdue=true` returns only overdue tasks; `?overdue=false` excludes them.
- The frontend "Overdue only" checkbox narrows the board and shows "showing X of Y".
- Columns and empty states stay visible when the filter matches nothing.

### US-1.4 — Change or clear a due date
**As a** user, **I want** to edit a task's due date **so that** I can reschedule it.

**Acceptance criteria**
- `PATCH /tasks/{id}` with `due_date` updates it; recomputes `overdue`.
- `PATCH` with `due_date: null` clears the date (task is no longer overdue).
- Inline edit on a card exposes the date field.

> **AI assumption I corrected:** the assistant first modeled `due_date` as a full
> `datetime` and proposed storing a pre-computed `overdue` boolean at write time.
> I rejected both: a *date* (no time-of-day) matches "due date" semantics, and a
> **stored** overdue flag goes stale overnight. I changed it to a `date` field with
> `overdue` as a Pydantic `@computed_field` evaluated on every read.

---

## Feature 2 — Tags / labels

### US-2.1 — Tag a task on creation
**As a** user, **I want** to add labels to a task **so that** I can categorize work.

**Acceptance criteria**
- The New Task modal accepts a comma-separated list; tags render as chips on the card.
- Tags are trimmed; surrounding whitespace and duplicates are removed
  (`" bug ", "bug"` → `["bug"]`).
- An empty/blank tag (`"   "`) is rejected with `422`.

### US-2.2 — Keep tags sane
**As a** user, **I want** reasonable limits on tags **so that** cards stay readable.

**Acceptance criteria**
- More than 10 tags → `422`.
- A tag longer than 30 characters → `422`.
- A task with no tags returns `tags: []`.

### US-2.3 — Filter the board by tag
**As a** user, **I want** to filter by a tag **so that** I can see one category.

**Acceptance criteria**
- `GET /tasks?tag=backend` returns tasks carrying that tag, case-insensitively.
- No matches → `200` with `[]` (never `404`).
- The frontend "Filter by tag…" box narrows the board live (substring match).

### US-2.4 — Edit tags without losing them
**As a** user, **I want** tags to survive unrelated edits **so that** I don't have
to re-enter them.

**Acceptance criteria**
- `PATCH` that changes only the description leaves `tags` unchanged.
- `PATCH` with a `tags` list replaces the set.

> **AI assumption I corrected:** the assistant proposed a normalized comma-separated
> **string** field (`"bug,urgent"`) to "keep storage simple." I rejected that — it
> pushes split/trim/escape logic onto every consumer and makes tag filtering
> fragile. I changed it to a real `list[str]` with a shared `_normalize_tags()`
> validator used by both create and update.
