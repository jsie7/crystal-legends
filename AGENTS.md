# AGENTS.md


## Agent-First Documentation Policy

For repository questions and implementation tasks, consult sources in this order:
1. `AGENTS.md`
2. `docs/decisions.md` (if present)
3. other relevant files in `docs/` such as `docs/README.md` and `docs/workflows.md`
4. source code and checked-in configuration
5. `plan/` for active work, drafts, and temporary notes

If docs and code conflict, treat code and checked-in configuration as the source of truth and update docs in the same change.

Keep docs standalone, concise, cross-linked, and aligned with current behavior.
Use `docs/workflows.md` for repeatable operating procedures when it is present.
Use `docs/decisions.md` for durable technical or policy decisions when it is present.

## Agent Planning Workspace

Use `plan/` for temporary agent artifacts such as:
- current notes and note indexes
- draft plans and execution checklists
- handoffs for active work

Promote durable guidance from `plan/` into `docs/`.
Keep active work in `plan/`.
Do not commit `plan/` artifacts.
