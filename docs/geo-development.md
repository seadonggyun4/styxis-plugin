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

## Deployed result and search observations

The existing website and public documentation are deployed and independently
verified. The public documentation receipt requires the exact final source commit
and page hashes, not just version text. Eight website pages require localized
guide links, scoped metadata and the exact published example JSON.

- [Korean public product page](https://styxis-io.com/ko/open-source/truthound)
- [English public product page](https://styxis-io.com/en/open-source/truthound)
- [한국어 실행 예제](https://truthound.netlify.app/guides/local-mcp-example/)
- [English execution example](https://truthound.netlify.app/en/guides/local-mcp-example/)
- [Live document verification](../evaluation/results/2026-11-02-geo-development/docs-live.json)
- [Live website verification](../evaluation/results/2026-11-02-geo-development/website-live.json)

Branded diagnostics returned established file-source and check-CLI documents.
A follow-up adds contextual links to the focused MCP guide and actual execution
example on those two pages in both languages, then repeats required docs QA and
exact live deployment checks. Both deployment-verification guides describe the
expanded explicit public page allowlist.

The same four unbranded search strings were submitted as pooled batches before
changes, after the first deployment and after the final contextual-link deployment.
Returned URL counts were 41, 41 and 40; none contained the target project. These
are displayed URL sets, not four independent engine-answer trials, complete
retrieval sets or a recommendation-rate denominator. All observations are retained.
The immediate observations do not establish either causal GEO success or failure.

The search tool could not directly access the four inspected new/current URLs,
while ordinary direct HTTP/live content checks succeeded. The tool exposed no
HTTP status, so this does not identify a WAF block, absence of indexing or any
particular provider's retrieval policy. Branded diagnostics found older documents
and external listings; they do not count as unbranded discovery successes.

The existing Claude CLI request was rejected before an answer/search by account
organization policy. Browser control was unavailable for a Gemini/Claude consumer
UI recheck. Completed new consumer-AI answers: zero; recommendation rates remain
unmeasured. Owner-console indexing remains unverified. No new account/API key,
outreach, scheduled monitoring or package release was introduced.

The external directory still returned Local 0.1.5/Core 3.3.0. Its inspected
OpenAPI exposes reads and manifest validation, not a listing refresh/update.
Owned surfaces consistently describe the current release; external synchronization
was not claimed as completed. See the [distribution observation](../evaluation/results/2026-11-02-geo-development/distribution.json).

## Preservation audit

All existing README bytes and banners are unchanged. No GitHub About write was
performed. An initial read-only comparison matched all three repository baselines;
a later comparison found the public catalog description had changed. The actor
was not identified. The current description was left untouched, not restored or
optimized. The final preservation receipt reports this drift separately rather
than claiming all initial About values still match. Field values, private
repository identities and private preservation snapshots are omitted.
