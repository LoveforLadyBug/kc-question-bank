# QUALITY_SCORE.md
# KakaoCloud Essential Basic Course — 문제 품질 점수 기준

> 이 문서는 `scripts/validate-quality.py` 가 자동 채점 시 참조하는 기준이며,
> 팀원이 수동 리뷰할 때도 동일한 기준을 적용합니다.
>
> 기준 변경은 팀 합의 후 PR로만 가능합니다. (AGENTS.md 참조)

---

## 1. 총점 구조

| 항목 | 배점 | 자동화 가능 여부 |
|------|------|----------------|
| A. 출처 명확성 | 20점 | ✅ 자동 |
| B. 문제 구조 완결성 | 20점 | ✅ 자동 |
| C. 오답 보기 품질 | 25점 | ⚠️ 부분 자동 |
| D. 해설 충실도 | 20점 | ⚠️ 부분 자동 |
| E. 챕터 적합성 | 15점 | ✅ 자동 |
| **합계** | **100점** | |

### 판정 기준

| 점수 | status 처리 | 의미 |
|------|------------|------|
| 75점 이상 | `draft` → `review` 유지, 팀원 승인 시 `active` | 팀 리뷰 통과 대상 |
| 74점 이하 | `draft` → `review` 강등 (수정 필요 표시) | 수정 후 재채점 필요 |

> **`active` 승격은 사람만 가능합니다.** `validate-quality.py`는 75점 이상이어도
> `active`로 직접 변경하지 않습니다. (AGENTS.md §4 참조)
>
> **`draft` → `review` 강등**: 점수와 무관하게 validate 실행 시 모든 draft 문제는
> review 상태로 전환됩니다. 75점 이상이면 "리뷰 통과 대상 review", 미만이면 "수정 필요 review"입니다.

---

## 2. 항목별 세부 기준

---

### A. 출처 명확성 (20점)

문제의 근거가 공식 문서에 있는지를 측정합니다.

| 점수 | 조건 |
|------|------|
| 20점 | `source` 필드에 유효한 `docs.kakaocloud.com` URL이 존재하고, URL이 실제 접근 가능 |
| 10점 | `source` 필드에 URL이 존재하나 접근 불가 (404 등) |
| 0점 | `source` 필드가 없거나 비어 있음 |

**자동 검증 로직:**
```python
# validate-quality.py 의 A 항목 검증
if not frontmatter.get("source"):
    score_A = 0
elif not source.startswith("https://docs.kakaocloud.com"):
    score_A = 0
elif http_head(source).status_code != 200:
    score_A = 10
else:
    score_A = 20
```

> `source` 가 없으면 A항목 0점이며, 이 경우 총점이 75점을 넘을 수 없습니다.
> (B+C+D+E 최대 합계 = 80점이지만, C·D는 부분 자동이므로 실질적으로 통과 불가)

---

### B. 문제 구조 완결성 (20점)

Markdown 포맷과 필수 섹션이 모두 갖춰져 있는지를 측정합니다.

| 점수 | 조건 |
|------|------|
| 20점 | 필수 섹션 5개 모두 존재 + 보기 개수 유효 + frontmatter 필수 필드 완비 |
| 각 항목 누락 시 | -4점 (5개 항목 × 4점) |

**필수 섹션 체크리스트:**

```
□ ## 문제        — 본문이 1줄 이상
□ ## 보기        — 보기 4개 (A/B/C/D) 고정 (core-beliefs.md §3 참조)
□ ## 정답        — A/B/C/D 중 하나
□ ## 해설        — 본문이 2줄 이상
□ ## 오답 포인트  — 오답 보기 3개(B/C/D) 모두 항목 존재
```

**frontmatter 필수 필드:**

```
□ id, chapter, topic, difficulty, type, tags, source, status, created
```

---

### C. 오답 보기 품질 (25점)

"그럴듯하게 틀린" 오답인지를 측정합니다. 단순 반대말이나 무관한 보기는 감점됩니다.

#### C-1. 자동 감점 조건 (각 -5점)

| 조건 | 감점 |
|------|------|
| 오답 보기 중 정답과 단어가 90% 이상 겹치는 항목 존재 | -5점 |
| 오답 보기 중 챕터 키워드가 하나도 없는 항목 존재 | -5점 |
| 보기 간 길이 편차가 3배 이상 (힌트 유출 가능성) | -5점 |

#### C-2. 수동 리뷰 기준 (팀원이 판단)

아래 기준으로 팀원이 보기 품질을 `_review-notes.md` 에 코멘트로 남깁니다.

```
Good  — 실제 시험에서 헷갈릴 만한 오답 (관련 개념의 다른 서비스명, 비슷한 기능의 혼동 등)
Weak  — 틀린 이유가 너무 명백하거나 무관한 보기
Bad   — 정답이 2개 이상이거나 보기 자체가 부정확한 정보 포함
```

