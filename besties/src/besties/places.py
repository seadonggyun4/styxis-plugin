"""Reviewed local-business facts and an independent visitor-guide template.

The entity is part of the reviewed plan. No ratings, opening hours or claims of
ownership are inferred from a category, a persona or a hosting account.
"""
import json
import re
from html import escape
from urllib.parse import quote
from .model import fields, require, text


def validate_entity(entity, evidence_ids):
    fields(entity, ('type', 'address', 'telephone', 'evidence'))
    require(entity['type'] == 'Restaurant', 'Unsupported place type')
    fields(entity['address'], ('streetAddress', 'addressLocality', 'addressRegion', 'addressCountry'))
    for value in entity['address'].values(): text(value)
    require(bool(re.fullmatch(r'[A-Z]{2}', entity['address']['addressCountry'])), 'ISO country code required')
    require(isinstance(entity['telephone'], str) and bool(re.fullmatch(r'\+[1-9][0-9-]{6,20}', entity['telephone'])), 'International telephone required')
    refs = entity['evidence']
    require(isinstance(refs, list) and refs and all(isinstance(e, str) and e in evidence_ids for e in refs), 'Unbound place evidence')


LABELS = {
    'ko': dict(skip='본문으로', guide='방문 안내', source='관광 안내 원문', address='찾아오시는 길',
               call='전화로 문의하기', map='지도에서 위치 확인', data='자료와 출처', checked='정보 확인 기준',
               notice='공개 출처를 바탕으로 만든 방문 안내입니다. 매장 공식 홈페이지가 아닙니다. 영업시간·휴무·가격은 방문 전 매장에 확인해 주세요.'),
    'en': dict(skip='Skip to content', guide='Visitor guide', source='Tourism reference', address='Find the restaurant',
               call='Call the restaurant', map='View location on map', data='Data and sources', checked='Information checked',
               notice='A visitor guide based on public sources, not the restaurant’s official website. Confirm hours, closures and prices with the restaurant before visiting.')}

