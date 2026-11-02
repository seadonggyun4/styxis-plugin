# Besties: independent Truthound pilot

Besties 0.3.0 is an independently installable, standard-library-only proposal and
inspection and resource-generation tool. Truthound is configuration, not a core dependency. This pilot
does not deploy content, change GitHub About, edit README banners, or claim that
passing its inspections causes AI recommendations.

## Architecture

`model` validates the public input contract. `planner` creates deterministic,
evidence-linked proposals. `adapters.Reader` supplies pages to `audit`.
`evaluation` imports explicit search/answer observations. `cli` handles filesystem
and optional HTTP operations. None imports catalog scripts or product runtimes.

The package lives in `besties/` and can be copied and installed independently.
It is a development tool within this repository, not a newly published marketplace
plugin. There is no mandatory LLM, browser, search subscription or API key.

## Run the Truthound pilot

From the repository root:

```sh
python3 -m venv /tmp/besties-env
/tmp/besties-env/bin/pip install ./besties
/tmp/besties-env/bin/besties validate besties/examples/truthound/project.json
/tmp/besties-env/bin/besties plan besties/examples/truthound/project.json --output /tmp/besties-proposal
/tmp/besties-env/bin/besties audit besties/examples/truthound/project.json --live --output /tmp/besties-audit
```

Output directories must not already exist. `plan` produces `draft.html` and
`result.json`. The draft deliberately has `noindex` and must be edited/reviewed
before publication. It uses supplied statements verbatim with HTML escaping;
it does not infer competitor capabilities or independently verify source claims.

`audit` reads only exact configured URLs, refuses redirects, limits response size,
and checks HTTP status, content text, required links and noindex. Article content
is preferred, then main, then body; navigation links cannot substitute for article
links when an article exists. Whitespace is normalized. It is not a browser
render, robots.txt checker, version-semantic validator, crawler visit detector,
indexing inspector or search recommendation test. Fetch failures are unmeasured,
not successful or evidence that a page is unindexed. HTML/CSS can hide text beyond
the script/style/template exclusions; rendered visibility needs a browser adapter.

## Input contract and extension boundaries

The executable contract is `besties/model.py`; the complete example is
`besties/examples/truthound/project.json`. Version 1 accepts exactly one product,
multiple public targets, evidence records, supported claims, development and
holdout queries, and preservation policy. Multiple products use separate manifests
and runs; multi-product scheduling is a future layer, not implied support.

All claims must cite a supplied public evidence ID. Queries must refer to claims.
Holdout questions never enter generated proposals. Unknown fields, private
evidence, missing bindings and unsupported policy modes are rejected.
Inputs are operator-approved public material: the tool cannot infer whether free
text is confidential. It is not a sanitizer for arbitrary private repositories.
Credentialed source adapters and publishing permissions belong outside this
public manifest. The CLI is a trusted local tool, not an internet-facing URL-fetch
service; a hosted service would need separate DNS/IP/network isolation controls.

To add a product, supply another manifest. To add a page source, implement
`Reader.read(url) -> Page` and reuse `audit`. To add an evaluation provider, map
its observable results to the imported observation contract. Keep provider/model
predictions distinct from live search or consumer-app observations.

Do not add product names, domain-specific rules or absolute workspace paths to
the core. Product-specific live gates can remain separate, stronger checks.

## Observation import

`besties evaluate PROJECT --observations OBSERVATIONS --output NEW_DIRECTORY`
accepts a JSON list. Each item requires `query_id`, `provider`, `surface`
(`search_results` or `ai_answer`), `observed_at`, `status` (`completed` or
`unavailable`), `urls`, `brand_mentioned` (boolean or null), `brand_prompted`
and `fresh_session` (booleans).

Only completed, unprompted, fresh-session records qualify as unbranded observations.
Unavailable records require empty URLs and a null mention. Returned configured
URLs and brand mentions remain separate; neither is automatically a recommendation.
Records are operator-supplied observations, not independently authenticated evidence.
No causal effect, global GEO score or cross-provider aggregate is calculated.

## Verification and next stages

The isolated test suite covers configuration-only product replacement, invalid
evidence, input privacy boundaries, holdout leakage, script escaping, inaccessible
pages, noindex, protected output directories and prompted/unavailable observations.
CI also retains the existing catalog validation and tests.

Resource generation, separate-host validation and exact local/live release checks
are now available; see [resource publishing](besties-resources.md).
Future milestones are versioned schema migration, source-aware patch adapters,
evidence-content verification, reviewed publication adapters, and engine-specific
observation integrations. Production edits require an adapter with explicit path
allowlists, preservation checks, concurrency checks and rollback. None is silently
enabled by this pilot.

## GX alternative / MCP category scenario

`besties/examples/truthound/category-project.json` is a second input for the same
engine. It binds the existing English and Korean comparison and MCP guides to
explicit article-content requirements and reciprocal links. Run `plan`, then
`audit --live` with that manifest using separate output directories before and
after publication. Navigation alone does not satisfy these checks.

The generated proposal is editorial input. Source changes and deployment use the
documentation repository's existing reviewed workflow; Besties does not perform
those writes. Fresh temporary Copilot and Gemini conversations provide separate
observations, imported through `evaluate`. Record the exact prompt including any
web-search instruction alongside the observations. An immediate post-deployment
answer is a smoke test, not evidence that a crawler has ingested the new pages.
