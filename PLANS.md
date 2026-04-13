# PLANS.md
# KakaoCloud Essential Basic Course — 전체 로드맵

> 이 문서는 문제은행 프로젝트의 전체 실행 계획과 마일스톤을 정의합니다.
> 진행 상황은 `docs/exec-plans/` 하위 문서에서 관리합니다.

---

## 1. 프로젝트 페이즈 개요

```
Phase 1 │ 기반 구축        │ 파이프라인 완성 + 첫 챕터 검증
Phase 2 │ 문제은행 확장    │ 전 챕터 문제 목표치 달성
Phase 3 │ 스터디 운영      │ 주차별 + 모의시험 실전 운영
Phase 4 │ 고도화 (선택)    │ 웹 UI + 약점 분석 대시보드
```

---

## 2. Phase 1 — 기반 구축

**목표**: 파이프라인이 실제로 돌아가는지 검증. 1개 챕터에서 완전한 흐름 확인.

| 주차 | 작업 | 산출물 | 담당 |
|------|------|--------|------|
| 1주차 | 핵심 문서 완성 확인 | ARCHITECTURE, AGENTS, QUALITY_SCORE, design-docs 전체 | — |
| 2주차 | `parse-kakao-docs.py` 작성 및 실행 | `docs/references/cloud-fundamentals-llms.txt` | — |
| 3주차 | `generate-questions.py` 작성 및 실행 | `questions/01-cloud-fundamentals/` q001~q010 (draft) | — |
| 3주차 | `validate-quality.py` 작성 및 실행 | `quality_score` 자동 계산 확인 | — |
| 4주차 | 팀 리뷰: q001~q010 검토 | active 승격 + `_review-notes.md` 작성 | 전체 |
| 4주차 | `build-exam.py` 작성 및 첫 시험 세트 생성 | `exams/weekly/week-01.md` | — |

**Phase 1 완료 기준**
- `01-cloud-fundamentals` 챕터에 active 문제 10개 이상
- 파이프라인 5단계(parse → generate → validate → 리뷰 → build) 1회 완전 순환
- `exams/weekly/week-01.md` 실제 스터디에서 사용 완료

---

## 3. Phase 2 — 문제은행 확장

**목표**: 7개 챕터 전체 목표 문제 수(145문제) 달성.

| 챕터 | 목표 문제 수 | 우선순위 | 예상 소요 |
|------|------------|---------|---------|
| 01-cloud-fundamentals | 20문제 | ★★★ (Phase 1에서 완성) | 완료 |
| 02-bcs | 30문제 | ★★★ | 2주 |
| 03-bns | 30문제 | ★★★ | 2주 |
| 04-bss | 20문제 | ★★☆ | 1주 |
| 05-container-pack | 15문제 | ★★☆ | 1주 |
| 06-data-store | 15문제 | ★☆☆ | 1주 |
| 07-management-iam | 15문제 | ★☆☆ | 1주 |

**Phase 2 완료 기준**
- 전 챕터 active 문제 수가 목표치의 80% 이상 (116문제+)
- `tech-debt-tracker.md` 운영 시작 (오답률 높은 문제 추적)
- 첫 모의시험 세트(`exams/mock-exam-01.md`) 생성 및 팀 시험 완료

---

## 4. Phase 3 — 스터디 운영

**목표**: 문제은행을 실제 스터디에 안정적으로 활용.

### 주차별 스터디 운영 계획

| 주차 | 챕터 | 문제 수 | 모드 |
|------|------|---------|------|
| Week 01 | 01-cloud-fundamentals | 10문제 | 주차별 |
| Week 02 | 02-bcs (기초) | 10문제 | 주차별 |
| Week 03 | 02-bcs (심화) + 03-bns (기초) | 10문제 | 주차별 |
| Week 04 | 03-bns (심화) | 10문제 | 주차별 |
| Week 05 | 04-bss | 10문제 | 주차별 |
| Week 06 | 05 + 06 + 07 | 10문제 | 주차별 |
| Week 07 | 전 챕터 약점 보완 | 가변 | 태그 기반 랜덤 |
| Week 08 | **모의시험 1회** | 40문제 | 모의시험 |

### 모의시험 운영 원칙

- 40문항, 챕터별 비중은 `question-taxonomy.md` §2 기준
- 난이도 분포: 1~2 (40%) / 3 (35%) / 4~5 (25%)
- 결과 리뷰: 오답 문제 해설 함께 논의
- 오답률 60% 이상 문제 → `tech-debt-tracker.md` 에 기록

**Phase 3 완료 기준**
- 8주 스터디 완주
- 모의시험 팀 평균 점수 75점 이상
- 실제 KakaoCloud Essential 시험 응시 및 결과 회고 완료

---

## 5. Phase 4 — 고도화 (선택)

팀 합의 후 진행. Phase 3 완료 후 필요성 판단.

| 항목 | 내용 | 조건 |
|------|------|------|
| 웹 퀴즈 UI | `FRONTEND.md` 기반 인터랙티브 퀴즈 | Phase 3 완료 + 팀 합의 |
| 약점 분석 대시보드 | 오답 통계 시각화 | 웹 UI 완성 후 |
| 문제 자동 갱신 | 공식 문서 변경 감지 + 재생성 파이프라인 | v2.0 이후 |

---

## 6. 현재 상태 트래커

> 이 섹션은 매주 업데이트합니다.

| 항목 | 상태 | 비고 |
|------|------|------|
| 핵심 문서 완성 | ✅ 완료 | ARCHITECTURE, AGENTS, QUALITY_SCORE, design-docs, product-specs |
| 스크립트 작성 | ⬜ 미시작 | Phase 1 2주차 |
| 첫 문제 생성 | ⬜ 미시작 | Phase 1 3주차 |
| 첫 스터디 세트 | ⬜ 미시작 | Phase 1 4주차 |
| 전 챕터 문제 완성 | ⬜ 미시작 | Phase 2 |
| 첫 모의시험 | ⬜ 미시작 | Phase 3 |

---

## 7. 관련 문서

- [`ARCHITECTURE.md`](../ARCHITECTURE.md) — 전체 시스템 구조
- [`docs/exec-plans/active/`](./exec-plans/active/) — 현재 진행 중인 주차 계획
- [`docs/exec-plans/tech-debt-tracker.md`](./exec-plans/tech-debt-tracker.md) — 오답률 높은 문제 추적
- [`docs/design-docs/question-taxonomy.md`](./design-docs/question-taxonomy.md) — 챕터별 목표 문제 수
