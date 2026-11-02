"""Descriptive comparisons of imported observations, never causal estimates."""
from collections import defaultdict
from .model import fields, identifier, require, public_url, text


def compare(rows):
    require(isinstance(rows, list), 'Observation list required')
    groups = defaultdict(lambda: dict(total=0, eligible=0, cited=0, mentioned=0, index_confirmed=0))
    seen = set()
    for r in rows:
        fields(r, ('id', 'condition', 'provider', 'query_id', 'observed_at', 'status',
                   'fresh', 'unprompted', 'index_status', 'mentioned', 'citation_urls', 'expected_url'))
        for key in ('id', 'condition', 'query_id'): identifier(r[key])
        require(r['id'] not in seen, 'Duplicate observation')
        seen.add(r['id'])
        for key in ('provider', 'observed_at'): text(r[key])
        require(r['status'] in ('completed', 'blocked', 'failed', 'unavailable'), 'Invalid observation status')
        require(r['index_status'] in ('confirmed', 'not-indexed', 'unknown'), 'Invalid index status')
        for key in ('fresh', 'unprompted', 'mentioned'): require(type(r[key]) is bool, 'Boolean required')
        public_url(r['expected_url'])
        require(isinstance(r['citation_urls'], list), 'Citation list required')
        for url in r['citation_urls']: public_url(url)
        group = groups[(r['condition'], r['provider'])]; group['total'] += 1
        group['index_confirmed'] += r['index_status'] == 'confirmed'
        if r['status'] == 'completed' and r['fresh'] and r['unprompted']:
            group['eligible'] += 1
            group['mentioned'] += r['mentioned']
            group['cited'] += any(u.rstrip('/') == r['expected_url'].rstrip('/') for u in r['citation_urls'])
    return {'groups': [dict(condition=c, provider=p, **values) for (c, p), values in sorted(groups.items())],
            'causal_effect': 'not-established', 'indexing_delay': 'not-inferred',
            'limitations': 'Exact-URL citation counts only; blocked runs remain in total, not eligible denominators.'}
