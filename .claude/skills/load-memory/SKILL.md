---
name: load-memory
description: Recall persisted project/user memory for the Task Tracker API at the start of a task. Use when you need context on what was done before, project conventions, decisions, or user preferences.
---

# Load Memory

Read the persistent memory for this project and summarize what's relevant to the
current task.

## Memory location

    C:\Users\wadih\.claude\projects\C--Users-wadih-OneDrive-Desktop-AUB-proj-task-tracker-api\memory\

- `MEMORY.md` — the index: one line per memory (`- [Title](file.md) — hook`).
- `*.md` — one fact per file, with frontmatter (`name`, `description`, `metadata.type`).

## Steps

1. Read `MEMORY.md` to see the index of available memories.
2. Based on the current task, pick the relevant entries and Read those individual
   `*.md` files (don't blindly read all of them if the task is narrow).
3. Follow `[[name]]` links between memories to pull in related facts.
4. Produce a short summary of what applies to the task at hand. Treat every recalled
   fact as *possibly stale* — if it names a file, function, or flag, verify it still
   exists in the codebase before relying on it.

If `MEMORY.md` is missing or empty, say so plainly — there is nothing to recall yet.
