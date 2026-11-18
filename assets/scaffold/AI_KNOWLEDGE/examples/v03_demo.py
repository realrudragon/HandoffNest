#!/usr/bin/env python3
"""Mixed-stack and universal-export fixture demo, zero model/provider calls."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from v02_demo import demo


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True); a = p.parse_args()
    tools = Path(__file__).resolve().parents[1] / 'tools'
    try:
        result = demo(tools, a.output.resolve())
        if not result['passed']: return 1
        root = a.output.resolve() / 'synthetic-project'
        def write(name, value):
            path = root / name; path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value, indent=2) if isinstance(value, dict) else value, encoding='utf-8')
        write('apps/web/package.json', {'dependencies': {'next': '^15', 'react': '^19'}, 'devDependencies': {'tailwindcss': '^4'}})
        write('api/requirements.txt', 'fastapi>=0.115\n')
        write('styles/main.css', '@import "bootstrap/dist/css/bootstrap.css";\n')
        results = []
        def run(tool, args, task=False):
            argv = [sys.executable, str(tools / tool), '--project-root', str(root)]
            if task: argv += ['--task', 'records/task.json']
            proc = subprocess.run(argv + args, capture_output=True, encoding='utf-8', timeout=60)
            results.append({'argv': argv + args, 'exit_code': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr})
            if proc.returncode: raise ValueError('Synthetic command failed: ' + tool)
            return json.loads(proc.stdout)
        stack = run('discover_stack.py', ['--out', 'AI_KNOWLEDGE/STACK_DISCOVERY.json'])
        if not {'nextjs', 'react', 'tailwindcss', 'bootstrap', 'fastapi'} <= {r['id'] for r in stack['detections']}:
            raise ValueError('Expected synthetic stack not found')
        # Original context remains source-current. Exports show declared host modes, not live provider access.
        for label, capabilities in [
            ('DeepSeek', {'read_files': True, 'write_files': True, 'run_commands': True, 'network': False}),
            ('GLM', {'read_files': True, 'write_files': False, 'run_commands': False, 'network': False}),
            ('Kimi', {'read_files': False, 'write_files': False, 'run_commands': False, 'network': False})]:
            write('records/' + label + '-profile.json', {'protocol_version': 1, 'provider': label, 'host': 'synthetic-fixture-not-connected', 'capabilities': capabilities})
            run('prepare_agent.py', ['--profile', 'records/' + label + '-profile.json', '--context', 'records/context-pack.md',
                                    '--out', 'records/' + label + '-handoff.md'], task=True)
        report = {'passed': True, 'kind': 'synthetic-fixture-only', 'provider_calls': 0, 'commands': results,
                  'limits': 'Host capabilities are declared fixtures; no real DeepSeek/GLM/Kimi integration or model quality tested'}
        (a.output / 'v03-results.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'passed': True, 'provider_calls': 0, 'output': str(a.output)})); return 0
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'error': str(exc)})); return 2


if __name__ == '__main__': raise SystemExit(main())
