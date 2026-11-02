import copy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from besties.domain import ProductFacts, PersonaDefinition
from besties.planning import compose
from besties.rendering import render, plan_digest
from besties.resources import ResourceSite, verify_files_live, encoded, digest
from besties.validation import validate_bundle
from besties.publishing import write_bundle, verify_files, hosting_files, publish, ReleaseJournal, batch_status
from besties.model import ContractError


def facts():
    return ProductFacts.parse({'schema_version': 1,
        'product': {'id': 'sample', 'name': 'Sample', 'category': 'Demonstration', 'version': '1'},
        'claims': [{'id': 'feature', 'statement': 'Processes a supplied file.', 'kind': 'capability', 'evidence': ['manual']},
                   {'id': 'limit', 'statement': 'Does not certify correctness.', 'kind': 'limitation', 'evidence': ['manual']}],
        'evidence': [{'id': 'manual', 'url': 'https://example.org/manual', 'label': 'Manual', 'visibility': 'public'}]})


def persona(reverse=False):
    sections = [dict(id='start', heading='Start with the task', explanation='Consider which file you want to inspect.', claim_ids=['feature']),
                dict(id='boundary', heading='Define the boundary', explanation='Decide what the result cannot establish.', claim_ids=['limit'])]
    if reverse: sections.reverse()
    return PersonaDefinition.parse(dict(schema_version=1, id='boundary-first' if reverse else 'task-first', version='1',
        language='en', audience='developers', title='Sample file inspection guide',
        description='A traceable explanation of the file inspection scope and its limitations.',
        heading='Inspect a file with a clear boundary', intro='Choose a question, then consult the documented scope.', sections=sections))


def site(mirror=False):
    return ResourceSite.parse(dict(schema_version=1, resource_url='https://mirror.example.org' if mirror else 'https://resources.example.org',
        canonical_url='https://resources.example.org', documentation_url='https://docs.example.org',
        product_url='https://example.org'), SimpleNamespace(data={'targets': []}))


