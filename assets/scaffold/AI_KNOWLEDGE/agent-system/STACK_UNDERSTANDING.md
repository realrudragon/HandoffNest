# Understanding any stack without pretending to know it

HandoffNest recognizes many common stacks and supplies a process for unfamiliar ones. A finite signature list cannot guarantee knowledge of every framework/version. Source, verified version-specific documentation and observed behavior establish understanding. Keep gaps visible and extend reviewed rules rather than guessing.

## Discover first

Default native path: inspect manifests/entrypoints/imports with host file/search tools and record observations/unknowns in STACK_MAP. No Python probe, helper invocation or generated STACK_DISCOVERY.json is required. The commands below are optional automation; do not fabricate their report when using native inspection. Use the same source-learning evidence levels in either path.

```sh
python AI_KNOWLEDGE/tools/discover_stack.py
python AI_KNOWLEDGE/tools/discover_stack.py --out AI_KNOWLEDGE/work-items/<id>/stack-discovery.json
python AI_KNOWLEDGE/tools/discover_stack.py --rules AI_KNOWLEDGE/work-items/<id>/custom-rules.json
```

Default prints a read-only JSON report. --out must be a new .json path inside AI_KNOWLEDGE. The bundled catalog has 183 recognition signatures and 53 language/file families; these are recognition coverage, not 183 verified framework implementations. Custom rules augment the registry; conflicting IDs/unsafe paths are rejected. Use templates/custom-stack-rules.json as a starting point. Each rule uses exact dependency names and/or filename glob markers, never executable plugins.

The scanner inspects package.json, composer.json, pyproject.toml/requirements, Cargo.toml, go.mod, Gemfile, Maven/Gradle, .NET project files and simple pubspec dependencies. Full TOML parsing needs Python 3.11+; on earlier Python versions it stays pending. Ruby/Gradle/YAML are limited static extraction, never full DSL evaluation. Lockfile resolution, aliases, includes, inherited/dynamic configuration and actual installed/runtime versions require follow-up. Script names are retained; script bodies are neither stored nor run.

Monorepo findings retain the nearest manifest directory and per-signal version constraint. Multiple declarations can coexist; do not collapse Tailwind v3 in one app and v4 in another. declared confidence means a dependency declaration exists, including dev/peer/optional requirements; candidate means filename/import/CDN evidence only. Neither proves a runtime path uses it. Marker-only signals can have no hash when content could not be read within limits.

Default limits: 20,000 enumerated files, 5,000 visited directories, depth 10, 16 MiB total content, 512 KiB per read. Use --max-files/--max-directories/--max-depth/--max-bytes to select a bounded scope. Vendor/generated/dependency folders, reparse points/symlinks and obvious secret paths are excluded. A capped/malformed scan returns partial (exit 1); configuration errors exit 2. Exit 0 means selected static discovery completed, never exhaustive semantics. Read warnings, excluded directories and coverage; unsupported formats/unknown extensions stay unknown. Review reports before sharing; metadata and redaction are best-effort privacy controls.

## Move from recognition to actual understanding

Fill STACK_MAP.md per workspace. Link evidence rather than copying secret-bearing configuration. Separate these levels:

1. **Detected:** dependency/marker, source hash, declared constraint, unresolved actual version.
2. **Mapped:** verified entrypoints, dependency wiring, routes, config precedence, storage boundary, assets/style pipeline and test commands.
3. **Traced:** one real input → route → handler/component → service/data → response/render chain, plus an error path, with current file/line references. Dynamic/inferred links are labeled.
4. **Verified:** after edits, functional + error/negative + regression checks actually run in a named environment, retaining assertions/output. Static discovery or a graph alone never earns this level.

Start with local manifests/lockfiles/installed metadata without executing build hooks. Treat constraints (^, ~, workspace aliases) separately from resolved versions. Inspect source and local docs; if a version-specific detail remains uncertain, verify official docs for the detected version when browsing is available. With no network or missing source, record pending and avoid unsupported changes. This does not authorize installing dependencies, migration, production traffic or reading credentials.

