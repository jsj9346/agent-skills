# Codex UI Render Bridge 재개 실행 플랜

- 상태: 초안
- 작성일: 2026-09-05
- 정본 설계: `docs/codex-ui-workflow-skills.md` §3.5, §7, §8.2~§8.3, §9
- 선행 실행 기록: `plans/20260905-codex-ui-workflow-skills-execute-report.md`
- 실행 명령: `$execute plans/20260905-codex-ui-render-bridge-plan.md`

## 1. 개요

### 1.1 목표

기존 UI 워크플로 스킬 구현은 그대로 보존하면서, 내부 `codex exec --sandbox workspace-write`에서 Chromium을 시작할 수 없는 평가 환경을 위한 **평가 전용 렌더 브리지**를 만든다. 외부 러너는 결정론적 시나리오를 실행하고 증거를 캡처하는 역할만 맡고, 동일한 피평가 플러그인을 사용하는 후속 Codex가 그 이미지를 직접 열어 판정한다.

이 플랜은 다음 세 가지 결과를 함께 닫는다.

1. 정본 §8.2의 `OrchestratedRender` 계약과 BR0~BR10 회귀 사례를 실행 가능한 하네스로 구현한다.
2. 선행 플랜에서 렌더 차단 때문에 부분 검증으로 남은 U5·U6·U7·U9와 GeneralAudit·Repair를 재평가한다.
3. 새 증거와 재사용 가능한 선행 증거를 묶어 §8.3 불변조건 전체를 독립 검증하고 실행 기록을 완료한다.

### 1.2 범위

포함:

- 저장소 수준의 평가 하네스 `scripts/ui_workflow_eval/`
- 브리지 요청·스냅샷·캡처·판정 계보의 스키마 검사와 해시 검증
- Playwright/Chromium 능력 탐지와 외부 캡처 어댑터
- BR0~BR10 구조·보안·종단간 회귀 검증
- 선행 실행 증거의 적격성 검사와 조건부 재사용
- 미완료 런타임 평가 재개, 독립 검증, 기록 갱신

제외:

- `codex-plugins/design-ui/**`의 기능 변경 (`review-ui`는 이 플러그인의 하위 skill이다.)
- 플러그인에 MCP 서버·브라우저 서버·런타임 의존성·평가 스크립트를 추가하는 일
- 제품용 브라우저 자동화 계층 또는 범용 테스트 프레임워크 도입
- npm/pip 패키지 설치, 외부 네트워크 사용, 공개/배포
- 선행 플랜 T-001~T-005를 다시 구현하거나 이력을 덮어쓰는 일

### 1.3 전제 기술 스택과 현재 상태

- Python 3 표준 라이브러리: manifest·해시·경로·상태 전이 검사
- Node.js와 이미 존재하는 Playwright/Chromium: 선언적 브라우저 동작과 PNG 캡처
- Codex CLI: 피평가 producer와 후속 adjudicator의 격리 호출
- Git과 기존 `scripts/validate_skill_links.py`: 스냅샷·보호 경로·프로젝트 표준 통합 검사

새 런타임이나 패키지는 도입하지 않는다. `design-ui`와 `review-ui` 제품 파일은 선행 플랜에서 구현되었고, 현재 남은 일은 sandbox browser blocker를 우회하지 않고 증거 계보로 다루는 평가 하네스와 미완료 런타임 검증이다. 정본 §8.2의 계약은 확정되어 있으며 착수 전 사용자 결정은 없다.

### 1.4 제약 조건

- 계약과 어긋나면 코드를 임의로 맞추지 않고 작업을 중단해 정본 문서를 먼저 재논의한다.
- 원자적 작업 커밋만 만들며 push는 사용자의 별도 확인 뒤에만 한다.
- 새 외부 의존성, 네트워크 접근, 제품 플러그인 변경은 허용하지 않는다.
- 호출 예산은 기본 24회, 재시도를 포함한 전체 36회다.
- 독립 검증과 통합 게이트가 green이 아니면 완료로 기록하지 않는다.

### 1.5 성공 조건

- `codex-plugins/design-ui`의 정확한 12개 파일과 기존 해시가 평가 전후 동일하다.
- 외부 러너가 판단을 내리지 않고 캡처만 수행한다.
- 캡처와 판정은 `producer_call_id`, `request_sha256`, fixture/product/design authority/UI spec/installed plugin inventory 해시로 닫힌 계보를 가진다.
- 원본 변경, 누락 캡처, 구식 요청, 불완전 계보는 어떤 경우에도 green이 되지 않는다.
- BR0~BR10이 정본의 기대 결과대로 각각 통과한다. BR1은 단위 테스트로 대체하지 않고 실제 InnerRender와 same-call 판정을 증명한다.
- U5·U6·U7·U9, GeneralAudit, Repair, lifecycle 재개, 잘못된 result status가 완전한 판정 증거를 가진다.
- 독립 검증에서 blocker/high/medium/low 발견이 0건이다.
- `python3 scripts/validate_skill_links.py`와 §6.5의 하네스 게이트가 모두 종료 코드 0이다.
- `test "$(find codex-plugins/design-ui -type f | wc -l)" -eq 12`가 통과하고 정본 §3.3 경로 집합 비교가 일치한다.

### 1.6 구현 원칙

- 브리지는 제품 플러그인이 아니라 계획 소유의 평가 하네스다.
- 요청은 선언적 allowlist만 허용하며 사례가 작성한 임의 스크립트를 실행하지 않는다.
- 외부 네트워크·비밀·사례 루트 밖 파일·지정 출력 밖 쓰기를 금지한다.
- outer capture와 Codex adjudication을 서로 다른 단계와 산출물로 분리한다.
- 수정이 일어나면 이전 캡처는 즉시 stale이며 반드시 재캡처한다.
- 선행 증거 재사용은 경로 존재만으로 허용하지 않고 보고서 해시와 현재 정본/플러그인 해시를 대조한다.
- 실행 중 설계 계약의 변경이 필요해지면 구현하지 않고 중단해 `/make-design`으로 되돌린다.

