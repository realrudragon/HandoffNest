#!/usr/bin/env python3
"""Compare current scoped source metadata with retained source_snapshot.json."""
from pathlib import Path
import json
import sys
from knowledge_inventory import collect


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    vault = Path(__file__).resolve().parents[1]
    root = vault.parent
    before = json.loads((vault / 'source_snapshot.json').read_text(encoding='utf-8'))
    expected = {x['path']: x['sha256'] for x in before['files']}
    current = {x['path']: x['sha256'] for x in collect(root)}
    result = {'added': sorted(current.keys() - expected.keys()),
              'missing': sorted(expected.keys() - current.keys()),
              'changed': sorted(p for p in current.keys() & expected.keys() if current[p] != expected[p])}
    stale = any(result.values())
    result['status'] = 'stale' if stale else 'current'
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if stale else 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({'status': 'error', 'error': str(exc)}))
        raise SystemExit(2)
