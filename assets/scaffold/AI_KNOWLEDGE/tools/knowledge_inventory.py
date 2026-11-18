"""Metadata-only inventory; no source bodies, credentials or symlink traversal."""
from pathlib import Path
import hashlib
import json
import os
import stat

EXCLUDED = {'.git', 'AI_KNOWLEDGE', 'node_modules', 'vendor', 'system', 'third_party',
            'modules0', '.venv', 'venv', '__pycache__', 'cache', 'logs', 'dist', 'build'}
SUFFIXES = {'.php', '.js', '.ts', '.tsx', '.jsx', '.vue', '.py', '.go', '.c', '.h',
            '.cpp', '.rs', '.rb', '.java', '.cs', '.sql', '.json'}
AGENT_OUTPUTS = {'AGENTS.md', 'CLAUDE.md', 'GEMINI.md', '.cursor/rules/ai-knowledge.mdc', '.github/copilot-instructions.md'}
catalog_path = Path(__file__).with_name('stack_rules.json')
if catalog_path.is_file():
    # Reuse declarative language coverage; no source/config/plugin execution.
    catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
    SUFFIXES.update(ext for exts in catalog.get('language_extensions', {}).values() for ext in exts)


def collect(root):
    root = Path(root).resolve()

    def within_scope(path):
        attributes = getattr(path.lstat(), 'st_file_attributes', 0)
        return (not path.is_symlink() and
                not (attributes & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)) and
                path.resolve().is_relative_to(root))

    rows = []
    for folder, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED and not d.startswith('ExcelLb')
                         and within_scope(Path(folder) / d))
        for name in sorted(files):
            path = Path(folder) / name
            if path.relative_to(root).as_posix() in AGENT_OUTPUTS:
                continue
            if not within_scope(path) or path.suffix.lower() not in SUFFIXES:
                continue
            if name.lower() in ('auth.json', 'credentials.json', 'secrets.json'):
                continue
            data = path.read_bytes()
            rows.append({'path': path.relative_to(root).as_posix(), 'bytes': len(data),
                         'lines': len(data.splitlines()), 'sha256': hashlib.sha256(data).hexdigest()})
    return rows
