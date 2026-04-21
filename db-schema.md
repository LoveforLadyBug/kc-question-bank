# db-schema.md
# KakaoCloud Essential Basic Course — 문제 파일 스키마 정의

> **이 파일이 frontmatter 스키마의 단일 소스(Single Source of Truth)입니다.**
>
> ARCHITECTURE.md, QUALITY_SCORE.md, AGENTS.md 는 이 파일을 *참조*할 뿐,
> 스키마를 직접 정의하지 않습니다.
> 필드 추가·변경·삭제는 반드시 이 파일을 먼저 수정한 후 PR을 통해 반영합니다.

---

## 1. 현재 스키마 버전

```
SCHEMA_VERSION: 1.1.0
최초 작성: 2026-04-13
최종 변경: 2026-04-21
변경 내용: evidence 필드 추가, hallucination-suspect 상태 추가
```

> `quality_schema_version` 필드가 이 버전을 추적합니다.
> 채점 기준(QUALITY_SCORE.md)이 변경될 때마다 이 버전을 올리고,
> `validate-quality.py --force` 로 전체 재채점을 실행합니다.

---

## 2. 전체 필드 명세

```yaml
# ── 식별자 ──────────────────────────────────────────────────
id:
  type: string
  format: "q{NNN}"          # NNN은 챕터 내 3자리 순번 (001~999)
  scope: chapter-local       # ID는 챕터 디렉토리 내에서 유일
  globally-unique-format: "{chapter}/{id}"   # 전역 참조 시 이 형식 사용
  example: "q001"
  note: |
    챕터 디렉토리가 다르면 동일 id 허용 (q001이 여러 챕터에 존재 가능).
    시험 세트 build 및 외부 참조 시에는 반드시 "{chapter}/{id}" 형식 사용.
    예: "02-bcs/q001", "03-bns/q001"

chapter:
  type: string
  allowed:
    - "01-cloud-fundamentals"
    - "02-bcs"
    - "03-bns"
    - "04-bss"
    - "05-container-pack"
    - "06-data-store"
    - "07-management-iam"
  note: docs/design-docs/question-taxonomy.md §2 와 동기화 유지

# ── 분류 ──────────────────────────────────────────────────
topic:
  type: string
  note: docs/design-docs/question-taxonomy.md §4 토픽 목록에서만 사용

difficulty:
  type: integer
  min: 1
  max: 5
  labels:
    1: "기초 I"
    2: "기초 II"
    3: "응용"
    4: "심화 I"
    5: "심화 II"
  note: docs/design-docs/difficulty-rubric.md 참조

type:
  type: string
  allowed: ["single"]
  note: |
    현재 single(4지선다) 유형만 허용.
    새 유형 추가 시 docs/design-docs/core-beliefs.md §3 개정 후
    이 파일의 allowed 목록에 추가.

tags:
  type: list[string]
  min_items: 2
  max_items: 4
  rules:
    - "영문 소문자 + 하이픈만 허용 (한글 금지)"
    - "서비스 태그 1~2개 + 인지 유형 태그 1~2개 권장"
  cognitive_type_tags:
    - definition
    - feature
    - comparison
    - usecase
    - architecture
    - constraint

# ── 출처 & 근거 인용 ──────────────────────────────────────────────────
source:
  type: string
  format: URL
  required: true            # 없으면 generator가 에러로 중단
  allowed_domains:          # parser가 fetch 허용하는 도메인 목록 (단일 소스)
    - "docs.kakaocloud.com"
    - "kakaocloud.com"
    - "blog.kakaocloud.com"
  note: |
    allowed_domains 변경은 이 파일 + AGENTS.md §2 도메인 화이트리스트를
    동시에 수정해야 함. 이 파일이 정의, AGENTS.md가 참조.

evidence:
  type: string | null
  required: false
  set_by: generator (LLM이 llms.txt에서 인용한 근거 원문)
  note: |
    정답 보기를 뒷받침하는 공식 문서 원문 문장을 그대로 인용합니다.
    할루시네이션 검증(grounding_check)의 기준 문자열로 사용됩니다.
    null = 검증 불가 (구버전 문제 또는 수동 생성 문제).

verify_result:
  type: string | null
  allowed: ["PASS", "FAIL", null]
  set_by: generator (3단계 검증 결과)

verify_reason:
  type: string | null
  set_by: generator (검증 실패 시 실패 단계 및 이유 기록)
  note: "PASS 시 null, FAIL 시 실패한 단계명과 이유를 기록"

# ── 상태 ──────────────────────────────────────────────────
status:
  type: string
  allowed: ["draft", "hallucination-suspect", "review", "active", "deprecated"]
  transitions:
    draft                  → review:               "validate-quality.py 실행 시 자동"
    hallucination-suspect  → draft:                "사람이 수동 수정 후 재생성"
    review                 → active:               "사람만 가능"
    active                 → deprecated:           "사람만 가능 (팀 합의 후)"
  note: |
    hallucination-suspect: 생성 후 3단계 할루시네이션 검증 실패 시 generator가 자동 지정.
    verify_reason 필드에 실패 이유가 기록됨.
    AGENTS.md §5 사람 전용 작업 목록 참조

# ── 메타데이터 ─────────────────────────────────────────────
created:
  type: date
  format: "YYYY-MM-DD"
  set_by: generator (생성 시점 자동 기록)

reviewed_by:
  type: list[string]
  default: []
  set_by: 사람만 (AGENTS.md §5 참조)

# ── 품질 점수 (validator 기록) ──────────────────────────────
quality_score:
  type: integer | null
  range: 0~100
  set_by: validate-quality.py
  note: "null = 아직 채점 안 됨"

quality_breakdown:
  type: object | null
  fields: [A_source, B_structure, C_choices, D_explanation, E_chapter]
  set_by: validate-quality.py

quality_checked_at:
  type: date | null
  format: "YYYY-MM-DD"
  set_by: validate-quality.py

quality_schema_version:
  type: string
  format: "MAJOR.MINOR.PATCH"
  set_by: validate-quality.py (실행 시 현재 SCHEMA_VERSION 자동 기록)
  note: |
    SCHEMA_VERSION(이 파일 §1)과 불일치하는 문제는
    validate-quality.py --force 재채점 대상.
    스크립트 시작 시 버전 불일치 문제 목록을 경고로 출력해야 함.

quality_issues:
  type: list[string] | null
  set_by: validate-quality.py (74점 이하 시만 기록)

# ── deprecated 전용 필드 ───────────────────────────────────
deprecated_reason:
  type: string | null
  required_when: "status == deprecated"

deprecated_at:
  type: date | null
  format: "YYYY-MM-DD"
  required_when: "status == deprecated"
```

