# Verification

Environment: Windows 11, `./venv/Scripts/python.exe`, FastAPI TestClient.

## 1. Baseline (before any change)
```
$ python -m pytest -q
40 passed, 7 warnings in 0.22s
```
The existing Module 1–3 suite was green before I started.

## 2. Backend smoke test (manual, TestClient)
Confirmed end-to-end before touching the frontend:
```
create 201 due_date=2026-07-25 tags=['Bug','urgent','bug'] overdue=True
overdue filter titles: ['A']          # ?overdue=true
tag=bug titles: ['A']                 # ?tag=BUG (case-insensitive)
bad date: 422                         # due_date='2026-13-40'
blank tag: 422                        # tags=['ok','  ']
done not overdue: False               # Done + past date
```

## 3. Final automated suite (after changes)
```
$ python -m pytest -q
61 passed, 7 warnings in 0.34s
```
21 new tests added (11 due-date, 10 tag) — well over the required 4. No existing
test was modified; the additions are purely additive, proving backward
compatibility of the CRUD contract.

## 4. Frontend check
```
$ node --check <extracted <script> block>
JS OK    # 11970 chars, no syntax errors
```

## 5. Break Test evidence (≥2 required)

**BT-1 — overdue "Done" guard.** Temporarily changed the computed field from
`if self.due_date is None or self.status == TaskStatus.DONE` to just
`if self.due_date is None`:
```
FAILED tests/test_tasks.py::test_done_task_with_past_due_is_not_overdue
FAILED tests/test_tasks.py::test_overdue_filter_returns_only_overdue_tasks
2 failed
```
→ Reverted with `git checkout app/models.py`. Proves the tests catch a real
regression, not a tautology.

**BT-2 — blank-tag guard.** Temporarily replaced `raise ValueError("Tags must not
be blank")` with `pass`:
```
FAILED tests/test_tasks.py::test_create_with_blank_tag_returns_422
1 failed, 1 passed
```
→ Reverted. `test_tags_are_trimmed_and_deduped` still passed (it doesn't rely on
the blank guard), which is the expected, discriminating result.

After both reverts: `61 passed` again.

## 6. Manual browser checks
Server: `python -m uvicorn app.main:app --reload --port 8000`; open
`frontend/index.html`.

| # | Action | Expected | Result |
|---|--------|----------|--------|
| 1 | Create task, due date in the past | red ⚠ overdue pill on card | ✅ |
| 2 | Create task, future due date | neutral 📅 date pill | ✅ |
| 3 | Create with tags `bug, urgent` | two chips render | ✅ |
| 4 | Toggle "Overdue only" | only overdue cards; "showing X of Y" | ✅ |
| 5 | Type a tag in "Filter by tag…" | board narrows live, no flicker | ✅ |
| 6 | Move overdue task to Done | overdue pill disappears | ✅ |
| 7 | Inline-edit → clear the date | pill removed, task persists | ✅ |
| 8 | Clear filters | full board returns | ✅ |

## 7. Behavior contract — before vs after refactor
The Module 3 behavior contract (drag/drop transitions, priority sort, Done
terminal, HTML-escaping, error toast) was re-run after adding the features:
- **Unchanged:** all 8 original behaviors still hold — status transitions, priority
  ordering within columns, Done-is-terminal, escaping, connection dot.
- **Added, non-breaking:** due/overdue pill and tag chips render inside the existing
  card `.meta` block; the new filter bar sits above the board and never alters the
  three-column layout or empty states.
- No original class/id/data hook was renamed, so drag-and-drop and inline edit
  continue to work exactly as before.
