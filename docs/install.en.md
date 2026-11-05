# Install Truthound through Styxis

Start at the [Styxis installation entry](../README.md#install). Choose Local for nulls, duplicates, aggregate profiling and sampled PII, or Core for additional validation, schema, drift and masking workflows.

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

Requires Git, uv, Python 3.11–3.13 and a plugin-capable client. For updates, refresh the marketplace with `codex plugin marketplace upgrade styxis-plugin` or `claude plugin marketplace update styxis-plugin`, then update only the profiles you already use. In Claude Code, run `claude plugin update truthound@styxis-plugin` or `claude plugin update truthound-core@styxis-plugin`. In Codex, run `codex plugin add truthound@styxis-plugin` or `codex plugin add truthound-core@styxis-plugin`. Reconnect and confirm the installed version and a permitted synthetic-data call.

## Claude Desktop ordinary chat

This is separate from Claude Code. Download `truthound-3.3.3.mcpb` for Local or `truthound-3.3.3-core.mcpb` for Core from the [Truthound 3.3.3 release](https://github.com/seadonggyun4/Truthound/releases/tag/v3.3.3) and open it in Desktop, then approve an existing persistent data directory. The two extensions have distinct IDs and compact icons. Restart Desktop after updating and verify both the tool list and an actual synthetic-data call. Keep Codex and Claude Code installed.

Installation alone grants no data access. Existing permissions must not be expanded during an update. Workspace writes, operator control and sensitive results require separate approval. PII findings are sampled estimates; full Core parity through MCP is not verified. See the [product guide](https://truthound-docs.vercel.app/en/guides/mcp/) for permissions and limitations.