> `validate-quality.py`는 C-1 자동 감점만 적용합니다.
> C-2 판단 결과가 `Weak` 이상이면 팀원이 직접 점수를 조정할 수 있습니다.

---

### D. 해설 충실도 (20점)

정답 이유와 오답 이유가 모두 설명되어 있는지를 측정합니다.

| 점수 | 조건 |
|------|------|
| 20점 | 해설 + 오답 포인트 모두 충실 |
| 15점 | 해설은 있으나 오답 포인트가 일부 누락 |
| 10점 | 해설만 있고 오답 포인트 없음 |
| 5점 | 해설이 1줄 이하 (단순 정답 확인 수준) |
| 0점 | 해설 섹션 없음 |

**자동 검증 로직:**
```python
has_explanation = len(explanation.strip().splitlines()) >= 2
wrong_point_count = count_items(wrong_points_section)
expected_wrong_count = len(choices) - 1  # 오답 수 = 보기 수 - 1

if not has_explanation:
    score_D = 0
elif wrong_point_count == 0:
    score_D = 10
elif wrong_point_count < expected_wrong_count:
    score_D = 15
else:
    score_D = 20
```

---

### E. 챕터 적합성 (15점)

문제가 선언된 챕터와 실제로 맞는지를 측정합니다.

| 점수 | 조건 |
|------|------|
| 15점 | `topic` 이 `docs/product-specs/{chapter}.md` 의 토픽 목록에 존재 |
| 10점 | `topic` 은 없지만 `tags` 중 하나가 챕터 키워드와 매칭 |
| 5점 | `chapter` 필드는 올바르나 topic/tags 모두 불일치 |
| 0점 | `chapter` 필드 자체가 유효하지 않은 값 |

---

## 3. 채점 결과 출력 형식

`validate-quality.py` 실행 후 각 문제 파일의 frontmatter가 아래와 같이 갱신됩니다.

```yaml
---
id: q001
...
quality_score: 82
quality_breakdown:
  A_source:      20
  B_structure:   20
  C_choices:     17   # C-1 자동 감점 -8점 적용
  D_explanation: 20
  E_chapter:     5    # topic 매칭 부분 감점
quality_checked_at: 2026-04-13
quality_schema_version: 1.0.0   # 채점 시점의 db-schema.md SCHEMA_VERSION
status: review        # 75점 이상이므로 review 유지 (active는 사람이 결정)
---
```

> `quality_schema_version` 이 현재 `db-schema.md`의 `SCHEMA_VERSION` 과 다른 문제는
> `validate-quality.py` 실행 시 경고로 표시되며 `--force` 재채점을 권장합니다.
> 스키마 변경 절차는 `docs/generated/db-schema.md §4` 참조.

75점 미만인 경우:

```yaml
quality_score: 58
...
status: review        # draft였다면 review로 강등
quality_issues:
  - "C_choices: 오답 보기 중 챕터 키워드 없는 항목 존재 (-5점)"
  - "D_explanation: 오답 포인트 누락 (-10점)"
```

---

## 4. 리뷰 노트 파일 (`_review-notes.md`)

`validate-quality.py` 실행 후 각 챕터 디렉토리에 자동 생성됩니다.

```markdown
# _review-notes.md
# 02-bcs 챕터 리뷰 노트 — 2026-04-13

| 문제 ID | 점수 | 주요 이슈 | 담당자 |
|---------|------|-----------|--------|
| q001 | 82 | C항목 보기 길이 편차 (-3점) | (미배정) |
| q002 | 58 | D항목 오답 포인트 2개 누락 | (미배정) |
| q003 | 90 | — | (미배정) |
```

팀원은 이 파일에서 리뷰할 문제를 확인하고, 담당자를 기입한 뒤
해당 `q{NNN}.md` 파일의 `reviewed_by` 에 이름을 추가합니다.

---

## 5. 공식 문서 변경 감지 및 알림

`parse-kakao-docs.py` 실행 시 기존 `*-llms.txt` 와 새 내용을 비교합니다.
변경이 감지된 경우, 해당 `source` URL을 참조하는 `active` 문제 목록을 출력합니다.

```
[WARN] docs/references/bcs-llms.txt 변경 감지
       영향 가능 문제: q001, q004, q011 (source 일치)
       → 팀 리뷰 권장. 자동 deprecated 처리는 하지 않습니다.
```

> 자동 deprecated 처리는 하지 않습니다. 문제 폐기는 팀원이 수동으로 판단합니다.

---

## 6. 관련 문서

- [`AGENTS.md`](../AGENTS.md) — validator 에이전트 허용/금지 작업
- [`ARCHITECTURE.md`](../ARCHITECTURE.md) — 전체 파이프라인 흐름
- [`docs/design-docs/core-beliefs.md`](./design-docs/core-beliefs.md) — 문제 설계 철학 (C항목 수동 리뷰 시 참조)
- [`docs/RELIABILITY.md`](./RELIABILITY.md) — 정답 오류 발견 시 처리 프로세스
