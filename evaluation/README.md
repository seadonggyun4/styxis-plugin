# Reproducible discovery evaluation

This harness separates **candidate retrieval**, **observed selection**, and
**execution conversion**. The local baseline calls no model. The optional Agent
runner uses an existing CLI login; it does not implement a production tool router,
add telemetry or reproduce a proprietary vendor's ranking algorithm.

## Inputs and scope

- `queries.json` 1.0.0: 70 author-written queries, 40 positives and 30 negatives/
  hard negatives, in English and Korean. Relevance targets the public Local
  summary surface only. Custom schema validation, cloud DLP, ETL and semantic
  RAG/eval tasks are explicit hard negatives. Query relevance never grants access.
- Translation pairs share a fixed split. The holdout was inspected during this
  iteration; it is a diagnostic slice, **not an untouched generalization test**.
  Add new independently annotated queries before making deployment-level claims.
- `candidates.json`: 17 server/plugin and 19 tool candidates. The 16 distractors
  are author-written task sketches, including GE/Pandera/Soda, **not official
  vendor metadata or a representative Registry snapshot**.
- `registry-2026-11-02.json`: actual public API observation; separate from those
  local candidate fixtures. The full ecosystem was not downloaded or indexed.
- `before`: original catalog/published contracts. `rejected`: first rewrite that
  reduced plugin recall. Current `installed` and `source` capture Core 3.3.1,
  Local 0.1.7 and the active Official Registry 3.3.1 record. Parity is established
  from installed tools/list and a separate public API snapshot.
- `candidates-2026-11-02-core3.3.0.json` preserves the exact prior corpus, including
  then-unreleased source metadata. Use `--candidates` with this file to reproduce
  historical reports and the availability probe hashes. Never relabel old runtime
  observations as a new installed measurement.

## Run the local baseline

```bash
python3 scripts/evaluate.py --variant before --output /tmp/before.json
python3 scripts/evaluate.py --variant rejected --output /tmp/rejected.json
python3 scripts/evaluate.py --variant installed --output /tmp/installed.json
python3 scripts/evaluate.py --variant source --output /tmp/source.json
python3 -m unittest discover -s tests -v
```

BM25 uses k1=1.5, b=.75, English word tokens and Korean words/bigrams. No stemming,
translation, dense embeddings, learned reranker, query expansion or selection
threshold is hidden in the measurement. Metadata snapshots are refreshed from
reviewed source and a passed actual E2E receipt:

```bash
python3 scripts/snapshot_metadata.py --truthound-root /path/to/Truthound \
  --e2e /tmp/truthound-e2e.json \
  --registry-snapshot evaluation/results/release-3.3.1/registry.json
```

## Import actual client/model observations

Prepare JSONL with one row per observed query/stage. Omit unobserved rows. Empty
rankings mean retrieval was attempted and found nothing; missing rows mean pending.
An optional `selected` list records an explicit decision; absence means selection
was not measured. A selected item must have been retrieved. Example (illustrative
format, **not a recorded model result**):

```json
{"query_id":"q001","stage":"tool","ranking":["check_file","profile_file"],"selected":["check_file"]}
{"query_id":"q041","stage":"tool","ranking":["dataset-editor","check_file"],"selected":["dataset-editor"]}
```

```bash
python3 scripts/evaluate.py --observations /tmp/observed.jsonl \
  --client 'client-name/version' --model 'exact-model-id' \
  --variant installed --output /tmp/observed-report.json
```

For model-free client observations use `--model none`. Capture the actual candidate
set and metadata first; do not import live Registry IDs into the curated fixture
or call local Recall@10 “Registry recall”. Supply `--candidates` and `--dataset`
for the corresponding frozen real observations and qrels. Unknown/duplicate
candidates or query-stage rows are rejected. Adapter/API collection is intentionally
not invented for unavailable client ranking exports. No credential is requested.

## Attempt actual Agent selection

```bash
python3 scripts/evaluate_agent.py --model EXACT_MODEL_ID \
  --output /tmp/agent.json --observations-out /tmp/choices.jsonl
```

This runner first sends a readiness prompt through the installed Codex CLI. Only
after success does it send a balanced 14-query sample and frozen tool metadata.
It withholds relevance labels and validates complete, unique decisions against
the candidate set. This measures metadata-conditioned closed-set selection,
not autonomous MCP search, live Registry ranking or execution. CLI-owned system
and tool context is outside this harness's audit. Import successful observations
with `evaluate.py --observations`; inspect positive and negative denominators.

The [2026-11-02 availability record](results/release-3.3.1/agent-availability.json)
contains actual readiness requests through existing Codex and Claude logins.
Codex requests returned `model_not_found`; Claude's organization disabled
subscription access for Claude Code. No evaluation queries were submitted after
those failures, and no new key/account or policy bypass was attempted. Observed
decisions are zero; selection accuracy and false-selection rate remain null.
Authentication availability failures are not incorrect tool choices.

## Execute actual installation and invocation

Use Python with MCP SDK installed, Claude CLI, Git and UV. The CLI install does
not call a model or alter existing user Claude settings/Truthound permissions:

```bash
python scripts/e2e.py --output /tmp/truthound-e2e.json
python3 scripts/evaluate.py --variant installed --e2e /tmp/truthound-e2e.json \
  --output /tmp/installed-with-execution.json
```

`--marketplace` can select a reviewed local catalog or Git source. The harness
creates synthetic fixtures, explicitly approves only that generated directory,
launches the installed command from unrelated cwd, and checks initialization,
`tools/list`, first CSV call, all three tools on CSV/Parquet, consent denial,
unapproved/symlink/traversal paths, rejected schema arguments, revocation,
unchanged source bytes and raw-value sentinels. Receipts retain no raw result
transcript. Sentinel absence is evidence for those test values, not a formal proof
that arbitrary inputs cannot disclose values. Upstream privacy tests complement it.

## Metrics and report contract

Each stage reports Recall@k, Hit@k, precision@k, full-ranking MRR and nDCG@k.
Registry/plugin/tool k are 10/5/3. Those labels describe the **stage represented
by the local fixture**, not a claim to have queried a production client. With one
relevant server, recall equals hit; multi-intent tool recall can differ from hit.
Negative-only cases have no recall/nDCG denominator. `negative_target_exposure`
measures a ranked Truthound target and is **not false selection**.

Correct-selection rate compares explicit positive selections with the relevant
set and negative abstention from Truthound. False-selection rate counts negative
queries where an explicit selection chose a Truthound target. Both remain null
without observed decisions. E2E rates use passed/attempted receipts; missing
checks in an attempted failed run count as failed. A single 1/1 proves that run,
not population reliability. Do not merge before/after artifacts into one rate.

Every report records date, client, model (null if none ran), Registry observation,
dataset version and digest, full candidate IDs and digest, variant, retrieval
method, k, denominators, slices, failure cases and rerun command. Unobserved web
visibility, live Registry/plugin ranking and external model selection stay pending.

See [results](results/) and the [audit/result interpretation](../docs/audit-2026-11-02.md).


## Verify canonical web deployment

```bash
python3 scripts/verify_web.py --base-url https://styxis-io.com --expect-core-version 3.3.1 --output /tmp/live-web.json
```

This fetches the eight localized public pages, parses canonical/hreflang/JSON-LD,
and checks sitemap and llms.txt. It verifies served content, not search indexing
or citation lift. `--web-root /path/to/styxis-io` instead inspects production build
HTML and always leaves deployment unverified.
