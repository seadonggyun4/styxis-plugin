import copy
import json
from pathlib import Path
import tempfile
import unittest
from besties.model import Project, ContractError
from besties.resources import ResourceSite, build, render_bundle, verify_directory, verify_live

ROOT = Path(__file__).resolve().parents[1]


class ResourceTests(unittest.TestCase):
    def setUp(self):
        self.project = Project.parse(json.loads((ROOT / 'examples/truthound/category-project.json').read_text()))
        self.config = json.loads((ROOT / 'examples/truthound/resource-site-netlify.json').read_text())
        self.config.pop('seo')
        self.config['schema_version'] = 1
        self.site = ResourceSite.parse(self.config, self.project)

    def test_separate_host_is_mandatory(self):
        for url in ['https://truthound.netlify.app/resources', 'https://truthound.netlify.app', 'https://styxis-io.com']:
            with self.assertRaises(ContractError):
                ResourceSite.parse(dict(self.config, resource_url=url), self.project)

    def test_deterministic_and_holdout_private_inputs_not_exported(self):
        files = render_bundle(self.project, self.site)
        self.assertEqual(files, render_bundle(self.project, self.site))
        body = b''.join(files.values()).decode()
        for query in self.project.data['queries']:
            self.assertNotIn(query['text'], body)
        self.assertNotIn('required_terms', body)
        facts = json.loads(files['facts.json'])
        self.assertEqual(facts['claims'], self.project.data['claims'])
        self.assertIn('noindex', files['_headers'].decode())
        self.assertNotIn('noindex', files['index.html'].decode())

    def test_hosts_share_facts_and_canonical_but_have_distinct_releases(self):
        second = ResourceSite.parse(dict(self.config, resource_url='https://other-resources.example'), self.project)
        first_files = render_bundle(self.project, self.site)
        second_files = render_bundle(self.project, second)
        for name in ('facts.json', 'facts.md', 'index.html'):
            self.assertEqual(first_files[name], second_files[name])
        self.assertNotEqual(first_files['release.json'], second_files['release.json'])
        self.assertNotEqual(first_files['sitemap.xml'], second_files['sitemap.xml'])

    def test_host_configuration_cannot_inject_robots_directives(self):
        with self.assertRaises(ContractError):
            ResourceSite.parse(dict(self.config, resource_url='https://example.org\nDisallow: /'), self.project)

    def test_detects_missing_tampered_extra_and_symlink_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'site'
            build(self.project, self.site, out)
            self.assertTrue(verify_directory(self.project, self.site, out)['passed'])
            with self.assertRaises(FileExistsError):
                build(self.project, self.site, out)
            original = (out / 'facts.md').read_bytes()
            (out / 'facts.md').write_text('incorrect version')
            with self.assertRaises(ContractError):
                verify_directory(self.project, self.site, out)
            (out / 'facts.md').write_bytes(original)
            (out / 'secret.txt').write_text('must never ship')
            with self.assertRaises(ContractError):
                verify_directory(self.project, self.site, out)
            (out / 'secret.txt').unlink()
            (out / 'facts.md').unlink()
            with self.assertRaises(ContractError):
                verify_directory(self.project, self.site, out)
            external = Path(tmp) / 'external.md'
            external.write_bytes(original)
            (out / 'facts.md').symlink_to(external)
            with self.assertRaises(ContractError):
                verify_directory(self.project, self.site, out)

    def test_escape_and_product_independence(self):
        data = copy.deepcopy(self.project.data)
        data['product']['name'] = 'Another <script>product</script>'
        data['claims'][0]['statement'] = '<script>alert(1)</script>'
        bundle = render_bundle(Project.parse(data), self.site)
        for name in ['index.html', 'facts.md']:
            self.assertNotIn(b'<script>', bundle[name])
        self.assertEqual(json.loads(bundle['facts.json'])['claims'][0]['statement'], '<script>alert(1)</script>')

    def test_live_requires_exact_bytes_status_mime_and_robots(self):
        bundle = render_bundle(self.project, self.site)
        def fetch(url):
            name = url.rsplit('/', 1)[-1] or 'index.html'
            mime = {'html':'text/html', 'css':'text/css', 'json':'application/json', 'md':'text/markdown', 'txt':'text/plain', 'xml':'application/xml'}[name.rsplit('.',1)[-1]]
            headers = {'content-type': mime}
            if name in ('facts.md', 'facts.json', 'release.json'):
                headers['x-robots-tag'] = 'noindex'
            return 200, headers, bundle[name]
        self.assertTrue(verify_live(self.project, self.site, fetch)['passed'])
        for modifier in [lambda s,h,b:(404,h,b), lambda s,h,b:(s,{},b), lambda s,h,b:(s,h,b+b'changed')]:
            self.assertFalse(verify_live(self.project, self.site, lambda url: modifier(*fetch(url)))['passed'])
        def unavailable(url):
            raise OSError('sensitive details')
        result = verify_live(self.project, self.site, unavailable)
        self.assertFalse(result['passed'])
        self.assertNotIn('sensitive details', str(result))
        self.assertEqual(result['indexing'], 'unmeasured')


if __name__ == '__main__':
    unittest.main()
