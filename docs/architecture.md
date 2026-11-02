# Architecture

Truthound owns every runtime and permission implementation. This catalog owns
metadata, immutable release references and evaluation. Styxis-io owns canonical
web definitions. No MCP implementation is vendored into this repository.

```text
web / GitHub / connected Registry / explicitly added marketplace
  → server/plugin candidates
  → selected installation and pinned upstream package
  → stdio initialize + tools/list
  → supported tool + valid input
  → explicit directory consent
  → bounded result + quality interpretation
```

Each edge can fail independently. Source/package pins, Registry versions, plugin
versions and model/client identities must not be collapsed into one “version”.

The original `strict: false` made the catalog the component authority. It did
not weaken runtime directory enforcement, but coupled packaging to the catalog
and hid the lack of a standalone Claude manifest behind a test fixture. The new
catalog uses `strict: true`, adds no component overrides, and validates the actual
Truthound `.claude-plugin/plugin.json`. Claude has its own absolute launcher;
portable/Codex files remain owned and tested upstream.

The public Local surface remains three tools with existing IDs. New descriptions
in Truthound source do not alter the already published Core 3.3.0 wheel. Candidate
variants therefore distinguish baseline, rejected rewrite, installed package and
unreleased source. Registry proposals are never labeled live observations.

## Distribution phases (internal)

Phase 1: the owned Styxis marketplace, Official MCP Registry, GitHub, official
documentation, canonical Styxis web pages, tool metadata, evidence and evaluations.

Phase 2: consider Anthropic/OpenAI official or community marketplace submission
only after sustained use beyond maintainers, stable permission/privacy/support
contracts, repeatable release provenance, vulnerability response and capacity to
maintain vendor review/listings. Do not execute those submissions now or expose
this deferral policy in the public README.

Only `truthound` is in this catalog. Do not add Golem/AWE (Alpha), `truthound-core`,
TRAP or Mabinogion placeholders. Existing separate upstream surfaces are not copied
into this catalog. No hosted service, account system, telemetry or central RAG is added.
