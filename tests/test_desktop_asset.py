import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import validate_metadata as v


class DesktopAssetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.plugin = self.root/'plugins/golem'
        self.entry = {'version': '0.2.8', 'source': {'url': 'https://github.com/example/Golem.git', 'path': 'plugins/golem'}}
        self.asset = {'url': 'https://github.com/example/Golem/releases/download/golem-plugin-v0.2.8/golem-launcher-0.2.8.mcpb',
                      'sha256': '0'*64, 'version': '0.2.8', 'manifest_name': 'golem-prepare'}
        self.payload = {'LICENSE': b'fixture license', 'assets/icon.png': b'fixture icon', 'scripts/launcher.py': b'# never executed\n'}
        for name, data in self.payload.items():
            path = self.plugin/name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(data)
        (self.plugin/'plugin.json').write_text(json.dumps({'license': 'PolyForm-Noncommercial-1.0.0'}))
        self.pin = {'desktop_asset': self.asset, 'source_file_sha256': {
            'plugins/golem/'+name: hashlib.sha256(data).hexdigest() for name, data in self.payload.items()}}
        self.manifest = {'manifest_version': '0.4', 'name': 'golem-prepare', 'version': '0.2.8', 'license': 'PolyForm-Noncommercial-1.0.0',
            'server': {'type': 'python', 'entry_point': 'scripts/launcher.py', 'mcp_config': {'command': 'python3', 'args': [
                '-I', '-B', '${__dirname}/scripts/launcher.py', 'serve', '--client', 'claude-desktop', '--state', '${user_config.state}']}},
            'user_config': {'state': {'type': 'directory', 'required': True}}}

    def archive(self, extra=None, mode=None):
        payload = dict(self.payload); payload['manifest.json'] = json.dumps(self.manifest).encode()
        if extra: payload.update(extra)
        result = io.BytesIO()
        with zipfile.ZipFile(result, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in payload.items():
                info = zipfile.ZipInfo(name); info.create_system = 3
                info.external_attr = ((mode if mode and name == 'scripts/launcher.py' else 0o100644) << 16)
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, data)
        data = result.getvalue(); self.asset['sha256'] = hashlib.sha256(data).hexdigest()
        return data

    def test_valid_archive_is_bound_to_verified_source_without_execution(self):
        v.inspect_desktop(self.archive(), self.root, self.entry, self.pin)
        self.assertIsNone(v.desktop_asset(self.entry, {}))

    def test_foreign_or_credential_or_unbounded_url_and_pin_rejected(self):
        for url in ('http://github.com/example/Golem/releases/download/v/a.mcpb',
                    self.asset['url']+'?token=secret', self.asset['url']+'#fragment',
                    self.asset['url'].replace('github.com/', 'token@github.com/'),
                    self.asset['url'].replace('/example/Golem/', '/other/Golem/'),
                    self.asset['url'].replace('/golem-plugin-v0.2.8/', '/%2e%2e/'),
                    self.asset['url'].replace('.mcpb', '.zip')):
            pin = copy.deepcopy(self.pin); pin['desktop_asset']['url'] = url
            with self.subTest(url=url), self.assertRaises(ValueError): v.desktop_asset(self.entry, pin)
        for key, value in (('sha256', 'a'*40), ('version', '0.2.7'), ('manifest_name', '../golem')):
            pin = copy.deepcopy(self.pin); pin['desktop_asset'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): v.desktop_asset(self.entry, pin)

    def test_bad_hash_unexpected_entries_symlinks_and_expanded_limit_rejected(self):
        data = self.archive()
        with self.assertRaises(ValueError): v.inspect_desktop(data+b'x', self.root, self.entry, self.pin)
        for data in (self.archive({'../outside': b'x'}), self.archive(mode=0o120777), self.archive({'LICENSE': b'x'*(v.ASSET_LIMIT+1)})):
            self.asset['sha256'] = hashlib.sha256(data).hexdigest()
            with self.assertRaises(ValueError): v.inspect_desktop(data, self.root, self.entry, self.pin)

    def test_source_or_manifest_drift_rejected_even_with_new_archive_pin(self):
        for key, value in (('name', 'other'), ('version', '0.2.9'), ('license', 'MIT')):
            saved = self.manifest[key]; self.manifest[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError): v.inspect_desktop(self.archive(), self.root, self.entry, self.pin)
            self.manifest[key] = saved
        self.manifest['server']['mcp_config']['args'].append('--approve-launcher')
        with self.assertRaises(ValueError): v.inspect_desktop(self.archive(), self.root, self.entry, self.pin)
        self.manifest['server']['mcp_config']['args'].pop()
        data = self.archive({'scripts/launcher.py': b'# replaced'})
        with self.assertRaises(ValueError): v.inspect_desktop(data, self.root, self.entry, self.pin)

    def test_download_is_bounded_and_redirects_stay_public_https(self):
        response = MagicMock(); response.__enter__.return_value = response
        response.geturl.return_value = 'https://release-assets.githubusercontent.com/path?signature=fixture'
        response.headers = {}; response.read.return_value = b'fixture'
        opener = MagicMock(); opener.open.return_value = response
        with patch.object(v, 'build_opener', return_value=opener):
            self.assertEqual(v.download_asset(self.asset['url']), b'fixture')
            response.read.assert_called_once_with(v.ASSET_LIMIT+1)
            response.read.return_value = b'x'*(v.ASSET_LIMIT+1)
            with self.assertRaises(ValueError): v.download_asset(self.asset['url'])
            response.headers = {'Content-Length': str(v.ASSET_LIMIT+1)}
            with self.assertRaises(ValueError): v.download_asset(self.asset['url'])
        for url in ('http://github.com/a', 'https://token@github.com/a', 'https://localhost/a', 'https://github.com:443/a'):
            with self.assertRaises(ValueError): v.asset_destination(url)

    def test_existing_releases_without_asset_are_unchanged(self):
        catalog = json.loads((ROOT/'.claude-plugin/marketplace.json').read_text())
        releases = json.loads((ROOT/'release.json').read_text())
        before = copy.deepcopy(releases)
        v.validate(catalog, releases)
        self.assertEqual(releases, before)


if __name__ == '__main__':
    unittest.main()
