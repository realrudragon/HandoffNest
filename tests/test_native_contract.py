"""Maintainer conformance checks; the default user workflow itself needs no Python."""
import copy
import json
from pathlib import Path, PurePosixPath
import re
import unittest

SKILL = Path(__file__).resolve().parents[1]


def plan_errors(plan):
    errors = []
    if plan.get('mode') != 'native' or plan.get('runtime_dependencies') != []:
        errors.append('Native mode must have no runtime dependencies')
    if plan.get('preserve_existing') is not True or plan.get('copy_helpers') is not False:
        errors.append('Preserve existing files; do not install helpers by default')
    files = plan.get('files', [])
    if not files or len(files) > 10: errors.append('Expected small native starter')
    targets = set()
    for row in files:
        source, target = row.get('source', ''), row.get('target', '')
        for value in (source, target):
            path = PurePosixPath(value)
            if not value or path.is_absolute() or '..' in path.parts or '\\' in value or ':' in value:
                errors.append('Unsafe native resource path')
        if not source.startswith('assets/') or not target.startswith('AI_KNOWLEDGE/') or not target.endswith('.md'):
            errors.append('Native setup copies Markdown resources only')
        if not (SKILL / source).is_file(): errors.append('Missing native resource')
        if target in targets: errors.append('Duplicate target')
        targets.add(target)
    return errors


class NativeContractTests(unittest.TestCase):
    def plan(self):
        path = SKILL / 'assets/native/setup-plan.json'
        self.assertTrue(path.is_file(), 'Native-first setup plan is missing')
        return json.loads(path.read_text(encoding='utf-8'))

    def test_native_mode_has_no_runtime_or_helper_dependency(self):
        self.assertEqual(plan_errors(self.plan()), [])

    def test_core_skill_declares_native_default_and_routes_automation(self):
        text = (SKILL / 'SKILL.md').read_text(encoding='utf-8')
        self.assertIn('Default: native', text)
        self.assertIn('## Optional automation', text)
        default = text.split('## Optional automation')[0]
        self.assertNotIn('scripts/bootstrap.py', default)
        self.assertNotRegex(default, r'(?m)^\s*(?:python3?|py)\s+')
        self.assertLess(len(text), 6500, 'Keep the entrypoint small; route detail into references')

    def test_quickstart_requires_invocation_not_terminal_command(self):
        text = (SKILL / 'README.md').read_text(encoding='utf-8')
        self.assertIn('$handoff-nest', text)
        self.assertNotIn('python scripts/bootstrap.py', text)
        self.assertNotIn('Requires **Python', text)
        self.assertIn('references/automation.md', text)

    def test_native_plan_contains_essentials_without_advanced_json_gate(self):
        plan = self.plan(); targets = {x['target'] for x in plan['files']}
        self.assertTrue({'AI_KNOWLEDGE/START_HERE.md', 'AI_KNOWLEDGE/QUICK_CONTEXT.md',
                         'AI_KNOWLEDGE/WORKING_RULES.md', 'AI_KNOWLEDGE/HANDOFF.md',
                         'AI_KNOWLEDGE/STACK_MAP.md'} <= targets)
        self.assertFalse(any(x.endswith('.py') or x.endswith('verification.json') for x in targets))

    def test_native_starter_links_resolve_in_its_small_file_set(self):
        plan = self.plan(); targets = {x['target'] for x in plan['files']}
        for row in plan['files']:
            body = (SKILL / row['source']).read_text(encoding='utf-8')
            for link in re.findall(r'\]\(([^)]+)\)', body):
                if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', link) or link.startswith('#'): continue
                target = (PurePosixPath(row['target']).parent / link.split('#')[0]).as_posix()
                self.assertIn(target, targets, row['target'] + ' has an unavailable native starter link')

    def test_generated_rules_explicitly_distinguish_native_and_automation(self):
        for name in ['WORKING_RULES.md', 'agent-system/CONTRACT.md', 'agent-system/VERIFICATION.md']:
            text = (SKILL / 'assets/scaffold/AI_KNOWLEDGE' / name).read_text(encoding='utf-8')
            self.assertIn('Native mode', text, name)
            self.assertIn('Automation mode', text, name)
            self.assertIn('Existing project requirements take precedence', text, name)

    def test_native_guide_does_not_fake_hashes_or_gate_equivalence(self):
        text = (SKILL / 'references/native-setup.md').read_text(encoding='utf-8')
        self.assertIn('not_computed', text)
        self.assertIn('not_run_optional', text)
        self.assertIn('chat-only', text)
        self.assertIn('preserve', text.lower())

    def test_optional_automation_helpers_are_preserved(self):
        self.assertTrue((SKILL / 'scripts/bootstrap.py').is_file())
        for name in ['run_verification.py', 'verify_task.py', 'build_context.py', 'prepare_agent.py']:
            self.assertTrue((SKILL / 'assets/scaffold/AI_KNOWLEDGE/tools' / name).is_file())

    def test_native_plan_validator_rejects_traversal_and_unreviewed_resource(self):
        plan = copy.deepcopy(self.plan()); plan['files'][0]['target'] = '../outside.md'
        self.assertTrue(plan_errors(plan))
        plan = copy.deepcopy(self.plan()); plan['files'][0]['source'] = 'assets/missing.md'
        self.assertTrue(plan_errors(plan))

    def test_native_plan_validator_rejects_required_runtime_or_overwrite(self):
        plan = copy.deepcopy(self.plan()); plan['runtime_dependencies'] = ['python']
        self.assertTrue(plan_errors(plan))
        plan = copy.deepcopy(self.plan()); plan['preserve_existing'] = False
        self.assertTrue(plan_errors(plan))


if __name__ == '__main__': unittest.main()
