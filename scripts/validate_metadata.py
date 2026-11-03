#!/usr/bin/env python3
"""Validate catalog pins; optionally inspect upstream files without running them."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def relative(value):
    require(isinstance(value, str) and value and not value.startswith('/'), 'Relative source path required')
    require('\\' not in value and all(p not in ('', '.', '..') for p in value.split('/')), 'Unsafe source path')
    return PurePosixPath(value)


def validate(manifest, releases):
    require(manifest.get('name') == 'styxis-plugin', 'Unexpected catalog name')
    entries = manifest.get('plugins')
    require(isinstance(entries, list) and entries, 'Plugins required')
    names = [p.get('name') for p in entries]
    require(all(isinstance(n, str) and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', n) for n in names), 'Invalid plugin name')
    require(len(names) == len(set(names)), 'Duplicate plugin name')
    require(releases.get('schema_version') == 2 and isinstance(releases.get('plugins'), dict), 'Unsupported release inventory')
    require(set(names) == set(releases['plugins']), 'Catalog/release inventory mismatch')
    for entry in entries:
        name = entry['name']; pin = releases['plugins'][name]; source = entry['source']
        require(entry.get('strict') is True, 'Product manifest must own components')
        require(not set(entry).intersection(('skills', 'mcpServers', 'hooks', 'agents', 'commands')), 'Catalog component override')
        require(isinstance(entry.get('description'), str) and entry['description'].strip(), 'Description required')
        require(re.fullmatch(r'\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?', entry['version']), 'Invalid version')
        require(source['source'] == 'git-subdir', 'Unsupported source kind')
        url = urlsplit(source['url'])
        require(url.scheme == 'https' and url.hostname and not url.username and not url.password and not url.query and not url.fragment, 'Public HTTPS source required')
        relative(source['path'])
        require(re.fullmatch(r'[a-f0-9]{40}', source['sha']), 'Full source SHA required')
        for key, expected in [('plugin_version', entry['version']), ('source_url', source['url']), ('source_path', source['path']), ('source_sha', source['sha'])]:
            require(pin.get(key) == expected, 'Catalog/release pin mismatch: '+name)
        hashes = pin.get('source_file_sha256')
        require(isinstance(hashes, dict) and hashes, 'Source file hashes required')
        require(source['path']+'/.claude-plugin/plugin.json' in hashes, 'Plugin manifest hash required')
        require(any(source['path']+'/'+p in hashes for p in ('.mcp.json', 'mcp.json')), 'MCP configuration hash required')
        for path, digest in hashes.items():
            relative(path)
            require(path.startswith(source['path']+'/'), 'Hash outside plugin directory')
            require(isinstance(digest, str) and re.fullmatch(r'[a-f0-9]{64}', digest), 'Invalid file hash')
    return entries


def validate_codex(catalog, entries):
    require(catalog.get('name') == 'styxis-plugin', 'Unexpected Codex catalog name')
    rows = catalog.get('plugins', [])
    require(len(rows) == len(entries) and {r['name'] for r in rows} == {r['name'] for r in entries}, 'Client catalog inventory mismatch')
    for row in rows:
        entry = next(e for e in entries if e['name'] == row['name'])
        source = dict(row['source'])
        source['path'] = source['path'].removeprefix('./')
        require(source == entry['source'], 'Client source pin mismatch')
        require(row.get('policy') == {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'}, 'Explicit install policy required')
        require(bool(row.get('category')), 'Codex category required')


def inspect_source(root, entry, pin):
    root = Path(root).resolve()
    for name, expected in pin['source_file_sha256'].items():
        path = root/name
        require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root), 'Invalid pinned file')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == expected, 'Source file hash mismatch: '+name)
    plugin = root/entry['source']['path']
    data = json.loads((plugin/'.claude-plugin/plugin.json').read_text())
    require(data.get('name') == entry['name'] and data.get('version') == entry['version'], 'Upstream manifest identity mismatch')
    portable = json.loads((plugin/'plugin.json').read_text())
    require(portable.get('name') == entry['name'] and portable.get('version') == entry['version'], 'Portable manifest identity mismatch')
    config = plugin/'.mcp.json'
    if config.exists():
        require(config.is_file() and not config.is_symlink() and config.resolve().is_relative_to(plugin.resolve()), 'Unsafe MCP configuration')
        servers = json.loads(config.read_text()).get('mcpServers')
    else:
        servers = data.get('mcpServers')
    require(isinstance(servers, dict) and servers, 'MCP server configuration required')


def remote(entries, releases):
    for entry in entries:
        source = entry['source']
        with tempfile.TemporaryDirectory(prefix='styxis-catalog-') as folder:
            def git(*args):
                return subprocess.check_output(['git', '-C', folder, *args], timeout=120, stderr=subprocess.PIPE)
            git('init', '--quiet'); git('remote', 'add', 'origin', source['url'])
            git('fetch', '--quiet', '--depth=1', 'origin', source['sha'])
            require(git('rev-parse', 'FETCH_HEAD').decode().strip() == source['sha'], 'Fetched source mismatch')
            git('sparse-checkout', 'set', '--cone', '--', source['path'])
            git('checkout', '--quiet', '--detach', 'FETCH_HEAD')
            inspect_source(folder, entry, releases['plugins'][entry['name']])
        print('Pinned plugin verified: '+entry['name'])


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--remote', action='store_true'); args = parser.parse_args()
    manifest = json.loads((ROOT/'.claude-plugin/marketplace.json').read_text())
    releases = json.loads((ROOT/'release.json').read_text())
    entries = validate(manifest, releases)
    validate_codex(json.loads((ROOT/'.agents/plugins/marketplace.json').read_text()), entries)
    if args.remote: remote(entries, releases)
    print('Catalog and release pins valid: '+str(len(entries)))


if __name__ == '__main__':
    main()
