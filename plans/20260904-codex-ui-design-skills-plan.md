# 구현 플랜 — Codex `design-ui` 플러그인

- 상태: **완료 (2026-09-04)**
- 실행 리포트: `plans/20260904-codex-ui-design-skills-execute-report.md`
- 작성일: 2026-09-04
- 정본 설계: `docs/codex-ui-design-skills.md`
- 구현 범위: Codex 전용 `design-ui` 플러그인과 그 안의 `design-ui`·`review-ui`
  스킬, 지원 문서·템플릿, Codex 카탈로그와 저장소 안내

## 1. 개요

### 목표

하나의 설치 가능한 Codex 플러그인 안에 UI 제작용 `design-ui`와 시각 검토용
`review-ui`를 구현하고, 정본 설계 §9의 구조·트리거·행동 불변 조건을 재현 가능한
검사와 독립 검증으로 입증한다.

### 확정된 기술 형태

- Markdown `SKILL.md` + YAML frontmatter
- Markdown reference·asset 파일
- `.codex-plugin/plugin.json`과 `.agents/plugins/marketplace.json`
- instruction-only: 신규 스크립트, MCP 서버, `agents/openai.yaml` 없음
- 현재 Codex CLI: `codex-cli 0.149.1`
- 현재 저장소 통합 게이트: `python3 scripts/validate_skill_links.py`

### 제약 조건

- `codex-plugins/`와 `.agents/plugins/marketplace.json`만 배포 대상으로 삼는다.
- `.claude-plugin/marketplace.json`과 `plugins/**`에는 대응판이나 등록을 만들지 않는다.
- 플러그인 이름은 `design-ui`, 스킬 이름은 `design-ui`와 `review-ui`다.
- screenshot·URL·Figma는 `design-ui` 입력 유형이며 별도 스킬로 분리하지 않는다.
- 실제 렌더링 근거가 없을 때 두 스킬 모두 Visual QA 통과를 선언하지 않는다.
- `review-ui`는 기본 Audit에서 제품 소스와 디자인 정본을 변경하지 않는다.
- 구현 중 정본과 어긋나는 요구를 발견하면 코드를 임의로 맞추지 않고 중단해
  `$make-design docs/codex-ui-design-skills.md §<관련 절>`로 되돌린다.

### 현재 상태

- 정본 설계는 확정됐고 `## 11. 미결`은 “없음”이다.
- 구현 플러그인과 카탈로그 항목은 아직 없다.
- 작업 원장과 별도 플랜 규약은 없다.
- 착수 시점 HEAD는 `df13fbd`이며, 정본 설계 문서는 아직 추적되지 않은 작업 관련
  파일이다. 실행자는 다른 사용자 변경과 섞이지 않도록 착수 직전 상태를 다시 기록한다.

### 성공 기준

아래 조건을 모두 만족해야 한다.

1. 정본 §3.2의 파일 구조가 모두 존재하고 플러그인 manifest가 두 스킬을 발견할 수 있다.
2. 정본 §4·§5의 입력·상태 전이·성공 출력·실패 경로가 각 스킬과 지원 파일에 대응된다.
3. 정본 §9.1 구조 검사와 기존 링크 게이트가 모두 통과한다.
4. 정본 §9.2의 다섯 활성화 유형과 최소 사례가 Codex 임시 환경에서 평가되고 결과가
   실행 리포트에 남는다.
5. 정본 §9.3의 여섯 행동 불변 조건이 정적 대조 또는 런타임 사례로 모두 판정된다.
6. Claude Code 트리에 변경이 없고, `git diff --check`가 통과한다.
7. 독립 검증자가 정본만 기대값으로 사용해 **등급과 무관하게 계약 위반 0건**을
   판정한다. 남길 수 있는 것은 계약 밖의 비차단 개선 제안뿐이다.

## 2. 작업 목록

| ID | 우선순위 | 작업명 | 선행 | 산출물 |
|---|---|---|---|---|
| T-001 | P0 | 플러그인 설치 골격을 생성한다 | 없음 | manifest, README, LICENSE |
| T-002 | P1 | `design-ui` 제작 워크플로우를 구현한다 | T-001 | SKILL, 디자인 정본 reference·template |
| T-003 | P1 | `review-ui` 검토 워크플로우를 구현한다 | T-001 | SKILL, Visual QA reference·report template |
| T-004 | P1 | Codex 카탈로그와 루트 안내를 통합한다 | T-002, T-003 | marketplace entry, README 갱신 |
| T-005 | P1 | 구조·계약 정적 검사를 수행한다 | T-002, T-003, T-004 | 검사 결과와 계약 대조표 |
| T-006 | P2 | Codex 활성화·실패 경로를 평가한다 | T-005 | 대표 요청별 런타임 평가 기록 |
| T-007 | P1 | 독립 재검증과 통합 게이트를 통과한다 | T-005, T-006 | 독립 판정, 최종 게이트 결과 |
| T-008 | P3 | 기록을 닫고 원자 커밋을 준비한다 | T-007 | 완료된 실행 리포트, 커밋 준비 상태 |

## 3. 역할 분담

프로젝트에 커스텀 에이전트 로스터가 없으므로 역할 이름을 새로 만들지 않는다.

| 구간 | 수행자 | 검증자 | 분리 원칙 |
|---|---|---|---|
| T-001~T-004 | 현재 실행 에이전트 | 배정하지 않음 | 정본에 따라 파일을 작성 |
| T-005 | 현재 실행 에이전트 | 배정하지 않음 | 기계적·정적 검사를 먼저 수행 |
| T-006 | 현재 실행 에이전트 | 배정하지 않음 | 임시 Codex 실행 결과를 그대로 기록 |
| T-007 | 읽기 전용 독립 서브에이전트 | 독립 서브에이전트 자신 | 정본, 모든 구현·통합 경로, 실행 리포트만 전달하고 작성 의도는 전달하지 않음 |
| T-008 | 현재 실행 에이전트 | T-007 판정 재사용 | 독립 판정이 green일 때만 완료 처리 |

독립 검증자는 구현을 수정하지 않는다. 발견은 경로·정본 절·재현 명령과 함께 반환하고,
수행자가 반영한 뒤 같은 검증자 또는 새 읽기 전용 검증자가 재판정한다.

## 4. 상세 작업 명세

### T-001 — 플러그인 설치 골격을 생성한다

