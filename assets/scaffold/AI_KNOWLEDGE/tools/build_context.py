#!/usr/bin/env python3
"""Build a scoped, provenance-bearing context pack with a strict character budget."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

from work_support import digest, json_write, load_object, load_snapshot, local_path, now, redact, safe_input


def graph_excerpt(root, task):
    name = task.get('graph_file', 'AI_KNOWLEDGE/graphify-out/graph.json')
    path = local_path(root, name)
    if not path.exists():
        return None
    graph = load_object(safe_input(root, name))
    nodes = {str(n['id']): n for n in graph.get('nodes', []) if isinstance(n, dict) and 'id' in n}
    scopes = task.get('context_files', []) + task.get('allowed_paths', []) + task.get('deliverables', [])
    def matches(node):
        source = str(node.get('source_file', '')).replace('\\', '/')
        return bool(source) and any(source == s or source.startswith(s.rstrip('/') + '/') or
                                    source.endswith('/' + s) for s in scopes)
    seeds = {key for key, node in nodes.items() if matches(node)}
    rows = []
    for edge in graph.get('links', graph.get('edges', [])):
        source, target = str(edge.get('source', '')), str(edge.get('target', ''))
        if not ({source, target} & seeds):
            continue
        a, b = nodes.get(source, {}), nodes.get(target, {})
        rows.append(str(a.get('label', source)) + ' -> ' + str(b.get('label', target)) +
                    '; relation=' + str(edge.get('relation', edge.get('label', 'unspecified'))) +
                    '; sources=' + str(a.get('source_file', '?')) + ', ' + str(b.get('source_file', '?')) +
                    '; confidence=' + str(edge.get('confidence', 'unverified')))
        if len(rows) == 12:
            break
    if not rows:
        return None
    return name, 'Graph relationships (static, may be stale/inferred; verify current owning source):\n' + '\n'.join(rows)


def build(root, task_name, output_name, budget=12000, include_source=False, replace=False):
    task_path = safe_input(root, task_name)
    task, task_hash = load_snapshot(task_path)
    if task.get('protocol_version') != 1:
        raise ValueError('Unsupported task protocol_version')
    if type(budget) is not int or budget <= 0:
        raise ValueError('max-chars must be positive')
    output = local_path(root, output_name)
    if output.suffix != '.md' or not output.is_relative_to(task_path.parent):
        raise ValueError('Context output must be a .md artifact inside the task directory')
    metadata = output.with_suffix('.manifest.json')
    reserved = {task_path, local_path(root, task['verification_file'])}
    reserved.update(task_path.parent / name for name in ('BRIEF.md', 'HANDOFF.md', 'events.md', 'REVIEW.md'))
    reserved.update(local_path(root, name) for name in task.get('deliverables', []))
    if output in reserved or metadata in reserved:
        raise ValueError('Context output cannot overwrite packet records, evidence pointer or deliverables')
    if (output.exists() or metadata.exists()) and not replace:
        raise ValueError('Context artifact exists; use --replace deliberately')
    if output.exists() or metadata.exists():
        if not output.is_file() or not metadata.is_file():
            raise ValueError('Replacement requires an intact generated pack and manifest')
        prior = load_object(metadata)
        if prior.get('producer') != 'worachote-context-builder/0.2' or prior.get('task_id') != task.get('task_id') or prior.get('pack_sha256') != digest(output):
            raise ValueError('Replacement requires this task\'s unchanged generated pack; human notes are preserved')
    required = ['AGENTS.md', (task_path.parent / 'BRIEF.md').relative_to(root).as_posix(),
                (task_path.parent / 'HANDOFF.md').relative_to(root).as_posix()]
    optional = task.get('context_files', [])
    if not isinstance(optional, list) or any(not isinstance(x, str) for x in optional):
        raise ValueError('context_files must be an array of project-relative paths')
    quick = 'AI_KNOWLEDGE/QUICK_CONTEXT.md'
    if (root / quick).is_file():
        optional = [quick] + optional
    # Preflight every supplied path, including files that later cannot fit the budget.
    selected = []
    for name in dict.fromkeys(required + optional):
        path = safe_input(root, name)
        if path in (output, metadata):
            raise ValueError('Context output cannot overwrite an input')
        if name not in required and path.suffix.lower() not in ('.md', '.txt', '.rst') and not include_source:
            raise ValueError('Raw source requires explicit --include-source: ' + name)
        selected.append((name, path, name in required))
    title = '# Context pack: ' + str(task.get('task_id', 'unknown')) + '\n\n'
    overview = {'task_file': task_name, 'goal': task.get('goal'), 'acceptance_criteria': task.get('acceptance_criteria'),
                'allowed_paths': task.get('allowed_paths'), 'owner': task.get('owner'),
                'notice': 'Current source and user instructions override this pack. Character budget is not a model token count.'}
    text = title + redact(json.dumps(overview, ensure_ascii=False, indent=2)) + '\n'
    included, omitted = [], []
    optional_sections = []
    for name, path, mandatory in selected:
        content = path.read_bytes()
        body = content.decode('utf-8', errors='replace')
        source_hash = hashlib.sha256(content).hexdigest()
        clean = redact(body)
        section = '\n## ' + name + '\nSource SHA-256: ' + source_hash + '\n\n' + clean + '\n'
        info = {'path': name, 'sha256': source_hash, 'lines': len(body.splitlines()),
                'redacted': clean != body, 'provenance': 'current_file', 'mandatory': mandatory}
        if mandatory:
            text += section
            included.append(info)
        else:
            optional_sections.append((section, info))
    if len(text) > budget:
        raise ValueError('Mandatory rules/task/handoff exceed character budget; increase budget or shorten the real handoff')
    graph = graph_excerpt(root, task)
    if graph:
        name, body = graph
        optional_sections.append(('\n## Graph navigation\n' + redact(body) + '\n',
                                  {'path': name, 'sha256': digest(root / name), 'provenance': 'static_graph', 'mandatory': False}))
    for section, info in optional_sections:
        if len(text) + len(section) <= budget:
            text += section
            included.append(info)
        else:
            omitted.append({'path': info['path'], 'reason': 'budget', 'characters': len(section)})
    result = {'protocol_version': 1, 'producer': 'worachote-context-builder/0.2', 'task_id': task.get('task_id'), 'created_at': now(),
              'task_file': task_name, 'task_sha256': task_hash,
              'budget_unit': 'unicode_codepoints', 'max_chars': budget, 'actual_chars': len(text),
              'included': included, 'omitted': omitted,
              'pack_sha256': hashlib.sha256(text.encode('utf-8')).hexdigest(),
              'limitations': ['No universal token estimate', 'Static graph does not prove runtime behavior',
                              'Redaction is best-effort; review before sharing', 'Source freshness is bound by included file hashes, not semantic truth']}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(text.encode('utf-8'))
    json_write(root, metadata, result)
    return {'status': 'built', 'pack': output_name, 'manifest': metadata.relative_to(root).as_posix(),
            'characters': len(text), 'omitted': omitted}


def main():
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', default=str(Path(__file__).resolve().parents[2]))
    p.add_argument('--task', required=True); p.add_argument('--out', required=True)
    p.add_argument('--max-chars', type=int, default=12000)
    p.add_argument('--include-source', action='store_true'); p.add_argument('--replace', action='store_true')
    a = p.parse_args()
    try:
        result = build(Path(a.project_root).resolve(), a.task, a.out, a.max_chars, a.include_source, a.replace)
        print(json.dumps(result, ensure_ascii=False, indent=2)); return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'error', 'error': redact(str(exc))}, ensure_ascii=False)); return 2


if __name__ == '__main__':
    raise SystemExit(main())
