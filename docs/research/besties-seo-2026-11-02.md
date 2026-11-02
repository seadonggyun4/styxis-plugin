# Besties SEO expansion and seven-week observation protocol

## Intervention

Besties 0.3.0 adds evidence-bound editorial inputs and deterministic search-oriented
HTML pages, per-page metadata, canonical-aware sitemaps, social metadata and
WebPage structured data. Truthound is a configuration-only pilot. Product and
documentation sites remain separate and unchanged; About and the README banner
remain protected. Public website URLs identify websites, not private source repos.

The two public resource hosts represent the same product publisher, not independent
endorsements. Vercel is canonical and Git-connected; Netlify is a manually uploaded
mirror. Preserve this distinction when scoring citations or discovery.

Design references: [Google SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)
and [structured data guidelines](https://developers.google.com/search/docs/appearance/structured-data/sd-policies).
These support readable useful content, crawlable links and truthful metadata, not
a guarantee of indexing or rankings. No external rich-results certification is
claimed for our local structural checks.

## Baseline and limitations

Before this SEO deployment on 2026-11-02, two existing development queries were
submitted together to the connected web search service:

1. Which alternatives to Great Expectations offer MCP tools for data validation?
2. GX 같은 데이터 검증 프레임워크 중 MCP를 제공하는 도구는 뭐가 있어?

Neither Truthound nor either new resource host appeared in the displayed merged
results. This is one bounded search-service observation, not Google/Bing rank,
a consumer-AI answer, or proof of non-indexing. The service did not expose stable
engine identity or separate per-query rankings in that response. Full results
were not archived; this summary is not complete original evidence. Representative
returned URLs included [ChatForest](https://chatforest.com/reviews/data-quality-observability-mcp-servers/)
and [Stackscape](https://stackscape.org/en/alt/great-expectations/); their product
claims were not used to author our pages or independently verified here.

Earlier fresh-session Copilot/Gemini observations remain in the
[category pilot report](besties-truthound-2026-11-02.md). They predate this intervention
and are historical context, not a complete matched baseline for 0.3.0.
Search Console index status, verified bot visits, organic impressions/clicks,
field performance and actual post-release AI recommendation rates are unmeasured.

## Review on 2026-12-21

Seven weeks is an observation window, not an indexing deadline. No scheduled task
or notification is created. Preserve the deployed inputs, release hashes and exact
questions. Log necessary factual/security fixes, outages and new external mentions;
otherwise avoid optimizing against the holdout questions during the window.

At review, execute all six frozen queries from
`besties/examples/truthound/category-project.json`, separating four development
and two holdout questions. Keep original wording; do not include Truthound, resource
URLs or follow-up hints in the unbranded trials. Use fresh temporary sessions and
record the provider, visible model/mode, language, date, web-search instruction,
completion status, answer mention and citation URLs. Use three fresh sessions per
query/provider as a practical repetition target; report all attempts and failures,
not just the best answer. Personalization/model changes remain confounders.

Measure separately:

- **Delivery:** current release and links work on both hosts; compare expected hashes.
- **Indexing:** owner-console evidence if access is available; `site:` observations
  alone cannot establish full index coverage. Count canonical pages, not mirrors.
- **SEO:** query/page impressions and clicks where owner-console data exists;
  record matching periods and limitations. Without a pre-period, do not claim lift.
- **AI discovery:** unbranded mention and citation counts with explicit denominators;
  compare matched questions/providers where possible. Report prompted trials separately.
- **Accuracy:** cited claims match current documented capabilities and limitations.

Interpretation: repeated unbranded mentions/citations would support discoverability
under the observed conditions. They would not establish that Besties caused the
change; time, model updates, indexing and third-party coverage can also contribute.
If delivery passes but discovery remains absent, the observed result is no measured
discovery benefit, not a reason to redefine deployment success as GEO success.
One product and two mirrored hosts cannot establish general effectiveness across
products. A subsequent independent-product or controlled rollout is needed.

## Deployment verification

Both hosts passed ten public artifact checks, including four HTML pages. The
[dated summary](../../evaluation/results/2026-11-02-besties-seo/summary.json) records
input hashes, implementation commit, test counts and delivery modes. The
[frozen query set](../../evaluation/results/2026-11-02-besties-seo/evaluation-queries.json)
is an evaluation artifact, not part of either resource site's generated bundle.
Source and isolated-package tests each passed 26 cases; catalog tests passed 10.
A nonexistent path returned 404 on both hosts. The 390px mobile viewport had no
horizontal overflow and was visually inspected. No index coverage or field
performance measurements are implied by these checks.
