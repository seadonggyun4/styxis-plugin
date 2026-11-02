"""Release packaging and recoverable, explicit deployment boundaries.

Adapters receive only generated public artifacts. Authentication and project creation
stay with the official provider CLI; private source inputs are never uploaded.
"""
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Protocol
from .model import require, identifier
from .resources import digest, encoded


def write_bundle(files, output):
    output = Path(output)
    require(all(not Path(p).is_absolute() and '..' not in Path(p).parts for p in files), 'Invalid artifact path')
    output.mkdir(parents=True, exist_ok=False)
    for name, raw in files.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)


def verify_files(files, directory):
    root = Path(directory)
    require(root.is_dir() and not root.is_symlink(), 'Invalid bundle directory')
    paths = list(root.rglob('*'))
    require(not any(p.is_symlink() for p in paths), 'Symlink in bundle')
    require({p.relative_to(root).as_posix() for p in paths if p.is_file()} == set(files), 'Unexpected artifacts')
    require(all((root / k).read_bytes() == v for k, v in files.items()), 'Bundle drift')
    return {'passed': True, 'files': len(files)}


def hosting_files(files, provider):
    """Return public hosting configuration, separate from canonical release hashes."""
    require(provider in ('vercel', 'netlify'), 'Unsupported hosting adapter')
    result = dict(files)
    if provider == 'vercel':
        result.pop('_headers')
        headers = [{'source': '/(.*)', 'headers': [{'key': 'X-Content-Type-Options', 'value': 'nosniff'}]}]
        for name, mime in [('facts.json', 'application/json'), ('facts.md', 'text/markdown'), ('release.json', 'application/json')]:
            headers.append({'source': '/' + name, 'headers': [
                {'key': 'Content-Type', 'value': mime + '; charset=utf-8'}, {'key': 'X-Robots-Tag', 'value': 'noindex'}]})
        result['vercel.json'] = encoded({'framework': None, 'buildCommand': None, 'outputDirectory': '.', 'headers': headers})
    else:
        result['netlify.toml'] = b'[build]\n  publish = "."\n'
    return result


class Publisher(Protocol):
    def deploy(self, directory: Path) -> str:
        """Publish to a preselected project and return its deployment identifier."""


@dataclass
class ReleaseJournal:
    """Private append-only receipts. An interrupted attempt requires reconciliation.

    This journal is single-writer. Keep it outside public source control.
    """
    path: Path

    def rows(self):
        return [json.loads(line) for line in self.path.read_text().splitlines()] if self.path.exists() else []

    def append(self, row):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        import os
        from datetime import datetime, timezone
        with os.fdopen(os.open(self.path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600), 'a') as f:
            f.write(json.dumps({**row, 'at': datetime.now(timezone.utc).isoformat()}) + '\n')
            f.flush(); os.fsync(f.fileno())


def publish(files, directory, target, adapter: Publisher, journal: ReleaseJournal, verify, layout_lock=None):
    """No retries on uncertain external effects; inspect/reconcile them first.

    Rollback uses this same function with a retained, verified prior bundle.
    Provider success alone is insufficient: GET verification must pass too.
    """
    identifier(target)
    verify_files(files, directory)
    if layout_lock is not None:
        from .layout import verify_layout
        verify_layout(files, layout_lock)
    release = digest(encoded({k: digest(v) for k, v in sorted(files.items())}))
    prior = [r for r in journal.rows() if r['target'] == target]
    require(not prior or prior[-1]['status'] not in ('started', 'uncertain'), 'Reconcile prior deployment before retry')
    row = {'target': target, 'release': release}
    journal.append({**row, 'status': 'started'})
    try:
        deployment = adapter.deploy(Path(directory))
    except Exception as exc:
        journal.append({**row, 'status': 'uncertain', 'error_type': type(exc).__name__})
        return {'target': target, 'status': 'uncertain', 'passed': False}
    try:
        verified = verify()
        passed = verified.get('passed') is True
    except Exception:
        passed = False
    status = 'verified' if passed else 'verification-failed'
    journal.append({**row, 'status': status, 'deployment': deployment})
    return {'target': target, 'status': status, 'passed': passed}


def batch_status(results):
    require(bool(results) and len({r['target'] for r in results}) == len(results), 'Unique batch targets required')
    return {'passed': all(r['passed'] is True for r in results), 'targets': results,
            'verified': sum(r['passed'] is True for r in results), 'total': len(results)}
