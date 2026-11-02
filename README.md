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

Start with the [data validation MCP guide](https://truthound.netlify.app/en/guides/data-validation-mcp/)
([한국어](https://truthound.netlify.app/guides/data-validation-mcp/)) for local CSV/Parquet
checks, installation, directory consent and the limits of sampled PII screening.

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

## Data validation MCP tasks

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

<!-- 비공개 회사 웹사이트 자산의 저장소 정보와 링크는 이 공개 README에 포함하지 않습니다. -->

- [Official Truthound MCP documentation](https://truthound.netlify.app/guides/mcp/)
- [Official MCP Registry metadata](https://registry.modelcontextprotocol.io/v0.1/servers/io.github.seadonggyun4%2Ftruthound/versions/latest) — active 3.3.1 verified on 2026-11-02
- [Reproducible discovery evaluation](evaluation/README.md) and [execution receipts](evaluation/results/)
- [Security reporting](SECURITY.md) · [Changelog](CHANGELOG.md)

Adding this custom marketplace makes its catalog available to your Claude
installation. A Registry record or a web page cannot guarantee discovery or
recommendations by every agent. Local retrieval fixtures, actual installation,
and external client/model evaluation are reported separately. Improved MCP descriptions ship in Core 3.3.1 and Local plugin 0.1.7.
The [actual Gemini/Claude browser search audit](docs/research/ai-search-2026-11-02.md)
records answer mentions and citations. The separate CLI tool-selection benchmark
remains unmeasured after account access rejections; see the dated
[release evidence](docs/releases/core-3.3.1.md).

## Besties — evidence-backed product publishing

**Besties turns one set of verified product facts into material for different
questions and consumption formats, then checks that the published material stays
consistent.** Truthound is the first pilot, not a dependency of the engine.

Besties(베스티)는 **하나의 검증된 제품 정보를 다양한 질문과 소비 형식에 맞춰
배포하고, 배포된 정보의 일치 여부를 검사하는 엔진**을 지향합니다.
제품별 기능·버전·제한·실행 예제·공개 근거를 관리하고, 사람이 읽는 문서와
기계가 소비하는 자료를 같은 원본에서 만들도록 확장합니다. 사이트 수나
키워드 반복 횟수가 아니라, 실제 질문에 대한 정확한 답변과 검증 가능한
근거를 늘리는 것이 목적입니다.

### Shared facts, distinct questions and formats

```text
Operator-approved public product facts and evidence
  capabilities · versions · limitations · examples · provenance
                           |
                        Besties
                           |
        +------------------+-------------------+
        |                  |                   |
  Human documentation  Question-led guides  Machine-readable resources
  onboarding/tutorials comparisons/tasks    Markdown/JSON/tool references
        |                  |                   |
        +------------------+-------------------+
                           |
           Publication and consistency checks
                           |
          Separate indexing/discovery observations
```

For Truthound, distinct questions include evaluating Great Expectations
alternatives, checking local CSV/Parquet through MCP, granting directory access,
and understanding sampled PII detection limits. Each guide must contribute a
useful answer with evidence; rewording the same page across many sites is not
the intended publishing strategy. Machine-readable resources are delivery formats,
not independent endorsements or a promise of indexing.

### Separate delivery without disrupting the product website

**Besties의 철칙: 제품·문서 사이트와 GEO 리소스 사이트는 별도로 유지합니다.
GEO 효과는 검증 중이며, 분리 배포 자체가 검색 노출 향상을 보장하지 않습니다.**

Besties requires a separately hosted public resource site. The Truthound pilot
targets both Vercel Hobby and Netlify Free, using the naming rule
`제품_목적_No.1` (`truthound_geo_No.1`); DNS-safe host labels use
`truthound-geo-no-1`. Both deployments share approved facts and identify the Vercel
resource landing page as the representative URL. They are not independent sources. Human-facing product and
documentation sites can retain their navigation, visual design and reading flow;
raw JSON and Markdown do not need to become primary menu items.

The resource site should have a finished landing page explaining its official
relationship to the product, supported versions, available formats and source
documentation. Resources remain accessible to people as well as crawlers. A
discreet developer/resources link can connect the sites without turning the
product interface into a file listing. Hosting on another domain is a delivery
choice, not evidence of greater search authority.

Publishing rules (implemented gates and remaining automation are distinguished below):

- Generate all formats from the same versioned, approved public facts. Bind each
  claim to evidence and preserve its limitations and scope across formats.
- Give each resource a stable identity, product/version metadata and links back
  to its authoritative documentation. Define representative URLs and indexing
  policy for equivalent representations; do not assume every duplicate should
  appear independently in search.
- Publish substantive question-specific guides where useful, with a clear source
  relationship. Do not present multiple owned sites as independent corroboration.
- Validate generated artifacts before publication and verify the deployed version,
  links and cross-format agreement afterward. Handle partial deployment failures
  explicitly, with rollback support rather than reporting a mixed release as current.
- Keep credentials and private source details outside public inputs and outputs.
  Preserve GitHub About and the README banner during every publishing operation.
- Measure deployment correctness, crawler/indexing observations and unbranded AI
  discovery separately. Consistent, accessible content does not guarantee retrieval
  or recommendation by a search engine or AI assistant.

### Persona features / 페르소나 기능

Besties는 **같은 제품 사실을 서로 다른 설명 방식으로 전달**합니다.
페르소나 체계의 이름·버전·유형·고정 번호는 외부 도메인 정의에 명시합니다.
공개 엔진은 특정 체계나 유형 개수를 하드코딩하지 않으며, 비공개 연구 정의는
저장소 밖에서 읽습니다. 설명은 검토된 입력이며, 성격 라벨만으로 자동 작성하거나
검색 효과가 입증됐다고 간주하지 않습니다.

| 기능 | 담당 모델·계층 | 보장하는 동작 |
| --- | --- | --- |
| 페르소나 체계 | PersonaSystem | 체계명·버전·멤버·고정 번호를 정의하고 중복·누락을 거부합니다. |
| 사이트 식별과 이름 | SiteIdentity · NamingPolicy | 도메인 정의에서 사이트를 도출하고 baseline을 번호 없는 별도 역할로 관리합니다. |
| 실제 배포 주소 | DeploymentRegistry | 플랫폼별 프로젝트·공개 URL을 기록하고 동일 페르소나의 미러끼리 canonical을 연결합니다. |
| 사실과 설명 분리 | ProductFacts · PersonaDefinition | 기능·제한·근거를 고정하고 설명 순서와 검토된 표현을 별도로 관리합니다. |
| 공통 콘텐츠 계획 | ContentPlan | 모든 사실·제한 사항을 포함하며, 조합 전에 사이트와 표현의 연결을 검사합니다. |
| 한국어·음식점 안내 | Facts v2 · Place template | 한국어·영어 방문 안내와 Restaurant 구조화 데이터를 생성하고 주소·전화번호를 HTML·Markdown·JSON에서 일치시킵니다. 기존 소프트웨어 출력은 유지합니다. |
| 다중 형식 출력 | Rendering | 같은 계획에서 HTML·Markdown·JSON·manifest를 생성합니다. |
| 화면 틀 고정 | Layout validation | 승인된 HTML 구조·CSS·출력 파일 구성이 바뀌면 현재 발행 경로에서 차단합니다. |
| 운영 환경 분리 | OperatorEnvironment | 인증·팀·로컬 파일 위치만 관리합니다. 유형 수·번호 규칙·주소 생성은 환경변수의 책임이 아닙니다. |
| 정적 발행·검증 | Publishing | 검증한 파일만 배포하며 일부 실패와 불확실한 결과를 성공으로 처리하지 않습니다. |
| 관찰과 비교 | Evaluation | 색인·언급·인용을 구분하고 실패·미측정을 보존합니다. GEO 효과는 검증 중입니다. |

비공개 체계명·유형 매핑·연구 가설은 공개 출력에 포함하지 않습니다.
기존 유형 번호의 재할당은 일반 설정 변경이 아닌 명시적인 마이그레이션으로 다룹니다.
제품·문서 사이트와 리소스 사이트의 분리, Git 연결 없는 정적 배포 원칙을 유지합니다.

### What works today and what is planned

Besties **0.6.0** is an independently installable Python development tool in
[`besties/`](besties/), with no runtime dependencies. It currently validates public
input manifests, creates evidence-linked review drafts, inspects configured HTML
pages and imports explicit search/AI-answer observations. It also generates a
separate HTML resource landing page and evidence-bound task guides with unique
search titles/descriptions, canonical URLs, social metadata and WebPage JSON-LD,
plus JSON facts, Markdown, sitemap and hashed
release manifest from shared facts. Local verification rejects missing, changed,
extra or symlinked files; live verification checks exact bytes, HTTP status,
content types and indexing headers. The operator supplies
approved claims; Besties does not yet independently verify their factual truth.

Separate-host configuration and Vercel/Netlify build adapters are implemented in
[`sites/truthound-resources/`](sites/truthound-resources/). Provider login and initial
project creation remain operator actions. Content agreement means deterministic
rendering from the same approved claims, not independent semantic fact-checking.
Source patching, automatic rollback, and search-provider integrations remain future
work. Version 0.4 adds independent product facts, versioned presentation definitions,
a shared content plan and exact-plan review hashes. HTML, Markdown, JSON and the
release manifest retain the same facts and presentation; all facts and limitations
are mandatory. Static packaging, append-only deployment receipts and imported
observation comparisons are separate boundaries. See the
[presentation architecture](docs/besties-presentations.md). Hosting configuration stays outside the core fact model; no Styxis product
runtime or hosting SDK is required. See the [resource publishing guide](docs/besties-resources.md)
for commands, deployment configuration and verification boundaries.

Pilot status: [Vercel resource site](https://truthound-geo-baseline.vercel.app/) (Hobby)
and [Netlify resource site](https://truthound-geo-baseline.netlify.app/) (Free Legacy)
are live. The dated receipts distinguish the initial resource release from the
SEO expansion and record each host’s verified artifact hashes. **Besties deploys only generated static artifacts.**
The original Vercel Git connection has been disconnected; Netlify also uses static
publication. A Git push does not deploy either resource site. Operator settings use
[`env-truthound/.env.template`](env-truthound/.env.template); actual `.env.local`
values are excluded from Git and all deployment artifacts. Existing CLI login
stores remain the default authentication method.
SEO/GEO effectiveness remains under evaluation. The planned seven-week review is
2026-12-21; see the [comparison protocol](docs/research/besties-seo-2026-11-02.md).
See the [SEO deployment verification](evaluation/results/2026-11-02-besties-seo/summary.json)
(ten public artifacts checked per host) and the
[initial resource verification](evaluation/results/2026-11-02-besties-resources/summary.json).

See the [architecture and local commands](docs/besties-development.md) and the
[Truthound deployment and search evaluation](docs/research/besties-truthound-2026-11-02.md).
Besties is not currently a published marketplace plugin; the catalog's installable
plugin remains Truthound.

## Repository ownership

| Repository | Responsibility |
| --- | --- |
| [Truthound](https://github.com/seadonggyun4/Truthound) | Core, MCP implementation, permission model, tool schemas, tests and packages |
| `styxis-plugin` | Discovery metadata, Claude distribution, immutable source pins, installation checks and discovery evaluation |

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
