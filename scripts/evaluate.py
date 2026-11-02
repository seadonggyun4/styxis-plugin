#!/usr/bin/env python3
"""Deterministic local retrieval baseline or strict import of observed client results.

This is evaluation tooling, not a production router or a claim about vendor ranking.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import platform

ROOT = Path(__file__).resolve().parents[1]
STAGES = {'registry': 10, 'plugin': 5, 'tool': 3}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tokens(text):
    words = re.findall(r'[a-z0-9]+|[가-힣]+', text.lower())
    return [part for word in words for part in
            ([word] + [word[i:i+2] for i in range(len(word)-1)] if re.search('[가-힣]', word) else [word])]


def rank(query, documents):
    term_counts = [Counter(tokens(d['text'])) for d in documents]
    lengths = [sum(c.values()) for c in term_counts]
    average = sum(lengths) / max(1, len(lengths)) or 1
    scores = []
    for document, counts, length in zip(documents, term_counts, lengths):
        score = 0
        for term in set(tokens(query)):
            df = sum(term in counts_ for counts_ in term_counts)
            idf = math.log(1 + (len(documents)-df+0.5)/(df+0.5))
            freq = counts[term]
            score += idf * freq * 2.5 / (freq + 1.5 * (0.25 + 0.75 * length/average))
        if score > 0:
            scores.append((score, document['id']))
    return [identity for _, identity in sorted(scores, key=lambda pair: (-pair[0], pair[1]))]


def ranking_metrics(ranking, relevant, k):
    """Queries with no relevant target have no recall/MRR/nDCG denominator."""
    if not relevant:
        return None
    gains = [relevant.get(item, 0) for item in ranking[:k]]
    recall = sum(gain > 0 for gain in gains) / len(relevant)
    hit = int(any(gains))
    # MRR is untruncated: caller records that convention explicitly.
    rr = next((1/i for i, item in enumerate(ranking, 1) if item in relevant), 0)
    dcg = sum((2**gain-1)/math.log2(i+2) for i, gain in enumerate(gains))
    ideal = sum((2**gain-1)/math.log2(i+2) for i, gain in enumerate(sorted(relevant.values(), reverse=True)[:k]))
    return {'recall': recall, 'hit': hit, 'precision': sum(gain > 0 for gain in gains)/k, 'mrr': rr, 'ndcg': dcg/ideal if ideal else 0}


def mean(values):
    return sum(values)/len(values) if values else None


def rate(values):
    return {'value': mean([int(x) for x in values]), 'attempted': len(values), 'passed': sum(values)}


def load_observations(path, queries, candidates):
    observed = {}
    allowed = {stage: {d['id'] for d in docs} for stage, docs in candidates.items()}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row['query_id'] not in queries:
            raise ValueError('unknown_query_id')
        key = (row['query_id'], row['stage'])
        if key in observed:
            raise ValueError('duplicate_query_stage')
        stage = row['stage']
        if stage not in STAGES:
            raise ValueError('unknown_stage')
        ranking = row['ranking']
        if not isinstance(ranking, list) or len(set(ranking)) != len(ranking) or not set(ranking) <= allowed[stage]:
            raise ValueError('invalid_or_unknown_candidates')
        if 'selected' in row:
            chosen = row['selected']
            if not isinstance(chosen, list) or len(set(chosen)) != len(chosen) or not set(chosen) <= set(ranking):
                raise ValueError('selection_must_be_unique_retrieved_candidates')
        observed[key] = row
    return observed


def evaluate(queries, candidates, observed):
    rows = []
    for query in queries:
        for stage, k in STAGES.items():
            key = (query['id'], stage)
            if key not in observed:
                continue
            observation = observed[key]
            ranking = observation['ranking']
            relevant = query['relevant'][stage]
            metrics = ranking_metrics(ranking, relevant, k)
            row = {'query_id': query['id'], 'language': query['language'], 'kind': query['kind'],
                   'category': query['category'], 'split': query['split'], 'stage': stage,
                   'ranking': ranking, 'relevant': relevant, 'metrics': metrics,
                   'negative_target_exposure': not relevant and bool(set(ranking[:k]) & {'truthound', 'check_file', 'profile_file', 'scan_pii'})}
            # Only explicit selection observations count; ranking is not selection.
            if 'selected' in observation:
                selected = observation['selected']
                selected_targets = {x for x in selected if x in {'truthound', 'check_file', 'profile_file', 'scan_pii'}}
                row['selected'] = selected
                row['selection_correct'] = (set(selected) == set(relevant)) if relevant else not selected_targets
                row['false_selection'] = not relevant and bool(selected_targets)
            rows.append(row)
    summary = {}
    for stage, k in STAGES.items():
        subset = [r for r in rows if r['stage'] == stage]
        positive = [r for r in subset if r['metrics'] is not None]
        selections = [r for r in subset if 'selected' in r]
        negative = [r for r in selections if not r['relevant']]
        summary[stage] = {
            'k': k, 'observed_queries': len(subset), 'total_queries': len(queries),
            f'recall_at_{k}': mean([r['metrics']['recall'] for r in positive]),
            f'hit_at_{k}': mean([r['metrics']['hit'] for r in positive]),
            f'precision_at_{k}': mean([r['metrics']['precision'] for r in positive]),
            'mrr_full_ranking': mean([r['metrics']['mrr'] for r in positive]),
            f'ndcg_at_{k}': mean([r['metrics']['ndcg'] for r in positive]),
            'positive_denominator': len(positive),
            'negative_target_exposure_at_k': mean([int(r['negative_target_exposure']) for r in subset if not r['relevant']]),
            'correct_selection_rate': rate([r['selection_correct'] for r in selections]),
            'false_selection_rate': rate([r['false_selection'] for r in negative]),
        }
    failures = [r for r in rows if (r['metrics'] and r['metrics']['recall'] < 1) or
                ('selection_correct' in r and not r['selection_correct'])]
    slices = {}
    for field in ['language', 'kind', 'category', 'split']:
        slices[field] = {}
        for value in sorted({q[field] for q in queries}):
            slices[field][value] = {stage: {
                'count': len(sub := [r for r in rows if r[field] == value and r['stage'] == stage and r['metrics']]),
                'recall': mean([r['metrics']['recall'] for r in sub]),
                'ndcg': mean([r['metrics']['ndcg'] for r in sub]),
            } for stage in STAGES}
    return summary, slices, failures, rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dataset', type=Path, default=ROOT/'evaluation/queries.json')
    p.add_argument('--candidates', type=Path, default=ROOT/'evaluation/candidates.json')
    p.add_argument('--variant', choices=['before', 'rejected', 'installed', 'source'], default='installed')
    p.add_argument('--observations', type=Path)
    p.add_argument('--client', default='local-bm25-harness')
    p.add_argument('--model', default=None)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--e2e', type=Path, action='append', default=[])
    args = p.parse_args()
    if args.observations and (args.client == 'local-bm25-harness' or not args.model):
        p.error('Observed client runs require explicit --client and --model (use none if no model ran)')
    dataset = json.loads(args.dataset.read_text())
    queries = dataset['queries']
    assert len({q['id'] for q in queries}) == len(queries), 'duplicate query'
    for query in queries:
        assert query['kind'] in {'positive', 'negative', 'hard-negative'}
        assert set(query['relevant']) == set(STAGES)
        assert all(isinstance(g, int) and g > 0 for rel in query['relevant'].values() for g in rel.values())
    corpus = json.loads(args.candidates.read_text())
    candidates = corpus['variants'][args.variant]
    for stage, docs in candidates.items():
        ids = [d['id'] for d in docs]
        assert len(ids) == len(set(ids)) and len(ids) > STAGES[stage], 'insufficient/distinct candidates'
        for q in queries:
            assert set(q['relevant'][stage]) <= set(ids), 'relevance target missing from corpus'
    if args.observations:
        observed = load_observations(args.observations, {q['id']:q for q in queries}, candidates)
    else:
        observed = {(q['id'], stage): {'ranking': rank(q['query'], docs)}
                    for q in queries for stage, docs in candidates.items()}
    summary, slices, failures, rows = evaluate(queries, candidates, observed)
    e2e = [json.loads(path.read_text()) for path in args.e2e]
    execution = {}
    for metric, check in {'install_success_rate':'install', 'mcp_startup_success_rate':'mcp_startup',
                          'first_call_success_rate':'first_call', 'permission_denial_correctness':'deny_unapproved_and_symlink'}.items():
        # Missing checks in failed attempts count as failed, never silently disappear.
        execution[metric] = rate([proof.get('checks', {}).get(check, False) is True for proof in e2e])
    report = {
        'schema_version': 1, 'date': datetime.now(timezone.utc).isoformat(),
        'client': args.client, 'model': args.model, 'python': platform.python_version(),
        'dataset_version': dataset['version'], 'dataset_sha256': digest(args.dataset),
        'registry_snapshot': corpus['registry_snapshot'], 'candidate_set_sha256': digest(args.candidates),
        'candidate_ids': {s:[d['id'] for d in docs] for s,docs in candidates.items()},
        'candidate_variant': args.variant, 'candidate_scope': corpus['scope'],
        'retrieval_method': 'observed-client' if args.observations else 'BM25 k1=1.5 b=0.75; EN words/KO bigrams; no query expansion',
        'top_k': STAGES, 'selection_method': 'explicit client observation only',
        'e2e_receipts': [str(path) for path in args.e2e],
        'scope_warning': 'Local fixture rankings do not measure live Registry, Claude recommendation, or model selection. Source variant contains UNRELEASED metadata.',
        'metrics': summary, 'execution': execution, 'slices': slices, 'failures': failures, 'rows': rows,
        'pending': ['live_registry_ranking', 'real_client_plugin_ranking', 'external_model_selection',
                    'web_citation_visibility', 'earned_vs_owned_source_selection'],
        'reproduce': 'python3 scripts/evaluate.py ' + ' '.join(__import__('shlex').quote(x) for x in __import__('sys').argv[1:]),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'variant':args.variant, 'metrics':summary, 'execution':execution, 'failures':len(failures)}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
