# Any model, explicit host capabilities

DeepSeek, GLM, Kimi and other models use the same canonical task/context/evidence protocol. Model identity is separate from the editor/CLI/agent host. The host must actually supply file access, writing, command execution or network tools; an instruction file cannot grant them. Existing Codex/Claude/Gemini/Cursor/Copilot pointers remain available. Native instruction discovery must be checked in each host/version; no invented DEEPSEEK.md/GLM.md/KIMI.md auto-loading assumption.

## Native handoff — default

Supply canonical rules, compact context, task BRIEF/HANDOFF, native VERIFICATION/evidence and owning source references directly using the host's tools. No Python/profile/exporter is required. Confirm actual read/write/run/network capabilities independently of model identity. Chat-only hosts return proposed content and missing-source requests; never claim writes/tests. Preserve explicit project-required schemas/gates; native Markdown review is not a machine-gate pass. Hashes not actually computed stay not_computed.

## Automated handoff — optional Python export

1. Copy a profile from adapters/profiles/ into the task directory (deepseek.json, glm.json, kimi.json or generic.json). Set descriptive provider/model/host labels and only capabilities observed in that host. Defaults are all false/unconfigured. Store no API keys, endpoints with credentials, shell commands or account secrets in profiles.
2. Create the normal task packet, inspect its scope/owner, build a current context pack using build_context.py. Prefer bounded source-backed context for smaller models; missing required files must stay missing, not be invented.
3. Export a new handoff:

```sh
python AI_KNOWLEDGE/tools/prepare_agent.py --task AI_KNOWLEDGE/work-items/<id>/task.json --profile AI_KNOWLEDGE/work-items/<id>/agent-profile.json --context AI_KNOWLEDGE/work-items/<id>/context-pack.md --out AI_KNOWLEDGE/work-items/<id>/agent-handoff.md
```

The exporter accepts any provider label. It verifies the generated context/task binding and current source/pack hashes, preserves inputs/human outputs and emits a source-bound manifest. --max-chars controls the entire export in Unicode characters; insufficient space fails rather than dropping canonical rules. Rebuild stale context before exporting. Use a new output name for each transfer; no destructive replace mode.

| Mode | Declared capabilities | Workflow |
|---|---|---|
| workspace | read + write + run | Give host the handoff, verify tools/ownership, inspect current source, implement and actually run checks. |
| assisted | read files, incomplete write/run | Agent investigates and returns proposed changes or commands; authorized writer/runner supplies missing operations/evidence. |
| chat-only | no file reading | Paste/attach the exported handoff and necessary owning files, ask for proposed changes, then hand them to a tool-equipped agent for application/testing. |

Capabilities in export are operator-declared, not tested/activated by the exporter. No network capability means external docs remain pending until checked by an authorized host. No run capability means tests cannot be claimed passed. Explanation-only Q&A remains exempt from work logging/testing. Before switching writers stop/checkpoint/transfer ownership explicitly.

The skill performs no provider API call, SDK install, paid operation or account/global-host configuration. Live compatibility, model availability/limits and native skill installation are not validated by synthetic export tests. For a real benchmark supply a reviewed adapter to benchmark_switch.py and define data/cost scope separately. No guarantee of equal reasoning or universal compliance.

## Primary provider references

Checked 2026-11-18; recheck before provider-specific implementation. These document provider APIs/tools; they do not prove that a particular chat app can access this repository.

- [DeepSeek API and agent integrations](https://api-docs.deepseek.com/) — use current integration/API documentation for the selected host.
- [Z.AI function calling](https://docs.z.ai/guides/capabilities/function-calling) — tool definitions/calls still need application-side execution.
- [Kimi tool-call workflow](https://platform.kimi.ai/docs/guide/use-kimi-api-to-complete-tool-calls) — the host executes requested tools and returns results.

No specific latest model ID, pricing or unverified maximum context is embedded in the skill.
