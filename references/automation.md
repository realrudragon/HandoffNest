# Optional Python automation / maintainer guide

Normal setup follows SKILL.md and native-setup.md with host file tools. This guide is for explicit automation or project-required formal gates. Python is not a prerequisite for the default skill; do not install it just to start native setup.

## Requirements and installation

Helpers require Python 3.9+; full TOML discovery needs Python 3.11+ tomllib. Standard library, no required provider SDK. Tested on Python 3.11.9 / Windows; other-OS/live provider compatibility must be verified separately.

For Codex on a new machine, if the destination does not exist:

```powershell
git clone https://github.com/realrudragon/HandoffNest.git "$HOME/.codex/skills/handoff-nest"
```

Host discovery paths vary; this public repository can be downloaded without repository access permissions. Preserve records and deliberately merge reviewed updates for existing installs/vaults.

## Automated scaffold

From the skill repository choose an existing authorized project root outside its public document root:

```powershell
python scripts/bootstrap.py --project-root "C:/Projects/my-app" --dry-run
python scripts/bootstrap.py --project-root "C:/Projects/my-app"
```

The fuller scaffold preserves existing files and adds metadata/stack reports, protocol templates, helper scripts and tests. It does not complete source understanding; fill maps from source/versions and keep unknowns visible. Current user/project authorization still applies.

## Tool contracts

| Helper | Details |
|---|---|
| discover_stack.py | [Stack recognition/source learning](../assets/scaffold/AI_KNOWLEDGE/agent-system/STACK_UNDERSTANDING.md):183 signatures/53 file families, no runtime proof |
| build_context.py | [Scoped context](../assets/scaffold/AI_KNOWLEDGE/agent-system/V02_TOOLS.md): task/source hashes, character budget, provenance/omissions |
| prepare_agent.py | [Automated universal export](../assets/scaffold/AI_KNOWLEDGE/adapters/UNIVERSAL_AGENT.md): current generated context/task/source hashes required |
| run_verification.py | Reviewed argv preview; explicit --execute retains real output/assertions/plan/current hashes |
| verify_task.py | Read-only JSON/evidence consistency gate, not correctness or merge authority |
| benchmark_switch.py | Fixture/model adapters, supplied probes; measured wall time/context vs unverified reported usage |

Protocol-v1 JSON packets remain compatible when formal gates are required. Native Markdown packets do not fake gate passes. Missing required runtime/gate stays pending; any fallback must be separately authorized and preserve project policy.

Graphify: [graphify.md](graphify.md). Missing tooling does not block a native starter or permit invented graphs.

## Demonstrations and maintainer tests

Choose a new output directory:

```powershell
python assets/scaffold/AI_KNOWLEDGE/examples/v03_demo.py --output "$env:TEMP/handoff-nest-demo-new"
python -m unittest discover -s tests -v
python -m unittest discover -s assets/scaffold/AI_KNOWLEDGE/tests -v
```

The demo uses real synthetic checks/provider-labeled fixtures with zero API calls. It is not a live provider benchmark or proof of model improvement. Maintainer Python tests are separate from the native-user workflow.

Commands/adapters are trusted code, not sandboxed. Rooted paths stop accidental traversal, not malicious processes. Redaction is best-effort; review before sharing. Direct-process timeout does not guarantee descendant cleanup. No credentials/account changes, paid calls, live DB mutation or deployments implied.

## Persistent protocol compatibility

HandoffNest 0.5.0 uses `handoff-nest` as the skill name and folder. The historical `worachote-structure-ai` managed AGENTS markers and `worachote-*` producer identifiers remain stable internal protocol values, so existing generated pointers, context manifests and their validating consumers stay compatible. These are not alternate skill commands. Keep existing vault files and evidence; review updates before merging tools. Do not install two active copies of the same skill.
