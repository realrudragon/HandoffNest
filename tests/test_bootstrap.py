from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import json
import os

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'bootstrap.py'


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='worachote-skill-test-')
        self.root = Path(self.temp.name).resolve()
        self.assertTrue(self.root.is_relative_to(Path(tempfile.gettempdir()).resolve()))
        self.addCleanup(self.temp.cleanup)
        self.source = self.root / 'public_html/application/modules/home/controllers/Home.php'
        self.source.parent.mkdir(parents=True)
        self.source.write_text('<?php class Home extends MY_Controller {}', encoding='utf-8')

    def run_bootstrap(self, *extra):
        return subprocess.run([sys.executable, str(SCRIPT), '--project-root', str(self.root), *extra],
                              capture_output=True, text=True)

    def test_scaffolds_ci3_project_without_changing_source(self):
        before = self.source.read_bytes()
        result = self.run_bootstrap()
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertTrue((self.root / 'AI_KNOWLEDGE/START_HERE.md').exists())
        self.assertTrue((self.root / 'AGENTS.md').exists())
        self.assertEqual(self.source.read_bytes(), before)
        snapshot = json.loads((self.root / 'AI_KNOWLEDGE/source_snapshot.json').read_text(encoding='utf-8'))
        self.assertIn('CI3', snapshot['stack'])

    def test_dry_run_creates_nothing(self):
        before = sorted(str(p.relative_to(self.root)) for p in self.root.rglob('*'))
        result = self.run_bootstrap('--dry-run')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(before, sorted(str(p.relative_to(self.root)) for p in self.root.rglob('*')))

    def test_generated_v02_tools_work_end_to_end(self):
        self.assertEqual(self.run_bootstrap().returncode, 0)
        for name in ('work_support.py', 'run_verification.py', 'build_context.py', 'benchmark_switch.py'):
            self.assertTrue((self.root / 'AI_KNOWLEDGE/tools' / name).is_file(), name)
        demo = self.root / 'AI_KNOWLEDGE/examples/v02_demo.py'
        exported = self.root / 'demo-output'
        argv = [sys.executable, str(demo), '--output', str(exported)]
        result = subprocess.run(argv, capture_output=True, encoding='utf-8', timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads((exported / 'demo-results.json').read_text(encoding='utf-8'))
        self.assertTrue(report['passed'])
        self.assertEqual(report['kind'], 'synthetic-fixture-only')
        before = (exported / 'demo-results.json').read_bytes()
        self.assertEqual(subprocess.run(argv, capture_output=True).returncode, 2)
        self.assertEqual((exported / 'demo-results.json').read_bytes(), before)

    def test_stack_report_recognizes_js_and_css_without_running_scripts(self):
        (self.root / 'package.json').write_text(json.dumps({'dependencies': {'react': '^19', 'tailwindcss': '^4'},
            'scripts': {'postinstall': 'DO_NOT_EXECUTE'}}), encoding='utf-8')
        result = self.run_bootstrap()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads((self.root / 'AI_KNOWLEDGE/STACK_DISCOVERY.json').read_text(encoding='utf-8'))
        self.assertTrue({'react', 'tailwindcss'} <= {x['id'] for x in report['detections']})
        self.assertNotIn('DO_NOT_EXECUTE', json.dumps(report))
        self.assertTrue((self.root / 'AI_KNOWLEDGE/STACK_MAP.md').exists())

    def test_html_css_inventory_and_existing_stack_knowledge_preserved(self):
        (self.root / 'index.html').write_text('<html></html>')
        (self.root / 'main.scss').write_text('$color:red;')
        self.assertEqual(self.run_bootstrap().returncode, 0)
        index = json.loads((self.root / 'AI_KNOWLEDGE/indexes/source-index.json').read_text(encoding='utf-8'))
        self.assertTrue({'index.html', 'main.scss'} <= {x['path'] for x in index})
        knowledge = self.root / 'AI_KNOWLEDGE/STACK_MAP.md'
        knowledge.write_text('Human confirmed source knowledge', encoding='utf-8')
        report = self.root / 'AI_KNOWLEDGE/STACK_DISCOVERY.json'
        before = report.read_bytes()
        self.assertEqual(self.run_bootstrap().returncode, 0)
        self.assertEqual(knowledge.read_text(encoding='utf-8'), 'Human confirmed source knowledge')
        self.assertEqual(report.read_bytes(), before)

    def test_generated_v03_universal_demo(self):
        self.assertEqual(self.run_bootstrap().returncode, 0)
        demo = self.root / 'AI_KNOWLEDGE/examples/v03_demo.py'
        p = subprocess.run([sys.executable, str(demo), '--output', str(self.root / 'v03-demo')],
                           capture_output=True, encoding='utf-8', timeout=60)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        result = json.loads((self.root / 'v03-demo/v03-results.json').read_text(encoding='utf-8'))
        self.assertTrue(result['passed'])
        self.assertEqual(result['provider_calls'], 0)

    def test_direct_ci_document_root_is_rejected_before_writes(self):
        (self.root / 'application/modules').mkdir(parents=True)
        (self.root / 'index.php').write_text('<?php', encoding='utf-8')
        result = self.run_bootstrap()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / 'AI_KNOWLEDGE').exists())
        self.assertFalse((self.root / 'AGENTS.md').exists())

    def test_existing_instructions_and_handoff_are_preserved(self):
        (self.root / 'AGENTS.md').write_text('Human existing policy\n', encoding='utf-8')
        handoff = self.root / 'AI_KNOWLEDGE/HANDOFF.md'
        handoff.parent.mkdir()
        handoff.write_text('Unfinished human task', encoding='utf-8')
        result = self.run_bootstrap()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Human existing policy', (self.root / 'AGENTS.md').read_text(encoding='utf-8'))
        self.assertEqual(handoff.read_text(encoding='utf-8'), 'Unfinished human task')

    def test_rerun_is_idempotent(self):
        self.assertEqual(self.run_bootstrap().returncode, 0)
        before = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(self.run_bootstrap().returncode, 0)
        after = {p.relative_to(self.root).as_posix(): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_sensitive_and_dependency_content_is_not_indexed(self):
        (self.root / '.env').write_text('PASSWORD=NEVER_COPY_ME', encoding='utf-8')
        (self.root / 'node_modules').mkdir()
        (self.root / 'node_modules/private.js').write_text('NEVER_COPY_ME', encoding='utf-8')
        self.assertEqual(self.run_bootstrap().returncode, 0)
        index = (self.root / 'AI_KNOWLEDGE/indexes/source-index.json').read_text(encoding='utf-8')
        self.assertNotIn('NEVER_COPY_ME', index)
        self.assertNotIn('node_modules', index)

    def test_freshness_checker_detects_changed_source(self):
        self.assertEqual(self.run_bootstrap().returncode, 0)
        checker = self.root / 'AI_KNOWLEDGE/tools/check_freshness.py'
        cmd = [sys.executable, str(checker)]
        self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
        self.source.write_text('<?php class Changed {}', encoding='utf-8')
        self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 1)

    def test_generated_freshness_handles_thai_path_with_cp1252(self):
        self.assertEqual(self.run_bootstrap().returncode, 0)
        (self.source.parent / '\u0e44\u0e17\u0e22.php').write_text('<?php class Added {}', encoding='utf-8')
        result = subprocess.run([sys.executable, str(self.root / 'AI_KNOWLEDGE/tools/check_freshness.py')],
                                capture_output=True, encoding='utf-8',
                                env=dict(os.environ, PYTHONIOENCODING='cp1252'))
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'stale')

    def test_directory_alias_to_outside_is_not_indexed(self):
        with tempfile.TemporaryDirectory(prefix='worachote-outside-source-') as t:
            outside = Path(t).resolve()
            self.assertTrue(outside.is_relative_to(Path(tempfile.gettempdir()).resolve()))
            (outside / 'outside-secret.php').write_text('<?php class Outside {}', encoding='utf-8')
            link = self.root / 'aliased-source'
            if os.name == 'nt':
                q = subprocess.run(['cmd.exe', '/d', '/c', 'mklink', '/J', str(link), str(outside)], capture_output=True)
                self.assertEqual(q.returncode, 0, q.stderr)
            else:
                link.symlink_to(outside, target_is_directory=True)
            try:
                result = self.run_bootstrap()
                self.assertEqual(result.returncode, 0, result.stderr)
                index = (self.root / 'AI_KNOWLEDGE/indexes/source-index.json').read_text(encoding='utf-8')
                self.assertNotIn('outside-secret.php', index)
            finally:
                if os.name == 'nt':
                    os.rmdir(link)
                else:
                    link.unlink()

    def test_unknown_stack_does_not_invent_ci3(self):
        empty = self.root / 'other-project'
        empty.mkdir()
        q = subprocess.run([sys.executable, str(SCRIPT), '--project-root', str(empty)], capture_output=True, text=True)
        self.assertEqual(q.returncode, 0, q.stderr)
        snapshot = json.loads((empty / 'AI_KNOWLEDGE/source_snapshot.json').read_text(encoding='utf-8'))
        self.assertEqual(snapshot['stack'], 'unverified')

    def test_missing_project_is_rejected_without_creating_it(self):
        missing = self.root / 'missing'
        q = subprocess.run([sys.executable, str(SCRIPT), '--project-root', str(missing)], capture_output=True)
        self.assertNotEqual(q.returncode, 0)
        self.assertFalse(missing.exists())

    def test_unicode_project_name_on_legacy_windows_encoding(self):
        project = self.root / '\u0e42\u0e1b\u0e23\u0e40\u0e08\u0e01\u0e15\u0e4c-\u03b1'
        project.mkdir()
        result = subprocess.run([sys.executable, str(SCRIPT), '--project-root', str(project)],
                                capture_output=True, encoding='utf-8',
                                env=dict(os.environ, PYTHONIOENCODING='cp1252'))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['project'], str(project))

    def test_malformed_managed_markers_fail_before_scaffolding(self):
        (self.root / 'AGENTS.md').write_text('<!-- worachote-structure-ai:begin -->', encoding='utf-8')
        result = self.run_bootstrap()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / 'AI_KNOWLEDGE').exists())

    def test_symlinked_output_cannot_escape_project(self):
        with tempfile.TemporaryDirectory(prefix='worachote-outside-test-') as external:
            outside = Path(external).resolve()
            self.assertTrue(outside.is_relative_to(Path(tempfile.gettempdir()).resolve()))
            link = self.root / 'AI_KNOWLEDGE'
            try:
                link.symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest('Host cannot create directory symlinks')
            try:
                result = self.run_bootstrap()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(list(outside.iterdir()), [])
                self.assertFalse((self.root / 'AGENTS.md').exists())
            finally:
                link.unlink()


if __name__ == '__main__':
    unittest.main()
