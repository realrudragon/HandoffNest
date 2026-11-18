# Work together without overwriting each other

Record owner/scope/status/next step in each task BRIEF/HANDOFF. One writer owns a path at a time; overlapping parent/child paths overlap. A coordinator assigns work and updates shared HANDOFF/TASKS/SESSION_LOG/DECISIONS. Workers write only assigned paths and task-local events/evidence.

Use an existing coordination registry when present. A native project can keep an ownership table in TASKS.md and task records; no new JSON registry is required. A file registry/table is advisory, not an enforced lock. Never steal ownership based only on elapsed time.

Use disjoint paths/worktrees when tools support them; otherwise serialize conflicting edits. Worktrees do not isolate databases/services. Transfer only after the old writer stops/checkpoints and the receiver verifies current scope/source/evidence. On conflict preserve both parties' work and reconcile deliberately.

Review actual changes/acceptance/functional/error/regression evidence before integration. Label self-review and independent review truthfully. Model labels do not guarantee competence or tool availability. No deployment, account/API/DB changes, commit/push or messages to others are authorized by a task board alone.
