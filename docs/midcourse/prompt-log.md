# Prompt Log

Representative prompts used while building the two features, with what the AI
returned and what I accepted, edited, or rejected.

---

## Feature 1 — Due dates + overdue

### P1.1 (weak → rewritten)
- **Weak prompt:** "add a due date to the task."
- **Why weak:** no type, no validation rules, no definition of "overdue", no
  frontend expectation — the AI guessed a `datetime` and a stored flag.
- **Stronger rewrite:** "Add an optional `due_date` to the Task model as a
  Pydantic `date` (not datetime). Add a computed `overdue` boolean on the response
  that is true only when `due_date` is in the past AND status != Done. Invalid date
  strings must return 422. Don't store `overdue`; compute it on read."
- **AI returned:** a `@computed_field` implementation matching the spec.
- **Decision:** **Accepted** with a one-line edit to the docstring explaining why
  it's computed.

### P1.2
- **Prompt:** "Add `?overdue=true|false` and `?tag=` query params to GET /tasks,
  filtering in `storage.get_all_tasks`. Keep the existing status/priority filters."
- **AI returned:** correct param wiring + list comprehensions.
- **Decision:** **Edited** — the AI's tag match was case-sensitive; I made it
  case-insensitive (`needle in {t.lower() ...}`) to match user expectation.

### P1.3
- **Prompt:** "Write pytest cases: past date → overdue true, future date → false,
  Done+past → false, `?overdue=true` returns only overdue, clearing due_date with
  null. Use dates relative to today so they don't rot."
- **AI returned:** tests hard-coding `"2020-01-01"`.
- **Decision:** **Rejected & rewrote** — replaced literals with
  `date.today() ± timedelta` (`PAST`/`FUTURE`) so the suite can't break on a
  future date change.

---

## Feature 2 — Tags / labels

### P2.1 (weak → rewritten)
- **Weak prompt:** "let tasks have tags."
- **Why weak:** doesn't say list vs string, no validation, no limits — the AI
  proposed a comma-separated string field.
- **Stronger rewrite:** "Add `tags: list[str]` to create/update/response. Write one
  reusable validator that trims each tag, rejects blank tags with 422, de-dupes,
  and caps count at 10 and length at 30. Reuse it in both TaskCreate and TaskUpdate."
- **AI returned:** the `_normalize_tags()` helper + two `field_validator`s.
- **Decision:** **Accepted**, edited the update validator so `None` means "field
  not provided" (partial update) rather than "empty list".

### P2.2
- **Prompt:** "In the frontend, add a comma-separated tags input to the modal and
  inline edit, render tags as chips, and a 'Filter by tag' box above the board that
  narrows the view without a refetch."
- **AI returned:** working chips + a filter that re-fetched from the API on every
  keystroke.
- **Decision:** **Edited** — switched to filtering a cached `currentTasks` list via
  `applyFilters()` so typing is instant and doesn't thrash the server.

### P2.3
- **Prompt:** "Break-test the blank-tag rule: temporarily disable the guard and show
  which test catches it."
- **AI returned:** the edit + the exact pytest command.
- **Decision:** **Accepted**; ran it, confirmed `test_create_with_blank_tag_returns_422`
  fails, reverted. Evidence in `verification.md`.
