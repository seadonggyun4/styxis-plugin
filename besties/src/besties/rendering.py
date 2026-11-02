"""Deterministic, shared-plan HTML/Markdown/JSON serialization."""
from html import escape
import json
from .domain import ProductFacts, PersonaDefinition
from .planning import compose
from .resources import encoded, digest
from .model import require

GENERATOR_VERSION = '0.4.0'
TEMPLATE_VERSION = 'presentation-1'


def plan_digest(plan):
    return digest(encoded(plan.data))


def render(plan, site, approved_plan_sha256):
    checked = compose(ProductFacts.parse(plan.data['facts']), PersonaDefinition.parse(plan.data['presentation']))
    require(checked.data == plan.data, 'Plan contains unrecognized data')
    require(approved_plan_sha256 == plan_digest(plan), 'Exact plan review required')
    facts, p = plan.data['facts'], plan.data['presentation']
    canonical = site.data['canonical_url'].rstrip('/') + '/'
    claims = {c['id']: c for c in facts['claims']}
    evidence = {e['id']: e for e in facts['evidence']}
    sections, md = [], [f"# {escape(p['heading'])}", '', escape(p['intro']), '',
                       f"Audience: {escape(p['audience'])}", '']
    for section in p['sections']:
        body = [f"<h2>{escape(section['heading'])}</h2><p>{escape(section['explanation'])}</p>"]
        md += [f"## {escape(section['heading'])}", '', escape(section['explanation']), '']
        for key in section['claim_ids']:
            c = claims[key]
            refs = [evidence[e] for e in c['evidence']]
            body.append(f'<div data-claim="{key}"><p class="tag">{escape(c["kind"])}</p><p>{escape(c["statement"])}</p><ul>' +
                        ''.join(f'<li><a href="{escape(e["url"], quote=True)}">{escape(e["label"])}</a></li>' for e in refs) + '</ul></div>')
            md += [escape(c['statement']), '', *[f'- {escape(e["label"])}: <{escape(e["url"])}>' for e in refs], '']
        sections.append(f'<section id="{section["id"]}">' + ''.join(body) + '</section>')
    notice = ('This resource companion is maintained alongside the product, not an independent endorsement. '
              'Product and documentation sites remain separate. Facts and explanations are operator-reviewed; '
              'Besties checks reference bindings, not the truth of source material. SEO and GEO effects are under evaluation.')
    md += ['## Documentation', '', site.data['documentation_url'], '', notice, '']
    ld = {'@context': 'https://schema.org', '@type': 'WebPage', 'url': canonical,
          'name': p['title'], 'description': p['description'], 'inLanguage': p['language'],
          'about': {'@type': 'SoftwareApplication', 'name': facts['product']['name'],
                    'softwareVersion': facts['product']['version']}}
    ld_text = json.dumps(ld, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    html = f'''<!doctype html><html lang="{p['language']}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(p['title'])}</title><meta name="description" content="{escape(p['description'], quote=True)}"><link rel="canonical" href="{escape(canonical, quote=True)}"><meta property="og:title" content="{escape(p['title'], quote=True)}"><meta property="og:description" content="{escape(p['description'], quote=True)}"><meta property="og:url" content="{escape(canonical, quote=True)}"><meta property="og:type" content="website"><meta name="twitter:card" content="summary"><link rel="stylesheet" href="/style.css"><script type="application/ld+json">{ld_text}</script></head><body><a class="skip" href="#content">Skip to content</a><main id="content"><nav><a href="{escape(site.data['documentation_url'], quote=True)}">Official documentation</a><a href="{escape(site.data['product_url'], quote=True)}">Product website</a></nav><header><p class="tag">{escape(facts['product']['name'])} / resource companion</p><h1>{escape(p['heading'])}</h1><p>{escape(p['intro'])}</p><p>For {escape(p['audience'])}</p><p class="muted">{escape(facts['product']['version'])}</p></header><article>{''.join(sections)}</article><footer><p>{notice}</p><nav><a href="/facts.md">Markdown</a><a href="/facts.json">JSON</a><a href="/release.json">Release manifest</a></nav></footer></main></body></html>'''
    css = b'*{box-sizing:border-box}body{margin:0;background:#f5f7fb;color:#17243c;font:18px/1.7 system-ui,sans-serif}main{max-width:920px;margin:auto;padding:40px 24px}nav{display:flex;gap:24px;flex-wrap:wrap}header{padding:48px 0}h1{font-size:clamp(34px,6vw,58px);line-height:1.15}h1,h2,a{overflow-wrap:anywhere}section{padding:28px;background:white;border:1px solid #dce3ee;border-radius:16px;margin:24px 0}h2{margin-top:0}.tag,.muted{color:#526079}.tag{font-size:13px;text-transform:uppercase;letter-spacing:1px}a{color:#214f9b}footer{padding:24px 0;font-size:15px}.skip{position:absolute;left:-9999px}.skip:focus{position:static}a:focus-visible{outline:3px solid #d98000;outline-offset:4px}'
    files = {'index.html': html.encode(), 'style.css': css,
             'facts.json': encoded(plan.data), 'facts.md': '\n'.join(md).encode(),
             'robots.txt': f"User-agent: *\nAllow: /\nSitemap: {site.data['resource_url']}/sitemap.xml\n".encode(),
             'sitemap.xml': f'<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{escape(canonical)}</loc></url></urlset>'.encode(),
             '_headers': b'/*\n  X-Content-Type-Options: nosniff\n/facts.json\n  Content-Type: application/json; charset=utf-8\n  X-Robots-Tag: noindex\n/facts.md\n  Content-Type: text/markdown; charset=utf-8\n  X-Robots-Tag: noindex\n/release.json\n  Content-Type: application/json; charset=utf-8\n  X-Robots-Tag: noindex\n'}
    files['release.json'] = encoded({'schema_version': 2, 'generator_version': GENERATOR_VERSION,
        'template_version': TEMPLATE_VERSION, 'facts_sha256': digest(encoded(facts)),
        'plan_sha256': plan_digest(plan), 'presentation': p,
        'resource_url': site.data['resource_url'], 'canonical_url': canonical,
        'geo_effect': 'under-evaluation', 'files': {k: digest(v) for k, v in sorted(files.items())}})
    from .validation import validate_bundle
    validate_bundle(plan, site, files)
    return files
