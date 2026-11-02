# Changelog

## 2026-11-02 — Core 3.3.1 publication

- Publish exact same-source verified Core wheel/sdist and Local/Core MCPB artifacts.
- Publish immutable Official MCP Registry 3.3.1 with reviewed task wording.
- Repin Local plugin 0.1.7 to published Core 3.3.1 with the frozen dependency lock.
- Record real CLI readiness failures separately from unmeasured Agent selection.
- Preserve repository About, the visible README banner and its retention comment.

## 2026-11-02 — Agent discovery distribution

- Require the upstream standalone Claude plugin manifest; remove the synthetic
  manifest validation fixture and marketplace component overrides.
- Ship plugin 0.1.6 with an absolute Claude launcher; retain published Core 3.3.0
  and existing tool IDs. Source-only tool/schema wording awaits a Core release.
- Explain supported tasks and boundaries in English and Korean. Keep RAG/eval
  preparation distinct from semantic evaluation and Depot's commercial scope.
- Add 70 query cases, frozen candidate fixtures, BM25 ranking/observation runner,
  immutable provenance, isolated CSV/Parquet installation E2E and minimal read-only CI.
- Preserve the rejected first description rewrite and report its regression.
- Record live Registry 3.3.0 separately from prepared, unpublished metadata.
