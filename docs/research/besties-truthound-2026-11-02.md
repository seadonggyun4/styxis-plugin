# Besties로 수행한 Truthound 카테고리 연결 보강

2026-11-02에 Besties 0.1.1과 Truthound 문서 보강을 커밋·푸시하고 실제 배포를
확인했다. 영어·한국어 네 페이지는 새 본문·링크 요구사항을 충족했다.
Copilot과 Gemini의 브랜드 없는 질문은 배포 전 각각 한 번, 배포 후 각각 한 번
완료했으며, 네 답변 모두 Truthound를 언급하지 않았다. 검색 노출 개선 효과는 확인되지 않았다.

## 무엇을 바꿨는가

- [GX 비교 안내](https://truthound.netlify.app/guides/gx-parity/)와
  [MCP 안내](https://truthound.netlify.app/guides/data-validation-mcp/)에
  “MCP를 제공하는 Great Expectations 대안 찾기” 절과 상호 본문 링크를 추가했다.
- [영어 GX 비교 안내](https://truthound.netlify.app/en/guides/gx-parity/)와
  [영어 MCP 안내](https://truthound.netlify.app/en/guides/data-validation-mcp/)에도
  같은 제품 관계·지원 작업·한계·실행 예제 연결을 반영했다.
- 한국어 GX 비교 페이지의 반복적인 임시 문구를 실제 비교 범위와 결과 해석으로 교체했다.
- 프레임워크 벤치마크와 Local MCP 세 도구를 구분했다. GX suite 가져오기,
  사용자 지정 규칙, 전체 기능 동등성을 지원한다고 확대하지 않았다.
- Besties는 article, main, body 순서로 본문을 검사한다. 메뉴에 있는 도구명·링크가
  본문 요구를 대신 충족하거나 빈 article을 우회하지 못하도록 회귀 검사를 추가했다.

Copilot이 이전에 제시한 자기 설명은 원인 가설로 취급했다. 이 작업은
카테고리·제품·MCP 관계의 문서상 공백을 보강한 것이며, 내부 검색 실패 원인을 입증한 것은 아니다.

## 실제 적용 경로

1. [카테고리 입력 명세](../../besties/examples/truthound/category-project.json)를 고정했다.
2. Besties로 검토용 초안과 계획을 만들고 공개된 기존 네 페이지를 검사했다.
3. 초안을 기존 문서 구조에 맞게 편집하고 공식 문서 저장소의 검증·배포 경로로 반영했다.
4. 독립 설치한 Besties로 빌드 산출물과 실제 배포 페이지를 검사했다.
5. 별도 임시 채팅의 AI 응답 관찰을 Besties `evaluate`로 가져왔다.

Besties의 자동 배포 어댑터가 구현된 것은 아니다. 이번 적용의 소스 편집·커밋·배포는
엔진 밖의 기존 저장소 절차를 사용했다. 제품 정보는 입력 명세에 있고 엔진에는 하드코딩하지 않았다.

## 검증 결과

| 검사 | 결과 |
| --- | --- |
| 독립 가상환경에 설치한 Besties 테스트 | 13개 통과 |
| 기존 카탈로그 테스트 | 10개 통과 |
| Truthound 문서 계약 테스트 | 57개 통과 |
| full/public 링크·빌드·한국어·공개 범위 등 문서 검사 | 10개 단계 통과 |
| 새 카테고리 본문 요구사항 | 배포 전 0/4, 배포 후 4/4 충족 |
| 배포 식별 | 공개 커밋과 네 페이지의 해시 일치 |
| Copilot 한국어 GX·MCP 질문 | 배포 전·후 모두 미언급 |
| Gemini 영어 GX·MCP 질문 | 배포 전·후 모두 미언급 |

본문 검사의 0/4는 새로 정의한 요구사항의 미충족 수치다. 기존 사이트 전체의
GEO 실패율이나 검색 점수가 아니다. 실제 배포 확인 시점은
`after-pages.json`의 `observed_at`이며, 이는 배포가 시작되거나 완료된 정확한 시각과 다르다.

두 엔진 모두 기존 계정에서 새 임시 채팅을 사용했고 제품명·제품 URL을 질문에 넣지 않았다.
질문에는 웹 검색과 공식 출처 요청을 덧붙였다. 정확한 전후 프롬프트는 각 notes 파일에 있다.
UI의 Auto 모드만 확인했으며 내부 모델 버전·전체 검색 결과·개인화 영향을 통제하지 않았다.
출처 목록은 답변에 명시된 URL이며 전체 검색·인용 집합이 아니다.
다른 제품에 대한 AI의 주장은 독립적으로 검증한 사실로 재게시하지 않는다.

이번 확인은 배포 직후의 소규모 점검이다. 크롤러가 새 페이지를 방문했거나 색인했다는
증거는 없으며, 전후 차이의 인과 효과·장기 추천 확률을 추정하지 않는다.
입력의 나머지 네 질문과 별도 holdout 성능은 미측정이다.

## 커밋과 증거

- [Besties 첫 구현](https://github.com/seadonggyun4/styxis-plugin/commit/4bf3fa24c1899aa36410b1eb0a83038379f8eecb)
- [Besties 본문 검사·카테고리 입력 보강](https://github.com/seadonggyun4/styxis-plugin/commit/682c524514072446026a5c917ce94a6837e495c4)
- [Truthound 문서 보강](https://github.com/seadonggyun4/truthound/commit/898e20c9501b5296de068c6382aefadbff928d3d)
- [Besties CI](https://github.com/seadonggyun4/styxis-plugin/actions/runs/41424732915)
- [Truthound 문서 CI](https://github.com/seadonggyun4/truthound/actions/runs/41426561983)
- [검증 요약](../../evaluation/results/2026-11-02-besties-category/summary.json)
- [배포 전 페이지 검사](../../evaluation/results/2026-11-02-besties-category/before-pages.json)
- [배포 후 페이지 검사](../../evaluation/results/2026-11-02-besties-category/after-pages.json)
- [배포 전 AI 관찰 가져오기](../../evaluation/results/2026-11-02-besties-category/before-evaluation.json)
- [배포 후 AI 관찰 가져오기](../../evaluation/results/2026-11-02-besties-category/after-evaluation.json)

README와 배너의 바이트를 보존했고 About 쓰기 작업은 수행하지 않았다.
이 후속 작업은 비공개 소스 저장소를 사용하지 않았다. 계정·UI 식별자와 전체 브라우저
원문은 공개 기록에서 생략했다. 공개 관찰 요약을 원본 전체의 재현 가능한 증거로 표현하지 않는다.
