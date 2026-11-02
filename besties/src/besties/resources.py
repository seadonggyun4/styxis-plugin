"""Deterministic resource releases, independent of product and hosting provider."""
import hashlib
import json
from dataclasses import dataclass
from html import escape
from pathlib import Path
from urllib.parse import urlsplit
from .model import Project, fields, public_url, require


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


@dataclass(frozen=True)
class ResourceSite:
    data: dict

    @classmethod
    def parse(cls, data, project):
        require(isinstance(data, dict), 'Site configuration must be an object')
        version = data.get('schema_version')
        require(type(version) is int and version in (1, 2), 'Unsupported site schema')
        keys = ('schema_version', 'resource_url', 'canonical_url', 'documentation_url', 'product_url')
        fields(data, keys + (('seo',) if version == 2 else ()))
        if version == 2:
            from .seo import validate_seo
            validate_seo(data['seo'], project)
        for key in ('resource_url', 'canonical_url', 'documentation_url', 'product_url'):
            public_url(data[key])
            require(not any(c.isspace() or ord(c) < 32 for c in data[key]), 'Whitespace in URL')
        resource = urlsplit(data['resource_url'])
        require(resource.path in ('', '/') and resource.port in (None, 443), 'Resource URL must be an origin')
        human_hosts = {urlsplit(data[k]).hostname for k in ('documentation_url', 'product_url')}
        human_hosts.update(urlsplit(t['url']).hostname for t in project.data['targets'])
        require(resource.hostname not in human_hosts, 'Resource host must be separate from human sites')
        canonical = urlsplit(data['canonical_url'])
        require(canonical.hostname not in human_hosts and canonical.path in ('', '/'),
                'Canonical must identify a separate resource landing page')
        return cls(dict(data, resource_url=data['resource_url'].rstrip('/')))


def payload(project):
    # Never serialize target configuration or evaluation queries into public resources.
    return {'schema_version': 1, **{k: project.data[k] for k in ('product', 'claims', 'evidence')},
            'verification': 'Operator-approved claims; evidence truth is not independently verified.',
            'geo_effect': 'under-evaluation'}


