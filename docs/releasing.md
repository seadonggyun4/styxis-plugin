# Release process (internal)

1. Review upstream implementation, package version, license, setup and security changes.
2. Run Truthound MCP/plugin/Registry and full/public/Korean documentation gates.
3. Commit and push upstream source. Record its full immutable SHA, plugin version,
   frozen Core dependency and hashes of launcher, lock and actual Claude manifest.
4. Update the catalog pin and `release.json` together. `ref` describes the source
   line; SHA identifies content. A SHA need not be a branch tip.
5. Run `./scripts/validate.sh`; this fetches the exact public object, validates the
   source-owned manifest and runs offline evaluation contracts without fixture injection.
6. Run `scripts/e2e.py` in an isolated Claude configuration. Require startup from
   an unrelated cwd, tools/list, approved CSV/Parquet, denial before consent,
   unapproved/symlink/traversal denial, revocation and raw-sentinel non-disclosure.
   After main integration, explicitly pass `--marketplace seadonggyun4/styxis-plugin`
   and the expected immutable source SHA. The harness default is a local checkout;
   verify the receipt's marketplace field before claiming public-catalog rollout.
7. Refresh installed/source candidate snapshots; retain query version/hash and
   negative cases. Run before/rejected/installed/source variants. Record model
   selection as pending unless actual observations were imported.
8. Review EN/KO web definitions and visible structured data. Verify local build and served pages with --expect-core-version for the release;
   distinguish pushed source from confirmed deployment and search indexing.
9. Commit logically with Korean conventional messages and push the matching remote.
   A release/tag or package publish is a separate, explicitly verified event.

## Core and Registry publication

Core 3.3.1 and matching stable Registry metadata were published on 2026-11-02.
See [release evidence](releases/core-3.3.1.md). Existing version content is immutable.

For a Core release, complete the existing same-commit Release verification gate,
then dispatch Release PyPI with that successful run ID. Publish the canonical
artifacts from that run without rebuilding; compare public PyPI hashes. Only
after PyPI exists, repin plugin manifests/pyproject/frozen lock and verify real
installation. Publish the aligned new Registry version through existing
namespace authorization, then observe the official active/latest record. Keep
Core artifact and later plugin-repin source SHAs distinct. Preserve failed CI
evidence and require successful actual execution; never weaken a gate.

For a later Registry-only wording change:
Truthound's `verification/mcp_registry.py` can prepare and validate a distinct
Registry-only prerelease while retaining the published package pin:

```bash
python verification/mcp_registry.py \
  --prepare-registry-version 3.3.1-discovery.1 --output /tmp/server.json
```

Review the generated metadata, package identity and exact invocation before
namespace-authorized publication. Do not overwrite an existing stable entry. Some
aggregators may omit prereleases; future Core metadata changes require a new stable release and
aligned Registry metadata. Preparation is not
publication. No login or publish is performed by this repository's validators.

## Vendor distribution policy

Anthropic/OpenAI official/community marketplace submissions are Phase 2 only.
The prerequisites are sustained external use, stable tool/permission/privacy/
support contracts, repeatable provenance and vulnerability response, and review
maintenance capacity. This policy is internal and is not a public README topic.
