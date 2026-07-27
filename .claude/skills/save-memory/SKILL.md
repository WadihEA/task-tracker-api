---
name: save-memory
description: Persist a durable fact about the Task Tracker API project or the user's preferences to file-based memory. Use after learning something non-obvious worth remembering across sessions.
---

# Save Memory

Write one durable fact to persistent memory and register it in the index.

## Memory location

    C:\Users\wadih\.claude\projects\C--Users-wadih-OneDrive-Desktop-AUB-proj-task-tracker-api\memory\

## File format

One fact per file, kebab-case filename, with frontmatter:

```markdown
---
name: <short-kebab-case-slug>
description: <one-line summary — used to decide relevance during recall>
metadata:
  type: user | feedback | project | reference
---

<the fact. For feedback/project, follow with **Why:** and **How to apply:** lines.
Link related memories with [[their-name]].>
```

Types: `user` (who the user is), `feedback` (how to work / corrections, include the
why), `project` (ongoing work, goals, constraints not derivable from code/git),
`reference` (pointers to URLs/tickets/dashboards).

## Steps

1. Check for an existing memory file that already covers this — update it rather than
   creating a duplicate. Delete memories that turn out to be wrong.
2. Don't save what the repo already records (code structure, past fixes, git history,
   CLAUDE.md) or what only matters to the current conversation.
3. Convert relative dates ("today", "last week") to absolute dates.
4. Write the `*.md` file with the frontmatter above.
5. Add a one-line pointer to `MEMORY.md`: `- [Title](file.md) — hook`.
   Never put memory content in `MEMORY.md` itself — it's just the index.