CSS = '''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#faf6ed;color:#292c25;font:17px/1.85 system-ui,sans-serif;word-break:keep-all}a{color:inherit;text-underline-offset:5px}main{max-width:1120px;margin:auto;padding:24px 32px}nav{display:flex;justify-content:space-between;gap:24px;align-items:center;padding:12px 0;border-bottom:1px solid #d7d2c6}nav a{text-decoration:none}nav strong{font-size:20px}.eyebrow,.number{font-size:12px;letter-spacing:2px;text-transform:uppercase;color:#7b4a37}.hero{display:grid;grid-template-columns:1.4fr 1fr;gap:48px;align-items:center;padding:72px 0 64px}h1{font-family:Georgia,serif;font-size:clamp(38px,5.5vw,64px);line-height:1.3;letter-spacing:-2px;margin:16px 0 24px}h2{font-size:29px;line-height:1.4;letter-spacing:-1px}p{max-width:70ch}header p{font-size:19px;color:#555b50}.actions{display:flex;flex-wrap:wrap;gap:12px;margin:28px 0}.button{background:#ab4c32;color:white;text-decoration:none;padding:12px 22px;border-radius:3px;font-weight:650}.secondary{background:transparent;color:#292c25;box-shadow:inset 0 0 0 1px #9f9e90}.art{background:#e9e7d8;aspect-ratio:1;border-radius:50% 50% 4px 4px;display:grid;place-items:center;position:relative;overflow:hidden}.art svg{width:90%;height:auto}.art span{position:absolute;bottom:18px;font-size:11px;letter-spacing:3px;color:#6d735f}.location{display:grid;grid-template-columns:1fr 2fr;gap:32px;padding:30px 0;border-top:1px solid #b8b9a7;border-bottom:1px solid #b8b9a7}.location h2{margin:0}.location p{margin:0}article section{display:grid;grid-template-columns:1fr 2fr;gap:32px;padding:44px 0;border-bottom:1px solid #d7d2c6}section h2{margin-top:8px}.facts{padding-left:20px;border-left:2px solid #cbb79a}.fact p{margin-bottom:6px}.refs{font-size:12px;color:#6c705f;margin-bottom:24px}.intro{margin-top:0}.note{color:#636857;font-size:14px}footer{padding:40px 0}details{font-size:13px}details a{margin-right:18px}.skip{position:absolute;left:-9999px}.skip:focus{position:static}a:focus-visible,summary:focus-visible{outline:3px solid #ab4c32;outline-offset:5px}@media(max-width:700px){main{padding:16px 22px}.hero{grid-template-columns:1fr;padding:32px 0;gap:16px}.art{max-width:320px;width:100%;justify-self:center}.location,article section{grid-template-columns:1fr;gap:8px}h1{font-size:42px}nav{font-size:13px}nav strong{font-size:17px}.actions{gap:8px}.button{padding:10px 16px}}'''
# Original vector illustration, deliberately not a photograph of an actual dish.
ART = '''<svg viewBox="0 0 400 400" aria-hidden="true"><path d="M145 106q-18-25 0-50m55 50q-18-25 0-50m55 50q-18-25 0-50" fill="none" stroke="#9b9c83" stroke-width="3"/><ellipse cx="200" cy="305" rx="139" ry="19" fill="#d0cfbc"/><path d="M65 191q12 113 135 113t135-113" fill="#fdfaf0" stroke="#b4a898" stroke-width="3"/><ellipse cx="200" cy="190" rx="135" ry="62" fill="#fdfaf0" stroke="#b4a898" stroke-width="3"/><ellipse cx="200" cy="190" rx="118" ry="47" fill="#dbbc86"/><path d="M122 185q40-47 85 0t72 0m-161 10q42-42 88 0t75 0m-155 11q42-35 82 0t57 0" fill="none" stroke="#fff0c8" stroke-width="7"/><path d="M140 155l33-15 32 20-33 18zm55-3 32-15 31 20-31 18z" fill="#ad6a4e" stroke="#edd3b8" stroke-width="7"/><path d="m250 182 15-19m-6 29 20-17m-40 8 10-21" stroke="#526e48" stroke-width="7"/><path d="m264 126 96-57m-88 63 94-52" stroke="#6a4635" stroke-width="5"/></svg>'''