내용:

- `codex-plugins/design-ui/.codex-plugin/plugin.json`을 기존 Codex manifest 관례에
  맞춰 작성한다. `version: 1.0.0`, MIT, homepage·repository, Developer Tools
  interface metadata는 새 제품 계약이 아니라 이 저장소의 모든 기존 Codex manifest가
  쓰는 패키징 관례를 그대로 적용하는 구현 세부다. 관례가 실제 파일과 다르면 임의로
  결정하지 않고 중단한다.
- `name: design-ui`, `skills: ./skills/`와 위 저장소 관례 metadata를 넣는다.
- `README.md`에는 Codex-only임을 명시하고 설치법, 두 스킬의 역할, 공통 흐름,
  Visual QA 한계, 라이선스를 설명한다.
- 루트 `LICENSE`와 같은 MIT 내용을 플러그인 `LICENSE`에 둔다.
- 아직 스크립트·MCP·`agents/openai.yaml`은 만들지 않는다.

산출물:

- `codex-plugins/design-ui/.codex-plugin/plugin.json`
- `codex-plugins/design-ui/README.md`
- `codex-plugins/design-ui/LICENSE`

검증 조건:

- [ ] `python3 -m json.tool codex-plugins/design-ui/.codex-plugin/plugin.json >/dev/null`
- [ ] `test "$(python3 -c 'import json; print(json.load(open("codex-plugins/design-ui/.codex-plugin/plugin.json"))["name"])')" = design-ui`
- [ ] `test "$(python3 -c 'import json; print(json.load(open("codex-plugins/design-ui/.codex-plugin/plugin.json"))["skills"])')" = ./skills/`
- [ ] `test ! -e codex-plugins/design-ui/agents/openai.yaml`
- [ ] `test ! -d codex-plugins/design-ui/scripts`

커밋 경계: T-001 산출물만 하나의 원자 커밋 후보로 묶는다.

### T-002 — `design-ui` 제작 워크플로우를 구현한다

내용:

- `SKILL.md` frontmatter description 앞부분에 “새 UI 제작·재설계·참고물의 코드
  번역” 트리거를 두고, review-only와 백엔드 설계 비트리거를 명시한다.
- 본문에는 프로젝트 선독, 입력 정규화, 정본 우선순위, `DESIGN.md` 생성·갱신
  조건, 재사용 우선 구현, 자동 검사, 실제 렌더링, maker Visual QA, 수정 루프,
  완료·blocked 보고를 순서대로 둔다.
- 접근 불가 URL/Figma와 보이지 않는 화면 상태를 추측하지 않는 규칙을 넣는다.
- `references/design-authority.md`에는 정본 우선순위와 충돌 처리, 네 가지
  `DESIGN.md` 상황별 동작, 문서 승격 기준을 상세화한다.
- `assets/DESIGN.template.md`에는 정본 §3.4의 여덟 최소 절을 복사 가능한 골격으로
  제공한다.
- reference와 asset은 `SKILL.md`에서 “언제 읽고 언제 복사하는지”와 함께 링크한다.

산출물:

- `codex-plugins/design-ui/skills/design-ui/SKILL.md`
- `codex-plugins/design-ui/skills/design-ui/references/design-authority.md`
- `codex-plugins/design-ui/skills/design-ui/assets/DESIGN.template.md`

검증 조건:

- [ ] frontmatter `name`이 정확히 `design-ui`다.
- [ ] `DesignUiRequest`의 네 intent와 다섯 Reference 변형이 본문 또는 reference에
      모두 대응된다.
- [ ] `target`의 네 변형, `requirements`, `constraints`, “참고물 부재만으로 중단 금지”가
      모두 표현된다.
- [ ] 정본 §4.3의 `Intake`, `Context ready`, `Design ready`, `Implementing`,
      `Renderable`, `Self-review`, `Done` 정상 흐름과 `Needs input`, `Reference blocked`,
      `Design conflict`, `Build blocked`, `Render blocked` 다섯 실패 상태가 누락 없이
      표현된다.
- [ ] `render-unverified` 종료가 명시되고 실제 렌더링 없는 합격 경로가 없다.
- [ ] 기존 디자인 정본과 공용 컴포넌트 확인이 구현보다 앞선다.
- [ ] blocker 보고에 원인, 완료 지점, 사용자에게 필요한 입력, 미검증 범위가 포함된다.
- [ ] 새 의존성은 현재 스택으로 충족할 수 없을 때만 허용된다.
- [ ] 정본 §4.5의 다섯 완료 출력과 §6의 viewport·상태·검사·참고물 비교 규칙이
      maker check에 연결된다.
- [ ] 능력 탐색·대체 경로, 프레임워크 비종속, `interview`·`make-design`·`verify`·
      `imagegen`과의 경계가 본문에 있다.
- [ ] `python3 scripts/validate_skill_links.py`

커밋 경계: T-002의 세 파일만 하나의 원자 커밋 후보로 묶는다.

### T-003 — `review-ui` 검토 워크플로우를 구현한다

내용:

- `SKILL.md` frontmatter description 앞부분에 “기존 UI의 브라우저 기반 시각
  검토” 트리거를 두고 새 UI 제작 비트리거를 명시한다.
- 입력을 `Audit | Repair`의 tagged union으로 쓰고, 명시적 fix 요청이 없으면
  반드시 Audit을 선택하게 한다.
- before 캡처 → 발견 고정 → Audit 종료 또는 Repair → 동일 행렬 재검증 → after
  캡처의 상태 전이를 구현한다.
- 디자인 결정이 필요한 발견은 `design-decision-required`로 남겨 review 단계가
  새 디자인을 정하지 못하게 한다.
- `references/visual-qa-rubric.md`에는 세 기본 viewport, 관련 UI 상태, 검사 범주,
  네 severity, 참고 이미지 비교 규칙과 접근성 감사 범위의 한계를 둔다.
- `assets/REVIEW-UI.template.md`에는 대상·모드·HEAD·정본·검토 행렬·`UiFinding`·
  before/after·미검토 범위를 갖춘 리포트 골격을 둔다.
- 실제 렌더링 실패 시 리포트를 `blocked`로 닫는 경로를 명시한다.

산출물:

