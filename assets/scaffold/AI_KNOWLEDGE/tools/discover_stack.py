#!/usr/bin/env python3
"""Bounded, read-only stack recognition. Signals are not semantic/runtime proof."""
import argparse
from collections import Counter
import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import xml.etree.ElementTree as ET

from work_support import json_write, local_path, now, redact, safe_input

EXCLUDED = {'.git', 'AI_KNOWLEDGE', 'node_modules', 'vendor', 'system', 'third_party',
            '.venv', 'venv', '__pycache__', 'dist', 'build', '.next', '.nuxt', 'coverage',
            'logs', 'cache', '.cache', '.idea', '.gradle', 'target', 'bin', 'obj'}
MANIFESTS = {'package.json', 'composer.json', 'pyproject.toml', 'requirements.txt', 'requirements.in',
             'Cargo.toml', 'go.mod', 'Gemfile', 'pom.xml', 'build.gradle', 'build.gradle.kts', 'pubspec.yaml'}
SOURCE_SIGNALS = {'.css', '.scss', '.sass', '.less', '.html', '.htm', '.php', '.phtml', '.vue', '.svelte', '.astro', '.jsx', '.tsx'}
MANAGERS = {'npm', 'composer', 'pypi', 'cargo', 'go', 'gem', 'maven', 'nuget', 'pub'}
CATEGORIES = {'frontend', 'backend', 'css', 'ui', 'build', 'test', 'data', 'mobile', 'desktop', 'infra'}


def registry(path):
    raw = path.read_bytes()
    value = json.loads(raw.decode('utf-8-sig'))
    if not isinstance(value, dict) or value.get('protocol_version') != 1 or not isinstance(value.get('rules'), list):
        raise ValueError('Invalid signature registry protocol/rules')
    ids = set()
    for row in value['rules']:
        if not isinstance(row, dict) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,63}', row.get('id', '')) or row['id'] in ids:
            raise ValueError('Registry needs unique safe rule ids')
        ids.add(row['id'])
        if not isinstance(row.get('label'), str) or not row['label'] or row.get('category') not in CATEGORIES:
            raise ValueError('Registry needs label/category')
        packages, markers = row.get('packages', {}), row.get('markers', [])
        if not isinstance(packages, dict) or not isinstance(markers, list):
            raise ValueError('Registry packages/markers malformed')
        for manager, names in packages.items():
            if manager not in MANAGERS or not isinstance(names, list) or any(not isinstance(n, str) or not re.fullmatch(r'[A-Za-z0-9@_.:/+-]{1,180}', n) for n in names):
                raise ValueError('Registry package names/manager malformed')
        for marker in markers:
            if not isinstance(marker, str) or not marker or marker.startswith('/') or '..' in PurePosixPath(marker).parts or '\\' in marker or ':' in marker:
                raise ValueError('Unsafe registry marker')
    return value, hashlib.sha256(raw).hexdigest()


def normalized(manager, name):
    return re.sub(r'[-_.]+', '-', name).lower() if manager == 'pypi' else name.lower() if manager == 'nuget' else name


def version(value):
    text = str(value).strip()
    if (text == '*' or re.search(r'\d', text)) and re.fullmatch(r'[A-Za-z0-9.*^~<>=!|, +\-]{1,80}', text):
        return text
    return 'non-version-spec' if text else 'unspecified'


