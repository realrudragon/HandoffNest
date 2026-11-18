---
name: handoff-nest
description: Set up or extend portable project knowledge and agent handoffs using the host's own file tools by default, with optional Python automation. Use when asked to organize a project for AI agents or bootstrap HandoffNest project knowledge across models including DeepSeek, GLM and Kimi; not for explanation-only questions or ordinary feature work alone.
---

# HandoffNest

Version 0.5.0. **Default: native** — use the host's own file/search/edit tools. No Python installation, runtime probe or bootstrap command is required for normal setup. Python helpers are optional advanced tools.

## Start from one request

The user only needs to install/open this skill, open their project and say:

```text
$handoff-nest จัดโครงสร้าง AI ให้โปรเจกต์นี้
```

Resolve routine choices yourself. Ask only for genuinely missing scope or permissions. Answer explanation-only questions directly without setup, logs or tests.

## Native workflow

1. Read existing instructions/handoff and inspect the actual project root. Parent Git repositories, siblings and old notes do not expand authorization. Keep internal knowledge outside public document roots; request a safe location if none is authorized.
2. Confirm real host tools. With file tools, continue directly. A chat-only host returns proposed files and missing-source requests; never claim saved files or executed tests. Model/provider labels do not grant capabilities.
3. Use [native setup](references/native-setup.md) and `assets/native/setup-plan.json` when accessible. Create only missing starter files with native file tools, preserve existing user text/ownership and fill placeholders from observed source. Do not run helpers or install dependencies for the default workflow.
4. The starter is `AI_KNOWLEDGE/START_HERE.md`, `QUICK_CONTEXT.md`, `PROJECT.md`, `STACK_MAP.md`, `WORKING_RULES.md`, `HANDOFF.md`, `TASKS.md` and `SETUP.md`, plus one bounded pointer in project AGENTS.md. If assets are unavailable, write equivalent documents with these purposes and the rules below. Never invent missing resources or copy another project's facts.
5. Inspect manifests/entrypoints/routes/modules/config precedence/data/auth and the CSS/template pipeline. Fill evidence/unknowns; trace real success/error paths before claiming understanding. Read the stack playbook/catalog when useful. For unfamiliar versions use owning source/local docs and official docs when available; keep missing verification pending.
6. For work keep a task folder with BRIEF.md, HANDOFF.md, events.md, VERIFICATION.md and relevant evidence. Record goal, owner/scope, done/pending, files, actual commands/environment/results, failures and next step. Checkpoint during work and before transfer/limits; one writer per path, coordinator-only shared summaries.
7. Use actual project runtimes/tools for functional, error/negative and regression checks after edits. Check links/source references and preservation for setup/docs work. Record passed/failed/not_run individually with evidence. Failed/unavailable required checks mean unverified; never fabricate a pass, hash or graph. Explanation-only Q&A is exempt.
8. Review and finish with a short user summary: what exists, what was verified, limitations and where the next agent starts. Keep helper details out of the normal user flow.

Native Markdown review is a different evidence path from the optional JSON gate. Existing project-required receipts/gates/security rules take precedence; never silently downgrade them. Compute hashes with actual native tools or record `not_computed`. Mark an unused optional gate `not_run_optional`, never passed/ready_for_review.

## Complete project edition

When the user asks for complete/thorough setup (including ฉบับสมบูรณ์), follow [complete setup](references/complete-setup.md) and its declarative native plan. Extend the eight-file starter with source-backed architecture/module/config/flow/data maps, unknowns, findings status, maintenance/collaboration and handoff guidance. Preserve existing files; completion is evidence or explicit unknowns, not empty templates or a claim that every runtime path was tested. This remains native and needs no Python/helper install.

## Optional automation

Only use this path when the user requests automation or an existing project requires it. Read [automation](references/automation.md) for bootstrap, discovery, hashed context, JSON gate, runner and benchmark commands. Their runtime requirements still apply. If unavailable keep required gates pending or use a separately authorized native path; do not force runtime installation to start normal setup.

Codex/Claude/Gemini/Cursor/Copilot pointers and DeepSeek/GLM/Kimi/arbitrary-label handoffs use actual host capabilities. Native handoffs need no exporter; automated exports have stricter task/source/hash prerequisites. Graphify is optional: use an actual current graph/tool when available, otherwise retain source maps and mark graph work pending, not fabricated.

Preserve secrets/PII and historical evidence. This skill grants no account changes, paid calls, live DB mutation, deployment, invitations, commits or pushes beyond current authorization. Do not promise universal host discovery, compliance or frontier-equivalent reasoning.
