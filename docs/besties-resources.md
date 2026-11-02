# Besties resource publishing

## Non-negotiable boundary

Product/documentation sites and GEO resource sites are maintained separately.
The resource configuration rejects the same hostname as the product, documentation
or configured human-facing targets. Existing website design, GitHub About and the
README banner are preserved. **GEO effectiveness remains under evaluation.**
This is a project architecture rule, not a claim that search engines require it.

Truthound uses one operator-approved public fact manifest and two host configurations:

- `besties/examples/truthound/resource-project.json`
- `besties/examples/truthound/resource-site-vercel.json`
- `besties/examples/truthound/resource-site-netlify.json`

Naming: `제품_목적_No.1`, expressed as `truthound_geo_No.1`; hostname-compatible
labels use `truthound-geo-no-1`. The intended free-tier targets are Vercel Hobby
and Netlify Free. Do not enable paid upgrades or add-ons. Provisioning and live
verification status are recorded separately from this configuration.

## Generated surface

| Path | Role |
| --- | --- |
| `/` | Finished public landing page; capabilities, boundaries and source links |
| `/facts.json` | Product/version, claims and evidence bindings |
| `/facts.md` | The same claims and references in a readable format |
| `/release.json` | Expected hashes, resource origin and fact identity |
| `/sitemap.xml` | Resource landing URL |
| `/robots.txt` | Crawl access and sitemap location |

The resource landing page has a canonical URL pointing to the Vercel resource
landing page on both hosts. This is a representative-URL hint, not an indexing
command or promise. Raw JSON/Markdown and the release manifest have `noindex`
response headers but remain directly accessible to clients. Crawling and direct
agent consumption are distinct from search-result inclusion. The two owned
hosts are not independent endorsements.

Evaluation questions, including holdouts, target inspection settings, credentials,
local paths and private source metadata are not serialized into generated resources.
Inputs must still be approved public material: this is not a general confidentiality
classifier. The public product website URL is permitted and identifies a website,
not its source repository.

## Local commands

Install `./besties` into a virtual environment, or set `PYTHONPATH=besties/src`.
From the repository root, using new output directories:

```sh
besties build-resources besties/examples/truthound/resource-project.json \
  --site besties/examples/truthound/resource-site-vercel.json --output /tmp/truthound-vercel-release
besties verify-resources besties/examples/truthound/resource-project.json \
  --site besties/examples/truthound/resource-site-vercel.json --directory /tmp/truthound-vercel-release
besties verify-resource-live besties/examples/truthound/resource-project.json \
  --site besties/examples/truthound/resource-site-vercel.json --live --output /tmp/truthound-vercel-observation
```

Use the Netlify configuration and distinct directories for the other host. Builds
are deterministic. There is no timestamp in the content hash. A changed product,
claim, reference or rendering changes the expected release. Live verification uses
locally generated expected bytes, never trusts an arbitrary remote manifest to
supply URLs, refuses redirects and bounds reads. Failed requests are unmeasured,
not proof of missing indexing. Content agreement is exact rendering agreement with
the approved input, not independent semantic verification of the claims.

## Hosting adapters

Build locally with the shared Besties package, then publish only the verified
static output. Do not connect either provider to a Git repository. The legacy
`sites/truthound-resources/build.py` remains a local convenience builder; hosting
configuration has no remote build or install command.

For new presentation releases use `publishing.hosting_files` to place delivery
headers in a clean staging directory. Netlify receives `_headers`; Vercel receives
`vercel.json`. Never upload the source or private-input parent directory. Existing
baseline contents are preserved when a hosting connection is changed.

Initial project creation/login is outside the Besties engine. Besties publication
uses generated static artifacts only; Git-connected deployments are disabled. Credentials must never
be added to the public manifest or artifacts. If a host cannot serve the expected
release, record a failed/partial deployment; do not declare both synchronized.
Providers retain previous deployments for operator-directed rollback. Automated
rollback and a distributed atomic publish transaction are not implemented.

## Validation and interpretation

Run the package tests, catalog checks, resource build and local verification before
pushing. After deployment, run live checks for each host: exact body hashes, HTTP
200, format MIME types and intended indexing headers. Verify the layout in a
browser and check links to public evidence. Keep the observed release separate from
future content changes.

A successful release says nothing about actual search-engine ingestion. Index
coverage, crawler activity and unbranded fresh-session AI answers require separate
observations. Do not convert a successful publication into a GEO success score.

## Verified pilot delivery (2026-11-02)

Both public resource sites are deployed: Vercel Hobby and Netlify Free Legacy
($0.00 plan observed). No paid upgrade or add-on was enabled. Each host passed
seven live artifact checks; JSON and Markdown fact hashes match across hosts.
See the [public verification receipts](../evaluation/results/2026-11-02-besties-resources/summary.json).

Historical initial delivery used a Vercel Git connection, disconnected later on
2026-11-02 at the operator’s request. Both hosts now use static publication only. Netlify was deployed through Netlify Drop with only
the eight verified generated files at the ZIP root. Its initial upload stalled
and was canceled; the subsequent upload to the existing project published
successfully. Netlify Git auto-deploy is not connected: a Git push alone does not
update both hosts. Rebuild and verify the Netlify bundle, then upload the complete
ZIP to the existing project's Deploys page and rerun live verification. Do not
create another project for each release. Authenticated static publishing is the only supported direction for future automation;
do not reconnect a Git repository. Historical receipts retain their original context.

Netlify's provider badge is visible in a browser; the exact-byte checks describe
the raw HTTP responses returned to Besties, not every provider-injected browser
representation. Both pages retain their official documentation links. Existing
product and documentation sites were not modified. Search ingestion and improved
AI discovery remain unmeasured for this release.

## SEO generation in 0.3.0

Resource-site schema v2 adds a bounded, operator-approved `seo` input: language,
landing title/description/heading/intro, and task pages with stable slugs, unique
metadata, claim IDs and editorial evidence IDs. Schema v1 remains supported for
existing inputs. No product names or hosting SDKs are hard-coded into the SEO
renderer. Editorial text is reviewed input, not automatically verified truth.

The Truthound v2 input generates four HTML pages: a local data validation MCP
landing page and task guides for CSV/Parquet checks, Great Expectations alternatives,
and profiling/PII screening. Each guide retains the relevant capabilities, all
supplied limitation claims, and links to evidence and the other guides. No
competitor feature table, rating, review or unverified performance claim is invented.

Each HTML page has a unique title and description, one H1, language declaration,
Open Graph metadata, a per-page canonical and WebPage JSON-LD matching the visible
metadata. Guide breadcrumbs point to the resource home. Structured data is not a
rich-result guarantee; fake ratings and FAQ rich-result claims are excluded.
The sitemap lists the four canonical Vercel URLs on both hosts. The Netlify mirror
is not expected to count as four additional independent search results.
Raw fact formats retain their `noindex` headers and direct accessibility.

Independent structural checks reject duplicate/missing metadata, broken internal
links, wrong canonicals, malformed or inconsistent JSON-LD, HTML noindex and
sitemap disagreement. Exact live checks include nested HTML routes and refuse an
unexpected redirect/noindex response. These are bounded technical checks, not
Search Console verification, Core Web Vitals field data or proof of rankings.

The generation inputs and evaluation protocol are frozen for the planned review
on 2026-12-21 (seven weeks after 2026-11-02), subject to necessary factual/security
corrections being logged. No reminder or scheduled job is created by this plan.
