# product-specs/07-management-iam.md
# 챕터 07 — Management & IAM 출제 스펙

> 출제 근거 공식 문서:
> https://kakaocloud.com/pricing/overview
> https://kakaocloud.com/services

---

## 1. 챕터 개요

| 항목 | 내용 |
|------|------|
| chapter 값 | `07-management-iam` |
| 목표 문제 수 | 15문제 |
| 모의시험 출제 비중 | 10% (40문항 기준 4문제) |
| 레퍼런스 파일 | `docs/references/management-llms.txt`, `docs/references/iam-security-llms.txt` |

### 이 챕터가 다루는 범위

IAM(권한 관리), Monitoring(모니터링), Logging(로깅), Notification(알림) 등
인프라 운영·관리에 필요한 서비스를 다룹니다.
IAM은 무료 서비스이며, 최소 권한 원칙이 핵심 개념입니다.

---

## 2. 토픽별 출제 명세

### topic: `iam-overview` — IAM 개요

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 5문제 |
| 난이도 분포 | 1×2, 2×2, 3×1 |
| 핵심 개념 | IAM 정의, 사용자/역할/정책, RBAC, 무료 서비스 |
| 출제 근거 URL | https://kakaocloud.com/pricing/overview |

**반드시 포함할 팩트**
- IAM: 카카오클라우드 리소스 접근 권한을 중앙에서 관리하는 서비스
- IAM은 무료 서비스
- RBAC(Role-Based Access Control) 기반
- 역할(Role): Project Admin / Project Member 등
- 사용자·그룹에 역할을 부여하여 권한 관리

**출제 예시 방향**
```
난이도 1: "카카오클라우드에서 사용자의 리소스 접근 권한을 중앙에서
           관리하는 서비스는?"
난이도 2: "IAM의 RBAC 모델에서 권한을 정의하는 단위는?"
난이도 3: "팀원에게 특정 프로젝트의 VM만 조회하도록 허용하려 할 때
           올바른 IAM 설정 방법은?"
```

---

### topic: `iam-policy` — IAM 정책 및 최소 권한 원칙

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 3문제 |
| 난이도 분포 | 2×1, 3×1, 4×1 |
| 핵심 개념 | 최소 권한 원칙(Principle of Least Privilege), 정책 설정 |

**반드시 포함할 팩트**
- 최소 권한 원칙: 업무 수행에 필요한 최소한의 권한만 부여
- 과도한 권한 부여는 보안 위협의 원인

---

### topic: `monitoring` — 모니터링

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 3문제 |
| 난이도 분포 | 1×1, 2×1, 3×1 |
| 핵심 개념 | 메트릭 수집·저장·분석, 실시간 대시보드, 관리형 모니터링 |
| 출제 근거 URL | https://kakaocloud.com/pricing/overview |

**반드시 포함할 팩트**
- 인프라·애플리케이션 성능을 실시간 모니터링
- 메트릭 데이터 수집·저장·분석 제공
- 관리형 모니터링 서비스(Prometheus 호환 등)

---

### topic: `logging` — 로깅

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 2문제 |
| 난이도 분포 | 2×1, 3×1 |
| 핵심 개념 | 사용자 활동 로그, 감사(Audit) 추적, 자동 수집·기록 |
| 출제 근거 URL | https://kakaocloud.com/pricing/overview |

**반드시 포함할 팩트**
- 로그인, 리소스 생성·변경·삭제 등 사용자 활동을 자동으로 수집·기록
- 무료 서비스
- 보안 감사 및 규정 준수에 활용

---

### topic: `notification` — 알림

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 2문제 |
| 난이도 분포 | 2×1, 3×1 |
| 핵심 개념 | 알림 조건 설정, 수신 채널, 장애 감지 |

**반드시 포함할 팩트**
- 다양한 알림 조건과 수신 채널 제공
- 장애를 신속하게 파악·대응하기 위한 서비스

---

## 3. 전체 난이도 분포 목표

| 난이도 | 목표 문제 수 | 비율 |
|--------|------------|------|
| 1 | 4문제 | 27% |
| 2 | 5문제 | 33% |
| 3 | 4문제 | 27% |
| 4 | 2문제 | 13% |

---

## 4. 챕터 특화 오답 설계 원칙

| 혼동 포인트 | 오답 활용 방법 |
|-------------|--------------|
| IAM 무료 여부 | 유료로 혼동 유도 |
| 모니터링 vs 로깅 | 실시간 성능 vs 이력 기록 혼동 |
| 최소 권한 원칙 | "모든 권한 부여가 편하다"는 반례 오답 활용 |
| RBAC 역할 단위 | 사용자 vs 역할 vs 정책 혼동 |

---

## 5. 관련 문서

- [`docs/references/management-llms.txt`](../references/management-llms.txt)
- [`docs/references/iam-security-llms.txt`](../references/iam-security-llms.txt)
- [`questions/07-management-iam/_index.md`](../../questions/07-management-iam/_index.md)
