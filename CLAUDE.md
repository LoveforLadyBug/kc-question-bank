# CLAUDE.md
# KakaoCloud Essential Basic Course — Claude Code 작업 지침

> 이 파일은 Claude Code가 이 레포지토리에서 작업할 때 따르는 규칙입니다.
> AGENTS.md(파이프라인 스크립트용)와 내용이 겹치는 부분은 의도적입니다.
> 충돌 시 이 파일이 Claude Code 행동의 우선 기준입니다.

---

## 1. 프로젝트 개요

KakaoCloud Essential Basic Course 자격증 스터디용 문제은행입니다.
AI 파이프라인이 문제 초안을 생성하고, 팀원이 검토해 확정합니다.

핵심 문서 읽는 순서:
1. `ARCHITECTURE.md` — 전체 시스템 구조와 디렉토리 설명
2. `AGENTS.md` — 파이프라인 에이전트 3개의 허용/금지 행동
3. `QUALITY_SCORE.md` — 문제 품질 채점 기준
4. `docs/design-docs/core-beliefs.md` — 좋은 문제의 설계 철학

---

## 2. 디렉토리별 작업 권한

| 경로 | 권한 | 비고 |
|------|------|------|
| `scripts/` | 읽기 + 쓰기 | 스크립트 구현·수정 |
| `docs/references/` | 읽기 + 쓰기 | parser 출력물 |
| `logs/` | 읽기 + 쓰기 | 에이전트 실행 로그 |
| `questions/{chapter}/` | 조건부 쓰기 | 아래 §3 규칙 적용 |
| `exams/` | 읽기 전용 | build-exam.py 출력물. 직접 수정 금지 |
| `docs/product-specs/` | 읽기 전용 | 출제 스펙. 팀 합의 없이 수정 금지 |
| `QUALITY_SCORE.md` | 읽기 전용 | 채점 기준. 팀 합의 없이 수정 금지 |
| `docs/design-docs/` | 읽기 전용 | 설계 철학. 팀 합의 없이 수정 금지 |
| `AGENTS.md` | 읽기 전용 | 에이전트 규칙. 팀 합의 없이 수정 금지 |

---

## 3. questions/ 작업 규칙

### 절대 금지
- `status: active` 문제의 **문제 본문, 보기, 정답, 해설** 수정
- `reviewed_by` 필드 수정 (사람만 기입 가능)
- `quality_score` 필드 직접 기입 (validate-quality.py 전용)
- `status`를 `active`로 변경 (사람만 가능)
- `source` 필드 없이 새 문제 파일 생성

### 허용
- `status: draft` 신규 파일 생성 (`q{NNN}.md` 형식, source 필드 필수)
- `status: draft` 또는 `review` 문제의 frontmatter 수정 (정답 제외)
- `_review-notes.md`, `_index.md` 파일 읽기·쓰기

### status 변경 가능 범위
```
draft  → review     : validate-quality.py (스크립트만)
review → active     : 사람만
active → deprecated : 사람만
```

---

## 4. 스크립트 구현 시 준수 사항

`scripts/` 아래 파이프라인 스크립트를 구현할 때:

### parse-kakao-docs.py
- `docs.kakaocloud.com` 이외의 도메인 fetch 금지
- 출력은 `docs/references/` 에만 저장
- 파싱 결과에 AI 요약·해석 추가 금지 (원문 그대로)

### generate-questions.py
- 실행 전 반드시 체크: `docs/references/{chapter}-llms.txt` 존재 여부
  → 없으면 에러 중단, parser 먼저 실행하도록 안내
- `source` 필드를 llms.txt의 SOURCE URL에서 자동 추출 (추측 금지)
- 한 번 실행 시 최대 10개 생성
- 생성 문제는 반드시 `status: draft`로 저장
- 기존 문제 파일 수정 금지 (신규 파일 생성만)

### validate-quality.py
- `status`를 `active`로 변경하는 코드 작성 금지
- `reviewed_by` 필드 수정하는 코드 작성 금지
- 문제 본문·보기·정답·해설 수정하는 코드 작성 금지
- `--force` 없이 `status: active` 문제 재채점 금지

### build-exam.py
- `status: active` 문제만 포함
- `status: deprecated` 문제 자동 제외
- AI를 사용하지 않는 순수 조립 스크립트

---

## 5. 파이프라인 실행 순서

스크립트를 실행하거나 디버깅할 때 이 의존 관계를 반드시 인식합니다.

```
[1] parse-kakao-docs.py   →  docs/references/*-llms.txt 생성
      ↓ (선행 필수)
[2] generate-questions.py →  questions/{chapter}/q{NNN}.md (draft)
      ↓ (선행 필수)
[3] validate-quality.py   →  quality_score 계산, status → review
      ↓ (사람 리뷰 후)
[4] 팀원 수동 승인         →  status → active
      ↓ (active 문제 존재 시에만)
[5] build-exam.py         →  exams/ 세트 생성
```

`docs/references/{chapter}-llms.txt`가 없는 상태에서 generate를 실행하려 하면:
- 스크립트 코드에 에러 중단 로직을 포함해야 함
- Claude Code도 이 상황을 인지하고 parser 먼저 실행을 안내할 것

---

## 6. 문제 파일 포맷 (`q{NNN}.md`)

신규 문제 파일 생성 시 이 포맷을 따릅니다.

> **chapter 허용 값**: `01-cloud-overview`, `02-kakao-services/bcs`,
> `02-kakao-services/bns`, `02-kakao-services/bss`,
> `02-kakao-services/container-pack`, `02-kakao-services/data-store`,
> `03-billing`, `04-security`, `05-operations`, `06-account`, `07-complex`

```markdown
---
id: q{NNN}
chapter: {chapter}
topic: {topic}                  # question-taxonomy.md §4 목록에서 선택
difficulty: {1~3}               # 1=기본, 2=이해, 3=응용. difficulty-rubric.md 기준
type: single                    # 현재는 single만 사용
tags: [{service-tag}, {cognitive-tag}]  # 총 2~4개
source: https://docs.kakaocloud.com/...  # 필수. 추측 금지
status: draft
created: {YYYY-MM-DD}
reviewed_by: []
quality_score: ~
---

## 문제

## 보기

- A. 
- B. 
- C. 
- D. 

## 정답

## 해설

## 오답 포인트

- B:
- C:
- D:
```

---

## 7. 관련 문서

- `AGENTS.md` — 파이프라인 에이전트 허용/금지 행동 (스크립트 구현 시 필독)
- `ARCHITECTURE.md` — 전체 시스템 구조
- `QUALITY_SCORE.md` — validator가 참조하는 채점 기준
- `docs/design-docs/core-beliefs.md` — 문제 설계 철학
- `docs/design-docs/question-taxonomy.md` — topic/tags 허용 값 목록
- `docs/design-docs/difficulty-rubric.md` — 난이도 판단 기준
