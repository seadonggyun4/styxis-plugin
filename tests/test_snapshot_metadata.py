"""Published parity must require matching installed versions and an active record."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).parents[1]


class PublicationSnapshotBoundary(unittest.TestCase):
    def snapshot(self, mutate=None):
        with tempfile.TemporaryDirectory() as td:
            work = Path(td)
            source = work/'source'
            (source/'plugins/truthound/.claude-plugin').mkdir(parents=True)
            (source/'src/truthound/mcp').mkdir(parents=True)
            manifest = {'version':'0.1.7', 'description':'fixture plugin'}
            registry = {'name':'io.github.seadonggyun4/truthound', 'version':'3.3.1',
                        'description':'fixture Registry', 'packages':[{'version':'3.3.1'}]}
            names = ['check_file','profile_file','scan_pii']
            tools = {name:(None,'fixture '+name) for name in names}
            receipt = {'status':'passed','plugin_version':'0.1.7','core_version':'3.3.1',
                       'tools':[{'name':name,'description':tools[name][1]} for name in names]}
            live = {'server':registry, '_meta':{'io.modelcontextprotocol.registry/official':
                                               {'status':'active','isLatest':True}}}
            if mutate:
                mutate(receipt, live)
            (source/'plugins/truthound/.claude-plugin/plugin.json').write_text(json.dumps(manifest))
            (source/'server.json').write_text(json.dumps(registry))
            (source/'src/truthound/mcp/server.py').write_text('TOOLS = '+repr(tools))
            (work/'receipt.json').write_text(json.dumps(receipt))
            (work/'registry.json').write_text(json.dumps(live))
            candidates = work/'candidates.json'
            before = (ROOT/'evaluation/candidates-2026-11-02-core3.3.0.json').read_bytes()
            candidates.write_bytes(before)
            result = subprocess.run([sys.executable,str(ROOT/'scripts/snapshot_metadata.py'),
                '--truthound-root',str(source),'--e2e',str(work/'receipt.json'),
                '--registry-snapshot',str(work/'registry.json'),'--candidates',str(candidates)],
                capture_output=True,text=True)
            return result.returncode, candidates.read_bytes(), before

    def test_unpublished_or_mismatched_records_cannot_rewrite_candidate_provenance(self):
        mutations = [
            lambda receipt, live: receipt.update(plugin_version='0.1.6'),
            lambda receipt, live: live['server']['packages'][0].update(version='3.3.0'),
            lambda receipt, live: live['_meta']['io.modelcontextprotocol.registry/official'].update(status='deprecated'),
            lambda receipt, live: live['_meta']['io.modelcontextprotocol.registry/official'].update(isLatest=False),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                code, after, before = self.snapshot(mutate)
                self.assertNotEqual(code,0)
                self.assertEqual(after,before)

    def test_matching_installed_metadata_can_replace_unreleased_provenance(self):
        code, after, _ = self.snapshot()
        self.assertEqual(code,0)
        corpus = json.loads(after)
        self.assertEqual(corpus['installed_core_version'],'3.3.1')
        self.assertEqual(corpus['source_metadata_status'],
                         'Matches tested installed artifact and observed Registry record')
        self.assertEqual(corpus['variants']['installed']['tool'][0]['text'],
                         'check_file fixture check_file')


if __name__ == '__main__':
    unittest.main()
