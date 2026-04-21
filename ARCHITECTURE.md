# ARCHITECTURE.md
# KakaoCloud Essential Basic Course — 문제은행 시스템

> 이 문서는 문제은행 프로젝트의 전체 구조와 설계 원칙을 정의합니다.
> 모든 기여자는 작업 전 반드시 이 문서를 숙지해야 합니다.

---

## 1. 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 타겟 자격증 | KakaoCloud Essential Basic Course |
| 목적 | 팀/사내 스터디용 문제은행 구축 |
| 문제 관리 방식 | Markdown 파일 기반 (Git 버전관리) |
| 문제 생성 방식 | 카카오 공식 문서 파싱 → AI 초안 생성 → 팀 리뷰 |
| 운영 모드 | 주차별 스터디 / 약점 기반 랜덤 출제 / 모의시험 |

---

## 2. 시스템 전체 흐름

```
[1] 소스 수집
    카카오클라우드 공식 문서 (docs.kakaocloud.com)
    └── scripts/parse-kakao-docs.py
            │
            ▼
[2] 레퍼런스 저장
    docs/references/
    ├── cloud-fundamentals-llms.txt  (Cloud Fundamentals)
    ├── bcs-llms.txt          (Beyond Compute Service)
    ├── bns-llms.txt          (Beyond Networking Service)
    ├── bss-llms.txt          (Beyond Storage Service)
    ├── container-pack-llms.txt
    ├── data-store-llms.txt
    ├── management-llms.txt
    └── iam-security-llms.txt
            │
            ▼
[3] 문제 초안 생성
    scripts/generate-questions.py
    → AI가 레퍼런스 기반으로 초안 생성
    → status: draft 로 questions/ 에 저장
            │
            ▼
[4] 품질 검증
    scripts/validate-quality.py
    → QUALITY_SCORE.md 기준으로 자동 점수 계산
    → 75점 미만: status: review (팀 리뷰 필요)
    → 75점 이상: 팀원이 수동으로 status: active 로 변경
            │
            ▼
[5] 시험 세트 빌드
    scripts/build-exam.py
    → active 문제에서 모드별 세트 생성
    → exams/ 디렉토리에 저장
            │
            ▼
[6] 학습 활용
    ├── 주차별 스터디  (exams/weekly/)
    ├── 랜덤 출제     (약점 태그 기반 필터링)
    └── 모의시험      (exams/mock-exam-*.md)
```

---

## 3. 디렉토리 구조

