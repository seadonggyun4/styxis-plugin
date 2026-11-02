# Discovery contracts

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
Internal distribution phase policy lives in [architecture](architecture.md).
