# Architecture

## Repository boundary

`styxis-plugin` is a distribution catalog, not a product monorepo. Its job is to
make independently developed Styxis products discoverable and installable while
keeping their implementations in their authoritative repositories.

```text
Truthound source repository
  -> tests and release review
  -> Claude package at plugins/truthound
  -> immutable source commit
  -> styxis-plugin marketplace reference
  -> Claude install and local MCP startup
```

The marketplace pins both the source branch and an immutable commit SHA. Updating
Truthound requires a reviewed manifest change in this repository.

The current Truthound package has no standalone Claude manifest. The marketplace
therefore declares `strict: false` and explicitly exposes its setup skill and
`.mcp.json`. Release validation adds a manifest fixture only inside a temporary
checkout so the complete assembled package can be checked by Claude Code without
forking the product implementation.

## Ownership

| Surface | Owner |
| --- | --- |
| Data-quality implementation and MCP tools | Truthound repository |
| Directory permission enforcement | Truthound repository |
| Claude marketplace catalog | `styxis-plugin` |
| Marketplace validation and install smoke tests | `styxis-plugin` |
| Product narrative and canonical web pages | `styxis-io` |

Implementation files must not be manually copied here. If a future client cannot
consume a pinned Git source, the Truthound release workflow may generate a
self-contained artifact. That artifact must record its source commit and checksum
and must not become a second implementation authority.

## Initial scope

The public catalog contains only `truthound`.

- `truthound-core` is not listed merely because it exists as an implementation
  layer. It becomes a separate plugin only if it has an independent user problem,
  tool surface, permission contract, and installation reason.
- Golem/AWE remains Alpha and is not listed until its public tool and permission
  contracts are stable.
- TRAP and Mabinogion are not placeholders in the public catalog.

## Distribution phases

### Phase 1: owned distribution

- Operate `seadonggyun4/styxis-plugin` as the supported Claude marketplace.
- Publish Truthound metadata to the Official MCP Registry for cross-client
  discovery when its package and E2E checks are ready.
- Prove install, permission, startup, first-call, support, and release workflows.
- Build usage and security-response evidence before expanding distribution.

### Phase 2: external marketplace review

Anthropic and OpenAI official/community marketplace registration is deferred to
Phase 2. Styxis will begin those submission processes only when the project has
meaningful scale, stable public contracts, repeatable release and vulnerability
response, and enough maintenance capacity for third-party review obligations.

Phase 2 is a distribution decision, not a claim that either vendor guarantees a
public listing or maintains a submission channel with identical requirements.
The applicable program and policies must be re-verified when Styxis is ready to
apply.
