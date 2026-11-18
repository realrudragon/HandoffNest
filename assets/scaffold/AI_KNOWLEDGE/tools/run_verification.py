#!/usr/bin/env python3
"""Preview or explicitly run reviewed checks and emit a real v1-compatible receipt."""
import argparse
import json
from pathlib import Path
import platform
import re
import sys

from work_support import (digest, execute, json_write, load_object, local_path, now,
                          public_output, redact, redact_value, load_snapshot, run_dir, safe_input, validate_command)


def run(root, task_name, plan_name, execute_checks=False):
    task_path = safe_input(root, task_name)
    task = load_object(task_path)
    plan_path = safe_input(root, plan_name)
    plan, plan_hash = load_snapshot(plan_path)
    if task.get('protocol_version') != 1 or plan.get('protocol_version') != 1:
        raise ValueError('Unsupported protocol_version')
    receipt_path = local_path(root, task['verification_file'])
    if receipt_path != task_path.parent / 'verification.json':
        raise ValueError('Runner receipt must be the task-local verification.json; cannot overwrite arbitrary project files')
    if receipt_path in (task_path, plan_path):
        raise ValueError('Receipt cannot overwrite task or plan input')
    files = {name: safe_input(root, name) for name in task['deliverables']}
    if receipt_path in files.values():
        raise ValueError('Receipt cannot be its own verified deliverable')
    checks = plan.get('checks')
    if not isinstance(checks, list) or not checks:
        raise ValueError('checks must be a nonempty list')
    ids = set()
    for check in checks:
        if not isinstance(check, dict) or not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}', check.get('id', '')) or check['id'] in ids:
            raise ValueError('Unique safe check id required')
        ids.add(check['id'])
        if check.get('kind') not in ('functional', 'error', 'regression', 'syntax', 'security', 'docs'):
            raise ValueError('Unknown check kind')
        validate_command(root, check)
        for key in ('expect_stdout', 'expect_stderr', 'forbid_stdout', 'forbid_stderr'):
            if not isinstance(check.get(key, []), list) or any(not isinstance(x, str) for x in check.get(key, [])):
                raise ValueError('Output assertions must be string arrays')
    if not {'functional', 'error', 'regression'}.issubset({c['kind'] for c in checks}):
        raise ValueError('Plan must include functional, error and regression checks')
    if not execute_checks:
        return 0, {'status': 'preview', 'checks': redact(json.dumps(checks, ensure_ascii=False)),
                   'notice': 'No commands run. Review trusted argv/cwd first; use --execute deliberately.'}
    before = {name: digest(path) for name, path in files.items()}
    folder = run_dir(root, task_path, 'verification-runs')
    snapshot = folder / 'plan.snapshot.json'
    json_write(root, snapshot, redact_value(plan))
    if receipt_path.is_file():
        json_write(root, folder / 'previous-latest-receipt.json', redact_value(load_object(receipt_path)))
    receipt = {'protocol_version': 1, 'task_id': task['task_id'], 'verified_at': now(),
               'producer': 'worachote-verification-runner/0.2', 'plan_sha256': plan_hash,
               'plan_snapshot_file': snapshot.relative_to(root).as_posix(), 'plan_snapshot_sha256': digest(snapshot),
               'verified_hashes': before, 'checks': [], 'run_directory': folder.relative_to(root).as_posix()}
    environment = 'runner Python ' + platform.python_version() + '; ' + platform.platform() + '; child version only as observed in check output'
    for check in checks:
        argv, cwd, timeout = validate_command(root, check)
        result = execute(argv, cwd, timeout)
        failures = []
        if result['timed_out']:
            failures.append('timeout; direct process stopped, descendant cleanup is not guaranteed')
        if result['exit_code'] != 0:
            failures.append('expected exit_code 0, observed ' + str(result['exit_code']))
        for field in ('stdout', 'stderr'):
            raw = result['_raw_' + field]
            for text in check.get('expect_' + field, []):
                if text not in raw:
                    failures.append('missing expected ' + field + ' content')
            for text in check.get('forbid_' + field, []):
                if text in raw:
                    failures.append('forbidden ' + field + ' content was emitted')
        evidence = folder / (check['id'] + '.json')
        artifact = public_output(result)
        artifact['assertions'] = redact_value({key: check.get(key, []) for key in
                                             ('expect_stdout', 'expect_stderr', 'forbid_stdout', 'forbid_stderr')})
        artifact['assertion_failures'] = failures
        json_write(root, evidence, artifact)
        receipt['checks'].append({'kind': check['kind'], 'status': 'failed' if failures else 'passed',
                                  'command': artifact['argv'], 'environment': environment,
                                  'observed_result': '; '.join(failures) if failures else 'Exit 0 and all declared output assertions satisfied',
                                  'exit_code': result['exit_code'], 'evidence_file': evidence.relative_to(root).as_posix(),
                                  'evidence_sha256': digest(evidence)})
    changed = [name for name, path in files.items() if not path.is_file() or digest(path) != before[name]]
    plan_changed = not plan_path.is_file() or digest(plan_path) != plan_hash
    receipt['plan_changed_during_run'] = plan_changed
    if plan_changed:
        changed.append(plan_name)
    if changed:
        evidence = folder / 'source_changed.json'
        json_write(root, evidence, {'source_changed': changed})
        receipt['checks'].append({'kind': 'regression', 'status': 'failed', 'command': ['internal-source-digest-check'],
                                  'environment': environment, 'observed_result': 'source_changed during verification; rerun after final edits',
                                  'exit_code': 1, 'evidence_file': evidence.relative_to(root).as_posix(), 'evidence_sha256': digest(evidence)})
    receipt['verified_at'] = now()
    json_write(root, folder / 'verification.json', receipt)
    # Every generated run retains its immutable receipt; this is only the latest pointer copy.
    json_write(root, receipt_path, receipt)
    failed = any(c['status'] != 'passed' for c in receipt['checks'])
    return int(failed), {'status': 'failed' if failed else 'verified', 'receipt': receipt_path.relative_to(root).as_posix(),
                         'source_changed': changed, 'checks': receipt['checks'],
                         'limitation': 'Actual execution evidence, not semantic certification or a command sandbox.'}


def main():
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', default=str(Path(__file__).resolve().parents[2]))
    p.add_argument('--task', required=True); p.add_argument('--plan', required=True)
    p.add_argument('--execute', action='store_true')
    a = p.parse_args()
    try:
        code, result = run(Path(a.project_root).resolve(), a.task, a.plan, a.execute)
        print(json.dumps(result, ensure_ascii=False, indent=2)); return code
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'error', 'error': redact(str(exc))}, ensure_ascii=False)); return 2


if __name__ == '__main__':
    raise SystemExit(main())