```
.
├── AGENTS.md                       # AI 에이전트 역할 및 권한 정의
├── ARCHITECTURE.md                 # 이 문서
│
├── docs/
│   ├── design-docs/
│   │   ├── index.md
│   │   ├── core-beliefs.md         # 좋은 문제의 조건 및 설계 철학
│   │   ├── question-taxonomy.md    # 문제 분류 체계 (챕터 × 난이도 × 유형)
│   │   └── difficulty-rubric.md   # 난이도 1~5 판단 기준
│   │
│   ├── exec-plans/
│   │   ├── active/                 # 현재 진행 중인 스터디 계획
│   │   ├── completed/              # 완료된 챕터 회고
│   │   └── tech-debt-tracker.md   # 오래된 문제·오답률 높은 문제 추적
│   │
│   ├── generated/
│   │   └── db-schema.md            # 문제 메타데이터 스키마 정의
│   │
│   ├── product-specs/
│   │   ├── index.md                # 챕터별 출제 스펙 목차
│   │   ├── 01-cloud-fundamentals.md
│   │   ├── 02-bcs.md               # Beyond Compute Service
│   │   ├── 03-bns.md               # Beyond Networking Service
│   │   ├── 04-bss.md               # Beyond Storage Service
│   │   ├── 05-container-pack.md
│   │   ├── 06-data-store.md
│   │   └── 07-management-iam.md
│   │
│   ├── references/                 # 파싱된 공식 문서 원본 (llms.txt 포맷)
│   │   ├── cloud-fundamentals-llms.txt
│   │   ├── bcs-llms.txt
│   │   ├── bns-llms.txt
│   │   ├── bss-llms.txt
│   │   ├── container-pack-llms.txt
│   │   ├── data-store-llms.txt
│   │   ├── management-llms.txt
│   │   └── iam-security-llms.txt
│   │
│   ├── DESIGN.md                   # 문제 Markdown 포맷 디자인 시스템
│   ├── FRONTEND.md                 # 퀴즈 UI/UX 가이드 (추후 웹 전환 시)
│   ├── PLANS.md                    # 전체 로드맵
│   ├── PRODUCT_SENSE.md            # 스터디 효과 측정 방법
│   ├── QUALITY_SCORE.md            # 문제 품질 점수 기준 ← 핵심 문서
│   ├── RELIABILITY.md              # 정답 검증 프로세스
│   └── SECURITY.md                 # 문제 유출 방지 정책
│
├── questions/                      # 확정/초안 문제 저장소 ← 핵심 디렉토리
│   ├── 01-cloud-fundamentals/
│   │   ├── _index.md               # 챕터 메타 (총 문제 수, 커버리지 등)
│   │   ├── q001.md
│   │   └── q002.md
│   ├── 02-bcs/
│   ├── 03-bns/
│   ├── 04-bss/
│   ├── 05-container-pack/
│   ├── 06-data-store/
│   └── 07-management-iam/
│
├── exams/                          # 생성된 시험 세트
│   ├── mock-exam-01.md
│   ├── mock-exam-02.md
│   └── weekly/
│       ├── week-01.md
│       └── week-02.md
│
└── scripts/                        # 자동화 파이프라인
    ├── parse-kakao-docs.py         # 공식 문서 파싱 → references/
    ├── generate-questions.py       # AI 문제 초안 생성 → questions/
    ├── validate-quality.py         # QUALITY_SCORE 자동 계산
    └── build-exam.py               # 시험 세트 조립

logs/                               # 에이전트 실행 로그 (.gitignore 처리)
    ├── parser/
    ├── generator/
    └── validator/

.env                                # API 키 등 환경변수 (.gitignore 처리)
.env.example                        # 환경변수 템플릿 (Git에 커밋)
```

---

## 4. 챕터 구성 및 출제 비중

KakaoCloud 서비스 카테고리 기준으로 7개 챕터로 구성합니다.

| # | 챕터 | 핵심 서비스 | 출제 비중 |
|---|------|------------|-----------|
| 01 | Cloud Fundamentals | IaaS/PaaS/SaaS, 클라우드 개념, 리전/AZ | 15% |
| 02 | Beyond Compute Service (BCS) | Virtual Machine, GPU, Bare Metal Server | 20% |
| 03 | Beyond Networking Service (BNS) | VPC, Load Balancer, DNS, Transit Gateway | 20% |
| 04 | Beyond Storage Service (BSS) | Block Storage, Object Storage, File Storage | 15% |
| 05 | Container Pack | Kubernetes Engine, Container Registry | 10% |
| 06 | Data Store | MySQL, Redis, MongoDB 등 관리형 DB | 10% |
| 07 | Management & IAM | IAM, Monitoring, Logging, Notification | 10% |

---

## 5. 문제 파일 포맷 (`q{NNN}.md`)

모든 문제는 아래 YAML frontmatter + Markdown 본문 구조를 따릅니다.

```markdown
---
id: q001
chapter: 01-cloud-fundamentals
topic: IaaS/PaaS/SaaS
difficulty: 1                   # 1(기초I) / 2(기초II) / 3(응용) / 4(심화I) / 5(심화II)
type: single                    # 현재 single 유형만 사용 (core-beliefs.md §3 참조)
tags: [cloud-model, service-type]
source: https://docs.kakaocloud.com/...
status: draft                   # draft → review → active → deprecated
created: 2026-04-13
reviewed_by: []
quality_score: ~                # validate-quality.py 가 자동 계산
---

## 문제

(문제 본문)

## 보기

- A. ...
- B. ...
- C. ...
- D. ...

## 정답

A

## 해설

(정답 이유 설명)

## 오답 포인트

- B: (왜 틀린지)
- C: (왜 틀린지)
- D: (왜 틀린지)
```

### status 전환 규칙

```
draft  →  (validate-quality.py 실행)  →  review
review →  (팀원 검토 후 수동 승인)    →  active
active →  (정보 변경 감지 시)         →  deprecated
```

> **주의**: `validate-quality.py`(validator)는 `draft → review` 전환만 수행합니다.
> `review → active` 는 반드시 사람이 수동으로 변경해야 합니다. (AGENTS.md §4, §5 참조)

