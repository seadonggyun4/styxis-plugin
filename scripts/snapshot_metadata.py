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
    p.add_argument('--registry-snapshot', type=Path, help='Actual official Registry response captured after publication')
    args = p.parse_args()
    corpus = json.loads(args.candidates.read_text())
    receipt = json.loads(args.e2e.read_text())
    if receipt['status'] != 'passed':
        raise ValueError('source_snapshot_requires_passed_e2e')
    r = args.truthound_root
    manifest = json.loads((r/'plugins/truthound/.claude-plugin/plugin.json').read_text())
    if manifest['version'] != receipt['plugin_version']:
        raise ValueError('source_plugin_and_installed_receipt_mismatch')
    registry = json.loads((r/'server.json').read_text())
    tree = ast.parse((r/'src/truthound/mcp/server.py').read_text())
    tools = ast.literal_eval(next(n.value for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(x, ast.Name) and x.id == 'TOOLS' for x in n.targets)))
    live = None
    if args.registry_snapshot:
        snapshot = json.loads(args.registry_snapshot.read_text())
        response = snapshot.get('response', snapshot)
        live = response['server']
        official = response['_meta']['io.modelcontextprotocol.registry/official']
        if official['status'] != 'active' or official['isLatest'] is not True:
            raise ValueError('registry_record_not_active_latest')
        if live['name'] != registry['name'] or live['version'] != receipt['core_version']:
            raise ValueError('live_registry_and_installed_core_mismatch')
        if live['packages'][0]['version'] != receipt['core_version']:
            raise ValueError('live_registry_package_mismatch')
        corpus['registry_snapshot'] = str(args.registry_snapshot)
    source_matches_installed = all(
        next(t for t in receipt['tools'] if t['name'] == name)['description'] == description
        for name, (_, description) in tools.items()
    )
    for variant in ['installed', 'source']:
        docs = corpus['variants'][variant]
        docs['plugin'][0]['text'] = 'Truthound '+manifest['description']
        for doc in docs['tool']:
            if doc['id'] not in tools:
                continue
            if variant == 'source':
                doc['text'] = doc['id']+' '+tools[doc['id']][1]
                doc['provenance'] = 'Reviewed source; metadata matches installed artifact' if source_matches_installed else 'UNRELEASED Truthound source tools/list'
            else:
                actual = next(t for t in receipt['tools'] if t['name'] == doc['id'])
                doc['text'] = actual['name']+' '+actual['description']
                doc['provenance'] = 'Published Core '+receipt['core_version']+' tools/list'
        if variant == 'source':
            docs['registry'][0]['text'] = 'Truthound '+registry['description']
            docs['registry'][0]['provenance'] = 'Reviewed source; matches published Registry record' if live == registry else 'Reviewed source Registry proposal; publication not established'
        elif live:
            docs['registry'][0]['text'] = 'Truthound '+live['description']
            docs['registry'][0]['provenance'] = 'Live official Registry '+live['version']+' snapshot'
    rejected = copy.deepcopy(corpus['variants']['before'])
    rejected['plugin'][0]['text'] = 'Truthound '+REJECTED
    rejected['plugin'][0]['provenance'] = 'Rejected first rewrite, preserved to reproduce a recall regression'
    corpus['variants']['rejected'] = rejected
    corpus['installed_plugin_version'] = receipt['plugin_version']
    corpus['installed_core_version'] = receipt['core_version']
    corpus['source_metadata_status'] = ('Matches tested installed artifact and observed Registry record' if source_matches_installed and live == registry else 'Source/installed/Registry parity not fully established; inspect provenance')
    args.candidates.write_text(json.dumps(corpus, ensure_ascii=False, indent=2)+'\n')

if __name__ == '__main__':
    main()