- `codex-plugins/design-ui/skills/review-ui/SKILL.md`
- `codex-plugins/design-ui/skills/review-ui/references/visual-qa-rubric.md`
- `codex-plugins/design-ui/skills/review-ui/assets/REVIEW-UI.template.md`

검증 조건:

- [ ] frontmatter `name`이 정확히 `review-ui`다.
- [ ] “검토해줘”가 Audit, “검토하고 고쳐줘”가 Repair로 매핑된다.
- [ ] Audit 경로는 제품 소스·`DESIGN.md` 변경을 금지한다.
- [ ] Repair 경로는 before 발견 고정과 같은 viewport·state의 after 재검증을 요구한다.
- [ ] `UiFinding`의 아홉 필드, 네 severity, 네 status가 모두 템플릿과 일치한다.
- [ ] 렌더링 불가가 빈 green 리포트가 아닌 `blocked`로 끝난다.
- [ ] 정본 §3.3의 일곱 단계 우선순위와 충돌 노출 규칙을 소비한다.
- [ ] 디자인 정본 부재 시 명백한 결함과 heuristic을 분리하고 취향을 계약 위반으로
      표현하지 않는다.
- [ ] 기본 리포트 경로와 정본 §5.4의 여섯 리포트 필드가 템플릿에 모두 대응된다.
- [ ] 제작+maker check는 `design-ui`, 독립 2차 판정은 `review-ui`, 새 UI 제작은
      비트리거라는 경계가 본문과 평가 사례에 있다.
- [ ] `python3 scripts/validate_skill_links.py`

커밋 경계: T-003의 세 파일만 하나의 원자 커밋 후보로 묶는다.

### T-004 — Codex 카탈로그와 루트 안내를 통합한다

내용:

- `.agents/plugins/marketplace.json`에 `design-ui` 항목을 정확히 한 번 추가하고
  source를 `./codex-plugins/design-ui`로 지정한다.
- 정책·category는 기존 Codex 플러그인 관례를 따른다.
- 루트 `README.md`가 런타임별 전용 스킬을 표현할 수 있도록 첫 설명과 포함 스킬 표를
  현행화한다.
- 표에는 `design-ui` 플러그인 아래 두 스킬이 있음을 표시하고 Claude Code `–`,
  Codex CLI `✅`로 표시한다.
- Codex 설치 예시에 `codex plugin add design-ui@jsj9346-skills`를 추가한다.
- `.claude-plugin/marketplace.json`과 `plugins/**`는 건드리지 않는다.

산출물:

- `.agents/plugins/marketplace.json`
- `README.md`

검증 조건:

- [ ] `python3 -m json.tool .agents/plugins/marketplace.json >/dev/null`
- [ ] 아래 명령이 항목 수와 source를 직접 검증하고 불일치 시 nonzero로 끝난다.

```bash
python3 - <<'PY'
import json
data = json.load(open('.agents/plugins/marketplace.json'))
matches = [p for p in data['plugins'] if p['name'] == 'design-ui']
assert len(matches) == 1, matches
assert matches[0]['source'] == {
    'source': 'local', 'path': './codex-plugins/design-ui'
}, matches[0]
PY
```

- [ ] 아래 명령이 README의 설치 예시·두 역할·Codex-only 지원 표시를 직접 검증한다.

```bash
python3 - <<'PY'
from pathlib import Path
t = Path('README.md').read_text()
assert 'codex plugin add design-ui@jsj9346-skills' in t
row = next(
    line for line in t.splitlines()
    if 'codex-plugins/design-ui' in line and line.startswith('|')
)
cells = [cell.strip() for cell in row.strip('|').split('|')]
assert 'design-ui' in cells[0] and 'review-ui' in cells[0], cells
assert '제작' in cells[1] and '검토' in cells[1], cells
assert cells[-2:] == ['–', '✅'], cells
PY
```

- [ ] 착수 시 생성한 protected-tree snapshot과 현재 `.claude-plugin/`, `plugins/`의
      경로·type·mode·symlink target·일반 파일 SHA-256을 비교해 동일하다.

커밋 경계: 카탈로그와 루트 README만 하나의 원자 커밋 후보로 묶는다.

### T-005 — 구조·계약 정적 검사를 수행한다

내용:

- 정본 §3.2의 9개 파일 목록과 실제 트리를 집합 비교한다.
- 모든 plugin·marketplace JSON을 파싱한다.
- 두 `SKILL.md`의 frontmatter key가 `name`·`description`뿐인지, 두 값이 존재하는지,
  name과 디렉터리명이 같은지 대조한다.
- `design-authority.md`, `visual-qa-rubric.md`, 두 asset 링크의 실재를 검사한다.
- 정본 §9.3 여섯 불변 조건을 행별로 `적합/위반/수단 부재` 판정해 실행 리포트에
  기록한다.
- `ui-design`, `ui-review`, `UiDesignRequest`, `UiReviewRequest` 같은 폐기된 이름이
  신규 플러그인과 README에 남지 않았는지 검사한다.
- 설계가 배제한 scripts·MCP·Claude 대응판이 생기지 않았는지 확인한다.

산출물:

- `plans/20260904-codex-ui-design-skills-execute-report.md` 안의 정적 검사 결과와
  계약 대조표

검증 조건:

- [ ] 아래 명령이 정본 §3.2의 9개 파일과 실제 파일 집합을 직접 비교한다.

```bash
python3 - <<'PY'
from pathlib import Path
root = Path('codex-plugins/design-ui')
actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
expected = {
    '.codex-plugin/plugin.json',
    'README.md',
    'LICENSE',
    'skills/design-ui/SKILL.md',
    'skills/design-ui/references/design-authority.md',
    'skills/design-ui/assets/DESIGN.template.md',
    'skills/review-ui/SKILL.md',
    'skills/review-ui/references/visual-qa-rubric.md',
    'skills/review-ui/assets/REVIEW-UI.template.md',
}
assert actual == expected, {'missing': expected - actual, 'extra': actual - expected}
PY
```

- [ ] 아래 명령이 frontmatter 계약을 직접 검증한다.

