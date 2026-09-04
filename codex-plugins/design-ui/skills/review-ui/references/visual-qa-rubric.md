# Visual QA 판정 기준

`review-ui`가 실제 브라우저 결과의 검토 행렬과 `UiFinding` severity를 정할 때 읽는다.
사용자나 프로젝트가 정한 기준이 있으면 그것을 우선하며, 이 문서는 없는 부분에 대한
기본값이다.

## 검토 행렬

사용자나 프로젝트가 viewport를 정하지 않았으면 다음 세 개를 기본으로 한다.

| 분류 | 기본 viewport |
|---|---|
| mobile | `390 × 844` |
| tablet | `768 × 1024` |
| desktop | `1440 × 900` |

대상에 실제로 존재하고 관련된 상태를 고른다. happy path 하나로 줄이지 않는다.

- `default`
- `loading`
- `empty`
- `error`
- `disabled`
- 핵심 `hover`, `focus`, `open/closed` interaction

존재하지 않는 상태를 만들어내지는 않는다. 확인할 수 없는 조합은 통과로 세지 말고
미검토 범위와 이유에 남긴다. Repair에서는 before와 같은 route·viewport·state 조합을
after에도 사용한다.

## 검사 범주

각 행렬 조합에서 다음을 관찰한다.

- alignment와 요소 간 정렬 관계
- spacing과 여백 리듬
- typography의 크기, 굵기, 행간, 가독성
- hierarchy와 주요 행동의 우선순위
- color 및 token consistency
- component consistency와 상태별 변형
- overflow, clipping, 겹침, 잘림
- responsive reflow, wrapping, 콘텐츠 우선순위
- 주요 interaction의 작동과 상태 피드백
- 키보드 focus visibility

발견은 실제 화면에서 관찰된 결과와 재현 단계에 연결한다. DOM 수치나 정적 코드만으로
시각 판정을 대신하지 않는다.

선택된 `ready-for-build` UI 명세가 있으면 finding의 `expected`에 명세 경로와 절 또는
정확한 `UI-AC-*` ID를 기록한다. 다른 디자인 정본이면 마찬가지로 경로와 해당 절을
기록한다. 일반 원칙만 근거라면 `heuristic`이라고 명시한다. 선택된 non-ready 명세와
독립적인 `GeneralAudit`에서는 그 명세를 expected로 인용하지 않는다.

## Acceptance 판정

UI 명세의 acceptance check는 owner/evidence 조합에 맞는 수단으로만 판정한다.

| owner | evidence | 판정 수단 | 허용 결과 |
|---|---|---|---|
| `codex` | `render` | 명시된 viewport·state의 실제 화면 근거 | `pass`, `fail`, `unverified` |
| `codex` | `automated-check` | 프로젝트에 이미 있는 관련 검사 | `pass`, `fail`, `unverified` |
| `user` | `user-decision` | 같은 check에 대한 사용자의 명시적 승인·거절 | `awaiting-user-acceptance`, `pass`, `fail` |

세 조합 밖의 입력은 명세 계약 오류다. 사용자 소유 check는 결정 전
`awaiting-user-acceptance`이며 Codex가 화면을 보고 자동으로 `pass` 처리하지 않는다.
사용자의 명시적 승인 뒤에만 `pass`, 거절 뒤에만 `fail`로 바꾼다. Codex 결과에
`awaiting-user-acceptance`, 사용자 결과에 `unverified`를 기록하지 않는다.

`GeneralAudit`은 acceptance result를 만들지 않는다. non-ready 명세 때문에 명세 기반
판정을 하지 못한 사실은 `non-ready 명세로 인해 미평가`로 보고하며, 이를 임의의
`unverified` 결과로 만들지 않는다.

## Severity

| severity | 판정 기준 |
|---|---|
| `blocker` | 페이지나 핵심 흐름을 볼 수 없거나 사용 자체가 불가능하다. |
| `major` | 핵심 위계·레이아웃·반응형·상호작용이 무너져 주요 사용을 방해한다. |
| `moderate` | 일관성이나 가독성을 분명히 해치지만 사용자는 우회할 수 있다. |
| `minor` | 국소적인 시각 다듬기 또는 낮은 영향의 불일치다. |

가장 높은 등급을 만들기 위해 가능성을 부풀리지 않는다. severity는 현재 viewport와 상태에서
관찰되는 사용자 영향으로 정한다. 여러 조합에 반복되는 원인이 하나라면 중복 발견을
남발하지 말고 영향을 받는 위치를 한 발견에 명시한다.

## Status

| status | 사용 조건 |
|---|---|
| `open` | 근거가 있고 아직 해결되지 않은 명백한 결함 또는 정본 위반이다. |
| `fixed` | Repair 후 같은 행렬의 after 근거로 해결이 확인됐다. |
| `design-decision-required` | 서로 충돌하는 정본이나 미규정 선택 때문에 새 디자인 결정이 필요하다. |
| `unverified` | 근거 수단 부재나 불완전한 재검증으로 현재 상태를 확인할 수 없다. |

`design-decision-required`는 review가 취향을 새 정본으로 확정하지 않도록 하는 경계다.
Repair에서도 이 상태는 수정하지 않는다.

## 참고 이미지 비교

- 사용자가 pixel-perfect를 명시했다면 같은 viewport와 상태에서 직접 비교하고, 기준 이미지,
  비교 조건, 남은 차이를 보고한다.
- 일반 참고물은 구조, 간격, 위계, 밀도, 반응형 행동의 충실도를 비교한다. 사용자가
  요청하지 않은 브랜드, 문구, 콘텐츠 차이는 결함으로 세지 않는다.
- 참고 이미지가 일부 화면만 보여주면 보이지 않는 상태나 breakpoint를 추론하지 않는다.
- URL·Figma·이미지에 접근할 수 없으면 내용을 꾸며내지 않고 해당 비교를 `unverified`와
  미검토 범위로 남긴다.

## 디자인 정본이 없을 때

명백한 clipping, 가로 overflow, 읽을 수 없는 겹침, 작동하지 않는 핵심 interaction처럼
관찰 가능한 렌더링 결함은 사실로 기록할 수 있다. 그 외 일반적인 디자인 원칙에 따른
발견은 `expected: heuristic`으로 표시하고 계약 위반과 구분한다. 단순 취향은 발견으로
승격하지 않는다.

## 접근성 범위

프로젝트에 자동 접근성 검사가 있으면 실행 결과를 함께 기록하고, 키보드 focus visibility와
시각적으로 관찰 가능한 문제를 행렬에서 확인한다. 그러나 이 Visual QA를 완전한 접근성
감사로 표현하지 않는다. 보조 기술 동작, 의미 구조, 동적 안내 등 별도 수단으로 확인하지
않은 항목은 미검토 범위에 남긴다.
