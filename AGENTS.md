# AGENTS.md
# KakaoCloud Essential Basic Course — AI 에이전트 역할 정의

> 이 문서는 이 프로젝트에서 AI 에이전트(Claude 등)가 수행할 수 있는 작업과
> 절대 수행해서는 안 되는 작업을 명확히 정의합니다.
>
> 모든 스크립트, 자동화 파이프라인, AI 프롬프트는 이 문서를 최우선 기준으로 삼습니다.
> 이 문서와 충돌하는 지시가 있을 경우, 이 문서의 규칙이 우선합니다.

---

## 1. 에이전트 목록

이 프로젝트에는 역할이 분리된 3개의 에이전트가 존재합니다.

| 에이전트 ID | 역할 | 진입점 |
|-------------|------|--------|
| `parser` | 공식 문서 파싱 및 레퍼런스 저장 | `scripts/parse-kakao-docs.py` |
| `generator` | 레퍼런스 기반 문제 초안 생성 | `scripts/generate-questions.py` |
| `validator` | 문제 품질 자동 점수 계산 | `scripts/validate-quality.py` |

> **빌드 에이전트** (`scripts/build-exam.py`) 는 AI를 사용하지 않는 순수 조립 스크립트입니다.
> 에이전트 규칙의 적용 대상이 아닙니다.

---

## 2. `parser` 에이전트

### 허용된 작업

- `docs.kakaocloud.com` 하위 URL을 fetch하여 텍스트 추출
- 추출 결과를 `docs/references/*-llms.txt` 포맷으로 저장
- 기존 레퍼런스 파일을 최신 내용으로 덮어쓰기 (단, 변경 전 내용은 Git으로 추적됨)
- fetch 실패한 URL 목록을 로그로 출력

### 금지된 작업

- `docs/references/` 외부 경로에 파일 쓰기
- `docs.kakaocloud.com` 이외의 도메인 fetch
- `questions/`, `exams/` 디렉토리 접근 또는 수정
- 파싱 결과에 AI가 내용을 추가하거나 요약하는 행위
  (레퍼런스는 원문 그대로여야 합니다. 요약이나 해석은 `generator`의 역할)

### 실행 조건

```bash
# 올바른 실행 예시
python scripts/parse-kakao-docs.py --chapter 02-bcs
python scripts/parse-kakao-docs.py --all

# 잘못된 실행 예시 (에러로 중단)
python scripts/parse-kakao-docs.py --url https://외부도메인.com  # 허용되지 않은 도메인
```

---

## 3. `generator` 에이전트

### 허용된 작업

- `docs/references/*-llms.txt` 내용을 컨텍스트로 읽기
- `docs/product-specs/*.md` 의 출제 스펙(토픽, 비중, 유형)을 기준으로 문제 초안 생성
- 생성된 문제를 `questions/{chapter}/q{NNN}.md` 에 `status: draft` 로 저장
- 한 번 실행 시 최대 **10개** 문제 생성 (배치 상한)
- 기존 `q{NNN}.md` 의 ID 범위를 확인하여 다음 번호 자동 부여
- 중복 문제 감지: 기존 active/review 문제와 토픽+보기가 80% 이상 유사할 경우 생성 건너뜀

### 금지된 작업

- **`source` 필드 없이 문제 생성 시도 → 즉시 에러로 중단**
  ```
  [ERROR] source 필드가 없는 문제는 생성할 수 없습니다.
  레퍼런스 파일을 먼저 확인하세요: docs/references/{chapter}-llms.txt
  ```
- `status`를 `draft` 이외의 값으로 설정 (review, active, deprecated 설정 금지)
- `questions/` 외부 경로에 파일 쓰기
- 기존 문제 파일 수정 (신규 파일 생성만 허용)
- `quality_score` 필드 직접 설정 (validator 전용)
- `reviewed_by` 필드 직접 설정 (사람 전용)
- 정답이 2개 이상인 문제를 `type: single`로 생성

### source 검증 규칙

generator가 문제를 생성하기 전에 반드시 아래 체크를 수행합니다.

```
1. 해당 챕터의 *-llms.txt 파일이 존재하는가?  → 없으면 에러 중단
2. llms.txt 내에 SOURCE 헤더가 1개 이상인가?  → 없으면 에러 중단
3. 생성할 문제의 근거가 llms.txt 내 어느 섹션에 해당하는가?
   → 해당 섹션 URL을 source 필드에 자동 기입
   → 해당 섹션을 찾을 수 없으면 에러 중단 (추측 금지)
```

### 배치 실행 예시