def render_place(plan, site):
    from .resources import encoded, digest
    from .rendering import plan_digest
    from .validation import validate_bundle
    facts, p = plan.data['facts'], plan.data['presentation']
    entity = facts['entity']; labels = LABELS[p['language']]
    e = lambda value: escape(value, quote=True)
    canonical = site.data['canonical_url'].rstrip('/') + '/'
    claims = {c['id']: c for c in facts['claims']}
    sources = {r['id']: r for r in facts['evidence']}
    address = ' '.join(entity['address'][k] for k in ('addressRegion', 'addressLocality', 'streetAddress'))
    phone = entity['telephone']; name = facts['product']['name']
    map_url = 'https://www.google.com/maps/search/?api=1&query=' + quote(address + ' ' + name)
    md = [f"# {escape(p['heading'])}", '', escape(p['intro']), '', f"{labels['address']}: {escape(address)}", '', phone, '']
    sections = []
    for i, section in enumerate(p['sections'], 1):
        parts = []
        md += [f"## {escape(section['heading'])}", '', escape(section['explanation']), '']
        for key in section['claim_ids']:
            claim = claims[key]
            refs = [sources[r] for r in claim['evidence']]
            parts.append(f'<div class="fact" data-claim="{key}"><p>{e(claim["statement"])}</p><div class="refs">' + ' · '.join(f'<a href="{e(r["url"])}">{e(r["label"])}</a>' for r in refs) + '</div></div>')
            md += [escape(claim['statement']), '', *[f'- {escape(r["label"])}: <{escape(r["url"])}>' for r in refs], '']
        sections.append(f'<section id="{section["id"]}"><div><span class="number">{i:02d}</span><h2>{e(section["heading"])}</h2></div><div><p class="intro">{e(section["explanation"])}</p><div class="facts">{"".join(parts)}</div></div></section>')
    md += [labels['notice'], '', *[f'- {escape(sources[k]["label"])}: <{escape(sources[k]["url"])}>' for k in entity['evidence']], '']
    restaurant = {'@type': 'Restaurant', 'name': name, 'address': {'@type': 'PostalAddress', **entity['address']}, 'telephone': phone}
    ld = {'@context': 'https://schema.org', '@type': 'WebPage', 'url': canonical, 'name': p['title'], 'description': p['description'], 'inLanguage': p['language'], 'about': restaurant}
    ld_text = json.dumps(ld, ensure_ascii=False, sort_keys=True).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    html = f'''<!doctype html><html lang="{p['language']}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(p['title'])}</title><meta name="description" content="{e(p['description'])}"><link rel="canonical" href="{e(canonical)}"><meta property="og:title" content="{e(p['title'])}"><meta property="og:description" content="{e(p['description'])}"><meta property="og:url" content="{e(canonical)}"><meta property="og:type" content="website"><meta name="twitter:card" content="summary"><link rel="stylesheet" href="/style.css"><script type="application/ld+json">{ld_text}</script></head><body><a class="skip" href="#content">{labels['skip']}</a><main id="content"><nav><strong>{e(name)}</strong><a href="{e(site.data['documentation_url'])}">{labels['source']} ↗</a></nav><header class="hero"><div><div class="eyebrow">{labels['guide']}</div><h1>{e(p['heading'])}</h1><p>{e(p['intro'])}</p><div class="actions"><a class="button" href="{e(map_url)}">{labels['map']} ↗</a><a class="button secondary" href="tel:{e(phone)}">{labels['call']}</a></div></div><div class="art" role="img" aria-label="{'국수 그릇 일러스트 · 실제 메뉴 사진이 아닙니다' if p['language']=='ko' else 'Noodle bowl illustration, not a menu photograph'}">{ART}<span>VISITOR GUIDE</span></div></header><aside class="location"><h2>{labels['address']}</h2><div><p>{e(address)}</p><p>{e(phone)}</p></div></aside><article>{''.join(sections)}</article><footer><p class="note">{labels['notice']}</p><p class="note">{labels['checked']}: {e(facts['product']['version'])}</p><details><summary>{labels['data']}</summary><a href="/facts.md">Markdown</a><a href="/facts.json">JSON</a><a href="/release.json">Manifest</a></details></footer></main></body></html>'''
    files = {'index.html': html.encode(), 'style.css': CSS.encode(), 'facts.json': encoded(plan.data), 'facts.md': '\n'.join(md).encode(),
        'robots.txt': f'User-agent: *\nAllow: /\nSitemap: {site.data["resource_url"]}/sitemap.xml\n'.encode(),
        'sitemap.xml': f'<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{e(canonical)}</loc></url></urlset>'.encode(),
        '_headers': b'/*\n  X-Content-Type-Options: nosniff\n/facts.json\n  Content-Type: application/json; charset=utf-8\n  X-Robots-Tag: noindex\n/facts.md\n  Content-Type: text/markdown; charset=utf-8\n  X-Robots-Tag: noindex\n/release.json\n  Content-Type: application/json; charset=utf-8\n  X-Robots-Tag: noindex\n'}
    files['release.json'] = encoded({'schema_version': 2, 'generator_version': '0.6.0', 'template_version': 'place-1', 'facts_sha256': digest(encoded(facts)), 'plan_sha256': plan_digest(plan), 'presentation': p, 'resource_url': site.data['resource_url'], 'canonical_url': canonical, 'geo_effect': 'under-evaluation', 'files': {k: digest(v) for k, v in sorted(files.items())}})
    validate_bundle(plan, site, files)
    return files