## 2. 작업 목록

| ID | 우선순위 | 작업 | 의존성 | 주요 산출물 | 완료 판정 |
|---|---|---|---|---|---|
| T-001 | P0 | 기준선·선행 증거 적격성 확정 | 없음 | 실행 전 스냅샷, reuse manifest, 신규 증거 루트 | 보호 경로/해시와 재사용·재실행 목록이 확정됨 |
| T-002 | P0 | 평가 전용 렌더 브리지 하네스 구현 | T-001 | `bridge.py`, `capture.mjs`, 단위 테스트 | 계보·경로·네트워크·상태 전이가 자동 검사됨 |
| T-003 | P0 | 캡처 능력 및 BR0 이미지 판정 게이트 검증 | T-002 | capability record, BR0 evidence | Codex가 실제 이미지를 열어 숨은 값을 맞춤 |
| T-004 | P0 | BR1~BR6 핵심 경로·실패 경로 검증 | T-003 | BR1~BR6 evidence | 직접/브리지 분기와 stale/incomplete 차단이 확인됨 |
| T-005 | P0 | BR7~BR10 모드·수정·보안 검증 | T-004 | BR7~BR10 evidence | Audit/Repair 계보와 보안 경계가 확인됨 |
| T-006 | P1 | 선행 런타임 평가의 미완료 계약 재개 | T-005 | U5/U6/U7/U9, GeneralAudit/Repair, lifecycle/status evidence | 부분 판정이 완전한 판정으로 대체됨 |
| T-007 | P0 | 독립 정본 대조 및 통합 게이트 | T-006 | 독립 검증 기록, 통합 검사 로그 | 발견 0건, 모든 필수 명령 통과 |
| T-008 | P1 | 기록·상태·커밋·정리로 종료 | T-007 | 실행 리포트, `workstate.md`, 원자적 커밋 | 재현 경로와 다음 단계가 기록됨 |

## 3. 역할 분리

| 작업 | 수행자 | 검증자 | 분리 규칙 |
|---|---|---|---|
| T-001 기준선/재사용 판정 | 실행 담당 Codex | T-007 독립 검증자 | 검증자는 reuse manifest를 선행 보고서와 직접 대조한다. |
| T-002 하네스 구현 | 실행 담당 Codex | T-002 단위 테스트 + T-007 독립 검증자 | 구현자는 테스트를 작성하지만 최종 계약 판정은 하지 않는다. |
| T-003~T-006 사례 실행 | producer Codex + 외부 capture runner + adjudicator Codex | T-007 독립 검증자 | capture runner는 이미지 의미를 판정하지 않는다. producer와 adjudicator 산출물을 분리한다. |
| Audit/GeneralAudit | 피평가 review-ui | T-007 독립 검증자 | Audit 실행은 제품/fixture를 수정할 수 없다. |
| Repair | 피평가 review-ui | adjudicator Codex + T-007 독립 검증자 | before/after 캡처와 소스 해시를 별도로 보존한다. |
| 최종 판정 | T-007 독립 검증자 | 실행 담당 Codex는 기록만 반영 | 독립 검증자는 구현자의 요약이 아니라 정본과 실물을 직접 읽는다. |

독립 검증은 `/verify` 절차에 준해 별도 에이전트가 수행한다. 실행 담당자는 검증자에게 정본 경로, 대상 경로, 증거 루트만 전달하고 기대 결과를 요약해 주입하지 않는다.

## 4. 상세 작업 명세

### T-001 — 기준선·선행 증거 적격성 확정

#### 목적

사용자 변경과 선행 실행 결과를 보존하고, 어떤 증거를 재사용할 수 있는지 결정론적으로 확정한다.

#### 수행

1. `git status --short`, `git diff --check`, 현재 HEAD, 정본 문서와 `design-ui` 플러그인의 파일 목록·SHA-256을 기록한다. `review-ui`는 `codex-plugins/design-ui/skills/review-ui`에 포함된다.
2. 현재 미커밋 정본 설계와 `workstate.md`, 이 플랜을 한 개의 실행 전 스냅샷 커밋으로 보존한다. 사용자 소유의 다른 변경이 발견되면 포함하지 않는다.
3. `plans/20260905-codex-ui-workflow-skills-execute-report.md`의 증거 인벤토리와 `/tmp/ui-workflow-eval.d1kdjz`의 실물을 대조한다.
4. 새 증거 루트는 `mktemp -d /tmp/ui-render-bridge-eval.XXXXXX`로 만들고 절대 경로를 실행 리포트에 즉시 적는다.
5. 다음 필드를 가진 `reuse-manifest.json`을 새 증거 루트에 만든다: case ID, 선행 commit/report hash, 원본 경로와 transcript hash, source inventory hash, installed-plugin inventory hash, 관련 정본 절과 그 절의 당시/현재 hash, `reuse|rerun|invalid` 판정, 근거.
6. 정본 §8.2 추가로 의미가 바뀐 렌더 의존 산출물은 재사용하지 않는다. U1~U4·U8·U10~U12의 비렌더 계약 증거만 선행 commit/report·transcript·source inventory·installed-plugin inventory가 일치하고 관련 비렌더 정본 절의 의미가 바뀌지 않았음을 line-level diff로 증명할 때 재사용 후보가 된다.
7. 설치나 다운로드 없이 Playwright JavaScript API와 Chromium executable을 탐지한다. 저장소의 기존 의존성 → 오프라인 npx 캐시 → workspace 내부 기존 설치 순서로 찾고, 절대 경로·버전·파일 해시를 `capability-preflight.json`에 기록한다. 찾지 못하면 T-002 구현 전에 중단한다.
8. 선행 임시 증거가 없거나 인벤토리 해시가 다르면 해당 사례를 `rerun`으로 돌린다. 호출 예산 안에서 비렌더 최소 사례를 재실행하며, 예산을 넘길 전망이면 T-006 전에 중단해 재계획한다.