def render_bundle(project, site):
    facts = payload(project)
    name = facts['product']['name']
    version = facts['product']['version']
    base = site.data['resource_url']
    evidence = {e['id']: e for e in facts['evidence']}
    cards = []
    markdown = [f'# {escape(name)} resources', '', f'Version: {escape(version)}', '',
                'GEO effect: under evaluation. Operator-approved public facts.', '']
    for claim in facts['claims']:
        refs = [evidence[i] for i in claim['evidence']]
        links = ' · '.join(f'<a href="{escape(e["url"], quote=True)}">{escape(e["label"])}</a>' for e in refs)
        cards.append(f'<section><span class="tag">{escape(claim["kind"])}</span><p>{escape(claim["statement"])}</p><div class="sources">{links}</div></section>')
        # HTML escaping prevents executable raw HTML in Markdown consumers.
        markdown += [f'## {claim["id"]} ({claim["kind"]})', '', escape(claim['statement']), '',
                     *[f'- {escape(e["label"])}: <{escape(e["url"])}>' for e in refs], '']
    markdown += ['## Official documentation', '', site.data['documentation_url'], '',
                 'This resource site is maintained alongside the product, not an independent endorsement.', '']
    css = '''*{box-sizing:border-box}body{margin:0;background:#f4f6fb;color:#16213a;font:17px/1.65 system-ui,sans-serif}main{max-width:1040px;margin:auto;padding:56px 24px}nav{display:flex;gap:24px;flex-wrap:wrap}a{color:#2353a5;text-underline-offset:4px}h1{font-size:clamp(36px,7vw,64px);line-height:1.1;letter-spacing:-2px;margin:24px 0}h2{font-size:25px}.eyebrow,.tag{font-size:12px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase}.hero{padding:32px 0 48px;max-width:780px}.muted,.sources{color:#526079;font-size:14px}.formats,.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}section,.format{background:white;padding:25px;border:1px solid #dfe5ef;border-radius:16px}.format{display:block;text-decoration:none}.format strong{display:block;font-size:22px}.tag{color:#526079}footer{margin-top:44px;border-top:1px solid #dfe5ef;padding-top:24px;font-size:14px}a:focus-visible{outline:3px solid #eb9900;outline-offset:5px}'''
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(name)} · Public resources</title><meta name="description" content="Versioned product facts, limitations and public evidence for {escape(name, quote=True)}."><link rel="canonical" href="{escape(site.data['canonical_url'], quote=True)}"><link rel="stylesheet" href="/style.css"></head><body><main><nav><strong>BESTIES / RESOURCES</strong><a href="{escape(site.data['documentation_url'], quote=True)}">Read the documentation ↗</a><a href="{escape(site.data['product_url'], quote=True)}">Product website ↗</a></nav><header class="hero"><p class="eyebrow">Official product resource companion</p><h1>{escape(name)}.<br>Facts you can trace.</h1><p>Capabilities, boundaries and public evidence in a consistent release. Built for developers and agents, with every claim open to inspection.</p><p class="muted">{escape(version)} · GEO effectiveness is under evaluation.</p></header><div class="formats"><a class="format" href="/facts.json"><strong>JSON ↗</strong>Structured facts and evidence bindings</a><a class="format" href="/facts.md"><strong>Markdown ↗</strong>Readable facts with source references</a><a class="format" href="/release.json"><strong>Release manifest ↗</strong>Content hashes for deployment verification</a></div><h2>Capabilities & boundaries</h2><article class="facts">{''.join(cards)}</article><footer><p>This companion is maintained alongside the product. It is not an independent review or endorsement. Product and documentation sites remain separate from this resource site.</p><p>Facts are operator-approved; linked evidence is not independently fact-checked by Besties. Publication does not prove search indexing or AI recommendation.</p></footer></main></body></html>'''
    files = {'index.html': html.encode(), 'style.css': css.encode(), 'facts.json': encoded(facts),
             'facts.md': '\n'.join(markdown).encode(),
             'robots.txt': f'User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n'.encode(),
             'sitemap.xml': f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{escape(base)}/</loc></url></urlset>'.encode(),
             '_headers': b'/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n/facts.json\n  Content-Type: application/json; charset=utf-8\n  X-Robots-Tag: noindex\n/facts.md\n  Content-Type: text/markdown; charset=utf-8\n  X-Robots-Tag: noindex\n/release.json\n  X-Robots-Tag: noindex\n'}
    if site.data['schema_version'] == 2:
        from .seo import render_pages, inspect_seo
        files.update(render_pages(project, site))
        files['style.css'] += b' .guide-list{padding-left:24px}.guide-list li{margin:24px 0}.guide-list p{margin:4px 0}.skip{position:absolute;left:-9999px}.skip:focus{position:static}h1{overflow-wrap:anywhere}section{min-width:0}a{overflow-wrap:anywhere}'
    files['release.json'] = encoded({'schema_version': 1, 'product': facts['product'],
                                    'facts_sha256': digest(files['facts.json']),
                                    'resource_url': base, 'geo_effect': 'under-evaluation',
                                    'files': {p: digest(b) for p, b in sorted(files.items())}})
    if site.data['schema_version'] == 2:
        inspect_seo(files, site)
    return files


def build(project, site, output):
    files = render_bundle(project, site)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    for name, data in files.items():
        (output / name).parent.mkdir(parents=True, exist_ok=True)
        (output / name).write_bytes(data)
    return {'passed': True, 'files': len(files), 'geo_effect': 'under-evaluation'}


def verify_directory(project, site, directory):
    directory = Path(directory)
    expected = render_bundle(project, site)
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}
    require(actual == set(expected), 'Unexpected or missing release files')
    require(not any(p.is_symlink() for p in directory.rglob('*')), 'Symlinks are not release artifacts')
    for name, data in expected.items():
        require((directory / name).read_bytes() == data, 'Resource content drift')
    result = {'passed': True, 'files': len(expected), 'geo_effect': 'under-evaluation'}
    if site.data['schema_version'] == 2:
        from .seo import inspect_seo
        result['seo'] = inspect_seo(expected, site)
    return result


def verify_live(project, site, fetch=None):
    """Read expected artifacts, not an untrusted remote manifest's URL list."""
    return verify_files_live(render_bundle(project, site), site.data['resource_url'], fetch)


def verify_files_live(expected, resource_url, fetch=None):
    """Verify a locally generated release, never a remotely supplied file list."""
    from urllib.request import Request, build_opener
    from .adapters import NoRedirect
    from datetime import datetime, timezone
    types = {'index.html': 'text/html', 'style.css': 'text/css', 'facts.json': 'application/json',
             'facts.md': 'text/markdown', 'release.json': 'application/json',
             'robots.txt': 'text/plain', 'sitemap.xml': 'application/xml'}

    def http(url):
        with build_opener(NoRedirect).open(Request(url, headers={'User-Agent': 'Besties/0.2 resources'}), timeout=20) as response:
            raw = response.read(2_000_001)
            require(len(raw) <= 2_000_000, 'Oversized response')
            return response.status, dict((k.lower(), v) for k, v in response.headers.items()), raw

    rows = []
    for name, data in expected.items():
        if name == '_headers':
            continue  # Hosting control file; its effects are verified on the responses.
        route = '/' + name
        if name.endswith('index.html'):
            route = route[:-10]
        url = resource_url + route
        try:
            status, headers, raw = (fetch or http)(url)
            mime = headers.get('content-type', '').split(';')[0].strip().lower()
            mime_ok = mime == ('text/html' if name.endswith('.html') else types[name]) or (name == 'sitemap.xml' and mime == 'text/xml')
            robots = headers.get('x-robots-tag', '').lower()
            robots_ok = 'noindex' in robots if name in ('facts.json', 'facts.md', 'release.json') else not name.endswith('.html') or not any(t in robots for t in ('noindex', 'none'))
            rows.append({'path': name, 'url': url, 'status': status,
                         'sha256': digest(raw), 'expected_sha256': digest(data),
                         'mime_ok': mime_ok, 'robots_ok': robots_ok,
                         'passed': status == 200 and raw == data and mime_ok and robots_ok})
        except Exception as exc:
            rows.append({'path': name, 'url': url, 'passed': False, 'status': 'unmeasured', 'error_type': type(exc).__name__})
    return {'passed': all(r['passed'] for r in rows), 'observed_at': datetime.now(timezone.utc).isoformat(),
            'pages': rows, 'indexing': 'unmeasured', 'geo_effect': 'under-evaluation'}
