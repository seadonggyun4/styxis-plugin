"""Structural parity gates. No claim of automated semantic verification."""
from html import escape
from html.parser import HTMLParser
import json
from types import SimpleNamespace
from .model import require
from .resources import digest, encoded
from .seo import inspect_seo


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.hidden = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'): self.hidden += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style'): self.hidden -= 1
    def handle_data(self, data):
        if not self.hidden: self.parts.append(data)


def validate_bundle(plan, site, files):
    require(json.loads(files['facts.json']) == plan.data, 'JSON plan drift')
    receipt = json.loads(files['release.json'])
    require(receipt['presentation'] == plan.data['presentation'], 'Manifest presentation drift')
    require(receipt['plan_sha256'] == digest(encoded(plan.data)) and
            receipt['facts_sha256'] == digest(encoded(plan.data['facts'])), 'Manifest source drift')
    require(receipt['files'] == {k: digest(v) for k, v in sorted(files.items()) if k != 'release.json'}, 'Artifact drift')
    visible = VisibleText(); visible.feed(files['index.html'].decode())
    texts = [c['statement'] for c in plan.data['facts']['claims']]
    p = plan.data['presentation']
    texts += [p['heading'], p['intro']] + [s[k] for s in p['sections'] for k in ('heading', 'explanation')]
    for value in texts:
        require(value in visible.parts and escape(value) in files['facts.md'].decode(), 'Cross-format content loss')
    if plan.data['facts']['schema_version'] == 2:
        from .seo import Metadata
        entity = plan.data['facts']['entity']
        metadata = Metadata(); metadata.feed(files['index.html'].decode())
        expected = {'@type': entity['type'], 'name': plan.data['facts']['product']['name'],
                    'address': {'@type': 'PostalAddress', **entity['address']}, 'telephone': entity['telephone']}
        require(json.loads(''.join(metadata.ld))['about'] == expected, 'Place structured data drift')
        address = ' '.join(entity['address'][k] for k in ('addressRegion', 'addressLocality', 'streetAddress'))
        for value in (address, entity['telephone']):
            require(value in visible.parts and escape(value) in files['facts.md'].decode(), 'Place contact parity drift')
    seo_site = SimpleNamespace(data={**site.data, 'seo': {'language': p['language']}})
    return inspect_seo(files, seo_site)
