#!/usr/bin/env python3
"""Read-only completion contract gate. Does not run commands or certify their semantics."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import sys


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_path(root, value):
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError('path must be a nonempty project-relative POSIX path')
    if PureWindowsPath(value).drive or Path(value).is_absolute() or '..' in Path(value).parts:
        raise ValueError('path escapes project or is absolute: ' + value)
    path = (root / value).resolve()
    if not path.is_relative_to(root):
        raise ValueError('path resolves outside project: ' + value)
    return path


def load_object(path):
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError('document must be a JSON object')
    return value


def validate(root, task_name):
    errors = []
    try:
        task_path = local_path(root, task_name)
        task = load_object(task_path)
    except (OSError, ValueError) as exc:
        return ['task path/document: ' + str(exc)]
    for name in ('BRIEF.md', 'HANDOFF.md', 'events.md'):
        document = task_path.parent / name
        try:
            if not document.resolve().is_relative_to(root) or not document.is_file() or not document.read_text(encoding='utf-8').strip():
                errors.append('missing or unsafe packet document: ' + name)
        except OSError:
            errors.append('unreadable packet document: ' + name)
    if task.get('protocol_version') != 1:
        errors.append('unsupported protocol_version')
    if not isinstance(task.get('task_id'), str) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]{2,63}', task['task_id']):
        errors.append('invalid task_id')
    kind = task.get('kind')
    if kind not in ('code', 'docs', 'audit'):
        errors.append('invalid kind')
    if task.get('status') not in ('review', 'done'):
        errors.append('task status must be review or done')
    for name in ('owner', 'goal'):
        if not isinstance(task.get(name), str) or not task[name].strip():
            errors.append('missing ' + name)
    if task.get('owner') == 'unassigned':
        errors.append('owner must be assigned before completion')
    criteria = task.get('acceptance_criteria')
    if not isinstance(criteria, list) or not criteria or any(not isinstance(x, str) or not x.strip() for x in criteria):
        errors.append('missing acceptance_criteria')
    allowed = []
    deliverables = []
    for key, output in [('allowed_paths', allowed), ('deliverables', deliverables)]:
        values = task.get(key)
        if not isinstance(values, list) or not values:
            errors.append(key + ' must be a nonempty list')
            continue
        for name in values:
            try:
                output.append((name, local_path(root, name)))
            except ValueError as exc:
                errors.append(key + ' ' + str(exc))
    for name, path in deliverables:
        if not path.is_file():
            errors.append('deliverable missing: ' + name)
        if not any(path == scope or scope in path.parents for _, scope in allowed):
            errors.append('deliverable outside assigned scope: ' + name)
    try:
        receipt = load_object(local_path(root, task.get('verification_file')))
    except (OSError, ValueError) as exc:
        errors.append('verification path/document: ' + str(exc))
        return errors
    if receipt.get('protocol_version') != 1:
        errors.append('verification protocol_version mismatch')
    if receipt.get('task_id') != task.get('task_id'):
        errors.append('verification task_id mismatch')
    try:
        stamp = datetime.fromisoformat(receipt.get('verified_at', ''))
        if stamp.tzinfo is None:
            raise ValueError('timezone required')
    except (TypeError, ValueError):
        errors.append('verified_at must be an ISO timestamp with timezone')
        stamp = None
    try:
        started = datetime.fromisoformat(task.get('started_at', ''))
        if started.tzinfo is None:
            raise ValueError('timezone required')
        if stamp is not None and stamp < started:
            errors.append('verification predates current task attempt')
    except (TypeError, ValueError):
        errors.append('started_at must be an ISO timestamp with timezone')
    hashes = receipt.get('verified_hashes')
    if not isinstance(hashes, dict):
        errors.append('verified_hashes must be an object')
        hashes = {}
    for name, path in deliverables:
        if name not in hashes:
            errors.append('missing verified hash: ' + name)
        elif path.is_file() and digest(path) != hashes[name]:
            errors.append('stale verified hash: ' + name)
    checks = receipt.get('checks')
    if not isinstance(checks, list) or not checks:
        errors.append('verification checks must be a nonempty list')
        checks = []
    categories = set()
    for index, check in enumerate(checks):
        prefix = 'check ' + str(index) + ': '
        if not isinstance(check, dict):
            errors.append(prefix + 'must be an object')
            continue
        category = check.get('kind')
        if category not in ('functional', 'error', 'regression', 'syntax', 'security', 'docs'):
            errors.append(prefix + 'unknown kind')
        status = check.get('status')
        if status == 'not_applicable':
            if category in ('functional', 'error') or (kind == 'code' and category == 'regression'):
                errors.append(prefix + 'required check cannot be not_applicable for ' + str(kind))
            reason = check.get('reason')
            if not isinstance(reason, str) or len(reason.strip()) < 16:
                errors.append(prefix + 'specific not_applicable reason required')
            categories.add(category)
            continue
        if status != 'passed':
            errors.append(prefix + 'unresolved status ' + str(status))
            continue
        categories.add(category)
        for field in ('environment', 'observed_result'):
            if not isinstance(check.get(field), str) or len(check[field].strip()) < 8:
                errors.append(prefix + 'specific ' + field + ' required')
        command = check.get('command')
        if not isinstance(command, list) or not command or any(not isinstance(x, str) or not x for x in command):
            errors.append(prefix + 'command must be an argv string array')
        if type(check.get('exit_code')) is not int or check['exit_code'] != 0:
            errors.append(prefix + 'passed check requires exit_code 0')
        try:
            evidence = local_path(root, check.get('evidence_file'))
            if not evidence.is_file() or digest(evidence) != check.get('evidence_sha256'):
                errors.append(prefix + 'evidence missing or digest mismatch')
        except (OSError, ValueError) as exc:
            errors.append(prefix + 'evidence path: ' + str(exc))
    for required in ('functional', 'error', 'regression'):
        if required not in categories:
            errors.append('missing required check category: ' + required)
    return errors


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument('--task', required=True, help='Task JSON path relative to project root')
    args = parser.parse_args()
    try:
        errors = validate(Path(args.project_root).resolve(), args.task)
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({'status': 'error', 'errors': [str(exc)]}, ensure_ascii=False))
        return 2
    print(json.dumps({'status': 'blocked' if errors else 'ready_for_review', 'errors': errors,
                      'limitation': 'Checks packet/evidence consistency only; does not run tests or replace review.'},
                     ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