def dependencies(name, text, warnings):
    """Parse declarations only; includes/build scripts/interpolation are never executed."""
    rows, scripts = [], []
    def add(manager, package, constraint='', section='dependencies'):
        if isinstance(package, str) and re.fullmatch(r'[A-Za-z0-9@_.:/+-]{1,180}', package):
            rows.append((manager, package, version(constraint), section))
    if name in ('package.json', 'composer.json'):
        data = json.loads(text)
        if not isinstance(data, dict): raise ValueError('Manifest object required')
        sections = ('dependencies', 'devDependencies', 'peerDependencies', 'optionalDependencies') if name == 'package.json' else ('require', 'require-dev')
        for section in sections:
            values = data.get(section, {})
            if not isinstance(values, dict): raise ValueError('Dependency section object required')
            for package, constraint in values.items():
                if not isinstance(constraint, str): raise ValueError('Dependency constraint string required')
                add('npm' if name == 'package.json' else 'composer', package, constraint, section)
        if isinstance(data.get('scripts'), dict): scripts = sorted(str(x) for x in data['scripts'])
    elif name in ('pyproject.toml', 'Cargo.toml'):
        try: import tomllib
        except ImportError:
            warnings.append('TOML parsing unavailable before Python 3.11; inspect manifest manually')
            return rows, scripts
        data = tomllib.loads(text)
        if name == 'pyproject.toml':
            sections = [('project.dependencies', data.get('project', {}).get('dependencies', []))]
            for k, v in data.get('project', {}).get('optional-dependencies', {}).items(): sections.append(('project.optional-dependencies.' + k, v))
            for section, values in sections:
                for spec in values:
                    m = re.match(r'\s*([A-Za-z0-9_.-]+)(?:\[[^\]]+\])?\s*(.*)', spec)
                    if m: add('pypi', m[1], m[2].split(';')[0], section)
            poetry = data.get('tool', {}).get('poetry', {})
            groups = [('tool.poetry.dependencies', poetry.get('dependencies', {}))]
            for k, v in poetry.get('group', {}).items(): groups.append(('tool.poetry.group.' + k, v.get('dependencies', {})))
            for section, values in groups:
                for package, spec in values.items():
                    if package != 'python': add('pypi', package, spec.get('version', '') if isinstance(spec, dict) else spec, section)
        else:
            groups = [(k, data.get(k, {})) for k in ('dependencies', 'dev-dependencies', 'build-dependencies')]
            for target, config in data.get('target', {}).items():
                groups += [('target.' + target + '.' + k, config.get(k, {})) for k in ('dependencies', 'dev-dependencies', 'build-dependencies')]
            for section, values in groups:
                for package, spec in values.items():
                    add('cargo', spec.get('package', package) if isinstance(spec, dict) else package,
                        spec.get('version', '') if isinstance(spec, dict) else spec, section)
            if data.get('workspace', {}).get('dependencies'):
                warnings.append('Cargo workspace dependency inheritance needs source/lock review')
    elif name in ('requirements.txt', 'requirements.in'):
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith('#'): continue
            if line.startswith('-'):
                warnings.append('requirements include/options not followed; inspect included files manually'); continue
            m = re.match(r'([A-Za-z0-9_.-]+)(?:\[[^\]]+\])?\s*(.*)', line)
            if m: add('pypi', m[1], m[2].split(';')[0].split('#')[0])
    elif name == 'go.mod':
        inside = False
        for line in text.splitlines():
            line = line.split('//')[0].strip()
            if line == 'require (': inside = True; continue
            if line == ')': inside = False; continue
            m = re.match(r'(?:require\s+)?([\w.\-/]+)\s+(v[^\s]+)', line)
            if m and (inside or line.startswith('require ')): add('go', m[1], m[2])
    elif name == 'Gemfile':
        for m in re.finditer(r'^\s*gem\s+[\'"]([^\'"]+)[\'"](?:\s*,\s*[\'"]([^\'"]+)[\'"])?', text, re.M): add('gem', m[1], m[2] or '')
        warnings.append('Gemfile static gem literals only; Ruby DSL/groups/includes not evaluated')
    elif name == 'pom.xml' or name.lower().endswith(('.csproj', '.fsproj', '.vbproj')):
        data = ET.fromstring(text)
        def tag(element): return element.tag.rsplit('}', 1)[-1]
        if name == 'pom.xml':
            for elem in data.iter():
                if tag(elem) != 'dependency': continue
                values = {tag(x): x.text or '' for x in elem}
                if values.get('groupId') and values.get('artifactId'):
                    add('maven', values['groupId'] + ':' + values['artifactId'], values.get('version', ''))
        else:
            if data.attrib.get('Sdk'): add('nuget', data.attrib['Sdk'], '', 'Project.Sdk')
            for elem in data.iter():
                if tag(elem) in ('PackageReference', 'FrameworkReference'):
                    child_version = next((x.text for x in elem if tag(x) == 'Version'), '')
                    add('nuget', elem.attrib.get('Include', elem.attrib.get('Update', '')), elem.attrib.get('Version', child_version or ''), tag(elem))
    elif name in ('build.gradle', 'build.gradle.kts'):
        text = re.sub(r'([\'"](?:\\.|[^\'"\\])*[\'"])|(/\*[\s\S]*?\*/|//[^\r\n]*)',
                      lambda m: m[1] if m[1] else '\n' * m[0].count('\n') + ' ', text)
        for m in re.finditer(r'(?:^|[;{}])\s*(?:implementation|api|compileOnly|runtimeOnly|testImplementation|testRuntimeOnly|annotationProcessor|kapt)\s*\(?\s*[\'"]([\w.-]+:[\w.-]+):([^\'"\s]+)[\'"]', text, re.M):
            add('maven', m[1], m[2], 'static-gradle-literal')
        warnings.append('Gradle static coordinates only; plugins/catalogs/interpolation not evaluated')
    elif name == 'pubspec.yaml':
        section = None
        for line in text.splitlines():
            m = re.match(r'^(dependencies|dev_dependencies):\s*(?:#.*)?$', line)
            if m: section = m[1]; continue
            if line and not line[0].isspace() and not line.startswith('#'): section = None
            m = re.match(r'^  ([A-Za-z0-9_]+):\s*([^#]*)', line)
            if section and m: add('pub', m[1], m[2].strip().strip('\'"'), section)
        warnings.append('pubspec static two-space dependency keys only; YAML anchors/includes not expanded')
    return rows, scripts