```bash
python3 - <<'PY'
from pathlib import Path
for name in ('design-ui', 'review-ui'):
    path = Path('codex-plugins/design-ui/skills') / name / 'SKILL.md'
    text = path.read_text()
    assert text.startswith('---\n')
    frontmatter = text.split('---\n', 2)[1]
    lines = frontmatter.splitlines()
    top = {}
    for index, line in enumerate(lines):
        if line and not line[0].isspace() and ':' in line:
            key, value = line.split(':', 1)
            top[key.strip()] = (value.strip(), index)
    assert set(top) == {'name', 'description'}, (name, top)
    assert top['name'][0] == name, (name, top['name'][0])
    description, description_line = top['description']
    if description in {'', '>', '>-', '|', '|-'}:
        continuation = [
            line.strip() for line in lines[description_line + 1:]
            if line[:1].isspace() and line.strip()
        ]
        assert continuation, (name, 'empty description')
    else:
        assert description, (name, 'empty description')
PY
```

- [ ] `python3 scripts/validate_skill_links.py`
- [ ] `find codex-plugins -path '*/.codex-plugin/plugin.json' -print0 | xargs -0 -n1 python3 -m json.tool >/dev/null`
- [ ] `python3 -m json.tool .agents/plugins/marketplace.json >/dev/null`
- [ ] `! rg -n 'ui-design|ui-review|UiDesignRequest|UiReviewRequest' codex-plugins/design-ui README.md`
- [ ] `test ! -d plugins/design-ui`
- [ ] 착수 protected-tree snapshot과 현재 `.claude-plugin/`, `plugins/`의 경로·type·
      mode·symlink target·일반 파일 SHA-256이 동일하다.
- [ ] 아래 검사가 신규·추적 파일의 trailing whitespace와 탭 들여쓰기를 검사한다.

```bash
python3 - <<'PY'
from pathlib import Path
files = [
    Path('README.md'),
    Path('.agents/plugins/marketplace.json'),
    Path('docs/codex-ui-design-skills.md'),
    Path('plans/20260904-codex-ui-design-skills-plan.md'),
]
report = Path('plans/20260904-codex-ui-design-skills-execute-report.md')
if report.exists():
    files.append(report)
files += [p for p in Path('codex-plugins/design-ui').rglob('*') if p.is_file()]
bad = []
for path in files:
    for number, line in enumerate(path.read_text().splitlines(), 1):
        if line != line.rstrip() or line.startswith('\t'):
            bad.append(f'{path}:{number}')
assert not bad, bad
PY
```
- [ ] 정본 §9.3의 모든 행이 판정됐고 `미대조`가 없다.

### T-006 — Codex 활성화·실패 경로를 평가한다

내용:

- 저장소 밖 임시 baseline fixture를 만들고 각 사례는 그 복사본에서 독립 실행한다.
  fixture에는 최소 `AGENTS.md`, 기존 디자인 체계를 가진 `DESIGN.md`, responsive
  `index.html`을 `apply_patch`로 만든다. `index.html`에는 default/empty/error 상태와
  desktop/mobile에서 관측 가능한 간격·overflow 결함 하나를 의도적으로 포함한다.
- Playwright CLI로 baseline을 실제 렌더링해 `reference.png`를 만든다. 이 파일을
  screenshot reference 사례의 `-i` 입력으로 사용한다.
- 각 case 디렉터리의 `.agents/skills/`에 두 스킬을 symlink한다. 사용자 marketplace나
  plugin 설정은 변경하지 않는다.
- 모든 `codex exec`는 `--ephemeral --ignore-user-config --json`을 사용하고 결과를 case
  디렉터리에 저장한다. 프롬프트의 `$design-ui`·`$review-ui`는 작은따옴표로 감싸 셸
  확장을 막는다.
- 아래 setup 명령은 한 셸 세션에서 그대로 실행한다.

```bash
ui_eval_root=$(mktemp -d)
mkdir -p "$ui_eval_root/baseline/.agents/skills"
mkdir -p "$ui_eval_root/evidence"
printf '%s\n' "$ui_eval_root"
printf '%s\n' "$ui_eval_root" >"$ui_eval_root/evidence/eval-root-path"
ln -s /home/13ruce/agent-skills/codex-plugins/design-ui/skills/design-ui "$ui_eval_root/baseline/.agents/skills/design-ui"
ln -s /home/13ruce/agent-skills/codex-plugins/design-ui/skills/review-ui "$ui_eval_root/baseline/.agents/skills/review-ui"
git -C "$ui_eval_root/baseline" init -q
```

- 위 setup 뒤 `<UI_EVAL_ROOT>`를 방금 출력된 `ui_eval_root`의 정확한 절대 경로로 바꿔
  다음 patch를 `apply_patch`로 적용한다. fixture 상태 URL은
  `index.html?state=default`, `?state=empty`, `?state=error`다. mobile 기준은 720px
  이하이고, `.stats`의 `min-width: 820px`가 의도적인 overflow 결함이다.