class PresentationTests(unittest.TestCase):
    def test_official_cli_state_cannot_modify_bundle_working_directory(self):
        from besties.hosting import execute
        from unittest.mock import patch
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            def fake(command, **options):
                self.assertNotEqual(Path(options['cwd']), bundle)
                (Path(options['cwd'])/'provider-state').write_text('local state')
                return subprocess.CompletedProcess(command, 0, b'{"deploy_id":"receipt"}', b'')
            with patch('besties.hosting.subprocess.run', side_effect=fake):
                self.assertEqual(execute(['official-cli'], bundle)['deploy_id'], 'receipt')
            self.assertEqual(list(bundle.iterdir()), [])

    def test_standalone_cli_review_build_and_verify(self):
        from besties.cli import main
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, data in [('facts', facts().data), ('persona', persona().data), ('site', site().data)]:
                (root/(name+'.json')).write_bytes(encoded(data))
            base = [str(root/'facts.json'), '--persona', str(root/'persona.json')]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(['plan-persona', *base, '--output', str(root/'review')]), 0)
            reviewed = json.loads(output.getvalue())['plan_sha256']
            args = [*base, '--site', str(root/'site.json'), '--approved-plan-sha256', reviewed]
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(['build-persona', *args, '--output', str(root/'bundle')]), 0)
                self.assertEqual(main(['verify-persona', *args, '--directory', str(root/'bundle')]), 0)

    def test_host_adapter_uses_static_directory_and_no_shell(self):
        from besties.hosting import StaticPublisher
        commands = []
        def runner(command, directory):
            commands.append(command)
            if '--project' in command:
                return {'status': 'ok', 'deployment': {'id': 'receipt', 'readyState': 'READY', 'secret': 'not retained'}}
            return {'deploy_id': 'receipt', 'secret': 'not retained'}
        with tempfile.TemporaryDirectory() as tmp:
            for host in ('vercel', 'netlify'):
                receipt = StaticPublisher(host, ('official-cli',), 'example-project', 'example-team', True, runner).deploy(Path(tmp))
                self.assertNotIn('secret', receipt)
            self.assertIn('--no-build', commands[1])
            self.assertIn('--project', commands[0])
            (Path(tmp)/'.env.local').write_text('sentinel')
            with self.assertRaises(ContractError):
                StaticPublisher('vercel', ('official-cli',), 'example-project', 'example-team', True, runner).deploy(Path(tmp))

    def test_comparison_keeps_unknown_and_failures_out_of_success_denominator(self):
        from besties.observations import compare
        row = dict(id='one', condition='condition-one', provider='search-provider', query_id='question',
            observed_at='2026-11-02T00:00:00Z', status='completed', fresh=True, unprompted=True,
            index_status='unknown', mentioned=True, citation_urls=['https://example.org/'], expected_url='https://example.org')
        result = compare([row, dict(row, id='two', status='blocked'), dict(row, id='three', unprompted=False)])
        self.assertEqual(result['groups'][0]['eligible'], 1)
        self.assertEqual(result['groups'][0]['total'], 3)
        self.assertEqual(result['groups'][0]['index_confirmed'], 0)
        with self.assertRaises(ContractError): compare([row, row])

    def test_deterministic_shared_facts_and_different_presentations_all_formats(self):
        p, q = compose(facts(), persona()), compose(facts(), persona(True))
        a, b = render(p, site(), plan_digest(p)), render(q, site(), plan_digest(q))
        self.assertEqual(a, render(p, site(), plan_digest(p)))
        for key in ('index.html', 'facts.md', 'facts.json', 'release.json'): self.assertNotEqual(a[key], b[key])
        self.assertEqual(json.loads(a['facts.json'])['facts'], json.loads(b['facts.json'])['facts'])
        self.assertEqual(json.loads(a['release.json'])['facts_sha256'], json.loads(b['release.json'])['facts_sha256'])

    def test_missing_duplicated_unknown_claims_fail(self):
        for selected in ([], ['feature'], ['feature', 'feature', 'limit'], ['feature', 'limit', 'invented']):
            p = persona(); p.data['sections'] = [dict(id='all', heading='All', explanation='Review scope.', claim_ids=selected)]
            with self.assertRaises(ContractError): compose(facts(), p)

    def test_private_extra_fields_fail_instead_of_serializing(self):
        for key in ('research_notes', 'generation_prompt', 'hypothesis'):
            raw = copy.deepcopy(persona().data); raw[key] = 'private sentinel'
            with self.assertRaises(ContractError): PersonaDefinition.parse(raw)

    def test_exact_review_invalidated_by_any_prose_change(self):
        p = compose(facts(), persona()); reviewed = plan_digest(p)
        p.data['presentation']['intro'] = 'A different explanation.'
        with self.assertRaises(ContractError): render(p, site(), reviewed)

    def test_html_script_and_attribute_escaping(self):
        raw = persona().data; raw['intro'] = '<script>alert("x")</script>'
        p = compose(facts(), PersonaDefinition.parse(raw)); files = render(p, site(), plan_digest(p))
        self.assertNotIn(b'<script>alert', files['index.html'])
        validate_bundle(p, site(), files)

    def test_independent_parity_gate_even_when_artifact_hash_updated(self):
        p = compose(facts(), persona()); files = render(p, site(), plan_digest(p))
        files['facts.md'] = files['facts.md'].replace(b'Does not certify correctness.', b'Everything is correct.')
        r = json.loads(files['release.json']); r['files']['facts.md'] = digest(files['facts.md']); files['release.json'] = encoded(r)
        with self.assertRaises(ContractError): validate_bundle(p, site(), files)

    def test_mirror_canonical_and_live_receipts(self):
        p = compose(facts(), persona()); files = render(p, site(True), plan_digest(p))
        types = {'html': 'text/html', 'css': 'text/css', 'json': 'application/json', 'md': 'text/markdown', 'txt': 'text/plain', 'xml': 'application/xml'}
        def fetch(url):
            path = url.split('.org', 1)[1].lstrip('/') or 'index.html'
            return 200, {'content-type': types[path.split('.')[-1]], 'x-robots-tag': 'noindex' if path.endswith(('.md', '.json')) else ''}, files[path]
        self.assertTrue(verify_files_live(files, site(True).data['resource_url'], fetch)['passed'])
        self.assertIn(b'https://resources.example.org/', files['sitemap.xml'])

    def test_publish_uncertainty_blocks_retry_and_partial_batch_fails(self):
        class Broken:
            def deploy(self, directory): raise TimeoutError('private provider response')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); files = {'index.html': b'public'}; write_bundle(files, root/'bundle')
            journal = ReleaseJournal(root/'journal.jsonl')
            failed = publish(files, root/'bundle', 'target-one', Broken(), journal, lambda: {'passed': True})
            self.assertEqual(failed['status'], 'uncertain')
            self.assertNotIn('private provider response', journal.path.read_text())
            with self.assertRaises(ContractError): publish(files, root/'bundle', 'target-one', Broken(), journal, lambda: {})
            self.assertFalse(batch_status([failed, {'target': 'target-two', 'passed': True}])['passed'])

    def test_verified_and_rollback_with_prior_bundle(self):
        class Good:
            def deploy(self, directory): return 'deployment-reference'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); journal = ReleaseJournal(root/'journal.jsonl')
            for i, value in enumerate((b'previous', b'new', b'previous')):
                files = {'index.html': value}; write_bundle(files, root/str(i))
                result = publish(files, root/str(i), 'target', Good(), journal, lambda: {'passed': True})
                self.assertTrue(result['passed'])
            self.assertEqual(journal.rows()[1]['release'], journal.rows()[-1]['release'])

    def test_exact_bundle_and_static_hosting_config(self):
        p = compose(facts(), persona()); files = render(p, site(), plan_digest(p))
        for provider in ('vercel', 'netlify'):
            hosted = hosting_files(files, provider)
            self.assertFalse(any('.git' in k for k in hosted))
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp)/'bundle'; write_bundle(hosted, path); verify_files(hosted, path)
                (path/'unexpected.txt').write_text('private')
                with self.assertRaises(ContractError): verify_files(hosted, path)


if __name__ == '__main__': unittest.main()
