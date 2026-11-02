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
