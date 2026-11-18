# HandoffNest automation tools (protocol v0.2)

These are optional Python automation tools. Normal v0.4 setup uses native host tools and Markdown evidence; it does not require these commands. Existing project-required gates remain mandatory and cannot be silently downgraded. Runtime requirements below apply only when using these helpers.

Three portable Python stdlib tools turn the handoff protocol into observable actions. Run from the project root; Python 3.9+ is required (tested on Python 3.11/Windows). Packet format remains protocol_version=1. Project source stays authoritative.

## Verification Runner

Create work-items/<id>/BRIEF.md, HANDOFF.md, events.md and task.json, then copy templates/verification-plan.json into that task and replace its checks with real project commands. Each argv is an array; cwd is project-relative. A reviewed command is executable code, including Python/shell programs explicitly named in argv.

```sh
python AI_KNOWLEDGE/tools/run_verification.py --task AI_KNOWLEDGE/work-items/<id>/task.json --plan AI_KNOWLEDGE/work-items/<id>/verification-plan.json
python AI_KNOWLEDGE/tools/run_verification.py --task AI_KNOWLEDGE/work-items/<id>/task.json --plan AI_KNOWLEDGE/work-items/<id>/verification-plan.json --execute
python AI_KNOWLEDGE/tools/verify_task.py --task AI_KNOWLEDGE/work-items/<id>/task.json
```

First command only previews. Execute runs all reviewed checks, requires functional/error/regression categories, expects exit 0 and applies expect_stdout/expect_stderr/forbid_stdout/forbid_stderr substring assertions. An error test must itself return 0 when it observes the expected failure. A category label alone cannot prove the command tests that category; reviewers inspect commands/assertions.

Each run retains argv, cwd, elapsed time, exit/timeout, redacted output, assertions, redacted plan snapshot, original plan SHA, deliverable hashes and immutable run receipt under task evidence/verification-runs/<run-id>/. The latest receipt is restricted to the task's verification.json; prior latest receipt is preserved before replacement. Changed deliverables or plan invalidate the run. Exit: 0 verified, 1 failed checks/drift, 2 invalid input/configuration. Gate ready_for_review still means packet consistency, not semantic certification.

## Context Builder

Add a task.context_files array of relevant project-relative files; do not list the entire repository. Rules, task summary, BRIEF and HANDOFF are mandatory. QUICK_CONTEXT and selected documents follow, then at most 12 Graphify relationships if available.

```sh
python AI_KNOWLEDGE/tools/build_context.py --task AI_KNOWLEDGE/work-items/<id>/task.json --out AI_KNOWLEDGE/work-items/<id>/context-pack.md --max-chars 12000
```

Budget counts Unicode codepoints, including Thai; it is not a model token estimate. Mandatory material never silently disappears: insufficient budget fails. Optional omissions appear in context-pack.manifest.json with reasons. Included files carry SHA-256, provenance and redaction flags. Graph excerpts are static navigation and may be stale/inferred. Re-read owning source before edits; the pack does not run freshness checks for you.

Raw source requires --include-source; obvious credential/key paths are refused. Default refuses overwrite; --replace refreshes only an unchanged generated pack with its matching producer/task/hash manifest. Packet records, human notes and deliverables are protected. Output stays inside the task directory.

## Agent Switch Benchmark

Copy templates/benchmark-plan.json and supply your own trusted adapter. The supplied template uses a synthetic fixture adapter from examples/v02_demo.py; copy/adjust that adapter before running. Preview before executing:

```sh
python AI_KNOWLEDGE/tools/benchmark_switch.py --task AI_KNOWLEDGE/work-items/<id>/task.json --plan AI_KNOWLEDGE/work-items/<id>/benchmark-plan.json
python AI_KNOWLEDGE/tools/benchmark_switch.py --task AI_KNOWLEDGE/work-items/<id>/task.json --plan AI_KNOWLEDGE/work-items/<id>/benchmark-plan.json --execute
```

Adapter argv uses {request} and {response} file placeholders. Request JSON contains protocol_version, case_id, variant, trial, prompt, context [{path, sha256, text}] and instructions. Expected answers are withheld from requests. Adapter writes UTF-8 JSON {"answers":{"key":"value"},"reported_usage":{"input_tokens":123}}. Usage is optional and self-reported. Use a fresh provider conversation per invocation and explicitly label adapter.kind=fixture or model. Supply model/API access yourself; this package installs no provider SDK, calls no API by default and authorizes no paid usage.

Harness shuffles paired variants deterministically by seed, runs 1..20 trials (max 200 calls), grades exact JSON field equality and retains trial requests, redacted responses/execution, original plan SHA, redacted plan snapshot, JSON/Markdown report. Invalid output/launch failure/timeout/plan drift means partial, exit 1; valid wrong answers yield low accuracy, completed exit 0. Invalid plans return 2. Compare scores alongside runtime errors, case count, wall time and context characters. Keep adapters/models/prompts/cases equal when comparing variants.

Scores cover only declared probes. Fixture scores prove harness behavior, not model improvement. This cannot establish that a smaller model equals a frontier model. Wall time/context length are measured; tokens/cost/usage from adapters are unverified. Requests/processes are separate; provider cache isolation, fairness and closed-book access are not enforced. Ground truth stays in the retained audit snapshot; trusted adapters can read local files.

## Runnable demonstration and limits

```sh
python AI_KNOWLEDGE/examples/v02_demo.py --output AI_KNOWLEDGE/work-items/<id>/evidence/demo-new
```

Output must not exist. Demo uses a temporary synthetic Python project, builds context, runs actual functional/error/regression assertions, validates its receipt and benchmarks a deterministic fixture across baseline/context variants. It exports the synthetic packet/evidence and command results; no application/DB/model/API use. A deliberately context-sensitive fixture will score better with context by construction; it is not an experiment on real agents.

All commands/adapters are trusted operator input, not sandboxed. Rooted path checks stop accidental traversal, not malicious processes or race attacks. Direct-process timeout does not guarantee descendant cleanup. Output capture is in memory, retained text capped at 100,000 characters; use bounded checks. Redaction is best-effort and snapshots may redact assertion values: inspect retained artifacts before publishing. These checks cannot guarantee secret removal. Never use secrets as literal argv or ground truth. Do not benchmark production mutation or external messaging as a convenience test.
