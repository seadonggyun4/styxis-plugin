#!/usr/bin/env python3
"""Reproduce Local MCP outputs on generated CSV/Parquet only.

Run with a Python environment containing truthound[mcp]==3.3.1 and the MCP SDK.
Only a temporary synthetic directory is allowed; existing plugin grants are untouched.
The receipt excludes temporary paths, raw values and volatile execution IDs/times.
"""
import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import sys
import tempfile


async def verify(work):
    import polars as pl
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    allowed = work / 'synthetic'
    allowed.mkdir()
    csv = allowed / 'example.csv'
    csv.write_text('email,score\ngeo-example-721@example.com,1\ngeo-example-721@example.com,1\n,3\n', encoding='utf-8')
    parquet = allowed / 'example.parquet'
    pl.read_csv(csv).write_parquet(parquet)
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [csv, parquet]}
    outside = work / 'outside.csv'
    outside.write_text('email\nnot-in-output-482@example.com\n', encoding='utf-8')
    results = []
    # CLI process-local allowlist; never reads or changes a desktop plugin consent file.
    params = StdioServerParameters(command=sys.executable,
        args=['-I', '-m', 'truthound.mcp', 'serve', '--allow-dir', str(allowed)],
        cwd=str(work), env={'POLARS_MAX_THREADS': '1'})
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as client:
            info = await client.initialize()
            assert info.serverInfo.version == version('truthound') == '3.3.1'
            tools = [t.name for t in (await client.list_tools()).tools]
            assert set(tools) == {'check_file', 'profile_file', 'scan_pii'}
            for file in [csv, parquet]:
                for name in tools:
                    result = await client.call_tool(name, {'path': str(file)})
                    assert not result.isError and result.structuredContent['ok']
                    payload = result.structuredContent
                    serialized = json.dumps(payload)
                    assert 'geo-example-721@example.com' not in serialized
                    assert 'not-in-output-482@example.com' not in serialized
                    assert str(work) not in serialized
                    if name == 'check_file':
                        assert payload['data']['success'] is False
                        assert payload['data']['issue_count'] == 2
                    elif name == 'profile_file':
                        assert payload['data']['row_count'] == 3
                        assert payload['data']['column_count'] == 2
                    else:
                        assert payload['data']['count_semantics'] == 'estimated_from_first_1000_non_null_values'
                        assert payload['data']['findings'][0]['count'] == 2
                    results.append({'format': file.suffix[1:], 'tool': name, 'result': payload})
            denied = await client.call_tool('check_file', {'path': str(outside)})
            assert denied.isError and denied.structuredContent['error']['code'] == 'access_denied'
    assert all(hashlib.sha256(p.read_bytes()).hexdigest() == before[p.name] for p in [csv, parquet])
    return {'schema_version': 1, 'observed_at': datetime.now(timezone.utc).isoformat(),
        'package_version': version('truthound'), 'mcp_sdk_version': version('mcp'),
        'protocol_version': info.protocolVersion, 'fixture': {'rows': 3, 'columns': 2,
        'csv_sha256': before[csv.name], 'contains_synthetic_email': True},
        'results': results, 'checks': {'outside_directory_denied': True,
        'source_files_unchanged': True, 'synthetic_raw_sentinels_absent': True},
        'scope': 'Actual published Local MCP execution on generated fixtures; not a web-search exposure or Agent-selection benchmark.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='truthound-local-example-') as directory:
        receipt = asyncio.run(verify(Path(directory)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
    print('Published Local MCP synthetic example completed: 6 calls and denied outside path.')


if __name__ == '__main__':
    main()
