#!/usr/bin/env python3
"""Inspect actual Next production HTML; never equate a build with deployment."""
import argparse
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


def main():
    p = argparse.ArgumentParser(description=__doc__)
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument('--web-root', type=Path)
    source.add_argument('--base-url', help='Inspect served pages; production verification requires the canonical origin')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--expect-core-version', help='Require this Core/Registry version in overview/evidence body text and served llms.txt')
    args = p.parse_args()
    if args.expect_core_version and not re.fullmatch(r'\d+\.\d+\.\d+', args.expect_core_version):
        p.error('Expected a stable numeric Core version')
    root = args.web_root/'.next/server/app' if args.web_root else None
    def read_url(path):
        with urllib.request.urlopen(args.base_url.rstrip('/')+path, timeout=15) as stream:
            assert stream.status == 200
            return stream.read(2*1024*1024).decode()
    pages = []
    for locale in ['en', 'ko']:
        for suffix in ['', '/use-cases', '/security', '/evidence']:
            path = f'/{locale}/open-source/truthound{suffix}'
            inspect = Inspect()
            inspect.feed((root/(path[1:]+'.html')).read_text() if root else read_url(path))
            assert any(x.get('rel') == 'canonical' and x.get('href') == 'https://styxis-io.com'+path for x in inspect.links)
            alternates = {x.get('hreflang'): x.get('href') for x in inspect.links if x.get('rel') == 'alternate'}
            for language, prefix in [('en', 'en'), ('ko-KR', 'ko')]:
                assert alternates[language] == 'https://styxis-io.com/'+prefix+'/open-source/truthound'+suffix
            assert 'x-default' in alternates
            expected = 'SoftwareApplication' if not suffix else 'TechArticle'
            assert any(x.get('@type') == expected and x.get('inLanguage') == locale for x in inspect.ld)
            if args.expect_core_version and suffix in {'', '/evidence'}:
                label = 'Core ' if not suffix else 'io.github.seadonggyun4/truthound '
                assert label+args.expect_core_version in ''.join(inspect.text), 'visible_release_version_mismatch: '+path
            pages.append(path)
    sitemap = (root/'sitemap.xml.body').read_text() if root else read_url('/sitemap.xml')
    assert all('https://styxis-io.com'+path in sitemap for path in pages)
    if not root:
        llms = read_url('/llms.txt')
        assert 'Truthound Local MCP' in llms and '/open-source/truthound' in llms
        if args.expect_core_version:
            assert 'Core '+args.expect_core_version in llms, 'llms_core_version_mismatch'
    report = {'date':datetime.now(timezone.utc).isoformat(), 'client':'Next.js production HTML inspection',
              'model':None, 'checks':{'pages':pages, 'canonical':True, 'hreflang':True,
                                    'json_ld':True, 'sitemap':True, 'llms_txt': True if not root else None,
                                    'core_version':args.expect_core_version},
              'base_url':args.base_url, 'deployment_verified':args.base_url == 'https://styxis-io.com'}
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print('Verified 8 HTML pages, canonical/hreflang, JSON-LD and sitemap; served=' + str(not bool(root)))

if __name__ == '__main__':
    main()
