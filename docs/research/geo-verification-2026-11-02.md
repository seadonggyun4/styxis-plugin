# GEO application verification — 2026-11-02

**The inspected technical implementation passes. Unbranded discovery and actual
AI recommendation are not demonstrated.** This is a read-only audit following
the [development/deployment](../geo-development.md), with no new product or menu
changes. It does not assign an invented overall GEO score.

| Stage | Current observation | Verdict and boundary |
| --- | --- | --- |
| Deployed content | Eight website pages pass canonical/hreflang, metadata, visible Core version, guide links and exact execution-receipt checks | Passed on inspected pages |
| Official documentation | Intended public commit and exact hashes match; bilingual focused guides, example, home/guide entry paths and contextual file/CLI links verified | Passed; not proof of indexing |
| Declared crawler access | Both origins allow Googlebot, Bingbot, OAI-SearchBot and Claude-SearchBot for inspected MCP paths | Allowed by robots policy |
| Local user-agent probes | Four supplied crawler tokens × two representative pages: eight HTTP 200 responses, visible three-tool content, no inspected noindex directives | Passed from this network; actual provider IP/CDN/WAF access unknown |
| Search index state | No owner-console URL inspection or authenticated crawler access logs available in this audit | Unverified |
| Unbranded search | Four fixed strings issued as four separate connected-search calls; returned URL counts 18, 19, 20 and 17; no target name or URL in the returned text/URL sets | 0/4 queries returned the target in this service snapshot |
| Consumer-AI answers | Browser control unavailable; known organization-policy CLI rejection not retried without an access-state change | Unmeasured; not zero recommendations |

The [dated summary](../../evaluation/results/2026-11-02-geo-verification/summary.json)
records the audit verdicts. Serving checks are in
[website](../../evaluation/results/2026-11-02-geo-verification/website.json) and
[documentation](../../evaluation/results/2026-11-02-geo-verification/docs.json)
receipts; [crawl-policy evidence](../../evaluation/results/2026-11-02-geo-verification/crawl-policy.json)
and [per-query search results](../../evaluation/results/2026-11-02-geo-verification/search.json)
remain separate.

## Crawler requirements used

Google requires public access, HTTP 200 and indexable content, but explicitly
does not guarantee indexing from these conditions alone.
[Google technical requirements](https://developers.google.com/search/docs/essentials/technical).

Official OpenAI documentation distinguishes search-related OAI-SearchBot from
training-related GPTBot and user-directed ChatGPT-User. It also calls for allowing
published crawler IP ranges; a successful local UA-token probe cannot establish
that those real IPs are permitted by the CDN.
[Official OpenAI crawler documentation](https://developers.openai.com/api/docs/bots).

Anthropic separately documents Claude-SearchBot, training-related ClaudeBot and
user-directed Claude-User. Their purposes must not be collapsed into one training
or discovery status.
[Anthropic crawler documentation](https://privacy.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler).

Only the inspected policy and responses are reported as verified. No crawler
source IP was impersonated, no access restriction bypassed and no provider log
claimed. No training-permission or robots policy was changed for this audit.

## Interpretation

Technical application and public serving are verified; the missing observations
are actual engine indexing, internal candidate retrieval and consumer-AI choice.
Older documents appeared in earlier branded diagnostics, so the entire domain
cannot be described as wholly unknown to search. These observations do not tell
us whether the new focused pages are currently indexed by a particular engine.

The four queries are an authored convenience sample, use the same operator/account
and expose only this tool's displayed results. No per-provider Google/Bing rank,
complete internet recall, population recommendation rate or causal improvement
is inferred. Earlier pooled batches used a different reporting protocol and are
not compared as a before/after rate. A successful direct read would also remain
separate from unbranded discovery.

Owner-authorized URL inspection and actual fresh unbranded consumer-AI answers
would resolve additional stages when those observations become available. No new
account, API key, outreach or recurring monitor was created. GitHub About and
README/banner were not modified; no private source identifiers or account traces
are included in public records.
