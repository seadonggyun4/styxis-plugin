"""Evidence-bound editorial inputs and static search-friendly HTML rendering."""
import json
from html import escape
from html.parser import HTMLParser
from xml.etree import ElementTree
from .model import fields, identifier, require, text


def validate_seo(seo, project):
    fields(seo, ('language', 'title', 'description', 'heading', 'intro', 'pages'))
    require(seo['language'] in ('en', 'ko'), 'Unsupported language')
    for key in ('title', 'description', 'heading', 'intro'):
        text(seo[key])
    require(isinstance(seo['pages'], list) and 1 <= len(seo['pages']) <= 12, 'Bounded editorial pages required')
    claims = {c['id'] for c in project.data['claims']}
    slugs, titles, headings = set(), {seo['title'].casefold()}, {seo['heading'].casefold()}
    holdouts = [q['text'].casefold() for q in project.data['queries'] if q['split'] == 'holdout']
    for page in seo['pages']:
        fields(page, ('slug', 'title', 'description', 'heading', 'intro', 'claims', 'evidence'))
        identifier(page['slug'])
        require(page['slug'] not in slugs, 'Duplicate page slug')
        slugs.add(page['slug'])
        for key in ('title', 'description', 'heading', 'intro'):
            text(page[key])
        require(page['title'].casefold() not in titles and page['heading'].casefold() not in headings, 'Duplicate title or heading')
        titles.add(page['title'].casefold())
        headings.add(page['heading'].casefold())
        require(isinstance(page['claims'], list) and bool(page['claims']) and len(set(page['claims'])) == len(page['claims'])
                and all(c in claims for c in page['claims']), 'Unbound page claims')
        evidence = {e['id'] for e in project.data['evidence']}
        require(isinstance(page['evidence'], list) and bool(page['evidence']) and all(e in evidence for e in page['evidence']), 'Unbound editorial evidence')
    published = json.dumps(seo, ensure_ascii=False).casefold()
    require(not any(q in published for q in holdouts), 'Holdout question leaked into editorial input')
    # Bounds are editorial guardrails, not search-engine ranking limits.
    for page in [seo, *seo['pages']]:
        require(10 <= len(page['title']) <= 100 and 40 <= len(page['description']) <= 300, 'Unhelpful metadata length')


def render_pages(project, site):
    seo = site.data['seo']
    canonical_root = site.data['canonical_url'].rstrip('/') + '/'
    evidence = {e['id']: e for e in project.data['evidence']}
    claims = {c['id']: c for c in project.data['claims']}
    limits = [c['id'] for c in project.data['claims'] if c['kind'] == 'limitation']
    name = project.data['product']['name']
    version = project.data['product']['version']
    pages = [('index.html', seo, list(claims))] + [(f"guides/{p['slug']}/index.html", p, p['claims']) for p in seo['pages']]
    result = {}
    guides = ''.join(f'<li><a href="/guides/{p["slug"]}/">{escape(p["heading"])}</a><p>{escape(p["description"])}</p></li>' for p in seo['pages'])

    def claim_html(key):
        c = claims[key]
        refs = ' · '.join(f'<a href="{escape(evidence[e]["url"], quote=True)}">{escape(evidence[e]["label"])}</a>' for e in c['evidence'])
        return f'<section data-claim="{key}"><p class="tag">{escape(c["kind"])}</p><p>{escape(c["statement"])}</p><div class="sources">{refs}</div></section>'

    for path, page, selected in pages:
        relative = '' if path == 'index.html' else path[:-10]
        canonical = canonical_root + relative
        structured = {'@context': 'https://schema.org', '@type': 'WebPage', '@id': canonical + '#webpage',
                      'url': canonical, 'name': page['title'], 'description': page['description'],
                      'inLanguage': seo['language'], 'about': {'@type': 'SoftwareApplication', 'name': name, 'softwareVersion': version},
                      'isPartOf': {'@type': 'WebSite', '@id': canonical_root + '#website', 'url': canonical_root, 'name': name + ' resources'}}
        if path != 'index.html':
            structured['breadcrumb'] = {'@type': 'BreadcrumbList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': name + ' resources', 'item': canonical_root},
                {'@type': 'ListItem', 'position': 2, 'name': page['heading'], 'item': canonical}]}
        ld = json.dumps(structured, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
        reference_ids = page.get('evidence', list(evidence))
        references = ''.join(f'<li><a href="{escape(evidence[e]["url"], quote=True)}">{escape(evidence[e]["label"])}</a></li>' for e in reference_ids)
        boundaries = [key for key in limits if key not in selected]
        body = f'''<nav aria-label="Main"><a href="/">{escape(name)} resources</a><a href="{escape(site.data['documentation_url'], quote=True)}">Official documentation ↗</a><a href="{escape(site.data['product_url'], quote=True)}">Product website ↗</a></nav>
<header class="hero"><p class="eyebrow">Official product resource companion</p><h1>{escape(page['heading'])}</h1><p>{escape(page['intro'])}</p><p class="muted">{escape(version)} · SEO / GEO effectiveness is under evaluation.</p></header>
<article><h2>What the product supports</h2><div class="facts">{''.join(claim_html(c) for c in selected)}</div>
{('<h2>Boundaries to keep in mind</h2><div class="facts">' + ''.join(claim_html(c) for c in boundaries) + '</div>') if boundaries else ''}
<h2>Check the official evidence</h2><ul>{references}</ul><p>Use the official documentation for installation, permission setup and runnable examples. This resource companion summarizes the stated scope; it does not replace those instructions.</p>
<h2>Explore by task</h2><ul class="guide-list">{guides}</ul></article>
<h2>Machine-readable versions</h2><div class="formats"><a class="format" href="/facts.json"><strong>JSON facts ↗</strong>Capabilities, limitations and evidence IDs</a><a class="format" href="/facts.md"><strong>Markdown facts ↗</strong>The same approved statements and sources</a><a class="format" href="/release.json"><strong>Release manifest ↗</strong>Verify the deployed files</a></div>
<footer><p>This companion is maintained alongside the product, not an independent review or endorsement. Product and documentation sites are maintained separately.</p><p>Claims and editorial summaries are operator-approved; Besties does not independently fact-check their sources. Publication and structured data do not guarantee search indexing, rankings or AI recommendations.</p></footer>'''
        result[path] = f'''<!doctype html><html lang="{seo['language']}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(page['title'])}</title><meta name="description" content="{escape(page['description'], quote=True)}"><link rel="canonical" href="{escape(canonical, quote=True)}"><meta property="og:type" content="website"><meta property="og:title" content="{escape(page['title'], quote=True)}"><meta property="og:description" content="{escape(page['description'], quote=True)}"><meta property="og:url" content="{escape(canonical, quote=True)}"><meta name="twitter:card" content="summary"><link rel="stylesheet" href="/style.css"><script type="application/ld+json">{ld}</script></head><body><a class="skip" href="#content">Skip to content</a><main id="content">{body}</main></body></html>'''.encode()
    # Only canonical URLs belong in the sitemap, including on the mirror host.
    locations = [canonical_root + ('' if path == 'index.html' else path[:-10]) for path in result]
    result['sitemap.xml'] = ('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{escape(url)}</loc></url>' for url in locations) + '</urlset>').encode()
    return result


class Metadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.titles, self.h1, self.canonical, self.descriptions, self.links, self.ld = [], 0, [], [], [], []
        self.in_title = self.in_ld = False
        self.language, self.robots, self.og = None, [], {}
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html': self.language = a.get('lang')
        if tag == 'meta' and a.get('name') == 'robots': self.robots.append(a.get('content', '').lower())
        if tag == 'meta' and a.get('property', '').startswith('og:'): self.og[a['property']] = a.get('content')
        if tag == 'title': self.in_title = True
        if tag == 'h1': self.h1 += 1
        if tag == 'link' and a.get('rel') == 'canonical': self.canonical.append(a.get('href'))
        if tag == 'meta' and a.get('name') == 'description': self.descriptions.append(a.get('content'))
        if tag == 'a': self.links.append(a.get('href', ''))
        if tag == 'script' and a.get('type') == 'application/ld+json': self.in_ld = True
    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False
        if tag == 'script': self.in_ld = False
    def handle_data(self, data):
        if self.in_title: self.titles.append(data)
        if self.in_ld: self.ld.append(data)


def inspect_seo(files, site):
    """Structural checks, not a ranking, accessibility or rich-results certification."""
    seen_titles, seen_descriptions, canonicals = set(), set(), set()
    for path, raw in files.items():
        if not path.endswith('.html'): continue
        doc = Metadata()
        doc.feed(raw.decode())
        title = ''.join(doc.titles).strip()
        require(title and title not in seen_titles, 'Missing/duplicate title')
        seen_titles.add(title)
        require(doc.h1 == 1, 'Exactly one H1 required')
        require(doc.language == site.data['seo']['language'], 'Incorrect page language')
        require(not any('noindex' in v or 'none' in v for v in doc.robots), 'HTML must remain indexable')
        require(len(doc.descriptions) == 1 and doc.descriptions[0] and doc.descriptions[0] not in seen_descriptions, 'Missing/duplicate description')
        seen_descriptions.add(doc.descriptions[0])
        expected = site.data['canonical_url'].rstrip('/') + '/' + ('' if path == 'index.html' else path[:-10])
        require(doc.canonical == [expected], 'Incorrect page canonical')
        canonicals.add(expected)
        require(doc.og.get('og:title') == title and doc.og.get('og:description') == doc.descriptions[0]
                and doc.og.get('og:url') == expected, 'Social metadata drift')
        ld = json.loads(''.join(doc.ld))
        require(ld['url'] == expected and ld['name'] == title and ld['description'] == doc.descriptions[0], 'Structured data metadata drift')
        for link in doc.links:
            if link.startswith('/'):
                target = link.lstrip('/')
                if not target or target.endswith('/'): target += 'index.html'
                require(target in files, 'Broken internal link')
    root = ElementTree.fromstring(files['sitemap.xml'])
    locations = [e.text for e in root.findall('{*}url/{*}loc')]
    require(len(locations) == len(canonicals) and set(locations) == canonicals, 'Sitemap/canonical mismatch')
    return {'passed': True, 'html_pages': len(canonicals), 'ranking': 'unmeasured'}
