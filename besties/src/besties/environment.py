"""Explicit operator configuration; never public rendering input or shell code."""
from dataclasses import dataclass, field
from functools import partial
import os
from pathlib import Path
import re
from .model import require, identifier

SETTINGS = ('BESTIES_ENV_VERSION', 'BESTIES_FACTS_PATH', 'BESTIES_STUDY_DIR',
            'BESTIES_OUTPUT_DIR', 'BESTIES_PROJECT_PREFIX', 'BESTIES_VERCEL_SCOPE',
            'BESTIES_NETLIFY_TEAM')
TOKENS = {'vercel': 'VERCEL_TOKEN', 'netlify': 'NETLIFY_AUTH_TOKEN'}
ALLOWED = set(SETTINGS) | set(TOKENS.values())
PROCESS_KEYS = ('PATH', 'HOME', 'USER', 'LOGNAME', 'SHELL', 'TMPDIR', 'TMP', 'TEMP',
                'LANG', 'LC_ALL', 'SYSTEMROOT', 'COMSPEC', 'APPDATA', 'LOCALAPPDATA',
                'XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'XDG_CACHE_HOME',
                'NODE_EXTRA_CA_CERTS', 'SSL_CERT_FILE', 'SSL_CERT_DIR',
                'HTTPS_PROXY', 'HTTP_PROXY', 'NO_PROXY')


def process_environment(provider, source=None):
    require(provider in TOKENS, 'Unsupported provider')
    source = os.environ if source is None else source
    result = {k: source[k] for k in PROCESS_KEYS if k in source}
    token = TOKENS[provider]
    if source.get(token): result[token] = source[token]
    return result


@dataclass(frozen=True)
class OperatorEnvironment:
    values: dict = field(repr=False)

    @classmethod
    def load(cls, path, environ=None):
        path = Path(path)
        require(path.is_file() and not path.is_symlink(), 'Regular environment file required')
        require(path.stat().st_size <= 65536, 'Environment file too large')
        if os.name == 'posix':
            require(path.stat().st_mode & 0o077 == 0, 'Environment file must be private (0600)')
        values = {}
        for line in path.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if not line or line.startswith('#'): continue
            require('=' in line, 'Expected KEY=value')
            key, value = line.split('=', 1); key = key.strip(); value = value.strip()
            require(key in ALLOWED and key not in values, 'Unknown or duplicate environment setting')
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            require(not re.search(r'[\x00-\x1f`$]', value), 'Shell interpolation and control characters are unsupported')
            values[key] = value
        source = os.environ if environ is None else environ
        values.update({k: source[k] for k in ALLOWED if k in source})
        require(all(isinstance(values.get(k), str) and values[k].strip() for k in SETTINGS), 'Required environment setting missing')
        require(values['BESTIES_ENV_VERSION'] == '1', 'Unsupported environment version')
        for key in ('BESTIES_PROJECT_PREFIX', 'BESTIES_VERCEL_SCOPE', 'BESTIES_NETLIFY_TEAM'):
            identifier(values[key])
        for key in ('BESTIES_FACTS_PATH', 'BESTIES_STUDY_DIR', 'BESTIES_OUTPUT_DIR'):
            require(Path(values[key]).is_absolute() and not re.search(r'[\x00-\x1f`$]', values[key]), 'Absolute literal paths required')
        study = Path(values['BESTIES_STUDY_DIR']).resolve()
        output = Path(values['BESTIES_OUTPUT_DIR']).resolve()
        facts = Path(values['BESTIES_FACTS_PATH']).resolve()
        require(output != study and output not in study.parents, 'Output cannot contain the private study')
        require(output != facts and output not in facts.parents, 'Output cannot contain private facts input')
        return cls(values)

    def setting(self, name):
        require(name in SETTINGS, 'Only noncredential settings can be read through setting()')
        return self.values[name]

    def runner(self, provider):
        from .hosting import execute
        env = process_environment(provider)
        token = TOKENS[provider]
        # An explicit empty override suppresses inherited token authentication.
        env.pop(token, None)
        if self.values.get(token): env[token] = self.values[token]
        return partial(execute, environment=env)

    def summary(self):
        return {'valid': True, 'schema_version': 1, 'values_redacted': True,
                'authentication': {host: 'environment' if self.values.get(key) else 'cli-login'
                                   for host, key in TOKENS.items()}}