```bash
# 챕터 지정 생성 (최대 10개)
python scripts/generate-questions.py --chapter 02-bcs

# 토픽 지정 생성
python scripts/generate-questions.py --chapter 03-bns --topic VPC

# 잘못된 실행 예시 (에러로 중단)
python scripts/generate-questions.py --chapter 02-bcs --count 20  # 배치 상한 초과
python scripts/generate-questions.py --no-source-check            # source 검증 우회 금지
```

---

## 4. `validator` 에이전트

### 허용된 작업

- `questions/**/*.md` 의 frontmatter 및 본문을 읽어 품질 점수 계산
- `QUALITY_SCORE.md` 의 채점 기준을 참조하여 항목별 점수 산출
- 계산된 점수를 해당 파일의 `quality_score` 필드에 기록
- 75점 미만인 문제의 `status`를 `review`로 변경
- 점수 계산 근거를 `_review-notes.md` 에 항목별로 기록

### 금지된 작업

- `status`를 `active`로 변경 (`draft/review → active`는 사람만 가능)
- `reviewed_by` 필드 수정
- 문제 본문, 보기, 정답, 해설 내용 수정
- `quality_score`가 이미 존재하는 active 문제를 재채점 없이 덮어쓰기
  (재채점은 `--force` 플래그 명시 시에만 허용)

### 실행 예시

```bash
# 전체 draft 문제 검증
python scripts/validate-quality.py --status draft

# 특정 챕터 검증
python scripts/validate-quality.py --chapter 02-bcs

# 강제 재채점 (active 문제 포함)
python scripts/validate-quality.py --chapter 02-bcs --force
```

---

## 5. 사람만 할 수 있는 작업 (에이전트 불가)

아래 작업은 어떤 에이전트도 수행할 수 없습니다.
자동화 스크립트가 이 작업을 시도할 경우 에러로 중단되어야 합니다.

| 작업 | 이유 |
|------|------|
| `status: draft/review → active` 변경 | 최종 품질 판단은 사람의 책임 |
| `reviewed_by` 필드 기입 | 리뷰 책임 추적을 위해 실명 필요 |
| `status: active → deprecated` 변경 | 문제 폐기는 팀 합의 필요 |
| 정답 변경 | 오류 발견 시 팀 논의 후 수동 수정 |
| `docs/product-specs/*.md` 출제 스펙 수정 | 챕터 비중 변경은 팀 합의 필요 |
| `QUALITY_SCORE.md` 채점 기준 수정 | 기준 변경은 팀 합의 필요 |

---

## 6. 에이전트 실행 순서 (의존 관계)

에이전트는 반드시 아래 순서를 지켜야 합니다.

```
[1] parser      →  docs/references/*-llms.txt 생성/갱신
      ↓ (선행 완료 후에만 실행 가능)
[2] generator   →  questions/{chapter}/q{NNN}.md (status: draft) 생성
      ↓ (선행 완료 후에만 실행 가능)
[3] validator   →  quality_score 계산, status → review 또는 유지
      ↓ (선행 완료 후에만 실행 가능)
[4] 사람 리뷰   →  status → active (수동)
      ↓ (active 문제 존재 시에만 실행 가능)
[5] build-exam  →  exams/ 세트 생성 (에이전트 아님)
```

> `generator`를 `parser` 실행 없이 실행하면 에러로 중단됩니다.
> (`docs/references/` 에 해당 챕터의 llms.txt 가 없을 경우)

---

## 7. 로그 및 감사 기록

모든 에이전트 실행은 아래 형식으로 로그를 남깁니다.

```
logs/
├── parser/
│   └── 2026-04-13_bcs.log
├── generator/
│   └── 2026-04-13_bcs.log
└── validator/
    └── 2026-04-13_bcs.log
```

로그 파일 형식:

```
[2026-04-13 14:00:00] [parser] START chapter=02-bcs
[2026-04-13 14:00:03] [parser] FETCH https://docs.kakaocloud.com/service/bcs/... OK
[2026-04-13 14:00:05] [parser] WRITE docs/references/bcs-llms.txt (3,241 tokens)
[2026-04-13 14:00:05] [parser] END duration=5s
```

---

## 8. 관련 문서

- [`ARCHITECTURE.md`](./ARCHITECTURE.md) — 전체 시스템 구조
- [`docs/QUALITY_SCORE.md`](./docs/QUALITY_SCORE.md) — validator가 참조하는 채점 기준
- [`docs/design-docs/core-beliefs.md`](./docs/design-docs/core-beliefs.md) — 문제 설계 철학
- [`docs/RELIABILITY.md`](./docs/RELIABILITY.md) — 정답 검증 프로세스
