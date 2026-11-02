#!/usr/bin/env python3
"""Run an actual Codex model on a frozen tool-choice fixture; never fake missing decisions.

This measures metadata-conditioned closed-set selection, not live Registry search,
MCP deferred retrieval or tool execution. Uses the existing CLI login, no new keys.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def outcomes(stdout):
    events = []
    for line in stdout.splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    failed = any(e.get('type') in {'error', 'turn.failed'} for e in events)
    # stderr can contain private host metadata; never persist it in public results.
    code = 'model_not_found' if 'model_not_found' in stdout else 'client_request_failed'
    usage = next((e.get('usage') for e in events if e.get('type') == 'turn.completed'), None)
    return failed, code, usage


def validate_choices(document, selected_queries, candidate_ids):
    expected = {q['id'] for q in selected_queries}
    rows = document['observations']
    seen = set()
    normalized = []
    for row in rows:
        query_id = row['query_id']
        if query_id not in expected or query_id in seen:
            raise ValueError('unknown_or_duplicate_query')
        seen.add(query_id)
        ranking, selected = row['ranking'], row['selected']
        if (not isinstance(ranking, list) or not isinstance(selected, list)
                or len(ranking) > 3 or len(set(ranking)) != len(ranking)
                or len(set(selected)) != len(selected) or not set(ranking) <= candidate_ids
                or not set(selected) <= set(ranking)):
            raise ValueError('invalid_ranking_or_selection')
        normalized.append({'query_id':query_id, 'stage':'tool', 'ranking':ranking, 'selected':selected})
    if seen != expected:
        raise ValueError('missing_query_decisions')
    return normalized


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model', required=True)
    p.add_argument('--variant', choices=['before','installed','source'], default='installed')
    p.add_argument('--dataset', type=Path, default=ROOT/'evaluation/queries.json')
    p.add_argument('--candidates', type=Path, default=ROOT/'evaluation/candidates.json')
    p.add_argument('--query-id', action='append')
    p.add_argument('--limit', type=int, default=14)
    p.add_argument('--probe-only', action='store_true')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--observations-out', type=Path, required=True)
    args = p.parse_args()
    data = json.loads(args.dataset.read_text())
    queries = data['queries']
    if args.query_id:
        queries = [q for q in queries if q['id'] in args.query_id]
        if {q['id'] for q in queries} != set(args.query_id):
            p.error('Unknown query ID')
    else:
        # Balanced language/kind round-robin; labels affect sampling only, not prompts.
        buckets = [[q for q in queries if q['language'] == lang and q['kind'] == kind]
                   for kind in ['positive','negative','hard-negative'] for lang in ['en','ko']]
        selected = []
        while any(buckets) and len(selected) < args.limit:
            for bucket in buckets:
                if bucket and len(selected) < args.limit:
                    selected.append(bucket.pop(0))
        queries = selected
    if not queries or args.limit < 1:
        p.error('A nonempty query sample is required')
    corpus = json.loads(args.candidates.read_text())
    docs = corpus['variants'][args.variant]['tool']
    ids = {doc['id'] for doc in docs}
    report = {'schema_version':1, 'date':datetime.now(timezone.utc).isoformat(),
              'client':'Codex CLI', 'model':args.model, 'reasoning_effort':'low',
              'dataset_version':data['version'], 'dataset_sha256':sha(args.dataset),
              'candidate_sha256':sha(args.candidates), 'variant':args.variant,
              'candidate_ids':sorted(ids), 'query_ids':[q['id'] for q in queries],
              'method':'actual model; metadata-conditioned closed-set selection; no MCP execution',
              'status':'not_evaluated', 'observed_decisions':0, 'selection_rate':None,
              'limits':['author-written distractors', 'no live Registry/plugin ranking',
                        'no autonomous tool search or execution', 'not an untouched benchmark']}
    report['client_version'] = subprocess.check_output(['codex','--version'], text=True, stderr=subprocess.DEVNULL).strip()
    observations = []
    with tempfile.TemporaryDirectory(prefix='truthound-agent-choice-') as td:
        work = Path(td)
        command = ['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check',
                   '--sandbox','read-only','--model',args.model,'-c','model_reasoning_effort="low"',
                   '-c','features.plugins=false','-c','features.apps=false','-c','features.shell_tool=false',
                   '--json','-C',str(work)]
        try:
            probe = subprocess.run(command, input='Return exactly {"ready":true}. Use no tools.',
                                   capture_output=True, text=True, timeout=90)
            failed, error_code, _ = outcomes(probe.stdout)
            if probe.returncode or failed:
                report['blocker'] = {'stage':'readiness', 'code':error_code, 'exit_code':probe.returncode}
            elif args.probe_only:
                report['status'] = 'ready_unmeasured'
            else:
                choice_schema = {
                    'type':'object', 'additionalProperties':False,
                    'required':['query_id','ranking','selected'],
                    'properties':{
                        'query_id':{'type':'string','enum':[q['id'] for q in queries]},
                        'ranking':{'type':'array','items':{'type':'string','enum':sorted(ids)}},
                        'selected':{'type':'array','items':{'type':'string','enum':sorted(ids)}},
                    },
                }
                schema = {
                    'type':'object', 'additionalProperties':False, 'required':['observations'],
                    'properties':{'observations':{'type':'array','items':choice_schema}},
                }
                schema_path, final = work/'schema.json', work/'final.json'
                schema_path.write_text(json.dumps(schema))
                prompt = ('Evaluate tool choice using ONLY the supplied metadata and user requests. '
                          'Do not read files or invoke tools. Do not assume any tool is required. '
                          'For each query rank up to three suitable candidate IDs and select the IDs '
                          'needed to fulfill it. Select none if no available candidate fits or clarification is required. '
                          'Do not substitute unsupported capabilities. IDs describe evaluation fixture tasks, '
                          'not an endorsement or verified vendor integration. Return only the schema-constrained JSON.\n'
                          +json.dumps({'candidates':[{'id':d['id'],'description':d['text']} for d in docs],
                                       'queries':[{'id':q['id'],'query':q['query']} for q in queries]},ensure_ascii=False))
                result = subprocess.run(command+['--output-schema',str(schema_path),'-o',str(final)],
                                        input=prompt, capture_output=True,text=True,timeout=300)
                failed,error_code,usage=outcomes(result.stdout)
                if result.returncode or failed or not final.exists():
                    report['blocker']={'stage':'selection','code':error_code,'exit_code':result.returncode}
                else:
                    observations=validate_choices(json.loads(final.read_text()),queries,ids)
                    report.update(status='observed',observed_decisions=len(observations),usage=usage)
        except subprocess.TimeoutExpired:
            report['blocker']={'stage':'client','code':'timeout'}
        except (ValueError,KeyError) as error:
            report['blocker']={'stage':'output-validation','code':type(error).__name__}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.observations_out.parent.mkdir(parents=True,exist_ok=True)
    args.observations_out.write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in observations))
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:report.get(k) for k in ['client_version','model','status','observed_decisions','blocker']}))
    return 0 if report['status'] in {'observed','ready_unmeasured'} else 2

if __name__ == '__main__':
    raise SystemExit(main())
