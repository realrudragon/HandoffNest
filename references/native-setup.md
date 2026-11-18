# Default native setup — agent procedure

The user invokes the skill; the agent handles file preparation with its host's own tools. Do not probe for Python, install runtimes, run bootstrap/helpers or ask the user to choose a technical mode for normal setup. Maintainer tests may use Python; that is separate from the user workflow.

## Scope and capabilities

Read current AGENTS/handoff. Resolve the authorized project root, source root and a nonpublic knowledge location. Follow project instructions and preserve existing files/permissions. Parent/sibling workspaces and old notes are not authorization. If no safe authorized location exists, request it before writing.

Check actual file tools. With read/write tools use the plan below. A read-only or chat-only host supplies proposed file contents/diffs and a next-step handoff; it must not claim saved files, hashes, executions or a completed setup. Request missing owning source as text/attachments. Model labels do not establish capabilities.

## Prepare the small starter

Read `assets/native/setup-plan.json` if available. It declares eight Markdown targets and no runtime dependencies. Inspect actual manifests/entrypoints first; resolve PROJECT_NAME, SOURCE_ROOT, STACK and CREATED_AT placeholders from observed facts. Use `unverified` for unknown values; never guess a version or fake a timestamp.

For each mapping, read the bundled source and write only a missing target using actual native file tools. Preflight all destinations before writes: stay under the authorized nonpublic root, reject traversal/symlink/junction escapes and check ownership. Do not copy scripts, JSON receipts, the full catalog or another project's reports into the default starter. If a target exists preserve it; do not overwrite it merely to match a template. Merge a specific user-requested correction deliberately with a record.

For AGENTS.md preserve all user text. Append the plan's bounded pointer only if no managed marker exists. Preserve existing valid markers. Mismatched/repeated markers require inspection/repair in scope; do not append a competing block. Root instructions remain authoritative. If a host does not discover AGENTS explicitly attach its rules; do not invent provider auto-loaded filenames.

If resources are inaccessible but the main skill is available, create equivalent core documents from SKILL.md and record missing resources as a limitation. A thin starter must not link to unavailable files.

## Fill knowledge, not just folders

Inspect owning source and fill compact project facts: purpose, routing/entrypoints/module wiring, config precedence without secret values, data/auth/IO boundaries and CSS/template authority. Separate version constraints from observed installed versions. For an unfamiliar framework trace a success/error path and consult matching local/official docs when available. A package/filename alone is not understanding. Add detailed maps only when useful; avoid dumping the codebase into a small model.

Keep existing source maps/Graphify snapshots with provenance. Use Graphify only when actually available/useful; otherwise note graph work pending and continue source-backed maps. Do not create fake graphs, indexes or successful helper output to satisfy templates.

## Native task and evidence

For work create work-items/<id>/BRIEF.md, HANDOFF.md, events.md, VERIFICATION.md and evidence. Identify owner/scope/acceptance. Checkpoint after meaningful work/failures and before transfer/limits; one writer per path, coordinator owns shared summaries. Explanation-only Q&A requires none of these mutations.

Use actual project tools after edits for functional, error/negative, regression and established suites. Retain exact commands/tool actions, environment, exit/result, observed assertions, changed paths, failures and evidence references. Unavailable execution leaves required checks not_run/unverified; writing files alone is not verified completion.

Compute hashes with real native tools or record `not_computed`; never fabricate SHA values. The optional JSON gate is `not_run_optional`, not passed/ready_for_review. Native evidence receives native Markdown review; it is not certified equivalent to the machine gate. Existing project requirements take precedence: mandatory receipts/gates still run or stay pending. Never silently downgrade policy to avoid dependencies.

For setup/docs check actual files, placeholders, links/source references and preservation of prior files/AGENTS. Exercise a missing-resource/unsafe-target/preservation case on disposable fixtures where possible. Distinguish deterministic contract checks, self-review and independently performed review. Keep required checks that cannot run visible.

## Finish and switch agents

Update SETUP/HANDOFF/TASKS from observed results. State saved vs proposed, understood vs unknown, passed vs not_run and next action. Transfer ownership only after the previous writer stops/checkpoints. A native handoff supplies rules, compact context, task BRIEF/HANDOFF and owning-source/evidence references directly; no exporter required. Keep sensitive data out.

Tell the user briefly what is ready and where to start. Keep helper/runtime details in the optional automation guide unless requested.
