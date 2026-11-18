"""Observable multi-ecosystem discovery tests on disposable first-party fixtures."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1] / 'tools'


class StackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='worachote-stack-')
        self.root = Path(self.temp.name).resolve()
        self.addCleanup(self.temp.cleanup)

    def write(self, name, value):
        p = self.root / name; p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(value) if isinstance(value, dict) else value, encoding='utf-8')
        return p

    def cli(self, *args):
        return subprocess.run([sys.executable, str(TOOLS / 'discover_stack.py'), '--project-root', str(self.root), *args],
                              capture_output=True, encoding='utf-8', timeout=20)

    def report(self, *args):
        p = self.cli(*args)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        return json.loads(p.stdout)

    def ids(self, report):
        return {x['id'] for x in report['detections']}

    def test_node_mixed_stack_tracks_declarations_not_installed_versions(self):
        path = self.write('package.json', {'dependencies': {'next': '^15.0.0', 'react': '^19.0.0'},
                                          'devDependencies': {'tailwindcss': '^4.0.0', 'vitest': '^3.0.0'},
                                          'scripts': {'test': 'DO_NOT_EXECUTE_SECRET=private-value'}})
        r = self.report()
        self.assertTrue({'nextjs', 'react', 'tailwindcss', 'vitest'} <= self.ids(r))
        d = next(x for x in r['detections'] if x['id'] == 'tailwindcss')
        self.assertEqual(d['evidence'][0]['version_constraint'], '^4.0.0')
        self.assertEqual(d['evidence'][0]['section'], 'devDependencies')
        self.assertEqual(d['evidence'][0]['sha256'], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(r['understanding_status'], 'discovery_only')
        self.assertNotIn('private-value', json.dumps(r))

    def test_php_composer_and_legacy_hmvc_candidates(self):
        self.write('composer.json', {'require': {'laravel/framework': '^11.0', 'symfony/console': '^7.0'}})
        self.write('public_html/application/config/routes.php', '<?php')
        self.write('public_html/application/modules/home/controllers/Home.php', '<?php')
        r = self.report()
        self.assertTrue({'laravel', 'codeigniter3', 'hmvc'} <= self.ids(r))
        d = next(x for x in r['detections'] if x['id'] == 'hmvc')
        self.assertEqual(d['confidence'], 'candidate')

    def test_python_requirements_and_toml(self):
        self.write('api/requirements.txt', 'fastapi==0.115.0\nuvicorn>=0.30\n-r private.txt\n')
        self.write('worker/pyproject.toml', '[project]\nname="worker"\nversion="0.1"\ndependencies=["Django>=5.0", "SQLAlchemy>=2.0"]\n')
        r = self.report()
        self.assertTrue({'fastapi', 'django', 'sqlalchemy'} <= self.ids(r))
        self.assertTrue(any('requirements include' in x for x in r['warnings']))

    def test_go_and_ruby(self):
        self.write('api/go.mod', 'module example.com/api\ngo 1.22\nrequire (\n github.com/gin-gonic/gin v1.10.0\n)\n')
        self.write('web/Gemfile', 'source "https://rubygems.org"\ngem "rails", "~> 7.1"\n')
        self.assertTrue({'gin', 'rails'} <= self.ids(self.report()))

    def test_gradle_comments_and_logging_are_not_declared_dependencies(self):
        self.write('build.gradle', '// implementation "org.springframework.boot:spring-boot-starter-web:3.4.0"\n/* api("org.springframework.boot:spring-boot-starter-web:3.4.0") */\nprintln "org.springframework.boot:spring-boot-starter-web:3.4.0"\n')
        self.assertNotIn('springboot', self.ids(self.report()))
        self.write('build.gradle', 'dependencies {\n implementation("org.springframework.boot:spring-boot-starter-web:3.4.0")\n}\n')
        self.assertIn('springboot', self.ids(self.report()))

    def test_rust_java_dotnet_and_dart(self):
        self.write('rust/Cargo.toml', '[package]\nname="sample"\nversion="0.1.0"\n[dependencies]\naxum="0.8"\n')
        self.write('java/pom.xml', '<project><dependencies><dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-web</artifactId><version>3.4.0</version></dependency></dependencies></project>')
        self.write('net/App.csproj', '<Project><ItemGroup><PackageReference Include="Microsoft.EntityFrameworkCore" Version="9.0.0" /></ItemGroup></Project>')
        self.write('mobile/pubspec.yaml', 'name: sample\ndependencies:\n  flutter:\n    sdk: flutter\n  riverpod: ^2.0.0\n')
        self.assertTrue({'axum', 'springboot', 'entityframework', 'flutter', 'riverpod'} <= self.ids(self.report()))

    def test_monorepo_workspace_and_versions_do_not_collapse(self):
        self.write('package.json', {'workspaces': ['apps/*']})
        self.write('apps/old/package.json', {'dependencies': {'tailwindcss': '^3.0'}})
        self.write('apps/new/package.json', {'dependencies': {'tailwindcss': '^4.0'}})
        rows = [x for x in self.report()['detections'] if x['id'] == 'tailwindcss']
        self.assertEqual({x['workspace'] for x in rows}, {'apps/old', 'apps/new'})
        self.assertEqual({x['evidence'][0]['version_constraint'] for x in rows}, {'^3.0', '^4.0'})

    def test_css_import_and_cdn_are_candidates_not_runtime_proof(self):
        self.write('src/main.css', '@import "tailwindcss";\n@import "bootstrap/dist/css/bootstrap.css";\n')
        self.write('index.html', '<link href="https://cdn.example/bootstrap@5.3.0/dist/css/bootstrap.min.css?token=never-retain" rel="stylesheet">')
        r = self.report()
        self.assertTrue({'tailwindcss', 'bootstrap'} <= self.ids(r))
        self.assertTrue(all(x['confidence'] == 'candidate' for x in r['detections']))
        self.assertNotIn('never-retain', json.dumps(r))
        self.assertIn('CSS', r['languages'])
        self.assertIn('HTML', r['languages'])

    def test_css_names_in_unrelated_prose_do_not_detect_framework(self):
        self.write('notes.txt', 'tailwindcss bootstrap next react')
        self.write('src/main.css', '/* bootstrap is a word in this comment */\n.btn { color:red; }')
        self.assertFalse(self.report()['detections'])

    def test_unknown_packages_extensions_have_actionable_fallback(self):
        self.write('package.json', {'dependencies': {'future-ui-2099': '^1.0'}})
        self.write('src/main.future', 'unknown language source')
        r = self.report()
        self.assertIn('future-ui-2099', {x['name'] for x in r['unknown_dependencies']})
        self.assertIn('.future', r['unclassified_extensions'])
        self.assertTrue(r['next_actions'])

    def test_custom_registry_extends_unknown_framework(self):
        self.write('package.json', {'dependencies': {'future-ui-2099': '^1.0'}})
        self.write('custom-rules.json', {'protocol_version': 1, 'rules': [
            {'id': 'future', 'label': 'Future UI', 'category': 'frontend',
             'packages': {'npm': ['future-ui-2099']}, 'markers': []}]})
        self.assertIn('future', self.ids(self.report('--rules', 'custom-rules.json')))

    def test_invalid_custom_registry_is_error(self):
        self.write('custom-rules.json', {'protocol_version': 1, 'rules': [{'id': '../bad'}]})
        self.assertEqual(self.cli('--rules', 'custom-rules.json').returncode, 2)

    def test_malformed_manifest_is_partial_and_retains_no_source_body(self):
        self.write('package.json', '{"secret":"do-not-retain", broken')
        p = self.cli()
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        r = json.loads(p.stdout)
        self.assertEqual(r['status'], 'partial')
        self.assertTrue(r['warnings'])
        self.assertNotIn('do-not-retain', p.stdout)

    def test_vendor_env_and_credentials_are_excluded(self):
        self.write('node_modules/private/package.json', {'dependencies': {'next': '^15'}})
        self.write('vendor/private/composer.json', {'require': {'laravel/framework': '^11'}})
        self.write('.env', 'API_KEY=do-not-retain')
        self.write('credentials.json', '{"secret":"do-not-retain"}')
        r = self.report()
        self.assertFalse(r['detections'])
        self.assertNotIn('do-not-retain', json.dumps(r))

    def test_secret_url_dependency_spec_is_not_persisted(self):
        self.write('package.json', {'dependencies': {'next': 'https://user:never-retain@example.com/next.tgz'}})
        r = self.report()
        self.assertNotIn('never-retain', json.dumps(r))
        self.assertEqual(r['detections'][0]['evidence'][0]['version_constraint'], 'non-version-spec')

    def test_scan_limit_is_partial_not_exhaustive_claim(self):
        for i in range(5): self.write(str(i) + '.css', 'body{}')
        p = self.cli('--max-files', '2')
        self.assertEqual(p.returncode, 1)
        self.assertTrue(json.loads(p.stdout)['coverage']['truncated'])

    def test_empty_directory_tree_is_bounded_separately(self):
        for i in range(12): (self.root / str(i)).mkdir()
        p = self.cli('--max-directories', '3')
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        coverage = json.loads(p.stdout)['coverage']
        self.assertTrue(coverage['truncated'])
        self.assertLessEqual(coverage['directories_visited'], 3)

    def test_existing_output_and_outside_output_preserved(self):
        self.write('AI_KNOWLEDGE/report.json', '{"human":true}')
        self.assertEqual(self.cli('--out', 'AI_KNOWLEDGE/report.json').returncode, 2)
        self.assertEqual((self.root / 'AI_KNOWLEDGE/report.json').read_text(), '{"human":true}')
        self.assertEqual(self.cli('--out', '../outside.json').returncode, 2)

    def test_no_output_option_is_read_only(self):
        self.write('package.json', {'dependencies': {'vue': '^3'}})
        before = {p.relative_to(self.root).as_posix() for p in self.root.rglob('*')}
        self.assertIn('vue', self.ids(self.report()))
        self.assertEqual(before, {p.relative_to(self.root).as_posix() for p in self.root.rglob('*')})

    def test_windows_junction_to_external_project_is_not_followed(self):
        with tempfile.TemporaryDirectory(prefix='worachote-stack-outside-') as temp:
            outside = Path(temp).resolve()
            (outside / 'package.json').write_text('{"dependencies":{"next":"15"}}')
            alias = self.root / 'alias'
            if os.name == 'nt':
                p = subprocess.run(['cmd.exe', '/d', '/c', 'mklink', '/J', str(alias), str(outside)], capture_output=True)
                self.assertEqual(p.returncode, 0)
            else: alias.symlink_to(outside, target_is_directory=True)
            try: self.assertFalse(self.report()['detections'])
            finally:
                if os.name == 'nt': os.rmdir(alias)
                else: alias.unlink()


if __name__ == '__main__': unittest.main()
