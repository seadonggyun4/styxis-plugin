import copy
import json
from pathlib import Path
import tempfile
import unittest
from besties.model import Project, ContractError
from besties.resources import ResourceSite, render_bundle, build, verify_directory, verify_live
from besties.seo import inspect_seo, Metadata

ROOT = Path(__file__).resolve().parents[1]


class SEOTests(unittest.TestCase):
    def setUp(self):
        self.project = Project.parse(json.loads((ROOT/'examples/truthound/resource-project.json').read_text()))
        self.config = json.loads((ROOT/'examples/truthound/resource-site-vercel.json').read_text())
        self.site = ResourceSite.parse(self.config, self.project)
        self.files = render_bundle(self.project, self.site)

    def test_four_unique_pages_and_canonical_sitemap(self):
        result = inspect_seo(self.files, self.site)
        self.assertEqual(result['html_pages'], 4)
        for path, body in self.files.items():
            if path.endswith('.html'):
                self.assertIn(b'application/ld+json', body)
                self.assertIn(b'og:description', body)
                self.assertIn(b'name="twitter:card"', body)
                for claim in self.project.data['claims']:
                    if claim['kind'] == 'limitation':
                        self.assertIn(claim['statement'].encode(), body)
        for q in self.project.data['queries']:
            if q['split'] == 'holdout':
                self.assertNotIn(q['text'], b''.join(self.files.values()).decode())

    def test_rejects_unbound_claim_duplicate_page_and_holdout_leak(self):
        for change in ['unbound','duplicate','holdout','path']:
            config=copy.deepcopy(self.config)
            if change=='unbound': config['seo']['pages'][0]['claims']=['unknown']
            if change=='duplicate': config['seo']['pages'].append(config['seo']['pages'][0])
            if change=='holdout': config['seo']['intro']=next(q['text'] for q in self.project.data['queries'] if q['split']=='holdout')
            if change=='path': config['seo']['pages'][0]['slug']='../escape'
            with self.assertRaises(ContractError): ResourceSite.parse(config,self.project)

    def test_independent_structural_gate_catches_regressions(self):
        for before,after in [(b'<h1>',b'<h2>'),(b'rel="canonical"',b'rel="alternate"'),(b'href="/facts.json"',b'href="/missing.json"')]:
            files=dict(self.files);files['index.html']=files['index.html'].replace(before,after)
            with self.assertRaises(ContractError): inspect_seo(files,self.site)
        files=dict(self.files);files['sitemap.xml']=b'<urlset/>'
        with self.assertRaises(ContractError): inspect_seo(files,self.site)

    def test_safe_structured_data_and_generic_product(self):
        config=copy.deepcopy(self.config)
        config['seo']['intro']='Text </script><script>alert(1)</script>'
        config['seo']['title']='Another product </script><script>alert(1)</script>'
        site=ResourceSite.parse(config,self.project)
        body=render_bundle(self.project,site)['index.html'].decode()
        self.assertNotIn('</script><script>',body)
        doc=Metadata();doc.feed(body)
        self.assertEqual(json.loads(''.join(doc.ld))['name'],config['seo']['title'])

    def test_nested_build_and_live_routes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'site';build(self.project,self.site,out)
            self.assertTrue(verify_directory(self.project,self.site,out)['passed'])
        seen=[]
        def fetch(url):
            seen.append(url)
            path=url.removeprefix(self.site.data['resource_url']+'/')
            if not path or path.endswith('/'): path+='index.html'
            mime='text/html' if path.endswith('.html') else {'css':'text/css','json':'application/json','md':'text/markdown','txt':'text/plain','xml':'application/xml'}[path.rsplit('.',1)[-1]]
            headers={'content-type':mime}
            if path in ('facts.json','facts.md','release.json'): headers['x-robots-tag']='noindex'
            return 200,headers,self.files[path]
        self.assertTrue(verify_live(self.project,self.site,fetch)['passed'])
        self.assertEqual(len(seen),10)
        self.assertTrue(any('/guides/' in url for url in seen))
        def blocked(url):
            status,headers,raw=fetch(url)
            if '/guides/' in url: headers['x-robots-tag']='noindex'
            return status,headers,raw
        self.assertFalse(verify_live(self.project,self.site,blocked)['passed'])

    def test_mirror_shares_canonical_pages_and_facts(self):
        config=copy.deepcopy(self.config);config['resource_url']='https://other-resource.example'
        mirror=render_bundle(self.project,ResourceSite.parse(config,self.project))
        for name in self.files:
            if name.endswith('.html') or name in ('facts.json','facts.md','sitemap.xml'):
                self.assertEqual(mirror[name],self.files[name])