#### 검증

```bash
git status --short
git diff --check
find codex-plugins/design-ui -type f -print | LC_ALL=C sort
sha256sum docs/codex-ui-workflow-skills.md codex-plugins/design-ui/.claude-plugin/plugin.json codex-plugins/design-ui/skills/review-ui/SKILL.md
python3 -m json.tool "$EVIDENCE_ROOT/reuse-manifest.json" >/dev/null
python3 -m json.tool "$EVIDENCE_ROOT/capability-preflight.json" >/dev/null
```

`$EVIDENCE_ROOT`는 실행 중 만든 정확한 임시 경로로 치환한다. 공용 환경 변수 이름을 재사용하지 않는다.

#### 산출물

- 실행 전 스냅샷 커밋
- `$EVIDENCE_ROOT/baseline/`
- `$EVIDENCE_ROOT/reuse-manifest.json`
- `$EVIDENCE_ROOT/capability-preflight.json`
- 실행 리포트의 T-001 절

#### 롤백

스냅샷 커밋 이후의 T-001 전용 기록만 `git revert`로 되돌린다. 선행 증거는 이동·삭제하지 않는다.

### T-002 — 평가 전용 렌더 브리지 하네스 구현

#### 목적

§8.2의 요청, 불변 스냅샷, 캡처, 판정 계보와 안전 경계를 저장소 수준의 작은 하네스로 구현한다.

#### 구현 파일

- `scripts/ui_workflow_eval/bridge.py`
- `scripts/ui_workflow_eval/capture.mjs`
- `scripts/ui_workflow_eval/tests/test_bridge.py`

#### 계약

`bridge.py`는 표준 라이브러리만 사용하고 다음 하위 명령을 제공한다.

- `snapshot`: `case_realpath`를 기준으로 fixture/product/design authority/UI spec/installed plugin inventory의 정확한 다섯 SHA-256 manifest를 만든다.
- `validate-request`: `RenderBridgePending` 요청의 필수 필드, bridge 활성화 5조건, `request_sha256`, case root, output root, 허용 action을 검사한다.
- `validate-capture`: `request_sha256`, `producer_call_id`, immutable snapshot, exact scenario matrix를 캡처 결과에 대조하고 누락·중복·구식 결과를 분류한다.
- `validate-adjudication`: adjudicator가 실제 이미지를 열었다는 이벤트, `producer_call_id`, `request_sha256`, producer/capture hash, 동일 skill·mode·설치본 hash, 결과 상태를 검사한다.
- `validate-index`: 여러 case의 증거 경로·hash·정본 매핑을 집계 검증한다.
- `probe-image`: BR0 전용 one-shot coordinator로 challenge 생성 → plan-owned capture → source/seed 삭제 검증 → 격리 Codex 호출 → 메모리 기대값 대조를 수행한다.
- `validate-probe`: BR0 전용 `ImageProbeEvidence`만 검사하며 producer, blocker, skill/mode/plugin lineage를 요구하지 않는다. 이 예외를 일반 bridge validator에 섞지 않는다.
- `finalize-inner`: BR1의 `InnerRender`만 검사한다. producer와 image adjudicator call ID가 같고 실제 image-open 귀속과 verdict가 있으며 `RenderBridgePending`·outer capture·후속 adjudicator 호출이 전혀 없을 때만 성공한다.
- `verify-archive`: deterministic redaction policy, 제외 목록, case index, 파일 hash inventory의 일관성을 검사하고 `auth.json`, `.env*`, private-key 파일, 원문 credential sentinel을 구조적으로 거부한다.
- `finalize`: `Captured`, `StaleRenderRequest`, `IncompleteCapture`, `CaptureBlocked`, `Adjudicated`, `AdjudicationUnverified`만 허용해 case verdict를 만든다.
- `self-test`: 배포된 환경에서 핵심 음성/양성 사례를 빠르게 실행한다.

`capture.mjs`는 계획 소유의 JSON 요청만 읽고 다음 allowlist action만 실행한다.

- `goto`
- `click`
- `fill`
- `press`
- `waitForVisible`
- `screenshot`

추가 제약:

- Playwright 패키지 위치와 Chromium 실행 파일은 capability probe가 발견한 절대 경로만 인자로 받으며 코드에 사용자 홈 경로를 고정하지 않는다.
- 요청 snapshot은 정본과 같은 `case_realpath`, fixture, product, design authority, UI spec, installed plugin inventory의 정확한 다섯 manifest hash를 가진다.
- bridge는 필수 build/check 성공, 허용된 blocker class와 원본 stderr, evaluation root 안이면서 repository root 밖인 case realpath, non-empty·unique scenario matrix, 완전한 snapshot의 다섯 조건이 모두 참일 때만 활성화된다.
- `request_sha256`은 canonicalized `RenderBridgePending` 전체에서 계산하며 임의 request ID로 대체하지 않는다.
- `file:` URL은 case root 내부, `http:` URL은 loopback만 허용한다. `https:`와 비-loopback 요청은 시작 전에 거절한다.
- 최초 URL뿐 아니라 브라우저가 요청하는 모든 `file:` resource의 realpath가 case root 안인지 검사하고, loopback/file 외 네트워크를 차단한다.
- 입력과 스크린샷은 지정된 evidence output root 아래에만 쓴다.
- `eval`, 임의 JavaScript, shell 문자열, credential/환경 비밀 전달, 임의 executable 선택을 허용하지 않는다. 자식 프로세스 환경은 이름이 고정된 최소 allowlist로 새로 구성한다.
- viewport, timeout, action 수, 문자열 길이에 상한을 둔다.
- 캡처 성공 여부만 반환하며 시각적 합격/불합격을 계산하지 않는다.
- `capture.mjs`의 실행 시점 SHA-256은 `runner_argv`의 고정 `--runner-sha256` 인자와 capability record 양쪽에 기록하며, validator가 실제 파일 hash와 맞는지 확인한다. 정본 schema를 늘리지 않는다.
- BR9/BR10 정책 거부는 임의 새 result variant를 만들지 않는다. plan-owned adapter의 고정 invocation이 browser 생성 전에 정책 exit code `64`로 끝나고, stderr path와 affected scenarios를 채운 `CaptureBlocked`로 기록한다.

