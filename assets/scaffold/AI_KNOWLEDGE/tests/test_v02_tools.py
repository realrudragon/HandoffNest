"""Observable integration/error tests; all child commands use disposable fixtures."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / 'tools'


class V02Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='worachote-v02-')
        self.root = Path(self.temp.name).resolve()
        self.assertTrue(self.root.is_relative_to(Path(tempfile.gettempdir()).resolve()))
        self.addCleanup(self.temp.cleanup)
        for d in ('records', 'src', 'docs', 'AI_KNOWLEDGE'):
            (self.root / d).mkdir()
        (self.root / 'AGENTS.md').write_text('Canonical rules: inspect source and verify work.', encoding='utf-8')
        (self.root / 'AI_KNOWLEDGE/QUICK_CONTEXT.md').write_text('Synthetic project, no real application.', encoding='utf-8')
        for name in ('BRIEF.md', 'HANDOFF.md', 'events.md'):
            (self.root / 'records' / name).write_text('Fixture ' + name + ': next read src/math.py.', encoding='utf-8')
        (self.root / 'src/math.py').write_text('def add(a,b): return a+b\n', encoding='utf-8')
        (self.root / 'docs/guide.md').write_text('Useful task documentation.', encoding='utf-8')
        self.task = {'protocol_version': 1, 'task_id': 'v02-fixture', 'kind': 'code', 'status': 'review',
                     'owner': 'fixture-agent', 'started_at': '2026-11-18T00:00:00+07:00',
                     'goal': 'Verify synthetic addition behavior', 'allowed_paths': ['src'],
                     'acceptance_criteria': ['Addition returns expected value'], 'deliverables': ['src/math.py'],
                     'context_files': ['docs/guide.md'], 'verification_file': 'records/verification.json'}
        self.save_task()
        self.plan = {'protocol_version': 1, 'checks': [self.check(k) for k in ('functional', 'error', 'regression')]}
        self.save('records/plan.json', self.plan)

    def save(self, name, value):
        (self.root / name).write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')

    def save_task(self):
        self.save('records/task.json', self.task)

    def check(self, kind):
        return {'id': kind, 'kind': kind, 'argv': [sys.executable, '-c', "print('fixture-ok')"],
                'timeout_seconds': 5, 'expect_stdout': ['fixture-ok']}

    def cli(self, tool, *args, env=None):
        return subprocess.run([sys.executable, str(TOOLS / tool), '--project-root', str(self.root),
                               '--task', 'records/task.json', *args], capture_output=True,
                              encoding='utf-8', env=env)

    def runner(self, execute=True, env=None):
        self.save('records/plan.json', self.plan)
        return self.cli('run_verification.py', '--plan', 'records/plan.json',
                        *(['--execute'] if execute else []), env=env)

    def test_runner_preview_does_not_execute_or_write_receipt(self):
        r = self.runner(False)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)['status'], 'preview')
        self.assertFalse((self.root / 'records/verification.json').exists())

    def test_runner_real_receipt_passes_existing_gate(self):
        r = self.runner()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        receipt = json.loads((self.root / 'records/verification.json').read_text(encoding='utf-8'))
        self.assertEqual(receipt['producer'], 'worachote-verification-runner/0.2')
        self.assertEqual(len(receipt['checks']), 3)
        gate = self.cli('verify_task.py')
        self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)

    def test_runner_retains_assertions_used_for_historical_run(self):
        self.assertEqual(self.runner().returncode, 0)
        receipt = json.loads((self.root / 'records/verification.json').read_text(encoding='utf-8'))
        evidence = json.loads((self.root / receipt['checks'][0]['evidence_file']).read_text(encoding='utf-8'))
        self.assertEqual(evidence['assertions']['expect_stdout'], ['fixture-ok'])
        self.assertTrue((self.root / receipt['plan_snapshot_file']).is_file())

    def test_runner_failure_is_retained_and_blocks_gate(self):
        self.plan['checks'][0]['argv'] = [sys.executable, '-c', 'raise SystemExit(7)']
        r = self.runner()
        self.assertEqual(r.returncode, 1, r.stderr)
        receipt = json.loads((self.root / 'records/verification.json').read_text(encoding='utf-8'))
        self.assertEqual(receipt['checks'][0]['exit_code'], 7)
        self.assertEqual(receipt['checks'][0]['status'], 'failed')
        self.assertEqual(self.cli('verify_task.py').returncode, 1)

    def test_runner_timeout_is_not_pass(self):
        self.plan['checks'][0].update(argv=[sys.executable, '-c', 'import time; time.sleep(3)'], timeout_seconds=0.1)
        r = self.runner()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn('timeout', r.stdout)

    def test_runner_checks_output_assertions_not_only_exit_zero(self):
        self.plan['checks'][0]['expect_stdout'] = ['never-emitted']
        self.assertEqual(self.runner().returncode, 1)

    def test_runner_source_change_during_check_invalidates_run(self):
        self.plan['checks'][0]['argv'] = [sys.executable, '-c', "from pathlib import Path; Path('src/math.py').write_text('changed'); print('fixture-ok')"]
        r = self.runner()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertIn('source_changed', r.stdout)

    def test_runner_redacts_secret_from_retained_output(self):
        secret = 'fixture-secret-never-retain'
        self.plan['checks'][0]['argv'] = [sys.executable, '-c', "import os; print('fixture-ok'); print(os.environ['DEMO_API_KEY'])"]
        r = self.runner(env=dict(os.environ, DEMO_API_KEY=secret))
        self.assertEqual(r.returncode, 0, r.stderr)
        for p in (self.root / 'records/evidence').rglob('*'):
            if p.is_file():
                self.assertNotIn(secret, p.read_text(encoding='utf-8'))

    def test_runner_rejects_shell_string_plan(self):
        self.plan['checks'][0]['argv'] = 'echo do-not-execute'
        self.assertEqual(self.runner().returncode, 2)
        self.assertFalse((self.root / 'records/verification.json').exists())

    def test_runner_rejects_outside_cwd(self):
        self.plan['checks'][0]['cwd'] = '..'
        self.assertEqual(self.runner().returncode, 2)

    def test_runner_cannot_overwrite_canonical_rules_with_receipt(self):
        before = (self.root / 'AGENTS.md').read_bytes()
        self.task['verification_file'] = 'AGENTS.md'; self.save_task()
        self.assertEqual(self.runner().returncode, 2)
        self.assertEqual((self.root / 'AGENTS.md').read_bytes(), before)

    def test_runner_rejects_receipt_collision_with_plan(self):
        self.save('records/verification.json', self.plan)
        before = (self.root / 'records/verification.json').read_bytes()
        r = self.cli('run_verification.py', '--plan', 'records/verification.json', '--execute')
        self.assertEqual(r.returncode, 2)
        self.assertEqual((self.root / 'records/verification.json').read_bytes(), before)

    def test_runner_requires_all_three_behavior_categories(self):
        self.plan['checks'] = self.plan['checks'][:1]
        self.assertEqual(self.runner().returncode, 2)
        self.assertFalse((self.root / 'records/verification.json').exists())

    def test_runner_flags_plan_change_during_checks(self):
        self.plan['checks'][0]['argv'] = [sys.executable, '-c', "from pathlib import Path; Path('records/plan.json').write_text('{}'); print('fixture-ok')"]
        self.assertEqual(self.runner().returncode, 1)
        receipt = json.loads((self.root / 'records/verification.json').read_text(encoding='utf-8'))
        self.assertTrue(receipt['plan_changed_during_run'])

    def context(self, *args):
        return self.cli('build_context.py', '--out', 'records/context-pack.md', *args)

    def test_context_contains_rules_task_and_handoff_with_provenance(self):
        r = self.context('--max-chars', '6000')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        text = (self.root / 'records/context-pack.md').read_text(encoding='utf-8')
        self.assertIn('Canonical rules', text)
        self.assertIn(self.task['goal'], text)
        self.assertIn('HANDOFF.md', text)
        self.assertLessEqual(len(text), 6000)
        meta = json.loads((self.root / 'records/context-pack.manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(meta['budget_unit'], 'unicode_codepoints')
        self.assertTrue(meta['included'])

    def test_context_fails_rather_than_dropping_mandatory_rules(self):
        r = self.context('--max-chars', '80')
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse((self.root / 'records/context-pack.md').exists())

    def test_context_replace_cannot_overwrite_event_history(self):
        before = (self.root / 'records/events.md').read_bytes()
        r = self.cli('build_context.py', '--out', 'records/events.md', '--replace')
        self.assertEqual(r.returncode, 2)
        self.assertEqual((self.root / 'records/events.md').read_bytes(), before)

    def test_context_replace_requires_existing_generated_manifest(self):
        (self.root / 'records/context-pack.md').write_text('Human notes', encoding='utf-8')
        self.assertEqual(self.context('--replace').returncode, 2)
        self.assertEqual((self.root / 'records/context-pack.md').read_text(), 'Human notes')

    def test_context_replace_can_refresh_its_own_pack(self):
        self.assertEqual(self.context().returncode, 0)
        self.assertEqual(self.context('--replace').returncode, 0)

    def test_context_budget_records_omissions(self):
        (self.root / 'docs/guide.md').write_text('x' * 20000, encoding='utf-8')
        r = self.context('--max-chars', '2000')
        self.assertEqual(r.returncode, 0, r.stderr)
        meta = json.loads((self.root / 'records/context-pack.manifest.json').read_text(encoding='utf-8'))
        self.assertTrue(any(x['reason'] == 'budget' for x in meta['omitted']))

    def test_context_large_unbroken_text_does_not_stall_redaction(self):
        (self.root / 'docs/guide.md').write_text('x' * 80000, encoding='utf-8')
        result = subprocess.run([sys.executable, str(TOOLS / 'build_context.py'), '--project-root', str(self.root),
                                 '--task', 'records/task.json', '--out', 'records/context-pack.md', '--max-chars', '2000'],
                                capture_output=True, encoding='utf-8', timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_context_rejects_sensitive_file(self):
        (self.root / '.env').write_text('PASSWORD=secret', encoding='utf-8')
        self.task['context_files'] = ['.env']; self.save_task()
        self.assertEqual(self.context().returncode, 2)

    def test_context_rejects_outside_source_reference(self):
        self.task['context_files'] = ['../outside.md']; self.save_task()
        self.assertEqual(self.context().returncode, 2)

    def test_context_source_is_opt_in_and_redacted(self):
        (self.root / 'src/config.php').write_text("<?php define('DB_PASSWORD', 'do-not-copy-fixture');", encoding='utf-8')
        self.task['context_files'] = ['src/config.php']; self.save_task()
        self.assertEqual(self.context().returncode, 2)
        r = self.context('--include-source')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn('do-not-copy-fixture', (self.root / 'records/context-pack.md').read_text(encoding='utf-8'))

    def test_context_includes_graph_relationships_without_claiming_runtime(self):
        (self.root / 'AI_KNOWLEDGE/graphify-out').mkdir()
        self.save('AI_KNOWLEDGE/graphify-out/graph.json', {'nodes': [
            {'id': 'a', 'label': 'add', 'source_file': 'src/math.py'},
            {'id': 'b', 'label': 'Caller', 'source_file': 'src/caller.py'}],
            'links': [{'source': 'b', 'target': 'a', 'relation': 'calls', 'confidence': 0.8}]})
        self.assertEqual(self.context().returncode, 0)
        text = (self.root / 'records/context-pack.md').read_text(encoding='utf-8')
        self.assertIn('Caller', text)
        self.assertIn('static', text)

    def benchmark_plan(self, bad_adapter=False):
        adapter = self.root / 'adapter.py'
        adapter.write_text("import json,sys\nfrom pathlib import Path\nr=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))\nassert 'expected_answers' not in r\nanswer='src/math.py' if r['context'] else 'unknown'\nPath(sys.argv[2]).write_text(json.dumps({'answers':{'owning_file':answer},'reported_usage':{'input_tokens':5}}),encoding='utf-8')\n", encoding='utf-8')
        (self.root / 'docs/prompt.md').write_text('Which file owns addition?', encoding='utf-8')
        plan = {'protocol_version': 1, 'benchmark_id': 'fixture-switch', 'trials': 2, 'seed': 1,
                'adapters': [{'id': 'fixture-agent', 'kind': 'fixture',
                              'argv': [sys.executable, 'adapter.py', '{request}', '{response}'], 'timeout_seconds': 5}],
                'cases': [{'id': 'addition', 'prompt_file': 'docs/prompt.md',
                           'expected_answers': {'owning_file': 'src/math.py'},
                           'variants': [{'id': 'baseline', 'context_files': []},
                                        {'id': 'with-context', 'context_files': ['docs/guide.md']}]}]}
        if bad_adapter:
            plan['adapters'][0]['argv'] = [sys.executable, '-c', 'raise SystemExit(4)']
        self.save('records/benchmark-plan.json', plan)
        return plan

    def benchmark(self, execute=True):
        return self.cli('benchmark_switch.py', '--plan', 'records/benchmark-plan.json',
                        *(['--execute'] if execute else []))

    def test_benchmark_preview_never_executes_adapter(self):
        self.benchmark_plan()
        r = self.benchmark(False)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)['status'], 'preview')

    def test_benchmark_scores_paired_variants_and_labels_fixture(self):
        self.benchmark_plan()
        r = self.benchmark()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        meta = json.loads(r.stdout)
        report = json.loads((self.root / meta['report']).read_text(encoding='utf-8'))
        self.assertEqual(len(report['trials']), 4)
        scores = {x['variant']: x['accuracy'] for x in report['summary']}
        self.assertEqual(scores, {'baseline': 0.0, 'with-context': 1.0})
        self.assertEqual(report['adapters'][0]['kind'], 'fixture')
        self.assertIn('reported_usage', report['trials'][0])
        self.assertIn('elapsed_seconds', report['trials'][0])

    def test_benchmark_adapter_failure_is_partial_not_clean_result(self):
        self.benchmark_plan(True)
        r = self.benchmark()
        self.assertEqual(r.returncode, 1, r.stderr)
        self.assertEqual(json.loads(r.stdout)['status'], 'partial')

    def test_benchmark_invalid_response_is_retained_as_error(self):
        self.benchmark_plan()
        (self.root / 'adapter.py').write_text("import sys; from pathlib import Path; Path(sys.argv[2]).write_text('not-json')", encoding='utf-8')
        self.assertEqual(self.benchmark().returncode, 1)

    def test_benchmark_preserves_loaded_plan_hash_and_flags_drift(self):
        self.benchmark_plan()
        original = hashlib.sha256((self.root / 'records/benchmark-plan.json').read_bytes()).hexdigest()
        adapter = self.root / 'adapter.py'
        adapter.write_text(adapter.read_text(encoding='utf-8') + "\nPath('records/benchmark-plan.json').write_text('{}')\n", encoding='utf-8')
        r = self.benchmark()
        self.assertEqual(r.returncode, 1, r.stderr)
        report = json.loads((self.root / json.loads(r.stdout)['report']).read_text(encoding='utf-8'))
        self.assertEqual(report['plan_sha256'], original)
        self.assertTrue(report['plan_changed_during_run'])

    def test_benchmark_rejects_outside_context(self):
        plan = self.benchmark_plan()
        plan['cases'][0]['variants'][1]['context_files'] = ['../outside.md']
        self.save('records/benchmark-plan.json', plan)
        self.assertEqual(self.benchmark().returncode, 2)

    def test_benchmark_rejects_unknown_adapter_kind(self):
        plan = self.benchmark_plan(); plan['adapters'][0]['kind'] = 'magical-frontier'
        self.save('records/benchmark-plan.json', plan)
        self.assertEqual(self.benchmark().returncode, 2)


if __name__ == '__main__':
    unittest.main()
