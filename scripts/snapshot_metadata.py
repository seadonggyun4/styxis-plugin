#!/usr/bin/env python3
"""Refresh local candidate metadata from reviewed Truthound source and an E2E receipt.

Never fetches, installs, changes product files or publishes. Run E2E independently.
Distractors and baseline metadata remain frozen in the candidate fixture.
"""
import argparse
import ast
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REJECTED = 'Local-first data quality and validation for AI agents: check CSV/Parquet nulls and duplicates, profile columns and estimate PII with explicit directory consent.'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--truthound-root', type=Path, required=True)
    p.add_argument('--e2e', type=Path, required=True)
    p.add_argument('--candidates', type=Path, default=ROOT/'evaluation/candidates.json')
    args = p.parse_args()
    corpus = json.loads(args.candidates.read_text())
    receipt = json.loads(args.e2e.read_text())
    if receipt['status'] != 'passed':
        raise ValueError('source_snapshot_requires_passed_e2e')
    r = args.truthound_root
    manifest = json.loads((r/'plugins/truthound/.claude-plugin/plugin.json').read_text())
    registry = json.loads((r/'server.json').read_text())
    tree = ast.parse((r/'src/truthound/mcp/server.py').read_text())
    tools = ast.literal_eval(next(n.value for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(x, ast.Name) and x.id == 'TOOLS' for x in n.targets)))
    for variant in ['installed', 'source']:
        docs = corpus['variants'][variant]
        docs['plugin'][0]['text'] = 'Truthound '+manifest['description']
        for doc in docs['tool']:
            if doc['id'] not in tools:
                continue
            if variant == 'source':
                doc['text'] = doc['id']+' '+tools[doc['id']][1]
            else:
                actual = next(t for t in receipt['tools'] if t['name'] == doc['id'])
                doc['text'] = actual['name']+' '+actual['description']
        if variant == 'source':
            docs['registry'][0]['text'] = 'Truthound '+registry['description']
    rejected = copy.deepcopy(corpus['variants']['before'])
    rejected['plugin'][0]['text'] = 'Truthound '+REJECTED
    rejected['plugin'][0]['provenance'] = 'Rejected first rewrite, preserved to reproduce a recall regression'
    corpus['variants']['rejected'] = rejected
    corpus['installed_plugin_version'] = receipt['plugin_version']
    corpus['installed_core_version'] = receipt['core_version']
    corpus['source_metadata_status'] = 'UNRELEASED Core descriptions and UNPUBLISHED Registry description'
    args.candidates.write_text(json.dumps(corpus, ensure_ascii=False, indent=2)+'\n')

if __name__ == '__main__':
    main()
