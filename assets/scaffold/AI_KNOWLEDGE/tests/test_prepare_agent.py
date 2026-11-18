"""Provider names never imply host tools; exported packs carry real provenance."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / 'tools'


class AgentBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='worachote-agent-')
        self.root = Path(self.temp.name).resolve(); self.addCleanup(self.temp.cleanup)
        (self.root / 'records').mkdir(); (self.root / 'AI_KNOWLEDGE').mkdir()
        self.write('AGENTS.md', 'Canonical rules: preserve scope and verify work.')
        for n in ('BRIEF.md', 'HANDOFF.md', 'events.md'): self.write('records/' + n, 'Task record: next inspect source.')
        self.write('records/task.json', {'protocol_version': 1, 'task_id': 'agent-fixture', 'owner': 'test',
                   'goal': 'Synthetic handoff', 'allowed_paths': ['src'], 'acceptance_criteria': ['Verify source'],
                   'deliverables': [], 'verification_file': 'records/verification.json'})
        self.profile = {'protocol_version': 1, 'provider': 'DeepSeek', 'host': 'unconfigured',
                        'capabilities': {'read_files': False, 'write_files': False, 'run_commands': False, 'network': False}}
        r = self.run_tool('build_context.py', '--out', 'records/context.md')
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def write(self, name, value):
        (self.root / name).write_text(json.dumps(value) if isinstance(value, dict) else value, encoding='utf-8')

    def run_tool(self, tool, *args):
        return subprocess.run([sys.executable, str(TOOLS / tool), '--project-root', str(self.root),
                               '--task', 'records/task.json', *args], capture_output=True, encoding='utf-8')

    def prepare(self, *args):
        self.write('records/profile.json', self.profile)
        return self.run_tool('prepare_agent.py', '--profile', 'records/profile.json', '--context', 'records/context.md',
                             '--out', 'records/agent-handoff.md', *args)

    def test_deepseek_glm_kimi_and_arbitrary_provider_are_not_hardcoded(self):
        for label in ('DeepSeek', 'GLM', 'Kimi', 'Future custom model ภาษาไทย'):
            with self.subTest(label=label):
                self.profile['provider'] = label
                r = self.prepare(); self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
                self.assertEqual(json.loads(r.stdout)['mode'], 'chat-only')
                self.assertIn(label, (self.root / 'records/agent-handoff.md').read_text(encoding='utf-8'))
                (self.root / 'records/agent-handoff.md').unlink()
                (self.root / 'records/agent-handoff.manifest.json').unlink()

    def test_workspace_mode_requires_explicit_read_write_and_run(self):
        self.profile['capabilities'].update(read_files=True, write_files=True, run_commands=True)
        r = self.prepare(); self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(json.loads(r.stdout)['mode'], 'workspace')

    def test_read_only_host_is_assisted_and_cannot_claim_test_execution(self):
        self.profile['capabilities']['read_files'] = True
        r = self.prepare(); self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(json.loads(r.stdout)['mode'], 'assisted')
        text = (self.root / 'records/agent-handoff.md').read_text(encoding='utf-8')
        self.assertIn('Do not claim commands were executed', text)

    def test_stale_context_source_is_rejected(self):
        self.write('AGENTS.md', 'Changed canonical rules')
        self.assertEqual(self.prepare().returncode, 2)

    def test_changed_task_scope_goal_or_owner_requires_rebuilt_context(self):
        path = self.root / 'records/task.json'
        task = json.loads(path.read_text(encoding='utf-8'))
        task.update(goal='New goal', owner='new-owner', allowed_paths=['new-scope'])
        self.write('records/task.json', task)
        self.assertEqual(self.prepare().returncode, 2)

    def test_context_pack_tampering_is_rejected(self):
        self.write('records/context.md', 'Fabricated pack')
        self.assertEqual(self.prepare().returncode, 2)

    def test_capability_strings_are_not_treated_as_booleans(self):
        self.profile['capabilities']['run_commands'] = 'false'
        self.assertEqual(self.prepare().returncode, 2)

    def test_profile_credentials_are_refused(self):
        self.profile['api_key'] = 'fixture-secret'
        r = self.prepare(); self.assertEqual(r.returncode, 2)
        self.assertNotIn('fixture-secret', r.stdout)

    def test_existing_human_output_is_preserved(self):
        self.write('records/agent-handoff.md', 'Human notes')
        self.assertEqual(self.prepare().returncode, 2)
        self.assertEqual((self.root / 'records/agent-handoff.md').read_text(), 'Human notes')

    def test_output_cannot_overwrite_packet_even_without_existing_manifest(self):
        r = self.run_tool('prepare_agent.py', '--profile', 'records/task.json', '--context', 'records/context.md', '--out', 'records/HANDOFF.md')
        self.assertEqual(r.returncode, 2)

    def test_budget_fails_instead_of_truncating_canonical_rules(self):
        self.assertEqual(self.prepare('--max-chars', '50').returncode, 2)
        self.assertFalse((self.root / 'records/agent-handoff.md').exists())


if __name__ == '__main__': unittest.main()
