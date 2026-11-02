# Discovery contracts

Current priority is **unbranded web discovery before additional packaging work**.
The [critical GEO review](research/geo-causal-review-2026-11-02.md) distinguishes
page availability/indexing, engine query rewriting and candidate retrieval,
answer selection, citation and brand mention. Upstream stages not exposed by a
provider remain unknown. No mention/citation is not proof of no retrieval.
Direct-URL reading and supplied-candidate selection are separate diagnostics,
not organic discovery successes. Formatting, FAQ and schema changes alone have
no established universal GEO benefit. Packaging remains necessary maintenance
when installation or use would otherwise fail.

Primary identity: local-first data quality and validation for AI agents. Connect
CSV/Parquet checks, profiling and sampled PII through actual tasks and explicit
input/result boundaries. Korean and English use the same product facts.

The public Local plugin supports nulls/duplicates, inferred types/aggregates and
sampled PII. It does not take custom schema/rule inputs or implement Pandera,
Great Expectations or Soda configuration formats. RAG/eval context means tabular
input preparation, not semantic answer/label evaluation. These are evaluation
boundaries, not competitor rankings.

Server/plugin descriptions supply candidate relevance. Live `tools/list` names,
descriptions and schemas supply post-install tool selection. Permission enforcement
comes from the runtime, not metadata hints or a retrieval score.

- GitHub About fields are a user-owned editorial surface. Inspecting them can
  inform an audit, but never change description, homepage or topics for GEO/SEO.
  Use README, documentation, package metadata and reproducible evidence instead.
- Claude custom catalogs must be added; do not imply global automatic custom-marketplace search.
- The Registry publishes metadata for aggregators; client ingestion and rankings vary.
- `llms.txt`, JSON-LD, canonical and hreflang aid explicit representation/navigation;
  ranking or universal consumption is not established.
- Task chunks should preserve identity, input, selected tool, limitation, version
  and a reproducible source together.

See [primary-source research](research/agent-discovery.md),
[traceable decisions](implementation-plan.md), and [evaluation protocol](../evaluation/README.md).
The [actual Gemini/Claude search observation](research/ai-search-2026-11-02.md)
records unbranded web-answer visibility separately from installed tool selection.
Internal distribution phase policy lives in [architecture](architecture.md).
