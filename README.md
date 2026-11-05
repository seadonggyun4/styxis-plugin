<!--
README BANNER LOCK / 배너 유지 규칙:
아래 Styxis 배너는 사용자가 지정한 필수 배너입니다.
사용자의 명시적인 요청 없이 제거, 교체, 숨김 처리하거나 Markdown 주석으로 감싸지 마세요.
Preserve this visible banner and its asset unless the user explicitly requests a change.
-->
![Styxis — Software Sworn to Truth](assets/Styxis-banner3.png)

# Styxis Plugin Marketplace

스틱시스 자산의 MCP 플러그인을 등록하고 검증된 소스로 설치하는 Claude Code·Codex 배포 카탈로그입니다. 각 제품 저장소가 MCP 서버·도구·권한·런타임 테스트를 관리합니다.

## Plugins

| Plugin | 기능 | 설정·문서 |
| --- | --- | --- |
| Truthound Local | 승인된 로컬 CSV·Parquet의 결측·중복 검사, 프로파일링, 개인정보 표본 탐지 | [공식 MCP 안내](https://truthound-docs.vercel.app/guides/mcp/) |
| Truthound Core | 명시적 검증·프로파일링·PII 및 드리프트·마스킹·스키마 작업. MCP 지원 범위는 부분적입니다 | [Core 설치·권한](https://truthound-docs.vercel.app/guides/mcp/#core-installation) |

<!-- MCP release maintenance: Always update the Styxis Local/Core plugin pins and locks, synchronize English/Korean installation docs, pass required CI, publish, and verify actual client updates. Styxis is the sole user-facing installation entry point, including Claude Desktop bundle links. MCP 변경 후 플러그인 반영·한영 문서 정리·검증·배포·실제 업데이트 설치를 모두 완료한다. -->

## Install

[English installation guide](docs/install.en.md)

### Claude Code

Claude Code의 Git 하위 디렉터리 플러그인 지원, Git, `uv`, Python 3.11–3.13이 필요합니다. 제품별 추가 요구사항은 공식 문서를 확인하세요.

```bash
claude plugin marketplace add seadonggyun4/styxis-plugin
claude plugin install truthound@styxis-plugin
# 또는 Core:
claude plugin install truthound-core@styxis-plugin
```

### Codex

```bash
codex plugin marketplace add seadonggyun4/styxis-plugin
codex plugin add truthound@styxis-plugin
# 또는 Core:
codex plugin add truthound-core@styxis-plugin
```

Codex CLI의 plugin marketplace 명령을 지원하는 버전이 필요합니다. 설치 검증은 Claude Code 2.1.196, Codex CLI 0.141.0에서 수행합니다. 기존 카탈로그는 Claude의 `claude plugin marketplace update styxis-plugin`, Codex의 `codex plugin marketplace upgrade styxis-plugin`으로 갱신합니다.

카탈로그 갱신 후 이미 사용하는 프로파일만 업데이트하세요. Claude Code는 `claude plugin update truthound@styxis-plugin` 또는 `claude plugin update truthound-core@styxis-plugin`, Codex는 `codex plugin add truthound@styxis-plugin` 또는 `codex plugin add truthound-core@styxis-plugin`을 실행합니다. 클라이언트를 재시작하거나 재연결한 뒤 설치 버전·도구 목록·승인된 합성 파일 호출을 확인합니다. 기존 데이터 권한은 유지합니다.

설치 후 해당 프로파일의 setup 스킬에서 접근할 디렉터리를 명시적으로 승인합니다. **설치만으로 데이터 접근 권한이 부여되지는 않습니다.** 개인정보 검사는 표본 기반이며 누락 가능성이 있습니다. Core의 작업공간·운영자 승인 저장소·민감 결과 접근은 각각 별도 승인 항목이며 변경 뒤 재연결해야 합니다. 자세한 권한·기능·제한은 제품 문서에서 관리합니다.

### Claude Desktop 일반 채팅

Claude Code 플러그인과 별도 설치입니다. [Truthound 3.3.3 릴리스](https://github.com/seadonggyun4/Truthound/releases/tag/v3.3.3)에서 Local은 `truthound-3.3.3.mcpb`, Core는 `truthound-3.3.3-core.mcpb`를 받아 Desktop으로 열고, 계속 유지할 데이터 폴더만 승인하세요. 두 확장은 서로 다른 ID와 아이콘을 사용해 함께 설치할 수 있습니다. 업데이트 뒤 Desktop을 재시작하고 도구 목록과 승인한 합성 파일 호출을 확인하세요. 기존 Codex·Claude Code 설치를 제거하지 않습니다.

## Repository scope

- `.claude-plugin/marketplace.json`: Claude용 제품 설명과 설치 소스.
- `.agents/plugins/marketplace.json`: 같은 고정 소스를 사용하는 Codex 카탈로그.
- `release.json`: 플러그인별 버전, 고정 소스 커밋과 파일 해시.
- `scripts/`: 카탈로그·릴리스 일치와 원격 플러그인 manifest 검증.
- `docs/releasing.md`: 플러그인 추가·업데이트 절차.

제품 저장소의 릴리스를 카탈로그에 등록하고 최소 검증을 통과하면 설치할 수 있습니다. 카탈로그는 현재 Truthound Local과 Core를 제공하며 제품 구현을 복제하지 않습니다. 일반 사용자 설치 창구는 이 저장소로 통일하고, 제품 저장소의 카탈로그는 배포 항목 없는 이전 호환 표식으로 유지합니다. 제품 CI는 별도 임시 개발 카탈로그를 사용합니다.

## Verify

```bash
./scripts/validate.sh
```

모든 등록 항목의 고정 소스를 가져와 두 카탈로그의 소스 일치, 클라이언트별 manifest 이름·버전·MCP 설정과 기록된 파일 해시를 검사합니다. 제품 서버는 실행하지 않습니다. 오프라인 검사는 `python3 scripts/validate_metadata.py`로 실행할 수 있습니다.

[플러그인 추가·업데이트](docs/releasing.md) · [보안 제보](SECURITY.md) · [변경 기록](CHANGELOG.md)

## License

카탈로그와 배포 도구는 Apache-2.0입니다. 각 제품은 해당 저장소의 라이선스를 따릅니다.
