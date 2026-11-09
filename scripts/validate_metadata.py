#!/usr/bin/env python3
"""Validate catalog pins; optionally inspect upstream files without running them."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import tempfile
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, build_opener
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ASSET_LIMIT = 2 * 1024 * 1024
DESKTOP_FILES = {'LICENSE', 'assets/icon.png', 'scripts/launcher.py', 'manifest.json'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def relative(value):
    require(isinstance(value, str) and value and not value.startswith('/'), 'Relative source path required')
    require('\\' not in value and all(p not in ('', '.', '..') for p in value.split('/')), 'Unsafe source path')
    return PurePosixPath(value)


def desktop_asset(entry, pin):
    asset = pin.get('desktop_asset')
    if asset is None:
        return None
    require(isinstance(asset, dict) and set(asset) == {'url', 'sha256', 'version', 'manifest_name'}, 'Invalid Desktop asset fields')
    source = re.fullmatch(r'https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?', entry['source']['url'])
    require(source is not None, 'Desktop asset requires public GitHub source')
    prefix = 'https://github.com/' + source[1] + '/' + source[2] + '/releases/download/'
    require(isinstance(asset['url'], str) and re.fullmatch(re.escape(prefix) + r'[A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*\.mcpb', asset['url']), 'Desktop asset must use the exact source GitHub release')
    require(isinstance(asset['sha256'], str) and re.fullmatch(r'[a-f0-9]{64}', asset['sha256']), 'Invalid Desktop asset hash')
    require(asset['version'] == entry['version'], 'Desktop asset version mismatch')
    require(isinstance(asset['manifest_name'], str) and re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', asset['manifest_name']), 'Invalid Desktop manifest name')
    return asset


def asset_destination(url):
    parsed = urlsplit(url)
    require(parsed.scheme == 'https' and parsed.netloc in {'github.com', 'release-assets.githubusercontent.com', 'objects.githubusercontent.com'} and not parsed.username and not parsed.password and not parsed.fragment, 'Unsafe Desktop asset download destination')


class AssetRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        asset_destination(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download_asset(url):
    asset_destination(url)
    with build_opener(AssetRedirect()).open(url, timeout=30) as response:
        asset_destination(response.geturl())
        length = response.headers.get('Content-Length')
        require(length is None or 0 <= int(length) <= ASSET_LIMIT, 'Desktop asset exceeds size limit')
        data = response.read(ASSET_LIMIT + 1)
    require(len(data) <= ASSET_LIMIT, 'Desktop asset exceeds size limit')
    return data


def inspect_desktop(data, root, entry, pin):
    asset = desktop_asset(entry, pin)
    require(asset is not None, 'Desktop asset pin required')
    require(len(data) <= ASSET_LIMIT and hashlib.sha256(data).hexdigest() == asset['sha256'], 'Desktop artifact hash/size mismatch')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        entries = archive.infolist()
        require(len(entries) == 4 and {i.filename for i in entries} == DESKTOP_FILES, 'Unexpected Desktop archive inventory')
        require(sum(i.file_size for i in entries) <= ASSET_LIMIT, 'Desktop expanded size limit')
        for item in entries:
            require(stat.S_ISREG(item.external_attr >> 16) and not item.flag_bits & 1 and item.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED), 'Unsafe Desktop archive entry')
        plugin = Path(root)/entry['source']['path']
        for name in DESKTOP_FILES - {'manifest.json'}:
            path = plugin/name
            source_pin = pin['source_file_sha256'].get(entry['source']['path']+'/'+name)
            require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(plugin.resolve()), 'Invalid Desktop source file')
            source_data = path.read_bytes()
            require(hashlib.sha256(source_data).hexdigest() == source_pin and archive.read(name) == source_data, 'Desktop/source file mismatch: '+name)
        manifest = json.loads(archive.read('manifest.json'))
    source_manifest = json.loads((plugin/'plugin.json').read_text())
    require(manifest.get('manifest_version') == '0.4' and manifest.get('name') == asset['manifest_name'] and manifest.get('version') == asset['version'], 'Desktop manifest identity mismatch')
    require(source_manifest.get('license') and manifest.get('license') == source_manifest['license'], 'Desktop license mismatch')
    require(manifest.get('server') == {'type': 'python', 'entry_point': 'scripts/launcher.py', 'mcp_config': {'command': 'python3', 'args': ['-I', '-B', '${__dirname}/scripts/launcher.py', 'serve', '--client', 'claude-desktop', '--state', '${user_config.state}']}}, 'Unexpected Desktop launcher declaration')
    config = manifest.get('user_config', {})
    require(set(config) == {'state'} and config['state'].get('type') == 'directory' and config['state'].get('required') is True and 'default' not in config['state'] and not config['state'].get('multiple'), 'Explicit Desktop state required')


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
        desktop_asset(entry, pin)
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
            pin = releases['plugins'][entry['name']]
            inspect_source(folder, entry, pin)
            asset = desktop_asset(entry, pin)
            if asset is not None:
                inspect_desktop(download_asset(asset['url']), folder, entry, pin)
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
