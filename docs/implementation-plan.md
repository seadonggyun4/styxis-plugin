# Agent discovery implementation decisions — 2026-11-02

This is internal engineering documentation. No vendor marketplace submission is authorized here.

| Decision | Evidence | Concrete implementation | Verification |
| --- | --- | --- | --- |
| Separate server retrieval, tool retrieval and execution | MCP Registry ecosystem; MCP tools spec; MCP-Zero | Three evaluation stages plus isolated install/E2E receipts | Rankings and execution denominators reported separately |
| Independent Claude manifest, strict mode | Claude marketplace strict-mode contract | Truthound owns `.claude-plugin/plugin.json`; catalog removes component overrides and fixture injection | CLI validation of actual source and real installation |
| Absolute Claude launcher | Baseline installed config drops `cwd`; real call failed looking for `/tmp/.../server.py` | Claude-specific manifest uses `${CLAUDE_PLUGIN_ROOT}` and `uv --directory` | Run installed effective command from an unrelated directory |
| Preserve three tool IDs | Existing clients and setup depend on names | Keep `check_file`, `profile_file`, `scan_pii`; improve source descriptions/schema | Actual `tools/list`, old-name calls |
| Do not promise general schema validation | Local tool accepts only `path`; implementation checks nulls/duplicates | Mark custom-schema, migrations, editing, cloud DLP as hard negatives | Extra `schema` parameter denied |
| Bounded bilingual metadata | Re-Invoke, MetaTool; multilingual GEO evidence is provisional | English contracts plus concise Korean intent explanations and localized canonical pages | EN/KO query slices, alternate-language links |
| Keep deployment identities distinct | Immutable Registry versions and frozen package lock | Plugin 0.1.6 still uses published Core 3.3.0; new Core descriptions remain unreleased | Record installed and source metadata separately |
| Use sparse baseline first | IR textbook; BEIR | Reproducible local BM25, Korean bigrams, frozen distractors | MRR/nDCG/recall, failures retained, no semantic/Agent claim |
| Do not invent external scores | AnyTool evaluation caveat; unavailable model/host runs | Observation import with coverage; missing measurements null | Tests for missing/duplicate/invalid observations |
| Evidence before claims | GEO KDD; no universal vendor contract | Synthetic CSV/Parquet proof, dated Registry snapshot, provenance | Source SHA, plugin/core version, hashes and rerun commands |

Sequence: audit → primary-source research → package repair + metadata → query/candidate
fixtures → real install and calls → failure analysis → source/canonical web updates →
checks → separate Korean conventional commits → push to each matching remote.

Phase 1 includes the owned marketplace, Registry, GitHub, official docs, owned web
and evaluation. Anthropic/OpenAI official/community submissions remain Phase 2;
maintainer-external use, stable support/privacy/permission contracts, repeatable
releases and vulnerability response, and review capacity are prerequisites. Keep
this policy out of the public README. No Core implementation is placed in this repository.
