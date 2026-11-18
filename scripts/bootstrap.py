#!/usr/bin/env python3
"""Create missing knowledge files and append one managed AGENTS pointer. Never overwrite user files."""
import argparse
from datetime import datetime, timezone, timedelta
import importlib.util
import json
from pathlib import Path
import re
import sys

SKILL = Path(__file__).resolve().parents[1]
ASSETS = SKILL / 'assets' / 'scaffold'
BEGIN = '<!-- worachote-structure-ai:begin -->'
END = '<!-- worachote-structure-ai:end -->'


def safe_target(root, relative):
    path = root / relative
    if not path.resolve().is_relative_to(root):
        raise ValueError('Refusing output path outside project: ' + relative)
    return path


def detect(root):
    for prefix in ('public_html', '.'):
        source = root / prefix
        modules = source / 'application/modules'
        core = source / 'system/core/CodeIgniter.php'
        if modules.is_dir():
            version = 'version unverified'
            if core.is_file():
                match = re.search(r"CI_VERSION\s*=\s*['\"]([^'\"]+)", core.read_text(encoding='utf-8', errors='replace'))
                if match:
                    version = match.group(1)
            return 'PHP CI3/HMVC layout (' + version + ')', prefix
    if (root / 'composer.json').is_file():
        return 'PHP project; framework unverified', '.'
    if (root / 'package.json').is_file():
        return 'JavaScript/TypeScript project; framework unverified', '.'
    if (root / 'pyproject.toml').is_file() or (root / 'requirements.txt').is_file():
        return 'Python project; framework unverified', '.'
    return 'unverified', '.'


def plan(root):
    module_path = ASSETS / 'AI_KNOWLEDGE/tools/knowledge_inventory.py'
    spec = importlib.util.spec_from_file_location('worachote_inventory', module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    stack, source = detect(root)
    # Discovery reads bounded first-party metadata; no manifest scripts are executed.
    discovery_path = ASSETS / 'AI_KNOWLEDGE/tools/discover_stack.py'
    original_search = sys.path[:]
    try:
        sys.path.insert(0, str(discovery_path.parent))
        stack_spec = importlib.util.spec_from_file_location('worachote_stack', discovery_path)
        stack_module = importlib.util.module_from_spec(stack_spec)
        stack_spec.loader.exec_module(stack_module)
        stack_report = stack_module.discover(root)
        stack_report = json.loads(stack_module.redact(json.dumps(stack_report, ensure_ascii=False)))
    finally:
        sys.path[:] = original_search
    labels = list(dict.fromkeys(row['label'] for row in stack_report['detections']))
    if labels:
        stack += '; static signals: ' + ', '.join(labels[:12])
    now = datetime.now(timezone(timedelta(hours=7))).isoformat(timespec='seconds')
    context = {'PROJECT_NAME': root.name, 'STACK': stack, 'SOURCE_ROOT': source, 'CREATED_AT': now}
    result = {}
    for asset in ASSETS.rglob('*'):
        if not asset.is_file() or '__pycache__' in asset.parts or asset.suffix == '.pyc':
            continue
        relative = asset.relative_to(ASSETS).as_posix()
        content = asset.read_text(encoding='utf-8')
        for key, value in context.items():
            content = content.replace('{{' + key + '}}', value)
        result[relative] = content
    rows = module.collect(root)
    snapshot = {'protocol_version': 1, 'created_at': now, 'project': root.name, 'stack': stack,
                'source_root': source, 'scope_note': 'metadata only, exclusions explicit; not semantic coverage',
                'excluded_directories': sorted(module.EXCLUDED), 'excluded_prefixes': ['ExcelLb'],
                'files': rows}
    result['AI_KNOWLEDGE/source_snapshot.json'] = json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n'
    result['AI_KNOWLEDGE/indexes/source-index.json'] = json.dumps(rows, ensure_ascii=False, indent=2) + '\n'
    result['AI_KNOWLEDGE/STACK_DISCOVERY.json'] = json.dumps(stack_report, ensure_ascii=False, indent=2) + '\n'
    managed = '\n'.join([BEGIN, '## Shared agent workflow',
        'Read AI_KNOWLEDGE/WORKING_RULES.md, QUICK_CONTEXT.md and HANDOFF.md before project work.',
        'Explanation-only Q&A requires no mandatory task/log/test. Work requires scope ownership, incremental checkpoints, functional/error/regression verification and a standalone handoff.',
        'See AI_KNOWLEDGE/agent-system/README.md. Evidence and source override stale notes. Never record secrets or invent successful checks.', END, ''])
    agent_path = safe_target(root, 'AGENTS.md')
    if agent_path.exists():
        old = agent_path.read_text(encoding='utf-8')
        if (BEGIN in old) != (END in old) or old.count(BEGIN) > 1 or old.count(END) > 1:
            raise ValueError('Malformed managed AGENTS markers; inspect/merge manually')
        if BEGIN not in old:
            result['AGENTS.md'] = old.rstrip() + '\n\n' + managed
    else:
        result['AGENTS.md'] = '# Project agent instructions\n\n' + managed
    return result


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    root = Path(args.project_root).resolve()
    if not root.is_dir():
        raise ValueError('Project root must already exist')
    if (root / 'index.php').is_file() and (root / 'application').is_dir():
        raise ValueError('Selected root appears to be a PHP document root. Choose an authorized non-public parent project directory; do not publish AI_KNOWLEDGE or auto-widen scope.')
    outputs = plan(root)
    # Check all paths before writing anything, including symlinked knowledge/adapter directories.
    for name in outputs:
        safe_target(root, name)
    created, preserved, updated = [], [], []
    for name, content in outputs.items():
        path = safe_target(root, name)
        if path.exists() and name != 'AGENTS.md':
            preserved.append(name)
            continue
        if path.exists():
            updated.append(name)
        else:
            created.append(name)
        if not args.dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
    print(json.dumps({'dry_run': args.dry_run, 'project': str(root), 'created': created,
                      'updated_managed_pointer': updated, 'preserved': preserved,
                      'next': 'Inspect source, fill project-specific knowledge, build/refresh Graphify, run verification and handoff.'},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(json.dumps({'status': 'error', 'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)
