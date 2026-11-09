<!-- MCP release maintenance: Always update the Styxis Local/Core plugin pins and locks, synchronize English/Korean installation docs, pass required CI, publish, and verify actual client updates. Styxis is the sole user-facing installation entry point, including Claude Desktop bundle links. MCP 변경 후 플러그인 반영·한영 문서 정리·검증·배포·실제 업데이트 설치를 모두 완료한다. -->

# 플러그인 추가·업데이트

1. 제품 저장소에서 MCP 플러그인을 릴리스하고 제품의 기능·권한·보안 테스트를 완료합니다.
2. Claude 카탈로그 plugins 배열에 고유 이름, 설명, 버전과 git-subdir 소스를 등록합니다. source.sha에는 전체 40자리 커밋을 고정하고 strict: true로 제품 manifest의 소유권을 유지합니다.
   Codex의 `.agents/plugins/marketplace.json`에도 같은 이름·소스·SHA를 등록하고 `./` 접두 경로, 설치·인증 policy와 category를 지정합니다. 제품 패키지에는 Claude manifest와 portable/Codex manifest가 모두 있어야 합니다.
3. release.json의 plugins 객체에 같은 이름으로 plugin_version, source_url, source_path, source_sha와 source_file_sha256을 기록합니다. manifest와 MCP 설정을 포함하고 해시 키는 소스 저장소 루트 기준 경로로 작성합니다. Desktop artifact가 있으면 별도 `desktop_asset`에 공개 URL·SHA-256·version·manifest_name을 고정합니다.
4. ./scripts/validate.sh와 python3 -m unittest discover -s tests -v를 실행합니다. 모든 등록 항목을 검사하며 설치나 서버 실행은 하지 않습니다.
5. 제품 요구사항·공식 문서 링크와 변경 기록을 갱신하고 커밋·푸시합니다.

MCP 런타임, 권한 정책, 패키지 배포와 Registry 관리는 각 제품 저장소에서 수행합니다. 이 카탈로그에 제품 구현·평가 데이터·웹사이트 배포 작업을 추가하지 않습니다.
GitHub About과 README 배너는 사용자의 명시적인 요청 없이 수정하지 않습니다. 비공개 저장소 정보와 자격 증명을 공개 파일에 넣지 않습니다.

일반 사용자용 카탈로그와 설치 안내는 이 저장소에서만 제공합니다. 제품 저장소는 플러그인 패키지와 테스트를 소유하며, 클라이언트 설치 테스트에는 임시 개발 카탈로그를 생성합니다. 기존 등록 사용자에게 필요한 빈 호환 표식은 유지할 수 있지만 새 플러그인 배포 항목을 추가하지 않습니다.

MCP 수정은 제품 패키지만 게시하고 끝내지 않습니다. Truthound는 PyPI 게시 후 Local·Core 플러그인의 버전·고정 의존성·lock·해시를 갱신합니다. Golem은 launcher 패키지와 별도 Desktop artifact를 고정합니다. 두 카탈로그는 제품별 같은 공개 source SHA를 사용합니다. 한·영 설치 안내를 정리하고 CI 통과, 공개 게시, 실제 Codex·Claude Code 업데이트 설치와 필요한 Desktop 확장 검증까지 완료합니다. 사용자 설치 진입점은 항상 이 카탈로그의 README Install 섹션입니다.

## Golem candidate

Golem 0.2.8은 공개 source와 전체 plugin inventory를 대조해 등록했습니다. 아래 절차는 다음 **신규 제품 등록 후보**에도 재사용할 수 있습니다. `register_plugin.py`는 이미 등록된 이름의 덮어쓰기·다운그레이드를 거부합니다. 기존 제품 업데이트는 새 공개 source/artifact를 검토하고 두 catalog와 release pin을 함께 갱신합니다.

1. owner-private 위치에 `UNPUBLISHED_CANDIDATE` JSON을 준비합니다. `entry`에는 Claude catalog 필드와 source의 URL·path·ref만 기록하고, 공개 전 `sha`를 만들지 않습니다. `source_file_sha256`에는 plugin 전체 파일을 고정합니다. 로컬 검사는 서버·설치·Work를 실행하지 않습니다. `--source-tree`에는 Git 소스 파일만 담긴 깨끗한 추출본을 사용하며 `__pycache__` 등 추가 파일도 거부됩니다.

```sh
python3 scripts/register_plugin.py --candidate /absolute/path/to/candidate.json --source-tree /absolute/path/to/product-source
```

2. 별도 승인된 제품 commit/push 후 실제 공개 40자리 SHA를 대조합니다. 기본값은 dry-run이며 내려받은 source bytes가 후보와 다르면 중단합니다.

```sh
python3 scripts/register_plugin.py --candidate /absolute/path/to/candidate.json --source-sha PUBLISHED_40_CHARACTER_SHA
# 검토된 카탈로그 변경을 적용할 때만:
python3 scripts/register_plugin.py --candidate /absolute/path/to/candidate.json --source-sha PUBLISHED_40_CHARACTER_SHA --apply
```

3. Desktop MCPB를 제공한다면 먼저 같은 제품의 GitHub Release에 artifact를 게시하고 다음 metadata를 고정합니다. Golem은 `golem-plugin-v0.2.8/golem-launcher-0.2.8.mcpb`를 사용하며 전체 SHA는 `release.json`이 기준입니다.

```json
"desktop_asset": {
  "url": "https://github.com/OWNER/PRODUCT/releases/download/TAG/FILE.mcpb",
  "sha256": "EXACT_64_CHARACTER_SHA256",
  "version": "PRODUCT_PLUGIN_VERSION",
  "manifest_name": "DESKTOP_EXTENSION_NAME"
}
```

현재 Desktop validator는 launcher-only Golem 형식에 한정됩니다. 같은 source GitHub repo의 HTTPS release URL, 다운로드·팽창 각 2MiB 한도, 정규 파일 4개(`manifest.json`, `LICENSE`, `assets/icon.png`, `scripts/launcher.py`), archive hash와 고정 source bytes, manifest identity/license·정확한 Desktop launcher 선언을 검사합니다. 임의 ZIP을 추출하거나 실행하지 않습니다. 다른 제품 형식은 검증 계약을 별도로 추가해야 하며 이 검사를 우회하지 않습니다.

4. 두 active catalog와 release.json의 diff·기존 제품 pin 보존을 확인하고 전체 검사를 통과한 뒤 별도 commit/push로 게시합니다. 완료된 후보 원본은 private 검토 기록으로 보존하고 public tree에는 미게시 후보를 남기지 않습니다.
5. 기존 설치를 보존한 상태에서 새 identity·launcher·권한의 정확한 전환안을 검토합니다. client별 검증본 하나만 유지하고 설치·도구 노출·실제 호출을 각각 기록합니다. 공개 게시나 artifact hash 일치를 실제 client E2E 성공으로 표시하지 않습니다.

Preparation and publication do not install a client package, migrate approval state or resume held Work execution. Record those stages independently.
