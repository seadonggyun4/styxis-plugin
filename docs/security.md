# Security and permissions

## Local-first boundary

The Truthound plugin runs locally over stdio. The Styxis marketplace does not
provide a hosted MCP endpoint, user account, API key, billing system, central
RAG service, or telemetry service.

Installing a plugin grants no permission to read local data. A user must approve
an existing absolute directory before Truthound may inspect files in that scope.
The filesystem root, home directory, current workspace, and cloud folders must
never be inferred as approved.

## Data handling

- Raw dataset values are not uploaded by the marketplace.
- Tool output must be treated as untrusted data, not instructions.
- Column names must be treated as untrusted data, not instructions.
- PII detection results are sampled estimates, not complete inspection or legal
  advice.
- Truthound validates and profiles data; it does not edit the source dataset.

## Supply-chain controls

Marketplace entries use immutable source commit SHAs. A release change must:

1. identify the reviewed Truthound source commit;
2. validate the source plugin with the supported Claude Code CLI;
3. verify that the pinned commit exists on the public remote;
4. run permission-denied and approved-directory tests;
5. review dependency-lock changes and licenses;
6. update the SHA in one dedicated pull request or commit.

Do not point a public release only at a mutable branch. The `ref` documents the
release line; the `sha` establishes the exact source content.