```diff
*** Begin Patch
*** Add File: <UI_EVAL_ROOT>/baseline/AGENTS.md
+This is a disposable UI evaluation fixture.
+Use the checked-in DESIGN.md as the visual authority.
+Do not access network resources or write outside this fixture.
*** Add File: <UI_EVAL_ROOT>/baseline/DESIGN.md
+# Fixture Design
+
+## Scope and principles
+A restrained analytics dashboard with clear hierarchy and dense reusable cards.
+
+## Foundations
+- Background: `#f8fafc`
+- Surface: `#ffffff`
+- Text: `#0f172a`
+- Muted: `#64748b`
+- Accent: `#2563eb`
+- Spacing scale: `4, 8, 16, 24, 32`
+- Radius: `12px`
+- Shadow: `0 8px 24px rgb(15 23 42 / 0.08)`
+
+## Layout and breakpoints
+- Content max-width: `1120px`
+- Mobile breakpoint: `720px`
+- Cards must reflow without horizontal page overflow.
+
+## Components and reuse rules
+- Metric cards use the shared `.card` treatment.
+- Do not introduce one-off colors or radius values.
+
+## Interaction and UI states
+- Support `default`, `empty`, and `error` states.
+- Interactive elements require a visible focus state.
+
+## Responsive behavior
+- Desktop uses a three-column metric grid.
+- Mobile uses one column and must not scroll horizontally.
+
+## Accessibility constraints
+- Preserve semantic headings and readable contrast.
+
+## Intentional exceptions and unresolved assumptions
+None.
*** Add File: <UI_EVAL_ROOT>/baseline/index.html
+<!doctype html>
+<html lang="en">
+<head>
+  <meta charset="utf-8">
+  <meta name="viewport" content="width=device-width, initial-scale=1">
+  <title>Analytics fixture</title>
+  <style>
+    :root { color: #0f172a; background: #f8fafc; font-family: system-ui, sans-serif; }
+    * { box-sizing: border-box; }
+    body { margin: 0; }
+    main { max-width: 1120px; margin: 0 auto; padding: 32px; }
+    header { display: flex; align-items: end; justify-content: space-between; gap: 16px; }
+    h1, p { margin: 0; }
+    .muted { color: #64748b; }
+    .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; min-width: 820px; margin-top: 24px; }
+    .card { border: 1px solid #e2e8f0; border-radius: 12px; background: #fff; padding: 23px; box-shadow: 0 8px 24px rgb(15 23 42 / 0.08); }
+    .value { margin-top: 8px; font-size: 28px; font-weight: 700; }
+    .state { margin-top: 24px; border-radius: 12px; background: #fff; padding: 24px; }
+    .state-error { color: #b91c1c; }
+    a:focus-visible { outline: 3px solid #2563eb; outline-offset: 3px; }
+    [hidden] { display: none; }
+    @media (max-width: 720px) {
+      main { padding: 16px; }
+      header { align-items: start; flex-direction: column; }
+      .stats { grid-template-columns: 1fr; }
+    }
+  </style>
+</head>
+<body>
+  <main>
+    <header>
+      <div><p class="muted">Overview</p><h1>Analytics</h1></div>
+      <a href="#states">Skip to state</a>
+    </header>
+    <section class="stats" aria-label="Metrics">
+      <article class="card"><p class="muted">Revenue</p><p class="value">$24,800</p></article>
+      <article class="card"><p class="muted">Orders</p><p class="value">1,284</p></article>
+      <article class="card"><p class="muted">Conversion</p><p class="value">4.8%</p></article>
+    </section>
+    <section id="states" class="state state-default"><h2>Recent activity</h2><p>12 new orders today.</p></section>
+    <section class="state state-empty" hidden><h2>No activity</h2><p>New events will appear here.</p></section>
+    <section class="state state-error" hidden><h2>Could not load activity</h2><p>Try again later.</p></section>
+  </main>
+  <script>
+    const state = new URLSearchParams(location.search).get('state') || 'default';
+    document.querySelectorAll('[class*="state-"]').forEach((node) => {
+      node.hidden = !node.classList.contains(`state-${state}`);
+    });
+  </script>
+</body>
+</html>
*** End Patch
```

- 다음 명령으로 baseline 파일을 초기 commit해 기준 HEAD를 만들고, 세 상태가 선택 가능한지
  정적으로 확인한 뒤 실제 screenshot을 생성한다.
  Playwright stdout·stderr·종료 코드를 보존한다. 실패하면 screenshot 사례를 통과 처리하지
  않되 나머지 사례는 계속 실행한다.

```bash
test -f "$ui_eval_root/baseline/AGENTS.md"
test -f "$ui_eval_root/baseline/DESIGN.md"
test -f "$ui_eval_root/baseline/index.html"
rg -n 'state-default|state-empty|state-error|min-width: 820px|max-width: 720px' "$ui_eval_root/baseline/index.html"
git -C "$ui_eval_root/baseline" add AGENTS.md DESIGN.md index.html
git -C "$ui_eval_root/baseline" -c user.name=Codex-UI-Eval -c user.email=codex-ui-eval@example.invalid commit -q -m 'test: create UI evaluation baseline'
git -C "$ui_eval_root/baseline" rev-parse HEAD >"$ui_eval_root/evidence/baseline-head"
mkdir -p "$ui_eval_root/evidence/playwright"
if npx playwright screenshot --browser chromium --viewport-size "390, 844" --full-page "file://$ui_eval_root/baseline/index.html?state=default" "$ui_eval_root/reference.png" >"$ui_eval_root/evidence/playwright/stdout.log" 2>"$ui_eval_root/evidence/playwright/stderr.log"; then
  playwright_status=0
else
  playwright_status=$?
fi
printf '%s\n' "$playwright_status" >"$ui_eval_root/evidence/playwright/exit-code"
if test "$playwright_status" -eq 0 && test -s "$ui_eval_root/reference.png"; then
  printf '%s\n' ready >"$ui_eval_root/evidence/playwright/status"
else
  printf '%s\n' unavailable >"$ui_eval_root/evidence/playwright/status"
fi
```

- 각 사례는 `cp -a "$ui_eval_root/baseline" "$ui_eval_root/<CASE>"`로 격리한 뒤 아래
  형식으로 실행한다.

```bash
mkdir -p "$ui_eval_root/evidence/<CASE>"
codex -C "$ui_eval_root/<CASE>" -s workspace-write -a never exec --ephemeral --ignore-user-config --skip-git-repo-check --json '<PROMPT>' >"$ui_eval_root/evidence/<CASE>/stdout.jsonl" 2>"$ui_eval_root/evidence/<CASE>/stderr.log"
```

- baseline과 empty 사례를 분리하고 전체 prompt를 실행하는 복붙 가능한 명령은 다음과
  같다. 이 블록도 setup과 같은 셸 세션에서 실행한다.

```bash
for case_id in D3 D4 D5 D6 R1 R2 R6; do
  cp -a "$ui_eval_root/baseline" "$ui_eval_root/$case_id"
done
for case_id in D1 R3 R4 R5; do
  mkdir -p "$ui_eval_root/$case_id/.agents/skills"
  ln -s /home/13ruce/agent-skills/codex-plugins/design-ui/skills/design-ui "$ui_eval_root/$case_id/.agents/skills/design-ui"
  ln -s /home/13ruce/agent-skills/codex-plugins/design-ui/skills/review-ui "$ui_eval_root/$case_id/.agents/skills/review-ui"
  git -C "$ui_eval_root/$case_id" init -q
done

run_ui_case() {
  case_id="$1"
  prompt="$2"
  mkdir -p "$ui_eval_root/evidence/$case_id"
  if codex -C "$ui_eval_root/$case_id" -s workspace-write -a never exec --ephemeral --ignore-user-config --skip-git-repo-check --json "$prompt" >"$ui_eval_root/evidence/$case_id/stdout.jsonl" 2>"$ui_eval_root/evidence/$case_id/stderr.log"; then
    case_status=0
  else
    case_status=$?
  fi
  printf '%s\n' "$case_status" >"$ui_eval_root/evidence/$case_id/exit-code"
}

run_ui_case D1 '$design-ui 새 대시보드 UI를 index.html로 만들어줘'
run_ui_case D3 'UI 좀 바꿔줘'
run_ui_case D4 'API와 DB 스키마를 설계해줘'
run_ui_case D5 'https://figma.example.invalid/file/missing 의 화면을 그대로 추측해서 구현해줘'
sha256sum "$ui_eval_root/D6/DESIGN.md" >"$ui_eval_root/D6.design.sha256"
run_ui_case D6 '기존 디자인 시스템을 유지해 새 통계 카드를 추가해줘'
sha256sum -c "$ui_eval_root/D6.design.sha256"

sha256sum "$ui_eval_root/R1/index.html" "$ui_eval_root/R1/DESIGN.md" >"$ui_eval_root/R1.sources.sha256"
run_ui_case R1 '$review-ui index.html을 Visual QA 해줘'
sha256sum -c "$ui_eval_root/R1.sources.sha256"

sha256sum "$ui_eval_root/R2/index.html" "$ui_eval_root/R2/DESIGN.md" >"$ui_eval_root/R2.sources.sha256"
run_ui_case R2 '이 화면의 반응형 깨짐과 시각적 불일치를 찾아 보고해줘'
sha256sum -c "$ui_eval_root/R2.sources.sha256"

run_ui_case R3 '검토해줘'
run_ui_case R4 '새 랜딩 페이지를 디자인하고 구현해줘'
run_ui_case R5 '이 UI를 Visual QA 해줘'
run_ui_case R6 'Visual QA 후 명백한 결함은 수정까지 해줘'
```

최소 평가 행렬은 **각 스킬별로** 직접·간접·불완전·비트리거·edge case를 모두 가진다.

| ID | 스킬/유형 | fixture·입력 | 기대 |
|---|---|---|---|
| D1 | design-ui 직접 | 빈 case, `$design-ui 새 대시보드 UI를 index.html로 만들어줘` | explicit 선택, greenfield 디자인 정본 선행 |
| D2 | design-ui 간접 | baseline + `-i reference.png`, `첨부 화면의 구조를 실제 프론트엔드 코드로 옮겨줘` | screenshot 입력 사용, 브랜드·문구 자동 복제 없음 |
| D3 | design-ui 불완전 | baseline, `UI 좀 바꿔줘` | 결과를 크게 가르는 정보만 질문 또는 Needs input |
| D4 | design-ui 비트리거 | baseline, `API와 DB 스키마를 설계해줘` | `design-ui`·`review-ui` 본문 미로드 |
| D5 | design-ui edge | baseline, 존재하지 않는 Figma URL 참조 | reference 내용을 날조하지 않고 Reference blocked |
| D6 | design-ui 최소 사례 | 기존 `DESIGN.md` baseline, `기존 디자인 시스템을 유지해 새 통계 카드를 추가해줘` | 기존 정본·토큰 우선, 불필요한 정본 재작성 없음 |
| R1 | review-ui 직접 | baseline, `$review-ui index.html을 Visual QA 해줘` | Audit, source hash 불변, before 근거·발견 |
| R2 | review-ui 간접 | baseline, `이 화면의 반응형 깨짐과 시각적 불일치를 찾아 보고해줘` | Audit 선택 |
| R3 | review-ui 불완전 | 빈 case, `검토해줘` | 대상 질문 또는 blocked, 취향 기반 위반 날조 없음 |
| R4 | review-ui 비트리거 | 빈 case, `새 랜딩 페이지를 디자인하고 구현해줘` | `review-ui` 미로드, 제작 목표는 design-ui 경계 |
| R5 | review-ui edge | 앱 없는 빈 case, `이 UI를 Visual QA 해줘` | green 금지, blocked와 미검토 범위 |
| R6 | review-ui Repair | 결함 있는 baseline, `Visual QA 후 명백한 결함은 수정까지 해줘` | before 고정, Repair, 같은 행렬 after 재검증 |

- D2는 global image 옵션을 포함해 아래 형태로 실행한다.

```bash
cp -a "$ui_eval_root/baseline" "$ui_eval_root/D2"
mkdir -p "$ui_eval_root/evidence/D2"
if test "$(cat "$ui_eval_root/evidence/playwright/status")" = ready; then
  if codex -C "$ui_eval_root/D2" -i "$ui_eval_root/reference.png" -s workspace-write -a never exec --ephemeral --ignore-user-config --skip-git-repo-check --json '첨부 화면의 구조를 실제 프론트엔드 코드로 옮겨줘' >"$ui_eval_root/evidence/D2/stdout.jsonl" 2>"$ui_eval_root/evidence/D2/stderr.log"; then
    d2_status=0
  else
    d2_status=$?
  fi
else
  d2_status=125
  printf '%s\n' 'skipped: Playwright reference screenshot unavailable' >"$ui_eval_root/evidence/D2/stderr.log"
  : >"$ui_eval_root/evidence/D2/stdout.jsonl"
fi
printf '%s\n' "$d2_status" >"$ui_eval_root/evidence/D2/exit-code"
```

- R1·R2 Audit 전에는 `index.html`과 `DESIGN.md`의 SHA-256을 저장하고 실행 후
  `sha256sum -c`로 source 불변을 확인한다. report·screenshot 신규 생성은 허용한다.
- 각 JSONL에서 SKILL 경로 read 여부, 선택 모드, 종료 상태, 근거 경로를 추출해 실행
  리포트에 기록한다. 단어 포함만으로 통과시키지 않고 실제 tool event와 최종 응답을 함께
  본다.
- 모든 사례 종료 후 정확한 임시 경로를 확인하고 그 경로만 정리한다. 평가 원문이 독립
  검증에 필요하므로 T-007 완료까지 보존한다. T-007 뒤에는 아래처럼 target을 검증한 뒤
  해당 temp만 삭제한다.

```bash
test -n "$ui_eval_root"
case "$ui_eval_root" in /tmp/*) ;; *) exit 1 ;; esac
test -d "$ui_eval_root/evidence"
rm -rf -- "$ui_eval_root"
```
- 비용·인증·브라우저 제약으로 일부 사례를 실행하지 못하면 통과로 간주하지 않고
  `수단 부재`, 원본 오류, 위 재현 명령을 기록한다.

산출물:

- `plans/20260904-codex-ui-design-skills-execute-report.md` 안의 활성화 평가 표

검증 조건:

- [ ] `design-ui`와 `review-ui` 각각 직접·간접·불완전·비트리거·edge case 다섯 유형이 실행됨
- [ ] greenfield, 기존 디자인 시스템 확장, 실제 `reference.png`, Audit, Repair가 실행됨
- [ ] R1·R2 Audit의 `index.html`·`DESIGN.md` SHA-256이 실행 전후 동일함
- [ ] D6의 `DESIGN.md` SHA-256이 실행 전후 동일함
- [ ] R6가 before 발견과 같은 viewport·state의 after 결과를 모두 남김
- [ ] 접근 불가 참고물에서 구체 UI 내용을 지어낸 응답이 없음
- [ ] 렌더링 불가 사례가 green으로 기록되지 않음
- [ ] 실행하지 못한 사례가 있다면 해당 행이 `미검증`이고 이유·재현 명령이 있음
- [ ] Playwright와 D1~D6·R1~R6 각각 stdout/stderr/exit-code 근거가 보존됨
- [ ] baseline HEAD와 정확한 `ui_eval_root` 경로가 evidence에 기록됨

### T-007 — 독립 재검증과 통합 게이트를 통과한다

내용:

- 읽기 전용 독립 서브에이전트에게 다음 경로만 전달한다.
  - `docs/codex-ui-design-skills.md`
  - `codex-plugins/design-ui/`
  - `.agents/plugins/marketplace.json`
  - `README.md`
  - `plans/20260904-codex-ui-design-skills-execute-report.md`
  - `.claude-plugin/`와 `plugins/`
  - 실행 리포트에 기록된 착수 HEAD·`git status` 및 정확한
    `<ui_plan_snapshot_dir>/protected-tree`, `protected-files`, `protected-sha256`
  - `evidence/eval-root-path`가 가리키는 정확한 `<ui_eval_root>/` 전체: baseline,
    D1~D6·R1~R6 case, `reference.png`, stdout·stderr·exit-code, baseline HEAD와 checksum
    파일
- 검증자는 정본 §3~§9의 계약에서 기대값을 뽑고 구현·카탈로그·README·T-006 결과를
  대조한다.
- 발견은 `blocker/major/moderate/minor`와 경로·정본 절·근거로 반환한다.
- 등급과 무관하게 계약 위반은 수행자가 반영하고 T-005·T-006 관련 검사를 다시 실행한다.
  계약 밖의 비차단 개선 제안만 근거를 기록하고 남길 수 있다.
- 설계가 틀렸거나 미규정인 발견은 구현으로 해결하지 않고 `$make-design`으로 승격한다.
- 마지막에 저장소 표준 링크 게이트와 diff 검사를 한 번만 통합 실행한다.

산출물:

- 실행 리포트의 독립 검증 절
- 필요 시 독립 검증 발견을 반영한 스킬·문서 수정

검증 조건:

- [ ] 독립 검증의 계약 위반 0; blocker·major·moderate·minor 어느 등급에도 계약 위반이 없음
- [ ] `python3 scripts/validate_skill_links.py`
- [ ] T-005의 whitespace 검사가 신규 파일을 포함해 통과
- [ ] 독립 검증자가 착수 protected-tree snapshot을 직접 읽고 현재 `.claude-plugin/`,
      `plugins/`의 경로·type·mode·symlink target·일반 파일 SHA-256 동일을 판정
- [ ] 독립 검증자가 `<ui_eval_root>/`의 원본 event·응답·종료 코드·source checksum·
      before/after 산출물을 직접 대조하고 실행 리포트 요약과 일치함을 판정
- [ ] `python3 -m json.tool .agents/plugins/marketplace.json >/dev/null`
- [ ] `python3 -m json.tool codex-plugins/design-ui/.codex-plugin/plugin.json >/dev/null`

### T-008 — 기록을 닫고 원자 커밋을 준비한다

내용:

- 실행 리포트에 각 T-ID의 완료 여부, 검사 출력, 독립 검증 결과, 미검증 범위를
  기록하고 상태를 `완료 (2026-09-04)` 또는 정확한 중단 상태로 닫는다.
- `docs/codex-ui-design-skills.md`와 이 플랜도 구현과 함께 추적할 작업 관련 문서로
  분류한다.
- 변경 파일을 T-001~T-004의 커밋 경계에 따라 검토하되, 실행 환경에서 실제 커밋 수는
  작은 원자 단위로 유지한다. 검증 전용 작업은 별도 소스 커밋을 만들지 않는다.
- 각 커밋 직전 정확한 task 파일만 stage한 뒤 `git diff --cached --check`를 통과시킨다.
  이미 만든 커밋은 `git show --check --oneline <commit>`으로 같은 검사를 재확인한다.
- 최종 diff에 사용자 소유의 무관한 변경이 섞이지 않았는지 확인한다.
- push는 하지 않고 사용자 확인을 기다린다.

산출물:

- `plans/20260904-codex-ui-design-skills-execute-report.md`
- 원자 커밋 또는 커밋 직전 staging 제안

검증 조건:

- [ ] `git status --short`의 모든 변경이 정본 또는 이 플랜의 산출물로 설명됨
- [ ] 실행 리포트에 T-001~T-008이 모두 `완료/중단` 중 하나로 닫힘
- [ ] 최종 통합 게이트 출력이 실행 리포트에 기록됨
- [ ] 신규 파일을 포함한 각 staged diff 또는 생성된 원자 커밋의 whitespace 검사가 통과
- [ ] push가 수행되지 않음

## 5. 의존성 그래프

```text
T-001 플러그인 골격
  ├── T-002 design-ui ───┐
  └── T-003 review-ui ───┤
                         ▼
                 T-004 카탈로그·README
                         ▼
                 T-005 정적 계약 검사
                         ▼
                 T-006 런타임 평가
                         ▼
                 T-007 독립 검증·통합 게이트
                         ▼
                 T-008 기록·커밋 준비
```

- 병렬 가능: T-002와 T-003
- 조건부 병렬 가능: T-004의 README 문안 초안은 T-002·T-003과 병행할 수 있으나,
  최종 경로·설명은 두 스킬 완료 뒤 확정한다.
- 임계 경로: T-001 → max(T-002, T-003) → T-004 → T-005 → T-006 → T-007 → T-008

## 6. 검증 실행 계획

### 6.1 수행자 1차 검증

각 변경 작업 직후 해당 상세 명세의 명령을 실행한다. T-005에서 정본 §9.3의 불변 조건을
행별로 대조하고, T-006에서 활성화·실패 경로를 임시 환경으로 평가한다. 실패한 검사를
나중으로 미루지 않고 해당 작업으로 되돌린다.

### 6.2 검증자 독립 재검증

T-007의 독립 서브에이전트는 작성 의도나 수행자 설명 없이 정본과 실물만 받는다. 기대값은
구현에서 역으로 만들지 않는다. 정적 검사 green만으로 트리거·비파괴성·침묵 실패 계약을
통과 처리하지 않는다.

### 6.3 통합 게이트

프로젝트 표준 통합 게이트는 아래 명령이다.

```bash
python3 scripts/validate_skill_links.py
```

이 명령에 JSON·diff 계약은 포함되지 않으므로 T-007의 명시적 구조 검사 명령을 함께
실행하되, 표준 게이트 자체를 복제하거나 새 스크립트로 확장하지 않는다.

## 7. 롤백 플랜

### 착수 전 스냅샷

1. `git status --short --branch`와 `git rev-parse HEAD`를 실행 리포트에 기록한다.
2. 아래 명령으로 변경 금지 경로의 경로·type·mode·symlink target과 일반 파일 SHA-256을
   저장한다. T-004, T-005, T-007에서는 아래 블록의 마지막 세 명령을 다시 실행해 착수
   snapshot과 비교한다.

```bash
ui_plan_snapshot_dir=$(mktemp -d)
find .claude-plugin plugins -printf '%p|%y|%m|%l\n' | LC_ALL=C sort >"$ui_plan_snapshot_dir/protected-tree"
find .claude-plugin plugins -type f -print0 | sort -z >"$ui_plan_snapshot_dir/protected-files"
while IFS= read -r -d '' path; do
  sha256sum "$path"
done <"$ui_plan_snapshot_dir/protected-files" >"$ui_plan_snapshot_dir/protected-sha256"

find .claude-plugin plugins -printf '%p|%y|%m|%l\n' | LC_ALL=C sort >"$ui_plan_snapshot_dir/protected-tree-current"
cmp "$ui_plan_snapshot_dir/protected-tree" "$ui_plan_snapshot_dir/protected-tree-current"
sha256sum -c "$ui_plan_snapshot_dir/protected-sha256"
```

3. 기존 미커밋 변경은 사용자 소유로 간주하고 수정·삭제하지 않는다.
4. 현재 추적되지 않은 정본 설계 문서는 이 작업의 입력이므로 보존하고 최종 변경 목록에
   명시한다.

### 롤백 트리거와 동작

| 트리거 | 동작 |
|---|---|
| T-001~T-004 개별 검사가 실패 | 아직 커밋 전이면 해당 작업의 파일만 `apply_patch`로 되돌려 재작성 |
| 원자 커밋 뒤 회귀 발견 | 대상 커밋을 특정한 뒤 사용자 확인을 받아 `git revert <commit>` 사용 |
| Claude 트리에 변경 발생 | 원인을 확인하고 이번 작업이 만든 해당 변경만 제거; 기존 변경은 보존 |
| 런타임 평가에서 오활성화·침묵 실패 | 완료 처리하지 않고 해당 SKILL description/body로 회귀 후 전체 행 재실행 |
| 설계 계약 자체가 모순·미규정 | 코드를 되돌려 맞추지 않고 실행 중단, 관련 §로 `$make-design` 승격 |
| 독립 검증에서 등급과 무관한 계약 위반 | T-005 또는 원인 작업으로 회귀; 수정 후 독립 재검증 |

`git reset --hard`, 광범위한 checkout, 추적되지 않은 파일 일괄 삭제는 사용하지 않는다.
임시 런타임 평가 디렉터리는 `mktemp -d`의 정확한 경로를 기록하고 그 경로만 정리한다.

## 8. 리스크 및 미결

### 기술 리스크

| 리스크 | 영향 | 실측 작업 | 대응 |
|---|---|---|---|
| Codex CLI의 implicit activation 관찰 결과가 모델 변동에 민감 | description 품질을 단일 실행으로 오판 | T-006 | 직접/간접/비트리거를 나눠 기록하고 모호한 결과는 미검증 처리 |
| 임시 Codex 환경에 브라우저 능력이 없을 수 있음 | 실제 Visual QA happy path를 이 저장소에서 end-to-end 검증 못 함 | T-006 | 렌더링 불가 실패 경로는 실측하고, happy path 미검증 범위와 실제 프로젝트 재검증 명령을 남김 |
| 루트 README가 “양쪽 런타임”만 전제 | Codex-only 스킬 표기가 모순될 수 있음 | T-004 | 저장소 전체는 양쪽을 지원하되 개별 플러그인은 한쪽만 가능하다고 문구 수정 |
| 두 스킬의 공통 규칙이 중복될 수 있음 | 유지보수 시 drift | T-005, T-007 | 각 스킬에 필요한 최소 불변만 두고 상세는 역할별 reference에 배치; 공유 파일을 억지로 만들지 않음 |
| `review-ui` Repair가 `design-ui`와 겹칠 수 있음 | 트리거 충돌 | T-006 | “기존 UI의 검토 후 명백한 결함 수정”과 “새 UI 제작·재설계” 사례를 분리 평가 |

### 추정

- [추정] 현재 manifest의 `interface` 필드 관례는 새 플러그인에도 그대로 적용 가능하다.
  T-001의 JSON 파싱과 T-006의 local discovery에서 확인한다.
- [추정] 신규 스크립트 없이 instruction과 asset/reference만으로 v1 계약을 충분히 표현할
  수 있다. T-005 계약 대조와 T-006에서 수단 부재가 반복되면 설계 §8의 재도입 트리거로
  보고한다.

### 착수 전 사용자 결정

없음.

### 이 플랜이 정하지 않는 것

- 공개 마켓플레이스 제출·배포 시점
- Claude Code 대응판 제작
- plugin icon과 `agents/openai.yaml`
- 전용 브라우저/MCP 및 캡처 자동화 스크립트

위 항목은 정본 설계 §8에서 의도적으로 배제됐다.
