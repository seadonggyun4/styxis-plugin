# 플러그인 추가·업데이트

1. 제품 저장소에서 MCP 플러그인을 릴리스하고 제품의 기능·권한·보안 테스트를 완료합니다.
2. Claude 카탈로그 plugins 배열에 고유 이름, 설명, 버전과 git-subdir 소스를 등록합니다. source.sha에는 전체 40자리 커밋을 고정하고 strict: true로 제품 manifest의 소유권을 유지합니다.
   Codex의 `.agents/plugins/marketplace.json`에도 같은 이름·소스·SHA를 등록하고 `./` 접두 경로, 설치·인증 policy와 category를 지정합니다. 제품 패키지에는 Claude manifest와 portable/Codex manifest가 모두 있어야 합니다.
3. release.json의 plugins 객체에 같은 이름으로 plugin_version, source_url, source_path, source_sha와 source_file_sha256을 기록합니다. manifest와 MCP 설정을 포함하고 해시 키는 소스 저장소 루트 기준 경로로 작성합니다.
4. ./scripts/validate.sh와 python3 -m unittest discover -s tests -v를 실행합니다. 모든 등록 항목을 검사하며 설치나 서버 실행은 하지 않습니다.
5. 제품 요구사항·공식 문서 링크와 변경 기록을 갱신하고 커밋·푸시합니다.

MCP 런타임, 권한 정책, 패키지 배포와 Registry 관리는 각 제품 저장소에서 수행합니다. 이 카탈로그에 제품 구현·평가 데이터·웹사이트 배포 작업을 추가하지 않습니다.
GitHub About과 README 배너는 사용자의 명시적인 요청 없이 수정하지 않습니다. 비공개 저장소 정보와 자격 증명을 공개 파일에 넣지 않습니다.
