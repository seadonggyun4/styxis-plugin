import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from besties.environment import OperatorEnvironment, process_environment
from besties.hosting import StaticPublisher
from besties.model import ContractError


class EnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = self.root / '.env.local'
        self.content = '\n'.join(['BESTIES_ENV_VERSION=1', f'BESTIES_FACTS_PATH={self.root}/study/facts.json',
            f'BESTIES_STUDY_DIR={self.root}/study', f'BESTIES_OUTPUT_DIR={self.root}/output',
            'BESTIES_PROJECT_PREFIX=sample-geo-no', 'BESTIES_VERCEL_SCOPE=sample-team',
            'BESTIES_NETLIFY_TEAM=other-team', f'BESTIES_LAYOUT_LOCK_PATH={self.root}/layout.json',
            'BESTIES_VERCEL_BASELINE_URL=https://base.example.org', 'BESTIES_NETLIFY_BASELINE_URL=https://base-mirror.example.org',
            'BESTIES_VERCEL_PERSONA_URL_TEMPLATE=https://site-{number}.example.org',
            'BESTIES_NETLIFY_PERSONA_URL_TEMPLATE=https://mirror-{number}.example.org',
            'BESTIES_PERSONA_FIRST=1', 'BESTIES_PERSONA_LAST=16', 'VERCEL_TOKEN=', 'NETLIFY_AUTH_TOKEN='])
        self.write(self.content)

    def write(self, content):
        self.path.write_text(content); self.path.chmod(0o600)

    def test_defaults_precedence_and_no_process_mutation(self):
        before = dict(os.environ)
        env = OperatorEnvironment.load(self.path, {'BESTIES_PROJECT_PREFIX': 'another-product'})
        self.assertEqual(env.setting('BESTIES_PROJECT_PREFIX'), 'another-product')
        self.assertEqual(env.summary()['authentication']['vercel'], 'cli-login')
        self.assertEqual(dict(os.environ), before)
        with self.assertRaises(ContractError): env.setting('VERCEL_TOKEN')
        self.assertEqual(env.site_url('vercel', 'persona', 16), 'https://site-16.example.org')
        self.assertEqual(env.site_url('netlify', 'baseline'), 'https://base-mirror.example.org')
        with self.assertRaises(ContractError): env.site_url('vercel', 'persona', 17)

    def test_url_collisions_and_template_expansion_fail_closed(self):
        for replacement in ('https://base.example.org', 'https://{unknown}.example.org', 'https://site-{number}.example.org/path'):
            self.write(self.content.replace('https://site-{number}.example.org', replacement))
            with self.assertRaises(ContractError): OperatorEnvironment.load(self.path, {})

    def test_unknown_duplicate_shell_expression_and_missing_values_rejected(self):
        for change in ('\nUNKNOWN=x', '\nBESTIES_ENV_VERSION=1', '\nBAD=$(touch marker)'):
            self.write(self.content + change)
            with self.assertRaises(ContractError): OperatorEnvironment.load(self.path, {})
        self.write(self.content.replace('sample-team', '$(touch marker)'))
        with self.assertRaises(ContractError): OperatorEnvironment.load(self.path, {})
        self.assertFalse((self.root/'marker').exists())
        self.write(self.content.replace('BESTIES_VERCEL_SCOPE=sample-team', 'BESTIES_VERCEL_SCOPE='))
        with self.assertRaises(ContractError): OperatorEnvironment.load(self.path, {})

    def test_permissions_symlinks_and_unsafe_output_rejected(self):
        self.path.chmod(0o644)
        with self.assertRaises(ContractError): OperatorEnvironment.load(self.path, {})
        self.path.chmod(0o600)
        link = self.root/'link'; link.symlink_to(self.path)
        with self.assertRaises(ContractError): OperatorEnvironment.load(link, {})
        self.write(self.content.replace(f'{self.root}/output', str(self.root)))
        with self.assertRaises(ContractError): OperatorEnvironment.load(self.path, {})

    def test_provider_credential_isolation_and_no_argument_leak(self):
        secrets = {'VERCEL_TOKEN': 'vercel-sentinel', 'NETLIFY_AUTH_TOKEN': 'netlify-sentinel', 'UNRELATED_SECRET': 'excluded'}
        env = OperatorEnvironment.load(self.path, secrets)
        self.assertNotIn('sentinel', repr(env))
        self.assertNotIn('sentinel', json.dumps(env.summary()))
        with patch('besties.hosting.execute') as execute:
            execute.return_value = {'status': 'ok', 'deployment': {'readyState': 'READY', 'id': 'receipt'}}
            runner = env.runner('vercel')
            StaticPublisher('vercel', ('official-cli',), 'project', 'team', False, runner).deploy(self.root/'empty')
            args, kwargs = execute.call_args
            self.assertNotIn('sentinel', repr(args))
            self.assertEqual(kwargs['environment']['VERCEL_TOKEN'], 'vercel-sentinel')
            self.assertNotIn('NETLIFY_AUTH_TOKEN', kwargs['environment'])
            self.assertNotIn('UNRELATED_SECRET', kwargs['environment'])
        self.assertNotIn('VERCEL_TOKEN', process_environment('netlify', secrets))

    def test_all_environment_variants_blocked_from_upload(self):
        for name in ('.env', '.env.production', '.env.template', 'env-sample'):
            target = self.root/'bundle'; target.mkdir(exist_ok=True)
            p=target/name; p.write_text('sentinel')
            with self.assertRaises(ContractError): StaticPublisher('netlify', ('cli',), 'project', 'team').deploy(target)
            p.unlink()

    def test_cli_validation_redacts_values(self):
        from besties.cli import main
        output = io.StringIO()
        with patch.dict(os.environ, {'VERCEL_TOKEN': 'private-sentinel'}), contextlib.redirect_stdout(output):
            self.assertEqual(main(['validate-environment', str(self.path)]), 0)
        self.assertNotIn('private-sentinel', output.getvalue())
        self.assertNotIn(str(self.root), output.getvalue())
