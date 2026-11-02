# GEO development and deployment — 2026-11-02

This iteration implements the [critical review](research/geo-causal-review-2026-11-02.md)
without a package release. The hypothesis is that clearer product identity, linked
task evidence and stronger public entry paths can help relevant sources reach
search candidates and support accurate answers. This is not a proven ranking lift.

## Development scope

- Connect the documentation home and guide index to Local dataset validation MCP.
- Explain the public Python package, Local MCP surface and installation catalog
  as related but distinct identities. Keep custom Core operations separate.
- Add a bilingual, reproducible CSV/Parquet example and the actual bounded results
  from published Core 3.3.1. Existing grants and private data are untouched.
- Put tool/task tables, direct documentation and execution-evidence links on the
  existing public product pages. Keep the commercial product distinction.
- Remove unrelated company-wide metadata keywords from these MCP pages; retain
  the company and other product positioning elsewhere.
- Publish a robots file advertising the documentation sitemap. Previous robots
  404 was not evidence that crawling was blocked; this supplies an explicit path.
- Replace repetitive placeholder prose on the Korean guide landing page with
  natural task navigation matching the actual public documentation.

## Verification boundaries

Local MCP calls, generated public HTML, live serving, web-search results and AI
answer citations are separate observations. A direct-URL read is not unbranded
discovery. Search-service result lists are not Gemini/Claude UI answers. Hidden
retrieval and owner-console indexing stay unknown when unavailable. Immediate
post-deployment results cannot establish causal efficacy or failure.

GitHub About and all existing README/banner bytes are preserved. Private source
identity, paths, commits and deployment records are excluded from public evidence.
Any private preservation comparison is reported only as an omitted-baseline summary.

## Local QA completed

- Published Core 3.3.1: six synthetic CSV/Parquet calls reproduced; an outside
  path was denied and the input bytes were preserved.
- Public documentation: 57 contract tests, full/public strict builds, link checks,
  full/public Korean checks and generated public-surface verification passed.
- Website: 15 existing tests, TypeScript checks, production build and eight-page
  HTML/metadata/evidence checks passed. Private build source and logs are omitted;
  the published check summary is not public reproducible source evidence.
- Catalog: metadata checks and ten tests passed, including stale/hidden version
  and noindex boundary checks.

[Receipts](../evaluation/results/2026-11-02-geo-development/) keep search-service
results, unavailable Agent evaluation and serving checks separate. Production
deployment and post-deployment search observations are recorded after serving
is independently verified.
