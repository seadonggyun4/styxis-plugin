import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('validator', ROOT/'scripts/validate_metadata.py')
v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = json.loads((ROOT/'.claude-plugin/marketplace.json').read_text())
        self.releases = json.loads((ROOT/'release.json').read_text())

    def test_second_plugin_needs_only_catalog_and_release_entry(self):
        entry = copy.deepcopy(self.catalog['plugins'][0]); entry['name'] = 'sample'
        self.catalog['plugins'].append(entry)
        self.releases['plugins']['sample'] = copy.deepcopy(self.releases['plugins']['truthound'])
        self.assertEqual(len(v.validate(self.catalog, self.releases)), 2)

    def test_duplicate_and_unmatched_releases_rejected(self):
        self.catalog['plugins'].append(copy.deepcopy(self.catalog['plugins'][0]))
        with self.assertRaises(ValueError): v.validate(self.catalog, self.releases)
        self.catalog['plugins'].pop(); self.releases['plugins']['extra'] = {}
        with self.assertRaises(ValueError): v.validate(self.catalog, self.releases)

    def test_pin_drift_and_component_override_rejected(self):
        entry = self.catalog['plugins'][0]; entry['source']['sha'] = '0'*40
        with self.assertRaises(ValueError): v.validate(self.catalog, self.releases)
        entry['source']['sha'] = self.releases['plugins']['truthound']['source_sha']
        entry['mcpServers'] = {}
        with self.assertRaises(ValueError): v.validate(self.catalog, self.releases)

    def test_unsafe_paths_and_credential_urls_rejected(self):
        entry = self.catalog['plugins'][0]
        for path in ('../plugin', '/plugin', 'plugins/../plugin', 'plugins\\plugin'):
            entry['source']['path'] = path
            with self.assertRaises(ValueError): v.validate(self.catalog, self.releases)
        entry['source']['url'] = 'https://secret@example.com/repo.git'
        with self.assertRaises(ValueError): v.validate(self.catalog, self.releases)

    def test_source_hash_and_manifest_identity_checked(self):
        entry = self.catalog['plugins'][0]
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); path = root/entry['source']['path']/'.claude-plugin/plugin.json'
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'name':'wrong','version':entry['version'],'mcpServers':{'sample':{}}}))
            pin = {'source_file_sha256':{str(path.relative_to(root)):v.hashlib.sha256(path.read_bytes()).hexdigest()}}
            with self.assertRaises(ValueError): v.inspect_source(root, entry, pin)
            path.write_text(json.dumps({'name':entry['name'],'version':entry['version'],'mcpServers':{'sample':{}}}))
            pin['source_file_sha256'][str(path.relative_to(root))] = v.hashlib.sha256(path.read_bytes()).hexdigest()
            v.inspect_source(root, entry, pin)
            path.write_text('{}')
            with self.assertRaises(ValueError): v.inspect_source(root, entry, pin)

if __name__ == '__main__': unittest.main()