BR0 전용 `ImageProbeEvidence`는 probe ID, PNG path/hash, capture runner hash, source/seed 삭제 검사, adjudicator call ID, image-open event 유무, 응답, 부모 coordinator의 비교 결과만 가진다. 일반 `RenderBridgePending`, `RenderCaptureEvidence`, `RenderAdjudicationResult`와 호환되는 척하지 않으며 bridge 성공 건수에도 포함하지 않는다.

테스트는 최소 다음을 포함한다.

- 올바른 요청·스냅샷·캡처·판정의 양성 경로
- BR0 probe와 일반 bridge schema의 완전한 분리, BR0를 일반 validator에 넣었을 때의 거부
- BR1 `InnerRender`의 same-call·image-open·bridge 미호출 양성 경로와 call ID 불일치/outer capture 존재 음성 경로
- fixture/product/design authority/UI spec/installed plugin inventory 각 해시 변경
- `request_sha256`·`producer_call_id` 불일치와 viewport/state/capture 누락
- case root 탈출, symlink 탈출, output root 탈출
- 외부 URL, 금지 action, 임의 script, 과도한 timeout/action 수
- Audit 불변성 및 Repair before/after 계보
- skill·mode·설치본 hash가 다른 adjudicator와 `skill-attribution-missing`
- 알려지지 않은 status의 fail-closed 처리

#### 검증

```bash
python3 -m unittest discover -s scripts/ui_workflow_eval/tests -p 'test_*.py'
python3 scripts/ui_workflow_eval/bridge.py self-test
python3 -m py_compile scripts/ui_workflow_eval/bridge.py scripts/ui_workflow_eval/tests/test_bridge.py
node --check scripts/ui_workflow_eval/capture.mjs
git diff --check
```

#### 산출물

- 위 3개 구현 파일
- `$EVIDENCE_ROOT/t002/`의 검사 로그
- T-002 원자적 커밋

#### 롤백

T-002 커밋만 `git revert`한다. 플러그인 파일은 이 작업의 수정 대상이 아니다.

### T-003 — 캡처 능력 및 BR0 이미지 판정 게이트 검증

#### 목적

비용이 큰 사례를 시작하기 전에 외부 캡처와 후속 Codex의 실제 이미지 열람 능력을 증명한다.

#### 수행

1. T-001의 capability record에 고정된 Playwright/Chromium 경로·버전·hash로 외부 캡처 어댑터가 local fixture를 열고 PNG를 만드는지 확인한다.
2. BR0 challenge는 one-shot coordinator가 실행 시 만든다. 임의 문자열·도형·색·배치 조합을 HTML로 렌더해 의미 없는 무작위 파일명의 PNG를 만든 뒤, adjudicator 호출 전에 HTML·seed·생성 로그를 삭제한다.
3. 기대값은 adjudicator가 읽을 수 있는 파일이나 환경에 쓰지 않고 부모 coordinator의 메모리에만 유지한다. adjudicator에게 노출되는 격리 디렉터리에는 metadata를 제거한 PNG와 응답 스키마만 둔다.
4. 피평가 환경과 같은 Codex CLI/모델/샌드박스 설정으로 adjudicator를 한 번 호출한다. JSONL에 직접 image-open event가 있으면 이를 우선 증거로 삼고, tool schema가 event를 노출하지 않을 때만 메모리에 보관한 숨은 기대값과 응답을 부모 coordinator가 대조한다.
5. 원본 HTML·seed·기대값이 호출 시점 filesystem, prompt, filename, PNG metadata, manifest에 없었다는 삭제·검사 로그를 남긴다. 파일 경로나 주변 텍스트만으로 맞힐 수 있는 challenge는 무효다.
6. BR0가 실패하면 T-004 이후를 실행하지 않는다. image-open 귀속과 숨은 값 대조 중 정본이 허용한 어느 방식으로도 시각 입력을 증명하지 못하면 `image-not-opened`다.

#### 검증

```bash
python3 scripts/ui_workflow_eval/bridge.py validate-probe --evidence "$EVIDENCE_ROOT/br0/probe-evidence.json"
file "$EVIDENCE_ROOT/br0/captures/primary.png"
```

#### 산출물

- `$EVIDENCE_ROOT/capability.json`
- `$EVIDENCE_ROOT/br0/`
- 실행 리포트의 BR0 판정과 실제 호출 수

#### 호출 예산

- 기본 1회, 동일 원인의 형식 오류에 한해 재시도 1회

#### 롤백/중단

BR0 실패는 구현 롤백 사유가 아니라 환경 능력 blocker다. 즉시 중단하고 증거를 보존한다. 새 패키지를 설치해 우회하지 않는다.

### T-004 — BR1~BR6 핵심 경로·실패 경로 검증

#### 목적

InnerRender/OrchestratedRender 선택, 성공 계보, stale 및 incomplete 실패를 검증한다.

#### 사례

