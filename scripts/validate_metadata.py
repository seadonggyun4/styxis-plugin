#!/usr/bin/env python3
"""Offline catalog/evidence consistency gate; CLI and remote checks live in validate.sh."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT/'.claude-plugin/marketplace.json').read_text())
    assert manifest['name'] == 'styxis-plugin'
    assert [p['name'] for p in manifest['plugins']] == ['truthound'], 'only public Local plugin is allowed'
    entry = manifest['plugins'][0]
    assert entry['strict'] is True, 'upstream manifest must own components'
    assert not any(key in entry for key in ['skills', 'mcpServers', 'hooks', 'agents', 'commands'])
    assert entry['source']['source'] == 'git-subdir'
    assert entry['source']['url'] == 'https://github.com/seadonggyun4/Truthound.git'
    assert entry['source']['path'] == 'plugins/truthound'
    assert re.fullmatch('[a-f0-9]{40}', entry['source']['sha'])
    assert re.fullmatch(r'\d+\.\d+\.\d+', entry['version'])
    readme = (ROOT/'README.md').read_text()
    assert 'Phase 2' not in readme and 'Anthropic/OpenAI' not in readme
    for command in ['claude plugin marketplace add seadonggyun4/styxis-plugin', 'claude plugin install truthound@styxis-plugin']:
        assert command in readme
    dataset = json.loads((ROOT/'evaluation/queries.json').read_text())
    queries = dataset['queries']
    assert len({q['id'] for q in queries}) == len(queries)
    assert {'positive', 'negative', 'hard-negative'} <= {q['kind'] for q in queries}
    assert {'ko', 'en'} <= {q['language'] for q in queries}
    assert {'schema-validation', 'csv-quality', 'parquet-profiling', 'pii', 'rag-preparation',
            'eval-validation', 'offline', 'multi-intent', 'great-expectations', 'pandera', 'soda'} <= {q['category'] for q in queries}
    provenance = json.loads((ROOT/'release.json').read_text())
    assert provenance['truthound_source_sha'] == entry['source']['sha']
    assert provenance['plugin_version'] == entry['version']
    assert provenance['core_package_version'] == '3.3.0'
    print('Offline catalog, provenance and query contracts passed')

if __name__ == '__main__':
    main()
