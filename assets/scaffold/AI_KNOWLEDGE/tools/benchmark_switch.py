#!/usr/bin/env python3
"""Run provider-neutral handoff probes; fixture results are not model-quality claims."""
import argparse
import json
from pathlib import Path
import random
import re
import statistics
import sys

from work_support import (digest, execute, json_write, load_object, local_path, now,
                          public_output, redact, redact_value, load_snapshot, run_dir, safe_input, validate_command)


def safe_id(value):
    return isinstance(value, str) and re.fullmatch(r'[a-zA-Z0-9_-]{1,64}', value)


def evaluate(root, task_name, plan_name, execute_adapters=False):
    task_path = safe_input(root, task_name)
    task = load_object(task_path)
    plan_path = safe_input(root, plan_name)
    plan, plan_hash = load_snapshot(plan_path)
    if task.get('protocol_version') != 1 or plan.get('protocol_version') != 1 or not safe_id(plan.get('benchmark_id')):
        raise ValueError('Valid protocol_version and benchmark_id required')
    adapters, cases = plan.get('adapters'), plan.get('cases')
    if not isinstance(adapters, list) or not adapters or not isinstance(cases, list) or not cases:
        raise ValueError('Nonempty adapters and cases arrays required')
    trials = plan.get('trials', 1)
    if type(trials) is not int or not 1 <= trials <= 20:
        raise ValueError('trials must be 1..20')
    adapter_ids, case_ids = set(), set()
    for adapter in adapters:
        if not safe_id(adapter.get('id')) or adapter['id'] in adapter_ids or adapter.get('kind') not in ('fixture', 'model'):
            raise ValueError('Unique adapter id and explicit kind fixture/model required')
        adapter_ids.add(adapter['id'])
        argv, _, _ = validate_command(root, adapter)
        if not any('{request}' in x for x in argv) or not any('{response}' in x for x in argv):
            # A deliberately failing executable is still allowed to demonstrate launch/exit failures.
            if adapter.get('kind') != 'fixture':
                raise ValueError('Model adapter argv must include {request} and {response}')
    jobs = []
    for case in cases:
        if not safe_id(case.get('id')) or case['id'] in case_ids:
            raise ValueError('Unique case id required')
        case_ids.add(case['id'])
        safe_input(root, case['prompt_file'])
        if not isinstance(case.get('expected_answers'), dict) or not case['expected_answers']:
            raise ValueError('Nonempty expected_answers object required for deterministic grading')
        variants = case.get('variants')
        if not isinstance(variants, list) or not variants:
            raise ValueError('Nonempty variants required')
        variant_ids = set()
        for variant in variants:
            if not safe_id(variant.get('id')) or variant['id'] in variant_ids:
                raise ValueError('Unique variant id required within each case')
            variant_ids.add(variant['id'])
            names = variant.get('context_files')
            if not isinstance(names, list) or any(not isinstance(x, str) for x in names):
                raise ValueError('context_files must be an array')
            for name in names:
                safe_input(root, name)
            for adapter in adapters:
                jobs.extend((adapter, case, variant, i + 1) for i in range(trials))
    if len(jobs) > 200:
        raise ValueError('Plan exceeds 200 adapter calls; reduce scope')
    seed = plan.get('seed', 0)
    if type(seed) is not int:
        raise ValueError('seed must be an integer')
    random.Random(seed).shuffle(jobs)
    if not execute_adapters:
        return 0, {'status': 'preview', 'adapter_calls': len(jobs), 'adapter_kinds': [a['kind'] for a in adapters],
                   'notice': 'No adapters run. Review trusted commands, costs, input disclosure and adapter isolation before --execute.'}
    folder = run_dir(root, task_path, 'switch-benchmarks')
    snapshot = folder / 'plan.snapshot.json'
    json_write(root, snapshot, redact_value(plan))
    rows = []
    for index, (adapter, case, variant, trial) in enumerate(jobs):
        item = folder / ('trial-' + str(index + 1))
        item.mkdir()
        prompt_path = safe_input(root, case['prompt_file'])
        context = []
        for name in variant['context_files']:
            path = safe_input(root, name)
            context.append({'path': name, 'sha256': digest(path), 'text': redact(path.read_text(encoding='utf-8', errors='replace'))})
        request = {'protocol_version': 1, 'case_id': case['id'], 'variant': variant['id'], 'trial': trial,
                   'prompt': redact(prompt_path.read_text(encoding='utf-8', errors='replace')), 'context': context,
                   'instructions': 'Return JSON {answers:{...},reported_usage?:{...}}. Use a fresh model conversation; no prior transcript. Do not change application files.'}
        request_path, response_path = item / 'request.json', item / 'response.json'
        json_write(root, request_path, request)
        argv, cwd, timeout = validate_command(root, adapter)
        argv = [x.replace('{request}', str(request_path)).replace('{response}', str(response_path)) for x in argv]
        result = execute(argv, cwd, timeout)
        row = {'adapter': adapter['id'], 'adapter_kind': adapter['kind'], 'case': case['id'],
               'variant': variant['id'], 'trial': trial, 'elapsed_seconds': result['elapsed_seconds'],
               'context_chars': sum(len(x['text']) for x in context), 'context_hashes': {x['path']: x['sha256'] for x in context},
               'assertions_total': len(case['expected_answers']), 'assertions_passed': 0,
               'reported_usage': None, 'errors': []}
        if result['timed_out'] or result['exit_code'] != 0:
            row['errors'].append('adapter timeout or nonzero/launch failure')
        try:
            # Adapter files are untrusted even though the operator chose the adapter.
            actual_response = local_path(root, response_path.relative_to(root).as_posix())
            raw = actual_response.read_text(encoding='utf-8')
            clean = redact(raw)
            # Retain only redacted adapter output, including malformed JSON for diagnosis.
            actual_response.write_text(clean[:100000], encoding='utf-8')
            if len(raw) > 100000:
                raise ValueError('response exceeds retained response limit')
            response = json.loads(clean)
            if not isinstance(response, dict) or not isinstance(response.get('answers'), dict):
                raise ValueError('response.answers must be an object')
            expected = case['expected_answers']
            row['assertions_passed'] = sum(
                key in response['answers'] and json.dumps(response['answers'][key], sort_keys=True) == json.dumps(value, sort_keys=True)
                for key, value in expected.items())
            row['reported_usage'] = response.get('reported_usage')
        except (OSError, ValueError, TypeError) as exc:
            row['errors'].append('response error: ' + redact(str(exc)))
        json_write(root, item / 'execution.json', public_output(result))
        row['request'] = request_path.relative_to(root).as_posix()
        row['response'] = response_path.relative_to(root).as_posix()
        rows.append(row)
    summary = []
    for adapter_id, variant_id in sorted({(r['adapter'], r['variant']) for r in rows}):
        group = [r for r in rows if r['adapter'] == adapter_id and r['variant'] == variant_id]
        total = sum(r['assertions_total'] for r in group)
        summary.append({'adapter': adapter_id, 'variant': variant_id, 'trials': len(group),
                        'accuracy': sum(r['assertions_passed'] if not r['errors'] else 0 for r in group) / total,
                        'runtime_errors': sum(bool(r['errors']) for r in group),
                        'median_elapsed_seconds': statistics.median(r['elapsed_seconds'] for r in group),
                        'mean_context_chars': statistics.mean(r['context_chars'] for r in group)})
    plan_changed = not plan_path.is_file() or digest(plan_path) != plan_hash
    partial = plan_changed or any(row['errors'] for row in rows)
    report = {'protocol_version': 1, 'benchmark_id': plan['benchmark_id'], 'created_at': now(),
              'status': 'partial' if partial else 'completed', 'seed': seed,
              'adapters': [{'id': a['id'], 'kind': a['kind']} for a in adapters],
              'plan_sha256': plan_hash, 'plan_changed_during_run': plan_changed,
              'plan_snapshot_file': snapshot.relative_to(root).as_posix(), 'plan_snapshot_sha256': digest(snapshot),
              'trials': rows, 'summary': summary,
              'limits': ['Scores cover supplied deterministic handoff probes only, not general coding/reasoning ability',
                         'Fixture adapters are synthetic and cannot establish model improvement',
                         'Elapsed wall time/context characters measured by harness; usage is adapter-reported/unverified',
                         'Separate invocations/requests do not prove provider cache isolation or comparable model cost',
                         'Trusted adapter execution is not sandboxed; fair closed-book behavior is not enforced']}
    report_path = folder / 'benchmark.json'
    json_write(root, report_path, report)
    lines = ['# Agent Switch Benchmark', '', 'Status: ' + report['status'], '',
             'Adapter kinds: ' + ', '.join(a['id'] + '=' + a['kind'] for a in adapters), '',
             '| Adapter | Variant | Trials | Assertion accuracy | Runtime errors | Median wall seconds |',
             '|---|---|---|---|---|---|']
    lines += ['| {adapter} | {variant} | {trials} | {accuracy:.2%} | {runtime_errors} | {median_elapsed_seconds:.4f} |'.format(**r) for r in summary]
    lines += ['', 'Limitations:', ''] + ['- ' + limit for limit in report['limits']]
    (folder / 'REPORT.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return int(partial), {'status': report['status'], 'report': report_path.relative_to(root).as_posix(),
                          'markdown_report': (folder / 'REPORT.md').relative_to(root).as_posix(), 'adapter_calls': len(rows)}


def main():
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', default=str(Path(__file__).resolve().parents[2]))
    p.add_argument('--task', required=True); p.add_argument('--plan', required=True)
    p.add_argument('--execute', action='store_true'); a = p.parse_args()
    try:
        code, result = evaluate(Path(a.project_root).resolve(), a.task, a.plan, a.execute)
        print(json.dumps(result, ensure_ascii=False, indent=2)); return code
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'error', 'error': redact(str(exc))}, ensure_ascii=False)); return 2


if __name__ == '__main__':
    raise SystemExit(main())
