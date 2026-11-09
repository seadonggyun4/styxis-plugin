#!/usr/bin/env python3
"""Inspect unpublished candidates; promote only exact remotely fetched bytes.

No plugin code, launcher, installation, Git checkout, commit or push is run.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from urllib.parse import urlsplit

import validate_metadata as v

ROOT = Path(__file__).resolve().parents[1]
CATALOGS = ('.claude-plugin/marketplace.json', '.agents/plugins/marketplace.json', 'release.json')


def candidate(path):
    data = json.loads(Path(path).read_text())
    v.require(set(data) == {'status', 'entry', 'source_file_sha256'}, 'Unexpected candidate fields')
    v.require(data['status'] == 'UNPUBLISHED_CANDIDATE', 'Unpublished candidate required')
    entry = data['entry']; source = entry['source']
    v.require(set(source) == {'source', 'url', 'path', 'ref'}, 'Candidate must not claim a source SHA')
    v.require(source['source'] == 'git-subdir', 'Git subdirectory required')
    v.relative(source['path'])
    v.require('.git' not in Path(source['path']).parts, 'Unsafe source path')
    url = urlsplit(source['url'])
    v.require(url.scheme == 'https' and url.hostname == 'github.com' and not url.username
              and not url.password and not url.port and not url.query and not url.fragment
              and re.fullmatch(r'/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?', url.path),
              'Public GitHub HTTPS repository required')
    v.require(re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', entry['name']), 'Invalid name')
    v.require(re.fullmatch(r'\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?', entry['version']), 'Invalid version')
    v.require(entry.get('strict') is True and bool(entry.get('description')), 'Strict description required')
    v.require(not set(entry).intersection(('skills', 'mcpServers', 'hooks', 'agents', 'commands')), 'Component override')
    hashes = data['source_file_sha256']
    v.require(isinstance(hashes, dict) and hashes, 'Complete file inventory required')
    for name, digest in hashes.items():
        v.relative(name)
        v.require(name.startswith(source['path']+'/') and '.git' not in Path(name).parts, 'Hash outside plugin')
        v.require(isinstance(digest, str) and re.fullmatch('[a-f0-9]{64}', digest), 'Invalid file hash')
    for name in ('plugin.json', '.claude-plugin/plugin.json', '.codex-plugin/plugin.json', '.mcp.json', 'mcp.json'):
        v.require(source['path']+'/'+name in hashes, 'Missing client file: '+name)
    return data


def inspect(root, data):
    root = Path(root).resolve(); entry = data['entry']; plugin = root/entry['source']['path']
    v.require(plugin.is_dir() and not any(p.is_symlink() for p in [plugin, *plugin.parents] if p != root and p.is_relative_to(root)), 'Unsafe plugin directory')
    actual = {}
    for path in plugin.rglob('*'):
        v.require(not path.is_symlink() and (path.is_file() or path.is_dir()), 'Unsupported source entry')
        if path.is_file(): actual[str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    v.require(actual == data['source_file_sha256'], 'Complete plugin inventory mismatch')
    v.inspect_source(root, entry, {'source_file_sha256': actual})
    configs = [json.loads((plugin/name).read_text())['mcpServers'] for name in ('.mcp.json', 'mcp.json')]
    for name in ('plugin.json', '.claude-plugin/plugin.json', '.codex-plugin/plugin.json'):
        manifest = json.loads((plugin/name).read_text())
        v.require(manifest.get('name') == entry['name'] and manifest.get('version') == entry['version'], 'Client identity mismatch')
        config = manifest.get('mcpServers')
        if config is None and name == 'plugin.json': config = './mcp.json'
        v.require(isinstance(config, dict) and bool(config) or config in ('./.mcp.json', './mcp.json'), 'Invalid client MCP reference')
        if isinstance(config, dict): configs.append(config)
    for servers in configs:
        v.require(isinstance(servers, dict) and bool(servers) and set(servers) == set(configs[0]), 'MCP server identity mismatch')
        for server in servers.values():
            v.require(isinstance(server, dict) and server.get('type', 'stdio') == 'stdio'
                      and isinstance(server.get('command'), str) and bool(server['command'].strip())
                      and isinstance(server.get('args', []), list)
                      and all(isinstance(arg, str) for arg in server.get('args', [])), 'Invalid client stdio declaration')
    # Client argv/cwd differences are intentional; exact bytes are pinned above.


def fetch(data, sha, folder):
    v.require(re.fullmatch('[a-f0-9]{40}', sha), 'Exact 40-character commit required')
    # Ignore global/system Git config, credentials and hooks; never checkout filters.
    env = {k: val for k, val in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT='0')
    def git(*args):
        return subprocess.check_output(['git', '-C', str(folder), '-c', 'credential.helper=',
            '-c', 'core.hooksPath='+os.devnull, '-c', 'protocol.file.allow=never', *args],
            env=env, stderr=subprocess.PIPE, timeout=120)
    git('init', '--quiet')
    git('fetch', '--quiet', '--depth=1', '--no-tags', data['entry']['source']['url'], sha)
    v.require(git('rev-parse', 'FETCH_HEAD^{commit}').decode().strip() == sha, 'Fetched source mismatch')
    prefix = data['entry']['source']['path']
    for item in git('ls-tree', '-r', '-z', sha, '--', prefix).split(b'\0'):
        if not item: continue
        metadata, rawname = item.split(b'\t', 1); mode, kind, oid = metadata.split(); name = rawname.decode()
        v.relative(name)
        v.require(name.startswith(prefix+'/') and '.git' not in Path(name).parts and kind == b'blob'
                  and mode in (b'100644', b'100755'), 'Unsafe fetched entry')
        target = Path(folder)/name; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(git('cat-file', 'blob', oid.decode()))
    inspect(folder, data)


def promote(root, data, sha, apply=False):
    root = Path(root); entry = copy.deepcopy(data['entry']); entry['source']['sha'] = sha
    original = {name: (root/name).read_bytes() for name in CATALOGS}
    claude, codex, releases = [json.loads(original[name]) for name in CATALOGS]
    entries = v.validate(claude, releases); v.validate_codex(codex, entries)
    v.require(entry['name'] not in releases['plugins'], 'Plugin already registered; explicit release update required')
    # Verify exact remote source even for dry runs; local inspection cannot promote.
    with tempfile.TemporaryDirectory(prefix='styxis-registration-') as folder:
        fetch(data, sha, folder)
    claude['plugins'].append(entry)
    codex_source = dict(entry['source']); codex_source['path'] = './'+codex_source['path']
    codex['plugins'].append({'name': entry['name'], 'source': codex_source,
        'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL'}, 'category': 'Developer Tools'})
    releases['plugins'][entry['name']] = {'plugin_version': entry['version'], 'source_url': entry['source']['url'],
        'source_path': entry['source']['path'], 'source_sha': sha, 'source_file_sha256': data['source_file_sha256']}
    v.validate_codex(codex, v.validate(claude, releases))
    proposed = dict(zip(CATALOGS, (claude, codex, releases)))
    if apply:
        for name in CATALOGS: v.require((root/name).read_bytes() == original[name], 'Catalog changed during verification')
        # Files cannot be atomically committed together. Preserve staged copies on
        # an I/O failure and report partial publication, without automatic rollback.
        stage = Path(tempfile.mkdtemp(prefix='.registration-', dir=root))
        (stage/'proposed').mkdir(); (stage/'original').mkdir()
        for i, name in enumerate(CATALOGS):
            (stage/'proposed'/str(i)).write_text(json.dumps(proposed[name], ensure_ascii=False, indent=2)+'\n')
            (stage/'original'/str(i)).write_bytes(original[name])
        try:
            for i, name in enumerate(CATALOGS):
                temporary = stage/('replace-'+str(i))
                shutil.copyfile(stage/'proposed'/str(i), temporary)
                os.replace(temporary, root/name)
        except OSError as error:
            raise RuntimeError('PARTIAL_CATALOG_PUBLICATION; preserve '+str(stage)) from error
        shutil.rmtree(stage)
    return proposed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--source-tree', type=Path); mode.add_argument('--source-sha')
    parser.add_argument('--apply', action='store_true'); args = parser.parse_args()
    data = candidate(args.candidate)
    if args.source_tree:
        v.require(not args.apply, 'Local source cannot activate a catalog')
        inspect(args.source_tree, data); print('UNPUBLISHED_CANDIDATE verified; no active catalog changes')
    else:
        promote(ROOT, data, args.source_sha, args.apply)
        print('Catalog applied locally' if args.apply else 'Fetched source verified; dry run, no catalog changes')


if __name__ == '__main__':
    main()
