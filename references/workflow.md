# Workflow reference

Canonical generated rules live in AI_KNOWLEDGE/WORKING_RULES.md and agent-system/*.md. Use them rather than copying policy into every provider adapter.

Default native packet: BRIEF.md + HANDOFF.md + events.md + VERIFICATION.md + evidence, using actual host tools. Optional automation packet adds task.json + verification.json and required hashes/gate. One observable goal with scope, source read order, acceptance, checks/environment and next step. Existing project-required schemas/gates take precedence; never silently downgrade them. No Python probe/install/helper invocation is needed for native setup. Record owner/transfer; only coordinator writes shared summaries/available registry. The registry is advisory, not a lock.

Model switch: previous writer stops and checkpoints; receiver reads packet, checks diff/current source/tools, reruns a relevant check and continues the first incomplete step. No capability claims without actual tools. Small-model tasks should be bounded by clear evidence and tests; ambiguous auth/crypto/migrations/payment invariants need stronger review or explicit limitation, not a promise of equal reasoning.

Q&A: explanation-only questions, including source reading to explain, need no task/log/tests. Persistent changes/audits/reports are work; record/test the action. User-requested durable rule changes are recorded even if phrased as a question.

Verification: after final edits run functional, error/negative and regression checks. Code needs all three passed; docs/audit functional/error required and genuinely inapplicable regression explained. Preserve failed/blocked/not_run checks and keep task open. Actual suite command must be discovered. Syntax/freshness/metadata gates don't prove business behavior.

verify_task.py validates a review/done packet's fields, categories, current deliverable hashes, scope and evidence digests. It never executes commands from JSON, authenticates logs or certifies correctness. A pass means ready_for_review only. Reviewer checks assertions and reruns meaningful tests; independent review only when actually performed, otherwise label self-review.

Keep provenance, current vs historical evidence, source exclusions and unknowns explicit. Don't persist credentials/PII/session tokens/hidden reasoning. No live testing/notification/deploy/DB mutation without current scope authorization.

v0.2 executable workflow: after reviewed plan preparation use run_verification.py (preview then explicit --execute), build_context.py for bounded handoff context, and benchmark_switch.py only when evaluating declared probes. Read generated agent-system/V02_TOOLS.md for contracts/limits. A packet gate never executes checks; the new runner does. Benchmark fixture results are harness checks, not real model measurements. Existing vault upgrades require deliberate helper/doc merging because bootstrap never overwrites files.

v0.3: inspect STACK_DISCOVERY and fill STACK_MAP via generated STACK_UNDERSTANDING.md. Each workspace/version has evidence levels: detected, mapped, traced, verified. Unrecognized stacks use source/official-doc learning and reviewed custom signatures; names never substitute for semantic understanding. DeepSeek/GLM/Kimi and arbitrary providers share the capability-based protocol in adapters/UNIVERSAL_AGENT.md. prepare_agent requires current task/pack/included-source hashes. Native host activation and capabilities are separately verified, never inferred from a model label. Profiles carry no credentials and invoke no API.
