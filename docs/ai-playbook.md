# My AI Coding Playbook

## 1. When I reach for AI first
- Scaffolding boilerplate: new routes, Pydantic models, pytest cases for a feature I've already scoped (e.g. due-dates, tags)
- First-draft docs and design write-ups (design docs, README sections) that I then edit down
- Getting unstuck fast on an error message before I go digging through the code myself

## 2. When I do not reach for AI
- Deciding which findings actually matter enough to land on a "Top 3 backlog" — that's my judgment call, not a scoring exercise
- Diagnosing "is this actually broken" before assuming the code is at fault (e.g. checking for a stale process on a port before blaming the app)
- The final call on anything that touches auth, secrets, or what gets exposed outside my own machine

## 3. My non-negotiables
- No destructive git commands (force-push, reset --hard, history rewrites) run by AI without me reviewing the command first
- Every AI-authored validation/business-logic change gets a test I wrote or hand-checked, not just AI-written tests I never read
- Guardrail files (like AGENTS.md) stay in place for any tool that can touch application code — docs-first, no silent scope creep

## 4. My review rules
- Full test suite runs locally before I accept any AI-authored change, every time, no exceptions
- I re-derive severity/confidence on security-style findings myself instead of accepting the AI's grade at face value
- If an AI-suggested fix touches something already flagged as an intentional course-scope tradeoff (e.g. open CORS, no auth), I check the reasoning still holds before touching it
- When AI adds a new constraint (a length cap, a validator), I check whether a test for the boundary actually exists before calling it done — I caught this gap myself during the final project's mini code review and had to add the missing tests after the fact

## 5. What I am still figuring out
- Where the line is between "let AI draft a self-assessment section" and quietly defeating the point of doing it myself
- Which hygiene findings (unpinned deps, unpinned base image) are worth actually fixing vs. acceptable for a course-scope project
- How much to trust AI-drafted governance docs before I've written my own rules for them

---

## Decision Card

AI-Assisted Coding - Module 5 Prompt Library
- For a new feature I reach for: an AI-scaffolded route/model/test skeleton that I then edit and test by hand
- For a code review I reach for: an AI pass first, followed by my own manual pass logged separately so the two don't blend together
- For debugging I reach for: AI to narrow down where the bug likely is, but I confirm root cause myself before trusting the diagnosis
- For infrastructure I reach for: AI to draft the Dockerfile/CI config, then I audit it myself for secrets and exposure before merging
- I will never paste real user data, credentials, or anything beyond this project's own code and output into an AI tool.
- My one rule is: if I can't explain what the AI wrote well enough to defend it in review, it doesn't get merged.