| 사례 | 실행 방식 | 기대 결과 |
|---|---|---|
| BR1 | 격리 local fixture에서 대상 skill이 브라우저를 직접 실행할 수 있는 Codex profile로 실제 InnerRender | bridge 미사용, 동일 producer 호출이 이미지 확인과 판정까지 완료. 성립하지 않으면 플랜 완료 금지 |
| BR2 | U5 또는 U7 producer가 sandbox browser blocker 반환 → outer capture → 동일 skill·mode·설치본 hash의 adjudicator | `Adjudicated`; `producer_call_id`, `request_sha256`, 다섯 snapshot hash 일치 |
| BR3 | capture 실행 전에 fixture/product/design authority/UI spec/plugin inventory 중 각 hash를 차례로 불일치시킨 요청 | `StaleRenderRequest`, 브라우저 프로세스 미실행 |
| BR4 | 유효 capture 뒤 source/UI spec/design authority를 각각 변경한 사본 | adjudication 거부, `AdjudicationUnverified(reason: stale-snapshot)` |
| BR5 | viewport 또는 state 누락, 빈 image, browser non-zero exit을 각각 재현 | `IncompleteCapture` 또는 `CaptureBlocked`; `Captured` 금지 |
| BR6 | 유효 캡처에서 adjudicator 결과/이미지-open 증거 제거 | `AdjudicationUnverified`, green 금지 |

BR3~BR6은 T-002 테스트만 재인용하지 않고 실제 BR2 산출물을 복제한 별도 evidence case에서 black-box 명령으로 재현한다. BR3은 adapter 시작 marker/PID가 생기지 않았음을 함께 검사한다. 테스트용 변조는 fixture/evidence 사본에서만 수행한다.

#### 검증

```bash
python3 scripts/ui_workflow_eval/bridge.py finalize-inner --case-root "$EVIDENCE_ROOT/br1"
python3 scripts/ui_workflow_eval/bridge.py finalize --case-root "$EVIDENCE_ROOT/br2"
python3 scripts/ui_workflow_eval/bridge.py finalize --case-root "$EVIDENCE_ROOT/br3"
python3 scripts/ui_workflow_eval/bridge.py finalize --case-root "$EVIDENCE_ROOT/br4"
python3 scripts/ui_workflow_eval/bridge.py finalize --case-root "$EVIDENCE_ROOT/br5"
python3 scripts/ui_workflow_eval/bridge.py finalize --case-root "$EVIDENCE_ROOT/br6"
```

#### 산출물

- `$EVIDENCE_ROOT/br1/` ~ `$EVIDENCE_ROOT/br6/`
- U5/U7 중 사용한 사례의 완전한 producer→capture→adjudicator transcript

#### 호출 예산

- BR2 계열 producer/adjudicator 합계 기본 4회 이내
- BR1 실제 경로 probe 1회 이내
- 재시도 포함 T-004 누적 8회 이내

### T-005 — BR7~BR10 모드·수정·보안 검증

#### 목적

Audit/GeneralAudit의 비변경성, Repair의 재캡처 계보, 외부 러너의 파일·네트워크 경계를 검증한다.

#### 사례

| 사례 | 실행 방식 | 기대 결과 |
|---|---|---|
| BR7 | U6/U9 또는 GeneralAudit을 bridge로 캡처·판정하고 전후 다섯 snapshot hash 비교 | `Adjudicated`; product·fixture·design authority·UI spec·plugin inventory 불변 |
| BR8 | 첫 Repair producer pending → 같은 scenario matrix의 before 캡처 → 첫 Repair adjudicator가 이미지를 열어 findings 고정·소스 수정·`repair-after` pending 발행 → 새 hash의 after 재캡처 → 두 번째 Repair adjudicator가 새 이미지를 열어 최종 판정 | 두 round가 같은 skill·설치본에 귀속되고 이전 캡처 stale, before/after 계보 분리, 수정 결과만 최종 판정 |
| BR9 | case-authored script를 outer에서 실행하라는 요청 | plan-owned hashed adapter가 정책 exit code로 실행 전 거부; 임의 명령 미실행 |
| BR10 | 외부 network·credential sentinel·evaluation root 밖 경로 및 symlink 접근 요청 | 고정 adapter invocation의 `CaptureBlocked`와 명시적 blocker; 외부 접근·credential 전달 없음 |

Audit, GeneralAudit, Repair는 각 모드의 실제 피평가 스킬을 사용한다. BR9~BR10은 하네스 black-box 검사와 파일 시스템 전후 hash/프로세스 로그로 증명한다.

#### 검증

```bash
python3 scripts/ui_workflow_eval/bridge.py finalize --case-root "$EVIDENCE_ROOT/br7"
python3 scripts/ui_workflow_eval/bridge.py finalize --case-root "$EVIDENCE_ROOT/br8"
python3 scripts/ui_workflow_eval/bridge.py finalize --case-root "$EVIDENCE_ROOT/br9"
python3 scripts/ui_workflow_eval/bridge.py finalize --case-root "$EVIDENCE_ROOT/br10"
git diff --exit-code "$BASELINE_SHA" HEAD -- codex-plugins/design-ui
```

BR8의 fixture 수정은 증거 루트 내부 복제본에서만 일어나므로 마지막 명령은 제품 플러그인의 무변경을 검사한다.

#### 산출물

- `$EVIDENCE_ROOT/br7/` ~ `$EVIDENCE_ROOT/br10/`
- Audit/GeneralAudit 전후 hash manifest
- Repair before/after lineage manifest

#### 호출 예산

- Audit/GeneralAudit producer+adjudicator 합계 기본 6회 이내
- Repair 생산·수정·판정 합계 기본 4회 이내
- 재시도 포함 T-005 누적 14회 이내

### T-006 — 선행 런타임 평가의 미완료 계약 재개

#### 목적

BR 증거를 U 사례에 연결하고, 렌더 외에 선행 플랜에서 완전 판정이 없었던 lifecycle/status 계약을 닫는다.

#### 수행

