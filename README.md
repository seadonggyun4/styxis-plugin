<!--
README BANNER LOCK / 배너 유지 규칙:
아래 Styxis 배너는 사용자가 지정한 필수 배너입니다.
사용자의 명시적인 요청 없이 제거, 교체, 숨김 처리하거나 Markdown 주석으로 감싸지 마세요.
Preserve this visible banner and its asset unless the user explicitly requests a change.
-->
![Styxis — Software Sworn to Truth](assets/Styxis-banner3.png)

# Styxis Plugin Marketplace

Local-first agent tools from Styxis.

This repository is the public Claude plugin catalog for Styxis products. It
owns discovery metadata, installation entry points, pinned release references,
and distribution checks. Product implementations remain in their source
repositories.

## Add the marketplace

```bash
claude plugin marketplace add seadonggyun4/styxis-plugin
```

## Available plugins

### Truthound

Truthound is a local-first data quality and validation tool for AI agents. It
validates, profiles, and scans approved local CSV and Parquet datasets without
uploading raw values.

```bash
claude plugin install truthound@styxis-plugin
```

Installing the plugin grants no data access. Truthound reads only directories
that the user explicitly approves. It runs locally over stdio and requires no
Styxis account, API key, hosted MCP server, telemetry, or subscription.

Example tasks:

- Check an approved CSV for missing values and duplicate rows.
- Profile an approved Parquet file before RAG ingestion.
- Scan an approved local dataset for likely PII.
- Validate an evaluation dataset without uploading raw values.

Truthound does not edit datasets, upload files, or provide a legal determination
about privacy compliance.

## Why this repository is separate

| Repository | Responsibility |
| --- | --- |
| [`Truthound`](https://github.com/seadonggyun4/Truthound) | Core, MCP implementation, permission model, tests, and releases |
| `styxis-plugin` | Claude marketplace metadata, pinned source references, installation, and release validation |
| [`styxis-io`](https://github.com/seadonggyun4/styxis-io) | Company and product narrative, canonical documentation, and discovery entry points |

Truthound Core and MCP implementation are not copied into this repository. The
marketplace manifest points to a reviewed Truthound commit so that implementation
and security fixes retain one source of truth.

## Public release policy

Only installable, validated products appear in the marketplace catalog.
Truthound is the first public plugin. Golem/AWE remains Alpha and is not listed.
Future products are added only after their public tool, permission, and support
contracts are stable.

See:

- [Architecture](docs/architecture.md)
- [Security and permissions](docs/security.md)
- [Release process](docs/releasing.md)
- [Discovery metadata](docs/discovery.md)

## Validate

Requirements:

- Claude Code CLI
- Git
- `uv` for the Truthound local MCP package

Run:

```bash
./scripts/validate.sh
```

The validator checks the marketplace schema, pinned source commit, documentation,
and the assembled Truthound source package with the Claude CLI. Truthound's
source package currently uses marketplace `strict: false`; the test fixture
supplies only the Claude manifest that the catalog composes and does not copy
the MCP implementation.

## License

Marketplace metadata and documentation in this repository are licensed under
Apache License 2.0. Each distributed product retains the license declared by its
source repository.
