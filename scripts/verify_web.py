#!/usr/bin/env python3
"""Inspect actual Next production HTML; never equate a build with deployment."""
import argparse
import hashlib
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import re
import urllib.request
from pathlib import Path


class Inspect(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ld, self.buffer = [], [], None
        self.anchors, self.meta = [], []
        self.text, self.hidden_depth = [], 0
        self.in_body = False
    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'body':
            self.in_body = True
        if tag in {'script', 'style'}:
            self.hidden_depth += 1
        if tag == 'link':
            self.links.append(attrs)
        if tag == 'a':
            self.anchors.append(attrs)
        if tag == 'meta':
            self.meta.append(attrs)
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.buffer = ''
    def handle_data(self, data):
        if self.in_body and not self.hidden_depth:
            self.text.append(data)
        if self.buffer is not None:
            self.buffer += data
    def handle_endtag(self, tag):
        if tag == 'body':
            self.in_body = False
        if tag in {'script', 'style'}:
            self.hidden_depth = max(0, self.hidden_depth - 1)
        if tag == 'script' and self.buffer is not None:
            self.ld.append(json.loads(self.buffer))
            self.buffer = None


def visible_core_version(inspect, version):
    # A current footer cannot hide a stale paragraph. Ignore scripts entirely.
    versions = re.findall(r'\bCore\s+(\d+(?:\.\d+){2,}(?:[A-Za-z+-][A-Za-z0-9.+-]*)?)', ' '.join(inspect.text))
    return bool(versions) and set(versions) == {version}


def require_indexable(inspect):
    for meta in inspect.meta:
        if meta.get('name', '').lower() in {'robots', 'googlebot', 'bingbot'}:
            assert not re.search(r'\b(?:noindex|none)\b', meta.get('content', ''), re.I), 'page_noindex'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument('--web-root', type=Path)
    source.add_argument('--base-url', help='Inspect served pages; production verification requires the canonical origin')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--expect-core-version', help='Require this Core version consistently in overview/evidence body text and served llms.txt')
    p.add_argument('--expect-example', type=Path, help='Require new guide links, scoped metadata and an exact copy of this public execution receipt')
    args = p.parse_args()
    if args.expect_core_version and not re.fullmatch(r'\d+\.\d+\.\d+', args.expect_core_version):
        p.error('Expected a stable numeric Core version')
    root = args.web_root/'.next/server/app' if args.web_root else None
    def read_url(path):
        with urllib.request.urlopen(args.base_url.rstrip('/')+path, timeout=15) as stream:
            assert stream.status == 200
            assert not re.search(r'\bnoindex\b', stream.headers.get('X-Robots-Tag', ''), re.I), 'response_noindex'
            return stream.read(2*1024*1024).decode()
    pages = []
    for locale in ['en', 'ko']:
        for suffix in ['', '/use-cases', '/security', '/evidence']:
            path = f'/{locale}/open-source/truthound{suffix}'
            inspect = Inspect()
            inspect.feed((root/(path[1:]+'.html')).read_text() if root else read_url(path))
            require_indexable(inspect)
            assert any(x.get('rel') == 'canonical' and x.get('href') == 'https://styxis-io.com'+path for x in inspect.links)
            alternates = {x.get('hreflang'): x.get('href') for x in inspect.links if x.get('rel') == 'alternate'}
            for language, prefix in [('en', 'en'), ('ko-KR', 'ko')]:
                assert alternates[language] == 'https://styxis-io.com/'+prefix+'/open-source/truthound'+suffix
            assert 'x-default' in alternates
            expected = 'SoftwareApplication' if not suffix else 'TechArticle'
            assert any(x.get('@type') == expected and x.get('inLanguage') == locale for x in inspect.ld)
            if args.expect_core_version and suffix in {'', '/evidence'}:
                assert visible_core_version(inspect, args.expect_core_version), 'visible_release_version_mismatch: '+path
            if args.expect_example:
                prefix = 'en/' if locale == 'en' else ''
                hrefs = {a.get('href') for a in inspect.anchors}
                for guide in ['data-validation-mcp', 'local-mcp-example']:
                    assert f'https://truthound.netlify.app/{prefix}guides/{guide}/' in hrefs, 'missing_guide_link: '+path
                assert '/examples/truthound-local-mcp-3.3.1.json' in hrefs, 'missing_example: '+path
                assert any(m.get('name') == 'classification' and m.get('content') == 'Local Data Validation MCP Software' for m in inspect.meta)
                keywords = ' '.join(m.get('content', '') for m in inspect.meta if m.get('name') == 'keywords')
                assert not re.search(r'TRAP|Modbus|OPC UA|Industrial Connectivity|Data/AI Governance', keywords, re.I)
            pages.append(path)
    sitemap = (root/'sitemap.xml.body').read_text() if root else read_url('/sitemap.xml')
    assert all('https://styxis-io.com'+path in sitemap for path in pages)
    if not root:
        llms = read_url('/llms.txt')
        assert 'Truthound Local MCP' in llms and '/open-source/truthound' in llms
        if args.expect_core_version:
            assert re.search(r'Core\s+'+re.escape(args.expect_core_version)+r'(?![0-9A-Za-z+-]|\.\d)', llms), 'llms_core_version_mismatch'
    example_sha = None
    if args.expect_example:
        expected_bytes = args.expect_example.read_bytes()
        served_bytes = (args.web_root/'public/examples/truthound-local-mcp-3.3.1.json').read_bytes() if root else read_url('/examples/truthound-local-mcp-3.3.1.json').encode()
        example_sha = hashlib.sha256(expected_bytes).hexdigest()
        assert hashlib.sha256(served_bytes).hexdigest() == example_sha, 'example_receipt_mismatch'
    report = {'date':datetime.now(timezone.utc).isoformat(), 'client':'Next.js production HTML inspection',
              'model':None, 'checks':{'pages':pages, 'canonical':True, 'hreflang':True,
                                    'json_ld':True, 'sitemap':True, 'llms_txt': True if not root else None,
                                    'core_version':args.expect_core_version, 'noindex_absent': True,
                                    'guide_links_and_scoped_metadata': True if args.expect_example else None,
                                    'example_sha256': example_sha},
              'base_url':args.base_url, 'deployment_verified':args.base_url == 'https://styxis-io.com'}
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print('Verified 8 HTML pages, canonical/hreflang, JSON-LD and sitemap; served=' + str(not bool(root)))

if __name__ == '__main__':
    main()
