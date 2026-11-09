import copy
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import register_plugin as r


class RegistrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.source = self.root/'source'; self.catalog = self.root/'catalog'
        self.plugin = self.source/'plugins/sample'; self.plugin.mkdir(parents=True)
        manifest = {'name': 'sample', 'version': '0.2.8', 'mcpServers': './.mcp.json'}
        for name in ('plugin.json', '.claude-plugin/plugin.json', '.codex-plugin/plugin.json'):
            p = self.plugin/name; p.parent.mkdir(exist_ok=True); p.write_text(json.dumps(manifest))
        for name in ('.mcp.json', 'mcp.json'):
            (self.plugin/name).write_text(json.dumps({'mcpServers': {'sample': {'command': 'never-run'}}}))
        self.data = {'status': 'UNPUBLISHED_CANDIDATE', 'entry': {'name': 'sample', 'version': '0.2.8',
            'description': 'Synthetic fixture', 'strict': True, 'source': {'source': 'git-subdir',
            'url': 'https://github.com/example/project.git', 'path': 'plugins/sample', 'ref': 'main'}},
            'source_file_sha256': {}}
        self.pending = self.root/'pending.json'; self.rehash()
        for name in r.CATALOGS:
            p = self.catalog/name; p.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(ROOT/name, p)
        self.before = self.snapshot()

    def rehash(self):
        self.data['source_file_sha256'] = {str(p.relative_to(self.source)): r.hashlib.sha256(p.read_bytes()).hexdigest()
            for p in self.plugin.rglob('*') if p.is_file()}
        self.pending.write_text(json.dumps(self.data))

    def snapshot(self):
        return {n: (self.catalog/n).read_bytes() for n in r.CATALOGS}

    def verified_remote(self, data, sha, folder):
        shutil.copytree(self.source/'plugins', Path(folder)/'plugins')
        r.inspect(folder, data)

    def test_repository_candidates_have_complete_client_metadata(self):
        for path in sorted((ROOT/'pending').glob('*.json')):
            with self.subTest(candidate=path.name):
                data = r.candidate(path)
                self.assertEqual(path.stem, data['entry']['name'])

    def test_offline_candidate_is_not_installable_or_a_source_commit(self):
        data = r.candidate(self.pending); r.inspect(self.source, data)
        self.assertNotIn('sha', data['entry']['source'])
        self.assertEqual(self.snapshot(), self.before)
        with patch.object(r, 'fetch', side_effect=self.verified_remote):
            proposed = r.promote(self.catalog, data, 'a'*40)
        self.assertEqual(self.snapshot(), self.before)
        self.assertEqual(proposed['release.json']['plugins']['sample']['source_sha'], 'a'*40)

    def test_inventory_rejects_changed_added_missing_and_symlink_files(self):
        path = self.plugin/'mcp.json'; saved = path.read_bytes()
        path.write_text('{}')
        with self.assertRaises(ValueError): r.inspect(self.source, self.data)
        path.write_bytes(saved); extra = self.plugin/'extra'; extra.write_text('new')
        with self.assertRaises(ValueError): r.inspect(self.source, self.data)
        extra.unlink(); path.unlink()
        with self.assertRaises(ValueError): r.inspect(self.source, self.data)
        path.write_bytes(saved); extra.symlink_to(path)
        with self.assertRaises(ValueError): r.inspect(self.source, self.data)

    def test_codex_identity_and_mcp_divergence_rejected_even_with_updated_hashes(self):
        path = self.plugin/'.codex-plugin/plugin.json'; m = json.loads(path.read_text()); m['version'] = '0.1.0'
        path.write_text(json.dumps(m)); self.rehash()
        with self.assertRaises(ValueError): r.inspect(self.source, self.data)
        m['version'] = '0.2.8'; path.write_text(json.dumps(m))
        (self.plugin/'mcp.json').write_text('{"mcpServers":{"different":{"command":"never"}}}'); self.rehash()
        with self.assertRaises(ValueError): r.inspect(self.source, self.data)

    def test_client_specific_argv_and_implicit_portable_config_are_supported(self):
        portable = self.plugin/'plugin.json'
        manifest = json.loads(portable.read_text()); manifest.pop('mcpServers')
        portable.write_text(json.dumps(manifest))
        (self.plugin/'mcp.json').write_text(json.dumps({'mcpServers': {'sample': {
            'type': 'stdio', 'command': 'python3', 'args': ['scripts/launcher.py', '--client', 'portable']}}}))
        claude = self.plugin/'.claude-plugin/plugin.json'; manifest = json.loads(claude.read_text())
        manifest['mcpServers'] = {'sample': {'command': 'python3', 'args': [
            '${CLAUDE_PLUGIN_ROOT}/scripts/launcher.py', '--client', 'claude-code']}}
        claude.write_text(json.dumps(manifest)); self.rehash()
        r.inspect(self.source, r.candidate(self.pending))
        for broken in ({'command': ''}, {'command': 'python3', 'args': [1]}, {'command': 'python3', 'type': 'http'}):
            manifest['mcpServers']['sample'] = broken; claude.write_text(json.dumps(manifest)); self.rehash()
            with self.assertRaises(ValueError): r.inspect(self.source, self.data)

    def test_candidate_refuses_invented_commit_unsafe_paths_and_credentials(self):
        for change in ({'sha': 'a'*40}, {'path': '../sample'}, {'path': '.git/sample'},
                       {'url': 'https://token@github.com/example/project.git'}):
            data = copy.deepcopy(self.data); data['entry']['source'].update(change)
            self.pending.write_text(json.dumps(data))
            with self.assertRaises(ValueError): r.candidate(self.pending)

    def test_fetched_sha_mismatch_stops_before_reading_source(self):
        with patch.object(r.subprocess, 'check_output', side_effect=[b'', b'', b'b'*40+b'\n']) as git:
            with self.assertRaisesRegex(ValueError, 'Fetched source mismatch'):
                r.fetch(self.data, 'a'*40, self.root)
        self.assertEqual(git.call_count, 3)
        self.assertEqual(self.snapshot(), self.before)

    def test_remote_inventory_failure_preserves_all_active_files(self):
        (self.plugin/'unexpected').write_text('not in candidate')
        with patch.object(r, 'fetch', side_effect=self.verified_remote):
            with self.assertRaises(ValueError): r.promote(self.catalog, self.data, 'a'*40, True)
        self.assertEqual(self.snapshot(), self.before)

    def test_promotion_preserves_existing_entries_and_rejects_repeat_or_downgrade(self):
        with patch.object(r, 'fetch', side_effect=self.verified_remote):
            proposed = r.promote(self.catalog, self.data, 'a'*40, True)
            for name in r.CATALOGS:
                old = json.loads(self.before[name])['plugins']; new = json.loads((self.catalog/name).read_text())['plugins']
                if isinstance(old, list): self.assertEqual(new[:-1], old)
                else: self.assertEqual({k: new[k] for k in old}, old)
            after = self.snapshot()
            with self.assertRaisesRegex(ValueError, 'already registered'): r.promote(self.catalog, self.data, 'a'*40, True)
            lower = copy.deepcopy(self.data); lower['entry']['version'] = '0.1.0'
            with self.assertRaisesRegex(ValueError, 'already registered'): r.promote(self.catalog, lower, 'b'*40, True)
            self.assertEqual(self.snapshot(), after)

    def test_catalog_drift_during_remote_check_blocks_apply(self):
        def drift(data, sha, folder):
            self.verified_remote(data, sha, folder)
            p = self.catalog/r.CATALOGS[0]; p.write_bytes(p.read_bytes()+b'\n')
        with patch.object(r, 'fetch', side_effect=drift):
            with self.assertRaisesRegex(ValueError, 'changed during'): r.promote(self.catalog, self.data, 'a'*40, True)
        for name in r.CATALOGS[1:]: self.assertEqual((self.catalog/name).read_bytes(), self.before[name])

    def test_partial_publication_preserves_all_originals_and_proposals(self):
        real_replace = r.os.replace; calls = []
        def fail_second(src, dst):
            calls.append(str(dst))
            if len(calls) == 2: raise OSError('synthetic disk failure')
            real_replace(src, dst)
        with patch.object(r, 'fetch', side_effect=self.verified_remote), patch.object(r.os, 'replace', side_effect=fail_second):
            with self.assertRaisesRegex(RuntimeError, 'PARTIAL_CATALOG_PUBLICATION'):
                r.promote(self.catalog, self.data, 'a'*40, True)
        stages = list(self.catalog.glob('.registration-*')); self.assertEqual(len(stages), 1)
        for i, name in enumerate(r.CATALOGS):
            self.assertEqual((stages[0]/'original'/str(i)).read_bytes(), self.before[name])
            self.assertTrue((stages[0]/'proposed'/str(i)).is_file())
        self.assertNotEqual((self.catalog/r.CATALOGS[0]).read_bytes(), self.before[r.CATALOGS[0]])
        for name in r.CATALOGS[1:]: self.assertEqual((self.catalog/name).read_bytes(), self.before[name])


if __name__ == '__main__':
    unittest.main()
