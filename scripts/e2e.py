#!/usr/bin/env python3
"""Isolated real Claude install + frozen UV/MCP checks on generated fixtures only.

Requires Python with mcp SDK installed, claude, uv and Git. No model/API call.
Permission approval applies only to the synthetic directory this program creates.
"""
import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone


def run(argv, *, cwd, env):
    return subprocess.run(argv, cwd=cwd, env=env, check=True, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180).stdout


async def probe(plugin, connection, work, env, proof):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    # Reproduce Claude's effective settings; do not repair cwd/arguments in the harness.
    args = [arg.replace('${CLAUDE_PLUGIN_ROOT}', str(plugin)) for arg in connection['args']]
    if any('${' in arg for arg in args):
        raise ValueError('unresolved_launcher_variable')
    approved = work / 'synthetic-approved'
    approved.mkdir()
    csv = approved / 'input.csv'
    sentinel = 'discovery-sentinel-721@example.com'
    csv.write_text(f'email,count\n{sentinel},1\n{sentinel},1\n,3\n')
    original = hashlib.sha256(csv.read_bytes()).hexdigest()
    outside = work / 'unapproved.csv'
    outside.write_text('email\nnever-disclose-482@example.com\n')
    escape = approved / 'escape.csv'
    escape.symlink_to(outside)
    config = work / 'consent' / 'permissions.json'
    runtime = work / 'uv-runtime'
    env = {**env, 'TRUTHOUND_OPENAI_CONFIG': str(config),
           'UV_PROJECT_ENVIRONMENT': str(runtime), 'UV_CACHE_DIR': str(work / 'uv-cache'),
           'POLARS_MAX_THREADS': '1'}
    checks = proof['checks']
    async with stdio_client(StdioServerParameters(command=connection['command'], args=args,
                            cwd=str(work), env=env)) as (read, write):
        async with ClientSession(read, write) as client:
            initialized = await client.initialize()
            checks['mcp_startup'] = True
            proof['protocol_version'] = initialized.protocolVersion
            proof['core_version'] = initialized.serverInfo.version
            listed = (await client.list_tools()).tools
            proof['tools'] = [tool.model_dump(mode='json', exclude_none=True) for tool in listed]
            assert {t.name for t in listed} == {'check_file', 'profile_file', 'scan_pii'}
            checks['tools_list'] = True
            transcripts = []
            for tool in listed:
                denied = await client.call_tool(tool.name, {'path': str(csv)})
                assert denied.isError and denied.structuredContent['error']['code'] == 'access_denied'
                transcripts.append(denied.model_dump_json())
            checks['deny_before_approval'] = True
            python = runtime / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
            configure = [str(python), str(plugin / 'permissions.py'), '--config', str(config)]
            # Explicit task-authorized approval of generated fixtures, never an existing user directory.
            run(configure + ['--allow-dir', str(approved), '--confirm'], cwd=work, env=env)
            result = await client.call_tool('check_file', {'path': str(csv)})
            assert not result.isError and result.structuredContent['ok']
            assert result.structuredContent['data']['success'] is False
            transcripts.append(result.model_dump_json())
            checks['first_call'] = True
            checks['quality_failure_is_not_transport_error'] = True
            for name in ['profile_file', 'scan_pii']:
                result = await client.call_tool(name, {'path': str(csv)})
                assert not result.isError and result.structuredContent['ok']
                transcripts.append(result.model_dump_json())
            checks['all_three_tools'] = True
            # Generate Parquet using the actual frozen installation, without extra dependencies.
            parquet = approved / 'input.parquet'
            run([str(python), '-c', 'import polars,sys; polars.read_csv(sys.argv[1]).write_parquet(sys.argv[2])',
                 str(csv), str(parquet)], cwd=work, env=env)
            for name in ['check_file', 'profile_file', 'scan_pii']:
                result = await client.call_tool(name, {'path': str(parquet)})
                assert not result.isError and result.structuredContent['ok']
                transcripts.append(result.model_dump_json())
            checks['parquet'] = True
            for target in [outside, escape]:
                denied = await client.call_tool('profile_file', {'path': str(target)})
                assert denied.isError and denied.structuredContent['error']['code'] == 'access_denied'
                transcripts.append(denied.model_dump_json())
            checks['deny_unapproved_and_symlink'] = True
            denied = await client.call_tool('profile_file', {'path': str(approved / '..' / 'unapproved.csv')})
            assert denied.isError and denied.structuredContent['error']['code'] == 'invalid_path'
            checks['deny_traversal'] = True
            extra = await client.call_tool('check_file', {'path': str(csv), 'schema': {}})
            assert extra.isError and extra.structuredContent['error']['code'] == 'invalid_arguments'
            checks['reject_unsupported_schema'] = True
            run(configure + ['--revoke'], cwd=work, env=env)
            denied = await client.call_tool('check_file', {'path': str(csv)})
            assert denied.isError and denied.structuredContent['error']['code'] == 'access_denied'
            checks['revoke_without_restart'] = True
            assert sentinel not in ''.join(transcripts)
            assert 'never-disclose-482@example.com' not in ''.join(transcripts)
            checks['no_raw_sentinel_in_results'] = True
            assert hashlib.sha256(csv.read_bytes()).hexdigest() == original
            checks['source_unchanged'] = True
    proof['launcher'] = connection


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--marketplace', default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--expect-source-sha', help='Fail if the actually installed source commit differs')
    args = parser.parse_args()
    proof = {'schema_version': 1, 'date': datetime.now(timezone.utc).isoformat(),
             'client': 'Claude Code CLI + Python MCP SDK', 'model': None,
             'sdk_version': importlib.metadata.version('mcp'), 'os': __import__('platform').platform(),
             'marketplace': args.marketplace, 'checks': {}, 'status': 'failed'}
    try:
        with tempfile.TemporaryDirectory(prefix='styxis-e2e-') as td:
            work = Path(td).resolve()
            env = {**os.environ, 'CLAUDE_CONFIG_DIR': str(work / 'claude')}
            proof['client_version'] = run(['claude', '--version'], cwd=work, env=env).strip()
            run(['claude', 'plugin', 'marketplace', 'add', args.marketplace, '--scope', 'user'], cwd=work, env=env)
            run(['claude', 'plugin', 'install', 'truthound@styxis-plugin', '--scope', 'user'], cwd=work, env=env)
            proof['checks']['install'] = True
            installed = json.loads(run(['claude', 'plugin', 'list', '--json'], cwd=work, env=env))
            entry = next(x for x in installed if x['id'] == 'truthound@styxis-plugin')
            proof['plugin_version'] = entry['version']
            index = json.loads((work / 'claude/plugins/installed_plugins.json').read_text())
            proof['source_sha'] = index['plugins']['truthound@styxis-plugin'][0].get('gitCommitSha')
            if args.expect_source_sha:
                assert proof['source_sha'] == args.expect_source_sha, 'installed_source_pin_mismatch'
                proof['checks']['source_pin'] = True
            plugin = Path(entry['installPath'])
            for file in ['.claude-plugin/plugin.json', '.mcp.json', 'uv.lock', 'server.py', 'permissions.py',
                         'skills/truthound-setup/SKILL.md']:
                assert (plugin / file).is_file(), file
            proof['checks']['standalone_manifest'] = True
            asyncio.run(probe(plugin, entry['mcpServers']['truthound'], work, env, proof))
            proof['status'] = 'passed'
    except BaseException as error:
        # Never persist subprocess stderr/paths/configs/secrets as evidence.
        proof['failure'] = {'type': type(error).__name__, 'message': 'See local execution diagnostics; no sensitive transcript retained.'}
        raise
    finally:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
        print(json.dumps({k:v for k,v in proof.items() if k != 'tools'}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
