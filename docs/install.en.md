# Install MCP plugins through Styxis

Start at the [Styxis installation entry](../README.md#install). Golem 0.2.10 is registered with a pinned public source commit and complete plugin inventory. For Truthound, choose Local for nulls, duplicates, aggregate profiling and sampled PII, or Core for additional validation, schema, drift and masking workflows.

## Codex

```bash
codex plugin marketplace add seadonggyun4/styxis-plugin
codex plugin add truthound@styxis-plugin
# Or:
codex plugin add truthound-core@styxis-plugin
```

## Claude Code

```bash
claude plugin marketplace add seadonggyun4/styxis-plugin
claude plugin install truthound@styxis-plugin
# Or:
claude plugin install truthound-core@styxis-plugin
```

Requires Git and a plugin-capable client. Truthound needs uv and Python 3.11–3.13; the Golem launcher needs Python 3.11 or later and a separately prepared native/MCP runtime. For updates, refresh the marketplace with `codex plugin marketplace upgrade styxis-plugin` or `claude plugin marketplace update styxis-plugin`, then update only the profiles you already use. In Claude Code, run `claude plugin update truthound@styxis-plugin` or `claude plugin update truthound-core@styxis-plugin`. In Codex, run `codex plugin add truthound@styxis-plugin` or `codex plugin add truthound-core@styxis-plugin`. Reconnect and confirm the installed version and a permitted synthetic-data call.

## Claude Desktop ordinary chat

This is separate from Claude Code. Download `truthound-3.3.4.mcpb` for Local or `truthound-3.3.4-core.mcpb` for Core from the [Truthound 3.3.4 release](https://github.com/seadonggyun4/Truthound/releases/tag/v3.3.4) and open it in Desktop, then approve an existing persistent data directory. The two extensions have distinct IDs and compact icons. Restart Desktop after updating and verify both the tool list and an actual synthetic-data call. Keep Codex and Claude Code installed.

Installation alone grants no data access. Existing permissions must not be expanded during an update. Workspace writes, operator control and sensitive results require separate approval. PII findings are sampled estimates; full Core parity through MCP is not verified. See the [product guide](https://www.truthound-docs.tech/en/guides/mcp/) for permissions and limitations.

## Golem

The Golem catalog pins public source commit `862579eccbe0c62663c9c0e9465340c4c3796237`. After registering the marketplace, install in the client you use:

```bash
codex plugin add golem@styxis-plugin
# Or in Claude Code:
claude plugin install golem@styxis-plugin
```

Use Golem Setup to select an exactly reviewed local launcher for that client. Native/runtime dependencies and permissions remain product-owned. Installation grants no Work access and imports no other client's approval. Replace an existing Golem connection only through a reviewed migration; keep one Golem installation per client.

Claude Desktop is separate from Claude Code. Download the [Golem 0.2.10 MCPB](https://github.com/seadonggyun4/Golem/releases/download/golem-plugin-v0.2.10/golem-launcher-0.2.10.mcpb), compare its SHA-256 with `desktop_asset.sha256` in [release.json](../release.json), and open it in Desktop. Select an owner-private state directory explicitly prepared for the `claude-desktop` launcher. This launcher-only bundle does not configure or approve itself at startup, embed the native/MCP runtime, or open an Owner window automatically. The historical extension name `golem-prepare` preserves update identity; it grants no prepare profile rights.

The Golem 0.2.10 Codex adapter requires Python 3.11+ and supports graceful refresh of an explicitly selected Golem connection. The Owner app and local runtime are separately reviewed; connection status is not proof of model tool delivery or action approval. Golem `connection-status` distinguishes server readiness, host catalog responses and model tool exposure. After selecting the reviewed new adapter path, use the supported host refresh and verify actual definitions in the chat's next turn. A notification or reload ACK alone is not acceptance; do not repeat installs or replay Work actions.

See [Codex/Claude Code setup](https://github.com/seadonggyun4/Golem/blob/main/docs/integration-codex-plugin.md), [Desktop setup](https://github.com/seadonggyun4/Golem/blob/main/docs/integration-mcpb.md), and the [candidate promotion procedure](releasing.md#golem-candidate). Catalog/package verification does not establish client installation, model tool discovery or Work execution success. An existing execution HOLD remains in force.
