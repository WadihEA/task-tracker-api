# Reflection

For this checkpoint I used AI assistance (Claude, via Claude Code) as a pair
programmer across the whole loop — drafting Pydantic model changes, wiring the
frontend, generating pytest cases, and running the Break Tests — while keeping the
design decisions and the final review for myself. I leaned on it most for the
mechanical, repetitive parts: adding a field to three models at once, mirroring a
query parameter through the route and storage layers, and writing twenty-plus
parametrized-style tests that would have been tedious to type by hand.

The clearest moment AI *helped* was the `overdue` design. When I asked it to add a
due date, it produced a complete, working `@computed_field` implementation in one
pass, including the subtlety that a `Done` task should never count as overdue.
Having a correct first draft let me spend my attention on the question that
actually mattered — whether "overdue" should be stored or computed — rather than on
syntax. It also generated the exact `git checkout` + targeted `pytest` commands for
the Break Tests, which made proving my tests had teeth fast and repeatable.

The clearest moment AI *slowed me down* was the frontend filtering. Its first
version re-fetched the entire task list from the API on every keystroke in the tag
box. It worked, but it was laggy and it fought the existing drag-and-drop
re-render. I had to stop, understand that the board already held the loaded tasks
in memory, and redirect it to filter a cached `currentTasks` array instead. The
lesson: AI optimizes for "produces correct output," not "fits the architecture,"
so an answer that passes a quick manual test can still be the wrong shape.

The place my review changed the result was tag storage. Left to its defaults, the
AI twice pushed toward the "simple" option — a comma-separated string field and,
later, hard-coded date literals in the tests. Both would have technically passed a
happy-path check. I rejected the string field in favor of a real `list[str]` with
one shared validator (so create and update can't drift), and I replaced the frozen
test dates with values computed relative to `date.today()` so the overdue tests
won't silently rot on a future run. Neither change was suggested by the model; both
came from asking "what breaks in six months?" — which is exactly the ownership the
tool can't take over for me.

Net, AI made the implementation roughly two to three times faster, but every
non-trivial correctness decision — computed vs stored, list vs string,
relative vs literal dates, cached vs refetched — was one I had to make and defend
myself. That division of labor felt right: it typed, I decided.
