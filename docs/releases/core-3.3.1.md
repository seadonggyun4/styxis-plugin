# Core 3.3.1 distribution evidence — 2026-11-02

Truthound Core 3.3.1 is published on [PyPI](https://pypi.org/project/truthound/3.3.1/)
and as [canonical GitHub artifacts](https://github.com/seadonggyun4/truthound/releases/tag/v3.3.1).
The Official MCP Registry publishes an active/latest immutable 3.3.1 record.
Local plugin 0.1.7 pins the published package with its frozen UV lock.

## Identity and publication

- Core artifact source: `80f8092d30918c825154e3ff8e5ed3ca4c328b17`.
- Plugin repin source: `54dae24c027e0a93af669bf7388d5af96a09bc97`. This later commit is not the Core artifact build identity.
- [Complete verification](https://github.com/seadonggyun4/truthound/actions/runs/41371907329) and [PyPI publication](https://github.com/seadonggyun4/truthound/actions/runs/41378219376).
- [Public package receipt](../../evaluation/results/release-3.3.1/core-publication.json) records wheel/sdist URLs and SHA256 values; canonical artifact hashes match PyPI.
- [Official Registry observation](../../evaluation/results/release-3.3.1/registry.json) records actual response metadata, active/latest status and the explicit directory-consent invocation.
- [Installed CLI/MCP E2E](../../evaluation/results/release-3.3.1/installed-e2e.json) checks the actual package, CSV/Parquet calls, consent/path denial, revocation, source immutability and output sentinels.

The improved descriptions and schemas now ship in the tested artifact. Tool IDs
remain `check_file`, `profile_file`, `scan_pii`. No validation capability,
implicit permission, raw-value disclosure or public catalog product is added.
Existing installations must refresh/reinstall and reconnect to use the new pin.

## Actual Agent selection availability

[Existing Codex/Claude readiness requests](../../evaluation/results/release-3.3.1/agent-availability.json)
were rejected before any evaluation query was sent. Codex reported
`model_not_found`; Claude organization policy disabled subscription access.
CLI-owned system/tool context was not audited. No new account/key or policy
bypass was attempted. Observed decisions are zero; accuracy and false-selection
rates are unmeasured. These failures are not wrong tool choices.

The optional `scripts/evaluate_agent.py` validates metadata-conditioned closed-set
choices when a CLI model is available. It is not autonomous MCP discovery or a
live Registry ranking experiment. Synthetic deterministic-provider Core tests
are native lifecycle QA, not an external Agent benchmark.

## Retrieval and CI limits

The 70-query BM25 experiments use author-written distractors and an inspected
holdout. They measure closed-fixture retrieval, not model selection or broad
Registry recall. Historical 3.3.0 candidate bytes are retained separately. Improved
retrieval can also increase negative target exposure; this is not false selection.

The [CI retry record](../../evaluation/results/release-3.3.1/ci-retry.json) retains
the first macOS/Python 3.13 failure and its original source/JUnit ZIP. The native
AI proposal failure did not reproduce locally; its root cause is unconfirmed.
The bounded same-source retry passed the existing gate before publication.
No tests, deadlines, permission checks or failure assertions were relaxed.

## Preservation and rollout

GitHub About and the README banner/retention comment are preserved. Branch
integration, default-catalog installation and live web deployment have separate
receipts in `release.json`; a Git push alone does not establish deployment,
indexing, recommendations or citation visibility.

The [public GitHub catalog E2E](../../evaluation/results/release-3.3.1/default-e2e.json)
explicitly installs `seadonggyun4/styxis-plugin` and passes all 16 checks against
plugin source `54dae24c027e0a93af669bf7388d5af96a09bc97`, Local 0.1.7 and Core
3.3.1. The [integration receipt](../../evaluation/results/release-3.3.1/integration.json)
records all three repositories on main and removal of only the three fully merged
task branches. Live website and documentation receipts confirm the deployed
3.3.1 content separately from the source commits.

## Local installation update

The [local CLI receipt](../../evaluation/results/release-3.3.1/local-cli-updated.json)
records an isolated 3.3.1 installation and byte parity with 1,187 canonical package
members. A broken legacy 1.2.5 launcher was preserved privately and redirected to
the managed installation; global Python dependencies were not changed.

The [local MCP receipt](../../evaluation/results/release-3.3.1/local-mcp-updated.json)
records Local 0.1.7 and Core 0.2.1. Fresh connections using the actual registered
commands initialize Core 3.3.1 and list 3/176 tools. Existing enabled settings,
environment and permission files are unchanged; no user-data file calls were made.
The user subsequently restarted Codex. The [current-chat observation](../../evaluation/results/release-3.3.1/current-chat-refresh.json)
confirms that all three Local descriptions and Core `check_file` match the
published installation. The 44 Core tools exposed to this chat are a host-visible
subset, separate from the fresh server tools/list count of 176 above. No user-data
call or Agent selection benchmark was performed for this metadata check.
