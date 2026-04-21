# KakaoCloud Essential 문제은행

KakaoCloud Essential Basic Course 시험 준비를 위한 팀/사내 스터디용 문제은행입니다.
공식 문서를 파싱하고 AI로 문제 초안을 생성한 뒤, 팀이 검토해서 품질을 보장하는 파이프라인으로 운영합니다.

---

## 이 저장소를 처음 보는 분께

**읽는 순서:**

```
1. 이 README          ← 지금 여기
2. ARCHITECTURE.md    ← 전체 구조 파악 (필수)
3. AGENTS.md          ← AI 스크립트 역할 이해 (스크립트 작성 전)
4. docs/PLANS.md      ← 우리 팀이 어디쯤 와 있는지 확인
5. docs/QUALITY_SCORE.md ← 문제 리뷰할 때 기준
```

**기여하고 싶다면:**
- 문제 리뷰/승인만 할 경우 → 2, 5번만 읽으면 됩니다
- 스크립트 개발에 참여할 경우 → 1~5번 모두 + `docs/generated/db-schema.md`

---

## 사전 요구사항

시작하기 전에 아래가 설치되어 있어야 합니다.

| 항목 | 버전 | 확인 방법 |
|------|------|-----------|
| Python | 3.10 이상 | `python --version` |
| pip | 최신 권장 | `pip --version` |
| Git | 2.x 이상 | `git --version` |

> Windows 사용자는 WSL2 또는 Git Bash 환경을 권장합니다.

---

## 설치

```bash
# 1. 저장소 클론
git clone <repo-url>
cd <repo-name>

# 2. Python 패키지 설치
pip install -r requirements.txt

# 3. 환경변수 설정
cp .env.example .env
# .env 파일을 열어 ANTHROPIC_API_KEY 값을 입력하세요
# API 키 발급: https://console.anthropic.com/

# 4. 초기 디렉토리 생성
python scripts/setup.py
```

---

## 빠른 시작 — 문제 하나 만들어보기

설치가 완료됐다면, 아래 순서로 첫 문제를 만들 수 있습니다.

```bash
# Step 1: 공식 문서 파싱 (레퍼런스 파일 생성)
python scripts/parse-kakao-docs.py --chapter 01-cloud-fundamentals
# 결과: docs/references/cloud-fundamentals-llms.txt 생성

# Step 2: 문제 초안 생성 (최대 10개)
python scripts/generate-questions.py --chapter 01-cloud-fundamentals
# 결과: questions/01-cloud-fundamentals/q001.md ~ q010.md 생성 (status: draft)

# Step 3: 품질 점수 자동 계산
python scripts/validate-quality.py --chapter 01-cloud-fundamentals
# 결과: 각 문제에 quality_score 추가, 75점 미만은 status → review

# Step 4: 생성된 문제 확인
cat questions/01-cloud-fundamentals/q001.md

# Step 5: 마음에 들면 status를 active로 변경 (사람만 가능)
# q001.md 파일을 열어 status: draft → status: active 로 수정

# Step 6: 시험 세트 빌드
python scripts/build-exam.py --mode weekly --chapter 01-cloud-fundamentals
# 결과: exams/weekly/week-01.md 생성
```

> 처음 실행 시 Step 1에서 수 초~수십 초가 걸릴 수 있습니다.
> Step 2에서 Claude API를 호출하므로 `ANTHROPIC_API_KEY`가 반드시 설정되어 있어야 합니다.

---

## 디렉토리 구조 한눈에 보기

```
.
├── README.md               ← 지금 여기
├── ARCHITECTURE.md         ← 전체 시스템 설계
├── AGENTS.md               ← AI 스크립트 역할 정의
├── requirements.txt        ← Python 패키지 목록
├── .env.example            ← 환경변수 템플릿
│
├── scripts/                ← 자동화 스크립트 (Phase 1에서 작성)
├── questions/              ← 문제 파일 (챕터별 디렉토리)
├── exams/                  ← 생성된 시험 세트
├── docs/                   ← 설계 문서 모음
└── logs/                   ← 실행 로그 (Git 미추적)
```

자세한 구조는 [ARCHITECTURE.md](./ARCHITECTURE.md)를 참고하세요.

---

## 자주 묻는 질문

**Q. `python scripts/parse-kakao-docs.py` 실행 시 `ModuleNotFoundError`가 나요.**
→ `pip install -r requirements.txt`를 먼저 실행했는지 확인하세요.

**Q. `ANTHROPIC_API_KEY` 오류가 나요.**
→ `.env` 파일에 키가 정확히 입력됐는지 확인하세요. `sk-ant-` 로 시작해야 합니다.

**Q. 생성된 문제가 이상해요. (정답이 틀린 것 같아요)**
→ [docs/RELIABILITY.md](./docs/RELIABILITY.md)의 오류 신고 프로세스를 따라주세요.

**Q. 문제를 직접 작성하고 싶어요 (AI 없이).**
→ [ARCHITECTURE.md §5](./ARCHITECTURE.md)의 문제 파일 포맷을 보고
   `questions/{챕터}/q{번호}.md` 파일을 직접 만들면 됩니다.
   만든 뒤 `validate-quality.py`로 점수를 확인하세요.

**Q. 스터디에서 어떻게 사용하나요?**
→ [docs/PLANS.md §3](./docs/PLANS.md)의 주차별 운영 계획을 참고하세요.

---

## 기여 가이드

```
문제 추가/수정:  draft 브랜치 생성 → 작업 → PR (리뷰어 1인 이상)
문제 승인:       PR에서 status draft/review → active 로 변경
오류 신고:       GitHub Issue 생성 ([오류신고] q{NNN} — 내용)
문서 수정:       docs/ 하위 수정 → PR
```

---

## 관련 링크

- [카카오클라우드 공식 문서](https://docs.kakaocloud.com)
- [Anthropic API 키 발급](https://console.anthropic.com/)
- [문제 품질 기준](./docs/QUALITY_SCORE.md)
- [전체 로드맵](./docs/PLANS.md)
