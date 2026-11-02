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

Both projects use the public catalog repository and root directory
`sites/truthound-resources`, with access to the repository's shared `besties/`
package and examples outside that root. Neither reads or modifies another site.

- Netlify: `netlify.toml`, build `python3 build.py`, publish `dist`.
- Vercel: `vercel.json`, framework Other, build
  `BESTIES_HOST=vercel python3 build.py`, output `dist`; include source files outside
  the root directory. No dependency installation is required.

The shared builder writes only its own new `dist` directory and refuses stale
output. Local repeat builds should use a new CLI output directory. Provider builds
must start without the previous generated `dist`. `_headers` is Netlify delivery
configuration; Vercel's equivalent headers live in `vercel.json`.

Initial project creation/login is outside the Besties engine. Git-based production
updates use each provider's existing deployment workflow. Credentials must never
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