def discover(root, custom_rules=None, max_files=20000, max_depth=10, max_bytes=16777216, max_directories=5000):
    root = Path(root).resolve()
    if not root.is_dir(): raise ValueError('Project root must exist')
    if any(type(x) is not int or x < 1 for x in (max_files, max_depth, max_bytes, max_directories)):
        raise ValueError('Scan limits must be positive integers')
    catalog, catalog_sha = registry(Path(__file__).with_name('stack_rules.json'))
    rules = {r['id']: r for r in catalog['rules']}
    custom_sha = None
    if custom_rules:
        extra, custom_sha = registry(safe_input(root, custom_rules))
        for row in extra['rules']:
            if row['id'] in rules: raise ValueError('Custom rule id collides with bundled rule')
            rules[row['id']] = row
    package_index = {}
    for rule in rules.values():
        for manager, names in rule.get('packages', {}).items():
            for name in names: package_index.setdefault((manager, normalized(manager, name)), []).append(rule)
    languages_by_ext = {ext: label for label, exts in catalog.get('language_extensions', {}).items() for ext in exts}
    files, warnings, excluded = [], [], Counter()
    truncated = False
    def inside(path):
        attributes = getattr(path.lstat(), 'st_file_attributes', 0)
        return not path.is_symlink() and not attributes & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400) and path.resolve().is_relative_to(root)
    directories_visited = 0
    for folder, dirs, names in os.walk(root, followlinks=False):
        if directories_visited >= max_directories:
            truncated = True; break
        directories_visited += 1
        relative = Path(folder).relative_to(root)
        kept = []
        for d in sorted(dirs):
            p = Path(folder) / d
            if d in EXCLUDED or d.startswith('ExcelLb') or not inside(p): excluded[d] += 1
            elif len(relative.parts) >= max_depth: truncated = True
            else: kept.append(d)
        dirs[:] = kept
        for name in sorted(names):
            p = Path(folder) / name
            if name.lower().startswith('.env') or name.lower() in ('credentials.json', 'secrets.json', 'auth.json') or p.suffix.lower() in ('.pem', '.key', '.p12') or not inside(p): continue
            if len(files) == max_files:
                truncated = True; break
            files.append(p)
        if len(files) == max_files and (dirs or len(names) > 0):
            # Hitting the cap is conservative: no exhaustive claim even at exact boundary.
            truncated = True; break
    def manifest(path): return path.name in MANIFESTS or path.suffix.lower() in ('.csproj', '.fsproj', '.vbproj')
    manifests = [p for p in files if manifest(p)]
    workspace_paths = {p.parent for p in manifests}
    def owner(path):
        matches = [p for p in workspace_paths if path.is_relative_to(p)]
        parent = max(matches, key=lambda p: len(p.parts)) if matches else root
        return parent.relative_to(root).as_posix()
    content, used = {}, 0
    def read(path):
        nonlocal used, truncated
        if path in content: return content[path]
        size = path.stat().st_size
        if size > 524288 or used + size > max_bytes:
            truncated = True; warnings.append('Read budget exceeded: ' + path.relative_to(root).as_posix()); return None
        raw = path.read_bytes(); used += len(raw)
        if len(raw) > 524288 or used > max_bytes:
            truncated = True; return None
        content[path] = (raw.decode('utf-8-sig', errors='replace'), hashlib.sha256(raw).hexdigest())
        return content[path]
    detections, unknown, scripts, manifests_read = {}, [], [], []
    def emit(rule, path, kind, constraint='unspecified', section='static'):
        workspace = owner(path); key = (rule['id'], workspace)
        row = detections.setdefault(key, {'id': rule['id'], 'label': rule['label'], 'category': rule['category'],
                                          'workspace': workspace, 'confidence': 'candidate', 'evidence': []})
        if kind == 'declared_dependency': row['confidence'] = 'declared'
        sha = content[path][1] if path in content else None
        item = {'path': path.relative_to(root).as_posix(), 'sha256': sha, 'kind': kind,
                'section': section, 'version_constraint': constraint}
        if item not in row['evidence']: row['evidence'].append(item)
    for path in manifests:
        data = read(path)
        if data is None: continue
        start_warnings = len(warnings)
        try: rows, names = dependencies(path.name, data[0], warnings)
        except (ValueError, TypeError, AttributeError, KeyError, ET.ParseError):
            warnings.append('Malformed/unsupported manifest shape: ' + path.relative_to(root).as_posix()); truncated = True; continue
        manifests_read.append({'path': path.relative_to(root).as_posix(), 'sha256': data[1], 'workspace': owner(path)})
        if names: scripts.append({'path': path.relative_to(root).as_posix(), 'workspace': owner(path), 'names': names})
        for manager, name, constraint, section in rows:
            matches = package_index.get((manager, normalized(manager, name)), [])
            for rule in matches: emit(rule, path, 'declared_dependency', constraint, section)
            if not matches: unknown.append({'ecosystem': manager, 'name': name, 'workspace': owner(path), 'source': path.relative_to(root).as_posix()})
        if len(warnings) > start_warnings:
            warnings[start_warnings:] = [path.relative_to(root).as_posix() + ': ' + x for x in warnings[start_warnings:]]
    for path in files:
        rel = path.relative_to(root).as_posix()
        for rule in rules.values():
            if any(PurePosixPath(rel).match(pattern) for pattern in rule.get('markers', [])):
                read(path); emit(rule, path, 'path_marker')
        if path.suffix.lower() not in SOURCE_SIGNALS or '.min.' in path.name: continue
        data = read(path)
        if data is None: continue
        # Comments are discarded for static CSS import detection. No source text/URL retained.
        text = re.sub(r'/\*.*?\*/', '', data[0], flags=re.S)
        text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
        literals = re.findall(r'@import\s+(?:url\(\s*)?[\'"]([^\'"\r\n]+)[\'"]', text)
        for literal in literals:
            if literal.startswith(('http:', 'https:', '//')): continue
            package = '/'.join(literal.split('/')[:2]) if literal.startswith('@') else literal.split('/')[0]
            for rule in package_index.get(('npm', package), []): emit(rule, path, 'static_css_import')
        if re.search(r'@tailwind\s+(?:base|components|utilities)\s*;', text): emit(rules['tailwindcss'], path, 'static_css_directive')
        for literal in re.findall(r'<(?:link|script)\b[^>]*(?:href|src)\s*=\s*[\'"]([^\'"\r\n]+)[\'"]', text, flags=re.I):
            clean = literal.split('?')[0].split('#')[0]
            for ident, marker in (('bootstrap', r'(?:^|[/@])bootstrap(?:[/.@-]|$)'), ('tailwindcss', r'(?:^|[/@])tailwindcss(?:[/.@-]|$)'),
                                  ('bulma', r'(?:^|[/@])bulma(?:[/.@-]|$)'), ('uikit', r'(?:^|[/@])uikit(?:[/.@-]|$)')):
                if re.search(marker, clean, re.I): emit(rules[ident], path, 'static_asset_reference')
    languages, unclassified = Counter(), Counter()
    for path in files:
        ext = path.suffix.lower()
        if ext in languages_by_ext: languages[languages_by_ext[ext]] += 1
        elif ext: unclassified[ext] += 1
    return {'protocol_version': 1, 'producer': 'worachote-stack-discovery/0.3', 'created_at': now(),
            'status': 'partial' if truncated else 'completed', 'understanding_status': 'discovery_only',
            'catalog_sha256': catalog_sha, 'custom_catalog_sha256': custom_sha, 'catalog_rules': len(rules),
            'detections': sorted(detections.values(), key=lambda x: (x['workspace'], x['category'], x['id'])),
            'manifests': manifests_read, 'scripts': scripts, 'languages': dict(sorted(languages.items())),
            'unknown_dependencies': unknown, 'unclassified_extensions': dict(sorted(unclassified.items())),
            'warnings': list(dict.fromkeys(warnings)),
            'coverage': {'files_enumerated': len(files), 'bytes_read': used, 'max_files': max_files, 'max_depth': max_depth,
                         'directories_visited': directories_visited, 'max_directories': max_directories,
                         'max_bytes': max_bytes, 'truncated': truncated, 'excluded_directories': dict(excluded)},
            'next_actions': ['Confirm version-specific framework docs and inspect owning source; declarations do not prove use',
                             'Fill STACK_MAP.md with entrypoints/routes/config/data/CSS/test evidence and unknowns',
                             'Resolve unknown dependencies/extensions with source and official docs or add reviewed custom rules',
                             'Discover real test commands; do not execute package scripts/config during discovery'],
            'limits': ['Static signals only, not semantic understanding, installed-version resolution or runtime verification',
                       'TOML parsing uses Python 3.11+ tomllib; earlier runtimes leave TOML pending',
                       'No lockfile/DSL execution or CSS visual/build verification; unknown files are retained as unknown',
                       'Excluded/limited/unreadable source is not inspected; review scan coverage and warnings']}


def main():
    sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project-root', default=str(Path(__file__).resolve().parents[2]))
    p.add_argument('--rules'); p.add_argument('--out')
    p.add_argument('--max-files', type=int, default=20000); p.add_argument('--max-depth', type=int, default=10)
    p.add_argument('--max-bytes', type=int, default=16777216)
    p.add_argument('--max-directories', type=int, default=5000)
    a = p.parse_args(); root = Path(a.project_root).resolve()
    try:
        out = local_path(root, a.out) if a.out else None
        if out and (not out.is_relative_to(root / 'AI_KNOWLEDGE') or out.suffix != '.json' or out.exists()):
            raise ValueError('Use a new .json report inside AI_KNOWLEDGE; existing files are preserved')
        result = discover(root, a.rules, a.max_files, a.max_depth, a.max_bytes, a.max_directories)
        # Redact diagnostic paths/metadata as a final best-effort step; no bodies or script values emitted.
        result = json.loads(redact(json.dumps(result, ensure_ascii=False)))
        if out: json_write(root, out, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if result['status'] == 'partial' else 0
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({'status': 'error', 'error': redact(str(exc))}, ensure_ascii=False)); return 2


if __name__ == '__main__': raise SystemExit(main())
