"""Small provider-neutral helpers. Commands are trusted operator input, not sandboxed."""
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid

from verify_task import local_path, load_object, digest


def now():
    return datetime.now(timezone(timedelta(hours=7))).isoformat(timespec='seconds')


def redact(text):
    text = str(text)
    for name, value in os.environ.items():
        if len(value) >= 6 and re.search(r'PASSWORD|PASSWD|SECRET|TOKEN|API_?KEY', name, re.I):
            text = text.replace(value, '[REDACTED]')
    text = re.sub(r"(define\s*\(\s*['\"][^'\"]*(?:PASSWORD|PASSWD|SECRET|TOKEN|API_KEY)[^'\"]*['\"]\s*,\s*)(['\"])(.*?)\2",
                  lambda m: m[1] + m[2] + '[REDACTED]' + m[2], text, flags=re.I)
    text = re.sub(r"(\b(?:[A-Z0-9_]{0,96}(?:PASSWORD|PASSWD|SECRET|TOKEN|API_?KEY)[A-Z0-9_]{0,96}|Authorization)['\"]?\s*(?:=>|=|:)\s*)(['\"])(.*?)\2",
                  lambda m: m[1] + m[2] + '[REDACTED]' + m[2], text, flags=re.I)
    text = re.sub(r'(?im)((?:PASSWORD|PASSWD|SECRET|API_?KEY|ACCESS_TOKEN|Authorization)\s*[:=]\s*)(?![\'\"])([^\s,;]+)',
                  lambda m: m[1] + '[REDACTED]', text)
    text = re.sub(r'(?i)(Bearer\s+)[A-Za-z0-9._~+/=-]+', r'\1[REDACTED]', text)
    return re.sub(r'(https?://)[^\s/:]+:[^\s/@]+@', r'\1[REDACTED]@', text)


def safe_input(root, name):
    path = local_path(root, name)
    if path.name.lower().startswith('.env') or path.suffix.lower() in ('.pem', '.key', '.p12') or path.name.lower() in ('auth.json', 'credentials.json', 'secrets.json'):
        raise ValueError('Sensitive input path is not allowed: ' + str(name))
    if not path.is_file():
        raise ValueError('Input file does not exist: ' + str(name))
    return path


def load_snapshot(path):
    raw = path.read_bytes()
    value = json.loads(raw.decode('utf-8-sig'))
    if not isinstance(value, dict):
        raise ValueError('Expected JSON object')
    return value, hashlib.sha256(raw).hexdigest()


def redact_value(value):
    if isinstance(value, str):
        return redact(value)
    if isinstance(value, list):
        return [redact_value(x) for x in value]
    if isinstance(value, dict):
        return {redact(k): redact_value(v) for k, v in value.items()}
    return value


def json_write(root, path, value):
    path = local_path(root, path.relative_to(root).as_posix())
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def run_dir(root, task_path, label):
    path = task_path.parent / 'evidence' / label / uuid.uuid4().hex
    path = local_path(root, path.relative_to(root).as_posix())
    path.mkdir(parents=True, exist_ok=False)
    return path


def validate_command(root, check):
    argv = check.get('argv')
    if not isinstance(argv, list) or not argv or any(not isinstance(x, str) or not x for x in argv):
        raise ValueError('argv must be a nonempty string array, never a shell string')
    cwd = local_path(root, check.get('cwd', '.'))
    if not cwd.is_dir():
        raise ValueError('Command cwd must be an existing directory')
    timeout = check.get('timeout_seconds', 60)
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < timeout <= 3600:
        raise ValueError('timeout_seconds must be between 0 and 3600')
    return argv, cwd, timeout


def execute(argv, cwd, timeout, limit=100000):
    start = time.perf_counter()
    try:
        proc = subprocess.run(argv, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True,
                              encoding='utf-8', errors='replace', timeout=timeout, shell=False)
        output = {'exit_code': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr, 'timed_out': False}
    except subprocess.TimeoutExpired as exc:
        def decode(x):
            return x.decode('utf-8', errors='replace') if isinstance(x, bytes) else (x or '')
        output = {'exit_code': None, 'stdout': decode(exc.stdout), 'stderr': decode(exc.stderr), 'timed_out': True}
    except OSError as exc:
        output = {'exit_code': None, 'stdout': '', 'stderr': str(exc), 'timed_out': False, 'launch_error': True}
    output['elapsed_seconds'] = round(time.perf_counter() - start, 6)
    output['argv'] = [redact(x) for x in argv]
    output['cwd'] = str(cwd)
    # Assertions use full in-memory output, but no raw logs are persisted.
    output['_raw_stdout'] = output['stdout']
    output['_raw_stderr'] = output['stderr']
    for field in ('stdout', 'stderr'):
        clean = redact(output[field])
        output[field + '_redacted'] = clean != output[field]
        output[field + '_truncated'] = len(clean) > limit
        output[field] = clean[:limit]
    return output


def public_output(output):
    return {key: value for key, value in output.items() if not key.startswith('_')}
