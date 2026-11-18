# Graphify integration

Prefer an existing current graph; query it before rebuilding. Check scoped source freshness. If another Graphify skill is available, follow its code-only workflow; do not invoke semantic agents for a code-only corpus.

Locate graphify CLI/interpreter in the current environment; don't hardcode the original author's user directory. Use a project/private venv if installation is authorized, otherwise record pending with an actionable tool requirement. Python package is graphifyy; AST needs no external LLM credentials. Do not install arbitrary similarly named packages.

Example CLI sequence (check installed --help; syntax may vary by version):

```text
graphify extract <first-party-source-root> --code-only --no-cluster --out <project-root>/AI_KNOWLEDGE
graphify cluster-only <project-root>/AI_KNOWLEDGE --graph <project-root>/AI_KNOWLEDGE/graphify-out/graph.json --no-label
graphify export html --graph <project-root>/AI_KNOWLEDGE/graphify-out/graph.json
```

For large or mixed repositories use the package Python APIs with an explicit list of first-party source files from discovery and stable root/cache_root rather than blindly indexing vendor/generated code. Review sensitive-file exclusions. Preserve node provenance, source root and versions; dynamic HMVC loads and duplicate class names need source confirmation. Record health warnings such as dangling endpoints or self-loops.

Retain graph.json, GRAPH_REPORT.md, graph.html, labels/extraction/health where available. Don't copy interpreter sidecars or virtualenv/cache into portable output. Record source_file's base directory clearly. If viewer scripts use a CDN, either state the network dependency or retain pinned assets with licenses/digests locally for offline viewing. Never call a graph verified solely because an HTML file exists.

Source: https://github.com/Graphify-Labs/graphify
