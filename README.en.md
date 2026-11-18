# HandoffNest

**v0.5.0 · Portable project knowledge and durable agent handoffs**

[ภาษาไทย / complete Thai guide](README.md) · [Download ZIP](https://github.com/realrudragon/HandoffNest/archive/refs/heads/main.zip)

Let an agent inspect your project, record source-backed knowledge, verify its work and prepare a durable handoff. Normal use requires the host's file tools, **not a Python installation or bootstrap command**. This repository is public; downloading does not require repository access permissions.

[Start](#quickstart) · [Install](#install) · [First run](#first-run) · [Complete edition](#complete) · [Outputs](#outputs) · [Daily use](#daily-use) · [Handoffs](#handoff) · [Agents](#agents) · [Stacks](#stacks) · [Checks](#verification) · [Help](#troubleshooting) · [Updates](#updating) · [Privacy](#privacy) · [Advanced](#advanced)

<a id="quickstart"></a>
## Start in three steps

1. Install/open the skill using your host's supported method.
2. Open the actual application project, not the skill repository.
3. Send:

```text
$handoff-nest Organize this project for AI agents without changing application code.
```

The agent handles missing knowledge files, source inspection, checkpoints and verification. Existing files and project requirements take precedence. A chat-only host proposes contents; it cannot claim saved files or executed tests.

<a id="install"></a>
## Install once

Open [HandoffNest on GitHub](https://github.com/realrudragon/HandoffNest). Use **Code → Download ZIP**, extract the archive and rename its folder to `handoff-nest`. Keep SKILL.md, assets/ and references/ together at the folder root. See [GitHub's archive guide](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives).

Use your host's documented skill installation/import method, or ask a file-equipped coding agent to install from that folder without overwriting unrelated settings or installing runtimes. Host discovery paths and menus differ; no single method is guaranteed for every app.

If the host has no native skill system, use direct file reading. Replace these example paths with real authorized locations:

```text
Read C:/Skills/handoff-nest/SKILL.md and its required local references.
Apply it to C:/Projects/my-app, not to the skill folder.
Keep internal knowledge outside the public document root; do not change app code.
```

If file access is unavailable, attach the required documents/source or grant access through the host's supported controls. Do not claim an installation/read succeeded when it did not.

<a id="first-run"></a>
## What the agent should do

Read existing instructions/handoff, resolve scope, inspect actual manifests/entrypoints/routes/modules/config/CSS, create only missing knowledge files and fill observed facts/unknowns. Finish with created/preserved paths, actual checks/evidence, limitations and the next read order. Empty templates are not completed analysis.

For web projects keep AI_KNOWLEDGE outside public/ or public_html/. If no safe authorized location exists, request one before writing; do not expand to a parent/sibling project silently.

<a id="complete"></a>
## Request the complete edition

```text
$handoff-nest Prepare the complete native edition for this project.
Fill source-backed architecture, modules, config, flows, data model and source map.
Include unknowns, collaboration, verification, maintenance and agent handoffs.
Preserve existing files and application code; use available tools without requiring Python.
Report inspected source, actual evidence/checks and everything still unverified.
```

The complete native plan extends eight starter documents with sixteen detailed maps/protocols, for 24 main documents plus AGENTS/task records. Every domain needs source evidence, an explicit unknown/next action, or a justified not_applicable. This is knowledge-domain completeness, not a claim of reading every line or verifying every runtime/security path. [Full procedure](references/complete-setup.md).

Graphify is optional. Use an actual current graph/tool with provenance when available; otherwise retain source maps and an honest pending/unavailable status. Never invent graph output.

<a id="outputs"></a>
## Outputs

The basic starter contains START_HERE.md, QUICK_CONTEXT.md, PROJECT.md, STACK_MAP.md, WORKING_RULES.md, HANDOFF.md, TASKS.md and SETUP.md inside AI_KNOWLEDGE, plus a bounded project AGENTS pointer.

The complete edition adds ARCHITECTURE, MODULES, SOURCE_MAP, CONFIG, FLOWS, DATA_MODEL, OPEN_QUESTIONS, FINDINGS, SESSION_LOG, DECISIONS, MAINTENANCE, GRAPHIFY, COLLABORATION, HANDOFF_PROTOCOL, VERIFICATION and NEXT_AGENT_PROMPT documents.

Work records go in work-items/<task-id>/ with BRIEF/HANDOFF/events/VERIFICATION/evidence. Existing mandatory JSON schemas/gates remain required. Start new agents from START_HERE, compact context and current handoff.

<a id="daily-use"></a>
## Everyday requests

```text
Read the knowledge vault and continue the next unfinished step within my assigned scope.
```

```text
Update the maps after these source changes. Preserve history and record actual functional,
error/negative and regression checks before completion.
```

```text
Checkpoint now: goal, owner/scope, done/pending, changed files, commands/results,
failures, limitations and the exact next action for a new agent.
```

Explanation-only questions need no mandatory task/log/test. File changes, durable reports, audits and work actions do.

<a id="handoff"></a>
## Switch agents or collaborate

Stop/checkpoint the previous writer before transferring the same paths. Send the receiver:

```text
Read AGENTS.md, AI_KNOWLEDGE/START_HERE.md, QUICK_CONTEXT.md and HANDOFF.md.
Then inspect the assigned task's BRIEF/HANDOFF/VERIFICATION and current source.
Confirm real tools, owner/scope and authorization; continue the first unfinished step.
```

One writer per path; a coordinator owns shared summaries. Workers use task-local records. Registries/ownership tables are advisory, not atomic locks. Serialize overlapping work or use appropriate isolated worktrees/fixtures. Chat-only agents need attached source/context and an authorized tool-equipped writer for application/testing.

<a id="agents"></a>
## Agent compatibility

Codex/AGENTS readers, Claude Code, Gemini, Cursor, Copilot and hosts using DeepSeek/GLM/Kimi/other models share the same knowledge/handoff protocol. Use a host's supported instruction mechanism or direct SKILL.md reading. Actual file/command/network capabilities determine what can be done; model names do not grant them.

Extra provider pointers exist in the scaffold, but the native starter does not copy every adapter automatically. Discovery must be verified per host/version. This package does not connect APIs, install SDKs or guarantee universal compliance/equal reasoning ability.

<a id="stacks"></a>
## Languages, frameworks and CSS

Inspect each project afresh, from PHP/CI3/HMVC/Laravel and JS/TS frontend stacks to Python, Go, Rust, Java/.NET, mobile or unfamiliar systems. Optional discovery includes 183 recognition signatures/53 language-file families; recognition is not universal semantic understanding.

For CSS/UI trace actual imports/build/layers/tokens/theme/template authority and preserve the existing visual system. Unfamiliar stacks follow owning-source and version-specific documentation, with unresolved facts kept unknown. [Stack guide](assets/scaffold/AI_KNOWLEDGE/agent-system/STACK_UNDERSTANDING.md).

<a id="verification"></a>
## Verification and honest limits

Require actual functional, error/negative and regression checks appropriate to the work after edits. Record exact tool actions/commands, environment, exit/results, observed assertions and evidence. Separate setup/document checks from application/browser/runtime coverage. Unavailable required checks remain unverified.

Native Markdown review does not imply a JSON machine-gate pass. Uncomputed hashes stay not_computed; an unused optional gate stays not_run_optional. Existing project-required gates cannot be silently downgraded.

<a id="troubleshooting"></a>
## Troubleshooting

| Problem | Next step |
|---|---|
| 404/download denied | Use the HandoffNest link above, check connectivity and branch `main`; this public download needs no access invitation or token |
| Skill name not found | Check for nested folders/SKILL.md location, or use direct file reading |
| Agent demands Python | Request native setup; keep pre-existing mandatory gates pending rather than bypassing them |
| No files appeared | Verify target path/write tools; chat-only output is a proposal until actually saved |
| Wrong project inspected | State skill-folder and application-folder paths separately |
| Empty templates | Ask for complete source-backed maps with evidence/unknowns/next steps |
| Existing vault | Preserve history/human rules; fill only missing or deliberately reviewed changes |
| No Graphify/test runtime | Record pending/unverified and provide exact next actions; do not fake output |
| Context/usage limit | Checkpoint and stop the old writer before assigning a new agent |

<a id="updating"></a>
## Update or move machines

Update the skill using the host's supported method or a coding agent that reviews diffs and preserves unrelated local work. Do not replace a real project's knowledge with blank templates. Move project code and reviewed knowledge together, install the skill in the new host and recheck paths/tools/permissions. Do not bundle credentials/session tokens. Removing a skill is not an instruction to delete project knowledge.

<a id="privacy"></a>
## Privacy and authorization

The reusable package contains instructions/templates/helpers/tests, not another user's project source/audit/customer data. Never persist credentials/cookies/tokens/hidden reasoning in generated knowledge. Keep internal docs outside public webroots and review before sharing. AI-service data behavior follows the chosen host/provider; this skill does not create a sandbox or offline environment.

Reading/installing the skill does not authorize deployment, migrations, live DB/API writes, paid calls, messages, pushes or invitations. Repository sharing/visibility changes need explicit authorization; this skill repository is public, while your project knowledge stays wherever you choose to store it.

<a id="advanced"></a>
## Optional automation and contributors

Normal users can skip Python helpers entirely. See [automation](references/automation.md) for bootstrap, hashed context, runner/formal JSON gate, benchmarks and maintainer tests; each has its own runtime requirements. [Native setup](references/native-setup.md), [complete setup](references/complete-setup.md), [universal handoffs](assets/scaffold/AI_KNOWLEDGE/adapters/UNIVERSAL_AGENT.md) and [Graphify](references/graphify.md) explain the respective paths.

Maintainer Python tests are separate from user dependencies. Distinguish deterministic contracts, actually exercised host behavior and untested provider/OS/runtime coverage.