1. BR2/BR7/BR8에 사용한 사례가 U5·U6·U7·U9, GeneralAudit, Repair의 원래 입력·예상 계약을 만족하면 동일 증거를 case mapping으로 재사용한다. 의미가 다른 사례는 별도로 실행한다.
2. lifecycle 재개 4종을 독립 호출로 검증한다: `NeedsInput`, `ReferenceBlocked`, `DesignConflictDuringDrafting`, `DesignConflictDuringDecisionCheck`. 각 호출은 persistent `UiSpec.status`와 영향을 받는 범위를 보존하고 허용된 phase로만 재개해야 한다.
3. 허용되지 않은 result status 두 종류를 명시적으로 주입한다: Codex-owned acceptance check에 `awaiting-user-acceptance`, user-owned acceptance check에 `unverified`. 둘 다 거부되고 입력 원문 값이 보존되어야 한다.
4. T-001에서 적격 판정된 비렌더 선행 증거와 새 증거를 하나의 `case-index.json`으로 묶는다. 각 항목은 재사용/신규 여부, 정본 절, producer/adjudicator transcript hash, request hash, capture evidence hash, installed-plugin inventory hash, exact scenario-matrix hash, 모든 evidence path/hash, 최종 판정을 가진다. InnerRender와 BR0에는 존재하지 않는 bridge 필드를 `null`로 꾸미지 않고 각 타입의 별도 필수 필드 집합을 적용한다.
5. 검증 대상 manifest, redacted JSONL transcript, 명령 로그, BR0~BR10 PNG를 `plans/evidence/20260905-codex-ui-render-bridge/`에 복사한다. deterministic redaction 규칙과 제외 파일 목록을 기록하고 초기 `inventory.sha256`을 만든다. BR10 credential sentinel은 원문이 아닌 SHA-256과 `redacted` marker만 보존한다.
6. 총 호출 수를 기본/재시도로 나누어 기록한다. 기본 24회, 전체 36회 상한을 넘기기 전에 중단한다.

#### 검증

```bash
python3 -m json.tool "$EVIDENCE_ROOT/case-index.json" >/dev/null
python3 scripts/ui_workflow_eval/bridge.py validate-index --index "$EVIDENCE_ROOT/case-index.json"
python3 scripts/validate_skill_links.py
git diff --check
```

#### 산출물

- `$EVIDENCE_ROOT/runtime/`
- `$EVIDENCE_ROOT/case-index.json`
- `plans/evidence/20260905-codex-ui-render-bridge/`의 검증 전 영속 증거 묶음
- 실행 리포트의 U/모드/lifecycle/status 대조표와 호출 예산표

#### 중단 조건

- 기본 24회 또는 총 36회 상한 초과 예상
- 동일 환경 blocker가 재시도 뒤에도 반복
- 정본이 허용하지 않은 결과 상태나 수정 필요 발견
- fixture/product/design authority/UI spec/plugin inventory hash가 실행 중 예고 없이 변경

### T-007 — 독립 정본 대조 및 통합 게이트

#### 목적

구현자와 분리된 검증자가 정본 §3.5·§7·§8.2·§8.3·§9에 실물과 증거를 직접 대조한다.

#### 독립 검증 범위

- `owner: codex`가 판정 책임이고 브라우저 프로세스 소유권이 아님
- 브리지 활성화 사유가 sandbox browser startup 또는 loopback bind blocker로만 제한됨
- app/build/route/reference 오류가 bridge로 우회되지 않음
- outer runner capture-only 및 선언적 action allowlist
- immutable snapshot과 producer/capture/adjudicator 계보
- stale/incomplete/unverified의 fail-closed 처리
- Audit/GeneralAudit 비변경성과 Repair before/after 재캡처
- BR0의 실제 image-open 또는 숨은 값 정답
- BR1~BR10 결과와 실제 transcript/hash
- 제품 플러그인에 브리지 의존성·서버·스크립트가 추가되지 않음
- 선행 증거 재사용 판정과 새 `case-index.json`의 완전성
- 정확한 12파일 계약 및 플러그인 링크/구문 검사

#### 필수 명령

독립 검증자는 판정을 `$EVIDENCE_ROOT`와 영속 evidence의 `verification/independent-review.md`에 쓰고 `commands.log` 기록을 먼저 종료한다. 그 뒤 archive를 읽기 전용으로 취급해 inventory를 한 번 생성·검사하며, checksum/secret-scan 출력은 이미 봉인한 `commands.log`에 덧붙이지 않고 실행 리포트에만 요약한다. 따라서 아래 `sha256sum -c`는 독립 검증 결과까지 포함한 최종 archive를 검사한다.

```bash
python3 -m unittest discover -s scripts/ui_workflow_eval/tests -p 'test_*.py'
python3 scripts/ui_workflow_eval/bridge.py self-test
python3 -m py_compile scripts/ui_workflow_eval/bridge.py scripts/ui_workflow_eval/tests/test_bridge.py
node --check scripts/ui_workflow_eval/capture.mjs
python3 scripts/validate_skill_links.py
git diff --check
test "$(find codex-plugins/design-ui -type f | wc -l)" -eq 12
git diff --exit-code "$BASELINE_SHA" HEAD -- codex-plugins/design-ui
python3 scripts/ui_workflow_eval/bridge.py verify-archive --root plans/evidence/20260905-codex-ui-render-bridge
(cd plans/evidence/20260905-codex-ui-render-bridge && find . -type f ! -name inventory.sha256 -print0 | LC_ALL=C sort -z | xargs -0 sha256sum > inventory.sha256 && sha256sum -c inventory.sha256)
if find plans/evidence/20260905-codex-ui-render-bridge -type f \( -name auth.json -o -name '.env*' -o -name '*.pem' -o -name 'id_rsa*' \) -print -quit | grep -q .; then exit 1; fi
if rg -n -i '(authorization:[[:space:]]*(basic|bearer)[[:space:]]+[[:alnum:]._-]{12,}|api[_-]?key[[:space:]]*[:=][[:space:]]*[[:alnum:]._-]{12,}|credential-sentinel-[[:alnum:]_-]+)' plans/evidence/20260905-codex-ui-render-bridge; then exit 1; fi
```

