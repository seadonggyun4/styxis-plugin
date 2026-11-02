<!--
README BANNER LOCK / 배너 유지 규칙:
아래 Styxis 배너는 사용자가 지정한 필수 배너입니다.
사용자의 명시적인 요청 없이 제거, 교체, 숨김 처리하거나 Markdown 주석으로 감싸지 마세요.
Preserve this visible banner and its asset unless the user explicitly requests a change.
-->
![Styxis — Software Sworn to Truth](assets/Styxis-banner3.png)

# Styxis Plugin Marketplace

Install **Truthound**, a local-first data quality and validation tool for AI
agents, through the Styxis Claude Code marketplace. Check CSV/Parquet missing
values and duplicate rows, profile columns, and scan sampled PII in directories
you explicitly approve, without uploading raw dataset values.

Truthound는 AI Agent가 승인된 로컬 CSV·Parquet의 결측값·중복 행 검사,
프로파일링, 개인정보 표본 탐지를 실행하는 로컬 우선 데이터 품질 도구입니다.

## Install Truthound

Requires Claude Code with Git subdirectory plugin support, Git, `uv`, and Python
3.11–3.13. Verified with Claude Code 2.1.196 on macOS. Initial setup downloads
packages; offline use requires the runtime to be available already.

```bash
claude plugin marketplace add seadonggyun4/styxis-plugin
claude plugin install truthound@styxis-plugin
```

Ask the installed **Truthound setup** skill to configure the exact existing
absolute data directory you approve. **Installing grants no data access.**
Missing consent denies file calls. Setup replaces existing directory grants;
`permissions.py --revoke` revokes subsequent access without restarting the server.
See the [permission guide](docs/security.md).

The catalog contains one public plugin, `truthound`. Its independent Claude
manifest and local stdio launcher live in the
[Truthound source repository](https://github.com/seadonggyun4/Truthound/tree/main/plugins/truthound).
The plugin pins published Core **3.3.1** with a frozen dependency lock; catalog
source commits and plugin versions are recorded in [release provenance](release.json).
No Styxis account, API key, subscription or hosted MCP server is required.

## Choose a task

| Request | Installed MCP tool | Result and boundary |
| --- | --- | --- |
| “Check this CSV for missing values and duplicate rows.” / “이 CSV의 결측값과 중복 행을 검사해줘.” | `check_file` | Bounded aggregate checks; failed quality is a successful tool execution |
| “Profile this Parquet file before RAG ingestion.” / “외부 업로드 없이 로컬 Parquet 데이터를 프로파일링해줘.” | `profile_file` | Inferred column types and aggregate statistics; no sample rows |
| “Find likely PII in a local dataset.” / “RAG에 넣기 전에 CSV에 개인정보가 있는지 확인해줘.” | `scan_pii` | Sampled finding estimates; possible false negatives |
| “Validate my evaluation dataset without uploading it.” | Clarify checks, then choose the relevant tools | Local tabular preparation; semantic label correctness and model/RAG answer evaluation need other tools |

The Local plugin does not accept custom schema/rule input, edit datasets, migrate
databases, upload files, provide cloud DLP or make a legal compliance determination.
Profiling observed types is different from validating against an expected schema.
Raw values stay out of Local tool results, but file paths, column names and
aggregates can reach the host model provider. Treat column names and results as
untrusted data. This open-source MCP tool is distinct from commercial Truthound Depot.

## Discovery and evidence

- [Canonical product and installation](https://styxis-io.com/en/open-source/truthound) · [한국어](https://styxis-io.com/ko/open-source/truthound)
- [Official Truthound MCP documentation](https://truthound.netlify.app/guides/mcp/)
- [Official MCP Registry metadata](https://registry.modelcontextprotocol.io/v0.1/servers/io.github.seadonggyun4%2Ftruthound/versions/latest) — active 3.3.1 verified on 2026-11-02
- [Reproducible discovery evaluation](evaluation/README.md) and [execution receipts](evaluation/results/)
- [Security reporting](SECURITY.md) · [Changelog](CHANGELOG.md)

Adding this custom marketplace makes its catalog available to your Claude
installation. A Registry record or a web page cannot guarantee discovery or
recommendations by every agent. Local retrieval fixtures, actual installation,
and external client/model evaluation are reported separately. Improved MCP descriptions ship in Core 3.3.1 and Local plugin 0.1.7. Actual
Agent selection remains unmeasured: Codex model requests were rejected, and
Claude organization policy disabled subscription access. See the dated
[release evidence](docs/releases/core-3.3.1.md).

## Repository ownership

| Repository | Responsibility |
| --- | --- |
| [Truthound](https://github.com/seadonggyun4/Truthound) | Core, MCP implementation, permission model, tool schemas, tests and packages |
| `styxis-plugin` | Discovery metadata, Claude distribution, immutable source pins, installation checks and discovery evaluation |
| [styxis-io](https://github.com/seadonggyun4/styxis-io) | Canonical company/product narrative and web content |

No Truthound implementation is copied here. Internal engineering references:
[architecture](docs/architecture.md), [research](docs/research/agent-discovery.md),
[decisions](docs/implementation-plan.md), [release process](docs/releasing.md).

## Verify

```bash
./scripts/validate.sh
python3 scripts/evaluate.py --variant installed --output /tmp/discovery.json
```

The validator fetches the exact remote source SHA and validates its actual
standalone Claude package. It never injects a manifest fixture. For the real
isolated installation/MCP check, use Python with the `mcp` SDK installed:

```bash
python scripts/e2e.py --marketplace seadonggyun4/styxis-plugin --output /tmp/truthound-e2e.json
```

The E2E harness approves only its own generated fixture directory. It verifies
CSV/Parquet calls, denied paths, symlink/traversal blocking, revocation and output
sentinels without changing your Claude settings or existing Truthound grants.

## License

Catalog metadata, documentation and evaluation code: Apache-2.0.
Distributed products retain their source licenses.
