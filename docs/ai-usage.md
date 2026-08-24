# AI Usage

How AI tools were used to build and harden this project, and what guardrails apply.

## Tools used

- **Claude Code** — primary tool for implementation, tests, docs, and this
  release-hardening pass. Runs with project-scoped memory
  (`.claude/`) and a `task-tracker` subagent that knows this repo's
  conventions.
- **Codex App** — used against `AGENTS.md`'s guardrails: docs-first,
  read-only by default, no changes to `app/` without explicit per-thread
  approval (see `AGENTS.md` section 4).

## What was AI-generated vs. human-directed

Every feature (CRUD, status transitions, due dates/overdue, tags, the Kanban
frontend, Docker/CI, the security and governance docs) started from an
explicit human request and was reviewed before being accepted — nothing was
merged from an unreviewed AI suggestion. Concretely:

- **Business rules were specified by me, implemented by AI.** E.g. "Done is
  terminal" and the valid status-transition graph in
  `app/business_rules.py` were my rules to enforce; AI wrote the
  implementation and tests against them.
- **Bugs found in review got fixed, not waved through.** The PATCH
  `title: null` gap (Optional can't distinguish "omitted" from "explicit
  null") was caught in review and fixed with a `model_validator`, not
  shipped as-is.
- **Security findings were graded, not accepted wholesale.** Every AI
  finding in `docs/security-review.md` has a Grade/Reason column filled in
  after checking it against the actual code — one finding (F6) was marked
  "overstated as a separate row" rather than accepted at face value.

## Review process

1. AI proposes a change (code, test, or doc).
2. I read the diff before accepting — not just the test output.
3. `python -m pytest -q` must pass locally before anything is treated as done.
4. Anything touching validation, business rules, or security-relevant config
   gets a second look against `docs/security-review.md` before merging.

## Boundaries

- No secrets, `.env` contents, credentials, or personal data are pasted into
  any AI tool — see `docs/governance-worksheet.md` for what was actually
  shared across the course.
- `AGENTS.md` sets hard limits on what the Codex App may touch without
  explicit approval in-thread.
- Self-assessment sections (grading AI findings, describing my own
  understanding of generated code) are filled based on genuinely checking
  the code, not rubber-stamped — see the Grade/Reason columns in
  `docs/security-review.md` and the "Do I Understand It Line by Line?"
  column in `docs/governance-worksheet.md`.

## Known gaps

- No confirmed incident of accidentally sharing real external data with an
  AI tool has occurred, but this hasn't been formally audited beyond the
  entries logged in `docs/governance-worksheet.md`.
- CORS being fully open and the lack of a request-size/task-count cap are
  known, accepted tradeoffs for course scope — not oversights. See the Top 3
  Unfixed Backlog in `docs/security-review.md`.