---

## 3. 완성된 예시 frontmatter

```yaml
---
id: q007
chapter: 03-bns
topic: vpc
difficulty: 3
type: single
tags: [vpc, usecase]
source: https://docs.kakaocloud.com/start/region-az
status: active
created: 2026-04-15
reviewed_by: [kim, lee]
quality_score: 88
quality_breakdown:
  A_source:      20
  B_structure:   20
  C_choices:     23
  D_explanation: 20
  E_chapter:     5        # topic 매칭 부분 감점
quality_checked_at: 2026-04-15
quality_schema_version: 1.0.0
quality_issues: null
deprecated_reason: null
deprecated_at: null
---
```

---

## 4. 스키마 변경 절차

스키마(이 파일)를 변경할 때 반드시 아래 절차를 따릅니다.

```
[1] 이 파일(db-schema.md)의 필드 명세 수정
[2] SCHEMA_VERSION 올리기
    - 필드 추가/삭제 → MINOR 버전 업 (예: 1.0.0 → 1.1.0)
    - 기존 필드 의미 변경 → MAJOR 버전 업 (예: 1.0.0 → 2.0.0)
    - 오타 수정 등 → PATCH 버전 업 (예: 1.0.0 → 1.0.1)
[3] QUALITY_SCORE.md, AGENTS.md, ARCHITECTURE.md 중
    영향 받는 부분 동기화
[4] validate-quality.py --force 전체 재채점 실행
    (quality_schema_version 불일치 문제 일괄 갱신)
[5] PR 설명에 변경 이유와 영향 범위 기록
```

---

## 5. 관련 문서

- [`ARCHITECTURE.md §5`](../../ARCHITECTURE.md) — 문제 파일 포맷 예시 (이 스키마 참조)
- [`docs/QUALITY_SCORE.md §2-B`](../QUALITY_SCORE.md) — frontmatter 필수 필드 체크 (이 스키마 참조)
- [`AGENTS.md §3,§4`](../../AGENTS.md) — 에이전트별 필드 접근 권한 (이 스키마 참조)
- [`docs/design-docs/question-taxonomy.md`](../design-docs/question-taxonomy.md) — chapter/topic 허용 값 목록