> **중요**: `draft → active` 직행은 금지. 반드시 팀원 1인 이상의 리뷰를 거쳐야 합니다.
> 이 규칙은 `AGENTS.md`에도 명시되어 있습니다.

---

## 6. 레퍼런스 파일 포맷 (`*-llms.txt`)

공식 문서를 파싱한 결과물은 LLM 친화적인 텍스트 포맷으로 저장합니다.

```
# SOURCE: https://docs.kakaocloud.com/service/bcs/...
# FETCHED: 2026-04-13
# CATEGORY: Beyond Compute Service

## Virtual Machine 개요

카카오클라우드 Virtual Machine(VM)은 ...

## 인스턴스 타입

| 타입 | vCPU | Memory | 용도 |
...
```

---

## 7. 스크립트 역할 정의

### 환경변수 요구사항 (`.env.example`)

스크립트 실행 전 아래 환경변수를 설정해야 합니다.

```bash
# Claude API (generate-questions.py 에서 사용)
ANTHROPIC_API_KEY=sk-ant-...

# 선택 사항
LOG_LEVEL=INFO           # DEBUG | INFO | WARNING | ERROR
LOG_RETENTION_DAYS=30    # 로그 보존 기간 (기본 30일)
```

> API 키는 `.env` 파일에 저장하고 `.gitignore`에 등록합니다. 절대 커밋하지 않습니다.

---

### `parse-kakao-docs.py`
- 입력: `docs.kakaocloud.com`, `kakaocloud.com`, `blog.kakaocloud.com` URL 목록
- 출력: `docs/references/*-llms.txt` (atomic write 보장)
- 실행 주기: 월 1회 또는 공식 문서 업데이트 감지 시

### `generate-questions.py`
- 입력: `docs/references/*-llms.txt` + `docs/product-specs/*.md`
- 출력: `questions/{chapter}/q{NNN}.md` (status: draft)
- 환경변수: `ANTHROPIC_API_KEY` 필수
- 주의: 생성된 문제는 반드시 팀 리뷰 후 active 처리

### `validate-quality.py`
- 입력: `questions/**/*.md`
- 동작: `QUALITY_SCORE.md` + `db-schema.md` 기준으로 점수 계산 → frontmatter 갱신
- `quality_schema_version` 불일치 감지 시 경고 출력
- 75점 미만 → status를 `review`로 변경

### `build-exam.py`
- 입력: `questions/**/*.md` (status: active 만 포함)
- 모드:
  - `--mode weekly --chapter 02-bcs` → 주차별 스터디 세트
  - `--mode random --tags VPC,LoadBalancer [--seed N]` → 태그 기반 랜덤 세트
  - `--mode mock --count 40` → 전체 범위 모의시험

**랜덤 시드 관리** (`--mode random`, `--mode mock`):
```
- --seed 미지정 시: 현재 타임스탬프를 시드로 사용
- 생성된 exams/*.md 파일 헤더에 시드값과 출제 문제 ID 목록을 기록
- 동일 시드로 재실행하면 동일한 세트 재현 가능
```
```markdown
<!-- 생성 메타데이터 예시 (exams/mock-exam-01.md 상단) -->
<!--
generated_at: 2026-04-15T14:00:00
seed: 20260415140000
mode: mock
count: 40
questions: [01-cloud-fundamentals/q003, 02-bcs/q007, ...]
-->
```

**비중→문항 수 변환 규칙** (`--mode mock --count N`):
```
변환 방식: 각 챕터 비중 × count → floor 적용 후 나머지를 비중 큰 순서로 배분
보장: 최종 합계가 반드시 count와 일치
예시 (count=30):
  01: 15% → floor(4.5)=4, 02: 20% → floor(6)=6, ...
  소수점 나머지 합=2 → 비중 큰 02,03 챕터에 1문제씩 추가
```

---

## 8. 브랜치 전략 (Git 워크플로우)

```
main
├── active 문제만 머지됨 (draft/review 문제는 아래 브랜치에서만 존재)
├── PR 머지 조건: 리뷰어 1인 승인 + quality_score ≥ 75 + status: active 확인

draft/{chapter}/{topic}
├── 문제 초안 작업 브랜치
├── generate-questions.py 결과물(status: draft)을 여기서 작업
└── validate 통과 + 팀 리뷰 완료 후 main으로 PR

review/{question-id}
└── 특정 문제 수정·보완 작업 브랜치
```