정확한 12파일 검사는 개수만 보지 않고 정본 §3.3의 경로 집합과 정렬 비교한다. `$BASELINE_SHA`는 T-001에서 기록한 보호 기준 커밋 SHA로 치환하며, 실행 중 커밋된 플러그인 변경까지 검사한다.

#### 판정

- blocker/high/medium/low 어느 하나라도 있으면 T-008 완료 처리 금지
- 설계 문제면 `/make-design docs/codex-ui-workflow-skills.md §8.2`
- 구현 문제면 수정 플랜을 새로 만들거나, 현재 플랜 범위 안의 해당 미완료 작업으로 되돌림
- green이면 검증자가 검사 항목, 명령, 증거 경로, 발견 0건을 서명된 기록으로 남김

#### 산출물

- `$EVIDENCE_ROOT/verification/independent-review.md`
- `$EVIDENCE_ROOT/verification/commands.log`
- `plans/evidence/20260905-codex-ui-render-bridge/verification/independent-review.md`
- 영속 증거의 재생성된 `inventory.sha256`, redaction 검사, secret scan 로그
- 실행 리포트의 독립 검증 절

### T-008 — 기록·상태·커밋·정리로 종료

#### 목적

실행 결과를 추적 가능한 작업 원장으로 닫고 임시 인증·프로세스를 정리한다.

#### 수행

1. `plans/20260905-codex-ui-render-bridge-execute-report.md`를 작성한다.
2. 리포트에 커밋 SHA, 파일 목록, capability, 호출 예산, BR0~BR10, U 사례, 재사용 증거, 독립 검증, 남은 제한을 기록한다.
3. `workstate.md`를 완료 상태와 다음 권장 단계(`/verify` 또는 사용자 검토)로 갱신한다.
4. 구현/테스트, 실행 기록을 의미 단위 원자적 커밋으로 만든다. 기존 커밋을 amend하지 않는다.
5. 실행 중 생성한 임시 인증 설정, 백그라운드 서버, 브라우저 프로세스를 종료한다. 원본 evidence root는 사용자가 후속 검증을 마칠 때까지 보존하고 정확한 경로를 보고한다.
6. T-007이 검증한 영속 증거에서 `sha256sum -c inventory.sha256`, deterministic redaction 검사, secret scan을 마지막으로 한 번 더 실행한다. 브라우저 캐시·`node_modules`·비밀·임시 auth가 없음을 확인한다.
7. 최종 `git status --short`, 전체 필수 명령, 커밋 로그를 다시 기록한다.

#### 완료 조건

- 실행 리포트의 모든 작업이 `완료`이고 blocker가 없다.
- 독립 검증 발견 수가 전 심각도 0이다.
- 보호된 플러그인 경로가 실행 전 기준과 동일하다.
- `workstate.md`와 실제 git 상태가 일치한다.
- 비밀·임시 auth/config가 저장소나 사용자 설정에 남지 않는다.
- `plans/evidence/20260905-codex-ui-render-bridge/inventory.sha256`으로 영속 증거를 재검증할 수 있다.

## 5. 의존성 그래프

```text
T-001 기준선/증거 적격성
  └─ T-002 브리지 하네스
       └─ T-003 capability + BR0 게이트
            └─ T-004 BR1~BR6
                 └─ T-005 BR7~BR10
                      └─ T-006 미완료 런타임 계약
                           └─ T-007 독립 검증
                                └─ T-008 기록/종료
```

순차 의존을 강제한다. 특히 BR0 이전에는 비용이 큰 피평가 호출을 시작하지 않고, T-007 green 이전에는 완료 기록을 만들지 않는다.

- 임계 경로: T-001 → T-002 → T-003 → T-004 → T-005 → T-006 → T-007 → T-008
- 병렬 가능 구간: 작업 간 병렬 실행은 없다. T-004/T-005 내부의 독립 음성 사례는 준비만 병렬화할 수 있으나, 공유 baseline과 호출 예산을 보호하기 위해 판정·기록은 순서대로 수행한다.

## 6. 검증 계획

검증은 세 단계로 진행한다. 각 작업 수행자가 해당 절의 명령으로 1차 확인하고, T-007의 독립 검증자가 정본에서 기대값을 다시 추출해 재검증하며, 마지막에 프로젝트 표준 명령 `python3 scripts/validate_skill_links.py`를 포함한 §6.5 통합 게이트를 한 번 실행한다.

### 6.1 정적 검증

- Python/Node 구문 검사
- 표준 라이브러리 외 새 의존성 없음
- 플러그인 링크와 정확한 파일 집합 검사
- 금지 문자열/기능 검사: arbitrary script, unrestricted URL, secret/env forwarding, plugin-local browser server
- JSON 산출물 스키마·필수 필드 검사

### 6.2 단위·black-box 검증

- 요청/스냅샷/캡처/판정 상태기계의 양성·음성 경로
- realpath·symlink·output escape
- 네트워크 allowlist
- action/timeout/viewport/count 상한
- hash mismatch와 stale 전이
- Audit 불변성과 Repair 재캡처

### 6.3 종단간 검증

- BR0: 이미지 직접 열람 능력
- BR1: 실제 InnerRender와 same-call 판정, bridge 미사용
- BR2: inner blocker → outer capture → same skill·mode·installed-plugin hash의 Codex adjudication
- BR3~BR6: stale/incomplete/blocked/unverified 실패 경로
- BR7: Audit/GeneralAudit 비변경 캡처·판정
- BR8: before → Repair → stale → after recapture → adjudication
- BR9~BR10: 임의 script, 외부 network, credential, root escape 거부
- U5/U6/U7/U9와 GeneralAudit/Repair 모드 계약
- lifecycle 4종과 invalid status 2종