## Read-order recipes

| Family | Read next and trace |
|---|---|
| PHP CI3/HMVC | index.php environment/system paths → application/config/routes.php and module routes → MY_Router/MY_Controller → MX loads → controller/library/model/view. Resolve repeated class names by full module path. |
| Laravel/Symfony/other PHP | composer/lock → front controller/bootstrap → route registration → middleware/container → controller/service/repository/model → view/serializer. Inspect providers/config override order. |
| React/Next/Remix | package/lock → framework config → actual app/pages/router ownership → server/client boundary → loaders/actions/API → data/auth → render/hydration. Do not assume routing mode from dependency alone. |
| Vue/Nuxt | package/lock → nuxt/vite config → pages/router/layouts/plugins → composables/server handlers → data/auth → render. Check auto-imports and runtime vs build configuration. |
| Angular | workspace/project config → bootstrap/application modules → route/guard/provider → component/service → HTTP/state/template. |
| Svelte/Astro/Solid/Qwik/Lit | manifest/version/config → actual route/island/component entry → server/client boundary → loaders/actions/integrations → render. Read that framework's version-specific semantics rather than transferring React assumptions. |
| Python | project/requirements/lock → module/ASGI/WSGI/app factory → routes/middleware/DI → service/ORM/session → response/template. Resolve settings and worker entrypoints separately. |
| Ruby | gem/lock → config/application/environment/routes → middleware/controller/job → service/model → view/serializer. Static Gemfile literals do not evaluate groups/engines. |
| Go/Rust | module/Cargo/workspace → main/lib → router/extractor/middleware → handler/service/traits → data/concurrency/error mapping. Confirm workspace version inheritance and build tags/features. |
| Java/Kotlin/.NET | build/project/lock → host/startup/main → DI/security/filter → route/controller → service/transaction/repository → response. Resolve profiles/framework references/central version files. |
| Flutter/React Native/native apps | package/pubspec/Gradle/project → app entry/navigation → state/provider → platform/plugin/data boundary → widget/component lifecycle. Verify supported targets before platform-dependent tests. |
| Desktop/embedded/CLI/data/infra/custom | identify executable/build target and deployment boundary → config/input → core operations → IO/device/storage → output/error/recovery. Use the same evidence levels even when no web router exists. |

These are questions/read-order recipes, not assumptions about a particular repository. For an unlisted framework, inspect its manifests/import graph/entrypoint and official architecture docs, map it through the same levels, then add a project-specific recipe backed by source.

## CSS, UI libraries and purchased templates

Recognizers cover utility frameworks, stylesheet frameworks, component libraries and CSS tooling (Tailwind, Bootstrap, Bulma, Foundation, UIkit, UnoCSS, Windi, daisyUI, Flowbite, MUI, Ant Design, Chakra, Mantine, Vuetify, Quasar, Prime, Radix, Sass/Less/PostCSS/CSS-in-JS and more). Unknown/custom CSS has the same investigation path.

Trace: stylesheet/component imports → bundler/PostCSS/Sass pipeline → global reset/layers/order → tokens/theme → component ownership/scoping → templates/assets → responsive/state variants → emitted CSS and visible behavior. Record original/purchased theme authority; preserve existing design tokens and assets. Dependency presence is insufficient to replace a site's visual language.

Version checks matter: do not assume every Tailwind project uses a JS config or that constructing class fragments will generate CSS. Verify local directives/config/plugins/content sources and installed-version docs. Tailwind's official [class detection guide](https://tailwindcss.com/docs/detecting-classes-in-source-files) explains static source detection; use the matching version for the project. Test actual styles at relevant breakpoints/states and inspect browser console/computed styles after UI edits. Runtime/browser requirements remain separate from the scanner.

Never silently substitute a familiar framework for an unfamiliar one. Never claim every tech stack is understood because a catalog matched names. Discovery, source mapping, tracing and runtime verification are distinct results.