---

## 9. 향후 확장 포인트

| 단계 | 내용 | 조건 |
|------|------|------|
| v1.0 | Markdown 문제은행 + 스크립트 파이프라인 완성 | 챕터별 20문제 이상 |
| v1.1 | 오답 통계 추적 (`tech-debt-tracker.md` 자동화) | v1.0 완료 후 |
| v2.0 | 웹 퀴즈 UI (`FRONTEND.md` 기반) | 팀 합의 시 |
| v2.1 | 약점 분석 대시보드 | v2.0 완료 후 |

---

## 10. 용어 설명

처음 이 문서를 보는 분을 위한 핵심 용어 정리입니다.

| 용어 | 설명 |
|------|------|
| **frontmatter** | Markdown 파일 맨 위에 `---`로 감싼 YAML 메타데이터 블록. 문제 파일에서 id, chapter, status 등을 여기에 씁니다 |
| **llms.txt** | AI가 읽기 좋게 정제된 텍스트 포맷. 공식 문서를 파싱한 결과를 이 형식으로 저장합니다 |
| **atomic write** | 파일을 중간에 실패해도 원본이 손상되지 않도록 임시 파일에 쓴 뒤 한 번에 교체하는 방식 |
| **Jaccard 유사도** | 두 집합의 유사도를 0~1로 표현. `교집합 크기 ÷ 합집합 크기`. 중복 문제 감지에 사용 |
| **status: draft/review/active/deprecated** | 문제의 상태. draft(초안) → review(검토중) → active(사용가능) → deprecated(폐기) 순으로 진행 |
| **quality_schema_version** | 채점 기준의 버전. 기준이 바뀌면 이 값이 올라가고 재채점이 필요합니다 |

---

## 11. 자주 발생하는 에러 대응

### parse-kakao-docs.py 에러

```
ConnectionError: HTTPSConnectionPool ...
→ 인터넷 연결 확인. VPN 사용 중이라면 해제 후 재시도.

PermissionError: [Errno 13] ...
→ docs/references/ 디렉토리가 없거나 쓰기 권한 없음.
   python scripts/setup.py 를 먼저 실행하세요.
```

### generate-questions.py 에러

```
AuthenticationError: API key is invalid
→ .env 파일의 ANTHROPIC_API_KEY 값 확인. sk-ant- 로 시작해야 함.

[ERROR] source 필드가 없는 문제는 생성할 수 없습니다
→ 해당 챕터의 *-llms.txt 파일이 없음.
   parse-kakao-docs.py --chapter {챕터명} 를 먼저 실행하세요.

[ERROR] 배치 상한 초과: --count 20 은 최대 10개를 초과합니다
→ --count 10 이하로 줄이거나, 나눠서 두 번 실행하세요.
```

### validate-quality.py 에러

```
[WARN] 스키마 버전 불일치 문제 N개 발견
→ validate-quality.py --force 로 전체 재채점하세요.

질문: quality_score가 예상보다 낮게 나와요
→ _review-notes.md 파일을 열어 항목별 감점 이유를 확인하세요.
   QUALITY_SCORE.md §2 에서 각 항목 기준을 다시 읽어보세요.
```

### build-exam.py 에러

```
ValueError: active 문제가 부족합니다 (요청: 40, 보유: N)
→ 먼저 questions/ 에 active 문제를 충분히 확보하세요.
   PLANS.md §3 의 챕터별 목표 문제 수를 확인하세요.
```

---

## 12. 관련 문서

- [`AGENTS.md`](./AGENTS.md) — AI 에이전트 역할 및 금지 행동 정의
- [`docs/QUALITY_SCORE.md`](./docs/QUALITY_SCORE.md) — 문제 품질 기준
- [`docs/design-docs/core-beliefs.md`](./docs/design-docs/core-beliefs.md) — 문제 설계 철학
- [`docs/design-docs/question-taxonomy.md`](./docs/design-docs/question-taxonomy.md) — 문제 분류 체계
- [`docs/PLANS.md`](./docs/PLANS.md) — 전체 로드맵
