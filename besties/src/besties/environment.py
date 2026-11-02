"""Explicit operator configuration; never public rendering input or shell code."""
from dataclasses import dataclass, field
from functools import partial
import os
from pathlib import Path
import re
from urllib.parse import urlsplit
from .model import require, identifier, public_url

SETTINGS = ('BESTIES_ENV_VERSION', 'BESTIES_FACTS_PATH', 'BESTIES_STUDY_DIR',
            'BESTIES_OUTPUT_DIR', 'BESTIES_PROJECT_PREFIX', 'BESTIES_VERCEL_SCOPE',
            'BESTIES_NETLIFY_TEAM', 'BESTIES_LAYOUT_LOCK_PATH',
            'BESTIES_VERCEL_BASELINE_URL', 'BESTIES_NETLIFY_BASELINE_URL',
            'BESTIES_VERCEL_PERSONA_URL_TEMPLATE', 'BESTIES_NETLIFY_PERSONA_URL_TEMPLATE',
            'BESTIES_PERSONA_FIRST', 'BESTIES_PERSONA_LAST')
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
        for key in ('BESTIES_FACTS_PATH', 'BESTIES_STUDY_DIR', 'BESTIES_OUTPUT_DIR', 'BESTIES_LAYOUT_LOCK_PATH'):
            require(Path(values[key]).is_absolute() and not re.search(r'[\x00-\x1f`$]', values[key]), 'Absolute literal paths required')
        study = Path(values['BESTIES_STUDY_DIR']).resolve()
        output = Path(values['BESTIES_OUTPUT_DIR']).resolve()
        facts = Path(values['BESTIES_FACTS_PATH']).resolve()
        require(output != study and output not in study.parents, 'Output cannot contain the private study')
        require(output != facts and output not in facts.parents, 'Output cannot contain private facts input')
        lock = Path(values['BESTIES_LAYOUT_LOCK_PATH']).resolve()
        require(output != lock and output not in lock.parents, 'Output cannot contain private layout locks')
        require(values['BESTIES_PERSONA_FIRST'].isdigit() and values['BESTIES_PERSONA_LAST'].isdigit(), 'Integer range required')
        first, last = int(values['BESTIES_PERSONA_FIRST']), int(values['BESTIES_PERSONA_LAST'])
        require(1 <= first <= last <= 100, 'Unsupported presentation range')
        origins = set()
        for provider in TOKENS:
            key = 'BESTIES_' + provider.upper()
            template = values[key + '_PERSONA_URL_TEMPLATE']
            require(template.count('{number}') == 1 and
                    not any(c in template.replace('{number}', '') for c in '{}'), 'One numeric URL placeholder required')
            urls = [values[key + '_BASELINE_URL']] + [template.replace('{number}', str(n)) for n in range(first, last + 1)]
            for url in urls:
                public_url(url); parsed = urlsplit(url)
                require(parsed.path in ('', '/') and parsed.port in (None, 443) and
                        not any(c.isspace() for c in url), 'Public origin required')
                origin = url.rstrip('/')
                require(origin not in origins, 'Duplicate publication origin')
                origins.add(origin)
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

    def site_url(self, provider, role, number=None):
        require(provider in TOKENS and role in ('baseline', 'persona'), 'Invalid publication role')
        prefix = 'BESTIES_' + provider.upper()
        if role == 'baseline':
            require(number is None, 'Baseline has no presentation number')
            return self.values[prefix + '_BASELINE_URL'].rstrip('/')
        require(type(number) is int and int(self.values['BESTIES_PERSONA_FIRST']) <= number <= int(self.values['BESTIES_PERSONA_LAST']), 'Presentation number outside configured range')
        return self.values[prefix + '_PERSONA_URL_TEMPLATE'].replace('{number}', str(number)).rstrip('/')

    def summary(self):
        return {'valid': True, 'schema_version': 1, 'values_redacted': True,
                'authentication': {host: 'environment' if self.values.get(key) else 'cli-login'
                                   for host, key in TOKENS.items()}}
