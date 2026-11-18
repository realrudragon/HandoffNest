"""Contract/error tests for the portable task completion gate."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

GATE = Path(__file__).resolve().parents[1] / 'tools' / 'verify_task.py'


class CompletionGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='agent-gate-test-')
        self.root = Path(self.temp.name).resolve()
        self.assertTrue(self.root.is_relative_to(Path(tempfile.gettempdir()).resolve()))
        self.addCleanup(self.temp.cleanup)
        (self.root / 'deliverables').mkdir()
        (self.root / 'records').mkdir()
        self.output = self.root / 'deliverables' / 'result.txt'
        self.output.write_text('finished fixture', encoding='utf-8')
        self.evidence = self.root / 'records' / 'test.txt'
        self.evidence.write_text('synthetic fixture evidence only', encoding='utf-8')
        for name in ('BRIEF.md', 'HANDOFF.md', 'events.md'):
            (self.root / 'records' / name).write_text('Synthetic packet record: ' + name, encoding='utf-8')
        self.task = {
            'protocol_version': 1, 'task_id': 'fixture-task', 'kind': 'code',
            'status': 'review', 'owner': 'fixture-agent', 'goal': 'Fixture only',
            'started_at': '2026-11-18T09:00:00+07:00',
            'allowed_paths': ['deliverables'], 'acceptance_criteria': ['fixture behavior'],
            'deliverables': ['deliverables/result.txt'],
            'verification_file': 'records/verification.json',
        }
        self.receipt = {
            'protocol_version': 1, 'task_id': 'fixture-task', 'verified_at': '2026-11-18T10:00:00+07:00',
            'verified_hashes': {'deliverables/result.txt': self.digest(self.output)},
            'checks': [self.check(k) for k in ['functional', 'error', 'regression']],
        }

    @staticmethod
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def check(self, kind):
        return {'kind': kind, 'status': 'passed', 'command': ['fixture-only', kind],
                'environment': 'Synthetic fixture environment; no real test claim',
                'observed_result': 'Fixture expectation satisfied in this test packet',
                'exit_code': 0, 'evidence_file': 'records/test.txt',
                'evidence_sha256': self.digest(self.evidence)}

    def run_gate(self):
        (self.root / 'records/task.json').write_text(json.dumps(self.task), encoding='utf-8')
        (self.root / 'records/verification.json').write_text(json.dumps(self.receipt), encoding='utf-8')
        return subprocess.run([sys.executable, str(GATE), '--project-root', str(self.root),
                               '--task', 'records/task.json'], capture_output=True, text=True)

    def assert_rejected(self, phrase):
        result = self.run_gate()
        self.assertEqual(result.returncode, 1, result.stderr + result.stdout)
        self.assertIn(phrase, result.stdout)

    def test_valid_current_packet_passes(self):
        result = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertEqual(json.loads(result.stdout)['status'], 'ready_for_review')

    def test_missing_error_category_is_rejected(self):
        self.receipt['checks'] = [c for c in self.receipt['checks'] if c['kind'] != 'error']
        self.assert_rejected('error')

    def test_failed_check_cannot_be_hidden_by_a_pass(self):
        self.receipt['checks'].append(dict(self.check('functional'), status='failed', exit_code=1))
        self.assert_rejected('failed')

    def test_pass_with_nonzero_exit_is_rejected(self):
        self.receipt['checks'][0]['exit_code'] = 2
        self.assert_rejected('exit_code')

    def test_unrun_check_is_rejected(self):
        self.receipt['checks'][0]['status'] = 'not_run'
        self.assert_rejected('not_run')

    def test_changed_deliverable_invalidates_receipt(self):
        self.output.write_text('changed after verification', encoding='utf-8')
        self.assert_rejected('stale')

    def test_missing_hash_is_rejected(self):
        self.receipt['verified_hashes'] = {}
        self.assert_rejected('hash')

    def test_tampered_evidence_is_rejected(self):
        self.evidence.write_text('tampered', encoding='utf-8')
        self.assert_rejected('evidence')

    def test_missing_evidence_is_rejected(self):
        self.evidence.unlink()
        self.assert_rejected('evidence')

    def test_deliverable_outside_assigned_scope_is_rejected(self):
        self.task['allowed_paths'] = ['different-area']
        self.assert_rejected('scope')

    def test_relative_path_escape_is_rejected(self):
        self.task['deliverables'] = ['../outside.txt']
        self.assert_rejected('path')

    def test_windows_absolute_path_is_rejected_even_on_unix(self):
        self.task['verification_file'] = 'C:\\private\\receipt.json'
        self.assert_rejected('path')

    def test_wrong_task_receipt_is_rejected(self):
        self.receipt['task_id'] = 'other-task'
        self.assert_rejected('task_id')

    def test_unknown_protocol_is_rejected(self):
        self.task['protocol_version'] = 999
        self.assert_rejected('protocol_version')

    def test_previous_attempt_receipt_is_rejected(self):
        self.task['started_at'] = '2026-11-18T11:00:00+07:00'
        self.assert_rejected('predates')

    def test_unassigned_owner_cannot_complete(self):
        self.task['owner'] = 'unassigned'
        self.assert_rejected('owner')

    def test_code_error_checks_cannot_be_not_applicable(self):
        self.receipt['checks'][1] = {'kind': 'error', 'status': 'not_applicable', 'reason': 'Convenience'}
        self.assert_rejected('code')

    def test_docs_can_explain_nonapplicable_regression(self):
        self.task['kind'] = 'docs'
        self.receipt['checks'][2] = {'kind': 'regression', 'status': 'not_applicable',
                                     'reason': 'No application behavior changed; functional/error checks validate documents.'}
        result = self.run_gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_empty_acceptance_criteria_is_rejected(self):
        self.task['acceptance_criteria'] = []
        self.assert_rejected('acceptance')

    def test_missing_handoff_blocks_completion(self):
        (self.root / 'records/HANDOFF.md').unlink()
        self.assert_rejected('HANDOFF.md')

    def test_missing_environment_blocks_completion(self):
        del self.receipt['checks'][0]['environment']
        self.assert_rejected('environment')

    def test_missing_observed_result_blocks_completion(self):
        del self.receipt['checks'][0]['observed_result']
        self.assert_rejected('observed_result')

    def test_broken_receipt_json_is_error_not_pass(self):
        self.task['verification_file'] = 'records/missing.json'
        self.assert_rejected('verification')


if __name__ == '__main__':
    unittest.main()
