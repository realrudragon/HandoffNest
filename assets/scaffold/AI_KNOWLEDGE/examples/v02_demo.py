#!/usr/bin/env python3
"""Disposable synthetic demo. No API calls; fixture scores are not model evaluations."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def demo(tools, output):
    # Never replace user files or clean up a user-selected directory.
    output.mkdir(parents=True, exist_ok=False)
    results = []
    with tempfile.TemporaryDirectory(prefix='worachote-demo-') as temp:
        root = Path(temp).resolve()
        for name in ('records', 'src', 'docs', 'AI_KNOWLEDGE'):
            (root / name).mkdir()
        def write(name, value):
            text = json.dumps(value, ensure_ascii=False, indent=2) if isinstance(value, dict) else value
            (root / name).write_text(text, encoding='utf-8')
        write('AGENTS.md', 'Synthetic project: inspect source, preserve scope, verify changes.\n')
        write('AI_KNOWLEDGE/QUICK_CONTEXT.md', 'Addition is owned by src/math.py. Synthetic demo only.\n')
        write('src/math.py', 'def add(a, b):\n    return a + b\n')
        write('docs/prompt.md', 'Which file owns addition? Return answers.owning_file.\n')
        for name in ('BRIEF.md', 'HANDOFF.md', 'events.md'):
            write('records/' + name, 'Synthetic addition task; next inspect src/math.py and run tests.\n')
        write('records/task.json', {
            'protocol_version': 1, 'task_id': 'synthetic-v02-demo', 'kind': 'code', 'status': 'review',
            'owner': 'demo-fixture', 'started_at': '2026-11-18T00:00:00+07:00',
            'goal': 'Verify addition and demonstrate portable handoff tools', 'allowed_paths': ['src'],
            'acceptance_criteria': ['add(2,3) returns 5', 'Invalid argument raises TypeError'],
            'deliverables': ['src/math.py'], 'context_files': ['AI_KNOWLEDGE/QUICK_CONTEXT.md'],
            'verification_file': 'records/verification.json'})
        checks = [
            ('functional', "assert add(2,3)==5"),
            ('error', "try:\n add(1,None)\nexcept TypeError:\n pass\nelse:\n raise AssertionError('TypeError expected')"),
            ('regression', "assert add(-2,2)==0; assert add(0,0)==0")]
        write('records/plan.json', {'protocol_version': 1, 'checks': [
            {'id': kind, 'kind': kind, 'argv': [sys.executable, '-c',
             "import runpy\nadd=runpy.run_path('src/math.py')['add']\n" + code + "\nprint('assertions-passed')"],
             'timeout_seconds': 10, 'expect_stdout': ['assertions-passed']} for kind, code in checks]})
        # Deliberately answers from supplied context only. Improvement is built into this fixture.
        write('adapter.py', "import json,sys\nfrom pathlib import Path\nr=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))\nassert 'expected_answers' not in r\ntext='\\n'.join(x['text'] for x in r['context'])\na='src/math.py' if 'src/math.py' in text else 'unknown'\nPath(sys.argv[2]).write_text(json.dumps({'answers':{'owning_file':a}}),encoding='utf-8')\n")
        write('records/benchmark-plan.json', {'protocol_version': 1, 'benchmark_id': 'synthetic-switch',
            'trials': 2, 'seed': 7, 'adapters': [{'id': 'context-fixture', 'kind': 'fixture',
                'argv': [sys.executable, 'adapter.py', '{request}', '{response}'], 'timeout_seconds': 10}],
            'cases': [{'id': 'owning-file', 'prompt_file': 'docs/prompt.md',
                'expected_answers': {'owning_file': 'src/math.py'},
                'variants': [{'id': 'baseline', 'context_files': []},
                             {'id': 'with-context', 'context_files': ['records/context-pack.md']}]}]})
        calls = [
            ('build_context.py', ['--out', 'records/context-pack.md', '--max-chars', '5000']),
            ('run_verification.py', ['--plan', 'records/plan.json', '--execute']),
            ('verify_task.py', []),
            ('benchmark_switch.py', ['--plan', 'records/benchmark-plan.json', '--execute'])]
        for tool, args in calls:
            argv = [sys.executable, str(tools / tool), '--project-root', str(root), '--task', 'records/task.json', *args]
            proc = subprocess.run(argv, capture_output=True, encoding='utf-8', timeout=60)
            results.append({'argv': argv, 'exit_code': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr})
            if proc.returncode:
                break
        # Records include the full synthetic root to keep relative evidence links resolvable.
        shutil.copytree(root, output / 'synthetic-project')
    report = {'kind': 'synthetic-fixture-only', 'commands': results,
              'passed': len(results) == len(calls) and all(x['exit_code'] == 0 for x in results),
              'limits': 'Not a real model evaluation. Archived argv/cwd identify the original temporary run; use --project-root on the exported synthetic-project to recheck its packet.'}
    (output / 'demo-results.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True, help='New export directory; never overwritten')
    args = p.parse_args()
    try:
        report = demo(Path(__file__).resolve().parents[1] / 'tools', args.output.resolve())
        print(json.dumps({'passed': report['passed'], 'kind': report['kind'], 'output': str(args.output)}))
        return 0 if report['passed'] else 1
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'error': str(exc)})); return 2


if __name__ == '__main__':
    raise SystemExit(main())