### 6.4 증거 등급

| 등급 | 의미 | 최종 green 사용 |
|---|---|---|
| E2E | 실제 producer·capture·adjudicator transcript와 해시가 모두 있음 | 가능 |
| Black-box | 실제 하네스 명령과 파일 시스템 결과가 있음 | 해당 보안/실패 계약에 가능 |
| Unit | 상태기계 또는 순수 함수 검사 | 보조 증거만 가능 |
| Reused | 선행 증거가 현재 해시·계약에 적격 | 비렌더 계약에만 가능 |

### 6.5 전체 게이트

```bash
python3 -m unittest discover -s scripts/ui_workflow_eval/tests -p 'test_*.py'
python3 scripts/ui_workflow_eval/bridge.py self-test
python3 -m py_compile scripts/ui_workflow_eval/bridge.py scripts/ui_workflow_eval/tests/test_bridge.py
node --check scripts/ui_workflow_eval/capture.mjs
python3 scripts/validate_skill_links.py
git diff --check
```

명령 결과뿐 아니라 `$EVIDENCE_ROOT/case-index.json`과 독립 검증 기록을 함께 통과해야 한다.

## 7. 롤백 전략

- 실행 시작 전 현재 정본/상태/플랜을 스냅샷 커밋으로 보존한다.
- 구현은 T-002, 실행 증거/기록은 T-003~T-006, 종료 기록은 T-008의 의미 단위 커밋으로 분리한다.
- 실패한 작업은 해당 커밋만 `git revert <sha>`로 되돌린다. `git reset --hard`, 광범위 checkout, 사용자 변경 삭제는 금지한다.
- `codex-plugins/design-ui/**` 전체(`skills/review-ui/**`와 `.claude-plugin/**` 포함)는 보호 경로다. 예상치 못한 변경이 생기면 즉시 중단하고 diff를 보존한다.
- 임시 fixture는 새 evidence root 내부에서만 만들며, 정리 시 그 정확한 경로만 대상으로 삼는다.
- 선행 `/tmp/ui-workflow-eval.d1kdjz`는 읽기 전용으로 취급하고 이동·수정·삭제하지 않는다.
- runtime 인증/설정 변경이 필요할 경우 기존 값을 먼저 백업하고 사례 종료 직후 복원한다. 비밀 값은 로그나 커밋에 기록하지 않는다.
- 설계 결함이 발견되면 구현을 임의로 고치거나 자동 revert하지 않는다. 증거와 blocker를 보존하고 사용자 확인을 받아 `/make-design docs/codex-ui-workflow-skills.md §8.2`로 승격한다.

## 8. 위험 및 미결 사항

### 8.1 위험

| 위험 | 영향 | 대응 |
|---|---|---|
| 내부 Codex가 이미지 파일을 실제로 열 수 없음 | adjudication 계약을 증명할 수 없음 | BR0에서 조기 중단하고 환경 blocker로 보고 |
| 기존 Playwright API를 탐지할 수 없음 | click/fill/press 포함 adapter 실행 불가 | T-001에서 설치 없이 탐지하고, 없으면 T-002 전에 중단 |
| 실제 InnerRender가 가능한 격리 Codex profile이 없음 | BR1 최소 회귀 사례 미충족 | T-004에서 bridge를 쓰지 않는 실제 same-call probe를 수행하고 실패 시 플랜을 완료하지 않음 |
| 선행 `/tmp` 증거가 소실 또는 변조됨 | 비렌더 사례 재사용 불가 | 적격 사례만 호출 예산 내 재실행; 상한 초과 전 재계획 |
| 긴 피평가 호출이 반복됨 | 시간·호출 예산 초과 | BR0 선행, 사례 중복 제거, 기본 24/전체 36 상한 적용 |
| adjudicator가 이미지 대신 텍스트 단서로 추론 | 거짓 시각 판정 | BR0 정답 은닉, image-open 이벤트/숨은 값 정답 강제 |
| outer runner가 판정 로직을 품음 | 독립 판정 계약 위반 | capture schema에는 시각 verdict 필드 금지, 독립 검증 |
| Audit가 fixture/제품을 수정함 | 모드 계약 위반 | 전후 hash 불일치 즉시 실패 |
| Repair 뒤 이전 캡처가 재사용됨 | 수정 결과 오판 | source hash 변경 즉시 stale, after 재캡처 없이는 finalize 금지 |
| 환경 경로를 코드에 고정함 | 다른 워크스페이스에서 재현 불가 | capability record를 통한 런타임 주입만 허용 |

### 8.2 추정

- [추정] 현재 워크스페이스 또는 오프라인 npx 캐시에서 Playwright JavaScript API를 찾을 수 있다. T-001 capability preflight로 확정한다.
- [추정] 외부 network와 credential을 노출하지 않는 격리 Codex profile에서 실제 InnerRender를 실행할 수 있다. T-004 BR1에서 확정하며 실패하면 완료하지 않는다.
- [추정] 내부 Codex adjudicator가 로컬 PNG를 직접 여는 도구를 사용할 수 있다. BR0으로 확정하며 실패 시 후속 작업을 진행하지 않는다.
- [추정] 선행 증거 중 비렌더 사례는 플러그인 해시가 유지되어 일부 재사용 가능하다. T-001 해시 대조 전에는 재사용으로 간주하지 않는다.

### 8.3 미결 결정

사용자 결정을 요구하는 미결 항목은 없다. 위 추정은 모두 실행 초기에 기계적으로 측정하며, 실패 시 범위를 임의 확장하거나 의존성을 설치하지 않고 blocker로 반환한다.
