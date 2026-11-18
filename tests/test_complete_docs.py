"""README/complete-profile conformance checks, not a claim of semantic agent compliance."""
import copy
import json
from pathlib import Path, PurePosixPath
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def profile_errors(profile):
    errors = []
    if profile.get('mode') != 'native' or profile.get('runtime_dependencies') != [] or profile.get('preserve_existing') is not True:
        errors.append('Complete native profile cannot require runtimes or overwrite')
    if profile.get('base_plan') != 'assets/native/setup-plan.json': errors.append('Default starter must be retained')
    targets = set()
    for row in profile.get('files', []):
        source, target = row.get('source', ''), row.get('target', '')
        for value in (source, target):
            path = PurePosixPath(value)
            if not value or path.is_absolute() or '..' in path.parts or '\\' in value or ':' in value:
                errors.append('Unsafe complete-profile resource')
        if not source.startswith('assets/') or not target.startswith('AI_KNOWLEDGE/') or not target.endswith('.md'):
            errors.append('Native profile copies knowledge Markdown only')
        if not (ROOT / source).is_file(): errors.append('Missing complete-profile template')
        if target in targets: errors.append('Duplicate complete target')
        targets.add(target)
    return errors


class CompleteDocsTests(unittest.TestCase):
    def profile(self):
        p = ROOT / 'assets/native/complete-plan.json'
        self.assertTrue(p.is_file(), 'Explicit complete native profile is missing')
        return json.loads(p.read_text(encoding='utf-8'))

    def test_readme_covers_beginner_journey_with_stable_navigation(self):
        text = (ROOT / 'README.md').read_text(encoding='utf-8')
        for ident in ('quickstart', 'install', 'first-run', 'complete', 'outputs', 'daily-use', 'handoff',
                      'agents', 'stacks', 'verification', 'troubleshooting', 'updating', 'privacy', 'advanced'):
            self.assertIn('id="' + ident + '"', text, ident)
        self.assertIn('README.en.md', text)
        self.assertIn('ไม่ต้องติดตั้ง Python', text)
        self.assertNotIn('python scripts/bootstrap.py', text)

    def test_every_readme_toc_anchor_exists(self):
        for name in ('README.md', 'README.en.md'):
            p = ROOT / name; self.assertTrue(p.exists(), name)
            text = p.read_text(encoding='utf-8')
            ids = re.findall(r'<a\s+id="([^"]+)"', text)
            self.assertEqual(len(ids), len(set(ids)), 'Duplicate README anchor')
            for link in re.findall(r'\]\(#([^)]*)\)', text): self.assertIn(link, ids, name + '#' + link)

    def test_copyable_prompts_cover_first_run_complete_and_takeover(self):
        text = (ROOT / 'README.md').read_text(encoding='utf-8')
        blocks = re.findall(r'```text\n(.*?)\n```', text, re.S)
        self.assertTrue(any('$handoff-nest' in x and 'โดยยังไม่แก้โค้ดแอป' in x for x in blocks))
        self.assertTrue(any('$handoff-nest' in x and 'ฉบับสมบูรณ์' in x for x in blocks))
        self.assertTrue(any('AGENTS.md' in x and 'HANDOFF.md' in x for x in blocks))

    def test_complete_profile_is_safe_scriptless_and_source_bound(self):
        profile = self.profile(); self.assertEqual(profile_errors(profile), [])
        self.assertTrue(profile.get('require_evidence_or_unknowns'))
        targets = {x['target'] for x in profile['files']}
        for name in ('ARCHITECTURE', 'MODULES', 'SOURCE_MAP', 'CONFIG', 'FLOWS', 'DATA_MODEL',
                     'OPEN_QUESTIONS', 'GRAPHIFY', 'COLLABORATION', 'VERIFICATION', 'NEXT_AGENT_PROMPT'):
            self.assertIn('AI_KNOWLEDGE/' + name + '.md', targets)

    def test_complete_request_is_routed_without_changing_default_eight(self):
        skill = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
        self.assertIn('references/complete-setup.md', skill)
        default = json.loads((ROOT / 'assets/native/setup-plan.json').read_text(encoding='utf-8'))
        self.assertEqual(len(default['files']), 8)
        self.assertEqual(default['runtime_dependencies'], [])

    def test_complete_guide_prevents_empty_maps_and_fake_graphs(self):
        p = ROOT / 'references/complete-setup.md'; self.assertTrue(p.exists())
        text = p.read_text(encoding='utf-8')
        for item in ('source evidence', 'unknown', 'not_run_optional', 'not_computed', 'preserve', 'Graphify'):
            self.assertIn(item, text)

    def test_complete_targets_do_not_overlap_the_default_starter(self):
        base = json.loads((ROOT / 'assets/native/setup-plan.json').read_text(encoding='utf-8'))
        base_targets = {x['target'] for x in base['files']}
        self.assertFalse(base_targets & {x['target'] for x in self.profile()['files']})

    def test_negative_profile_errors_detect_traversal_and_runtime_requirement(self):
        profile = copy.deepcopy(self.profile()); profile['files'][0]['target'] = '../outside.md'
        self.assertTrue(profile_errors(profile))
        profile = copy.deepcopy(self.profile()); profile['runtime_dependencies'] = ['python']
        self.assertTrue(profile_errors(profile))

    def test_complete_starter_links_resolve_in_combined_targets(self):
        base = json.loads((ROOT / 'assets/native/setup-plan.json').read_text(encoding='utf-8'))
        rows = base['files'] + self.profile()['files']; targets = {x['target'] for x in rows}
        for row in rows:
            text = (ROOT / row['source']).read_text(encoding='utf-8')
            for link in re.findall(r'\]\(([^)]+)\)', text):
                if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', link) or link.startswith('#'): continue
                target = (PurePosixPath(row['target']).parent / link.split('#')[0]).as_posix()
                self.assertIn(target, targets, row['target'] + ' -> ' + link)


if __name__ == '__main__': unittest.main()
