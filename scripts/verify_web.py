#!/usr/bin/env python3
"""Inspect actual Next production HTML; never equate a build with deployment."""
import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path


class Inspect(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ld, self.buffer = [], [], None
    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'link':
            self.links.append(attrs)
        if tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.buffer = ''
    def handle_data(self, data):
        if self.buffer is not None:
            self.buffer += data
    def handle_endtag(self, tag):
        if tag == 'script' and self.buffer is not None:
            self.ld.append(json.loads(self.buffer))
            self.buffer = None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--web-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    root = args.web_root/'.next/server/app'
    pages = []
    for locale in ['en', 'ko']:
        for suffix in ['', '/use-cases', '/security', '/evidence']:
            path = f'/{locale}/open-source/truthound{suffix}'
            inspect = Inspect()
            inspect.feed((root/(path[1:]+'.html')).read_text())
            assert any(x.get('rel') == 'canonical' and x.get('href') == 'https://styxis-io.com'+path for x in inspect.links)
            alternates = {x.get('hreflang'): x.get('href') for x in inspect.links if x.get('rel') == 'alternate'}
            for language, prefix in [('en', 'en'), ('ko-KR', 'ko')]:
                assert alternates[language] == 'https://styxis-io.com/'+prefix+'/open-source/truthound'+suffix
            assert 'x-default' in alternates
            expected = 'SoftwareApplication' if not suffix else 'TechArticle'
            assert any(x.get('@type') == expected and x.get('inLanguage') == locale for x in inspect.ld)
            pages.append(path)
    sitemap = (root/'sitemap.xml.body').read_text()
    assert all('https://styxis-io.com'+path in sitemap for path in pages)
    report = {'date':datetime.now(timezone.utc).isoformat(), 'client':'Next.js production HTML inspection',
              'model':None, 'checks':{'static_pages':pages, 'canonical':True, 'hreflang':True,
                                    'json_ld':True, 'sitemap':True}, 'deployment_verified':False}
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print('Verified 8 production HTML pages, canonical/hreflang, JSON-LD and sitemap')

if __name__ == '__main__':
    main()
