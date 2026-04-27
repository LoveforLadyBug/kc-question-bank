# question-taxonomy.md
# KakaoCloud Essential Basic Course — 문제 분류 체계

> 이 문서는 문제은행 전체의 분류 기준을 정의합니다.
> `generate-questions.py` 가 문제 생성 시 태그와 챕터를 자동 부여할 때,
> 그리고 `build-exam.py` 가 시험 세트를 조립할 때 이 문서를 참조합니다.
>
> **v2 개정 (2026-04-27)**: 공식 시험 블루프린트 기준으로 챕터 체계 전면 개편.
> 서비스 기반(bcs/bns/bss/...) → 평가 영역 기반(7개 도메인)으로 전환.

---

## 1. 분류 3축

모든 문제는 아래 3축의 교차점에 위치합니다.

```
평가 영역 (chapter)   ×   난이도 (difficulty 1~3)   ×   인지 유형 (cognitive type)
```

> **난이도 스케일 변경**: 기존 1~5에서 공식 시험 배점 기준인 1~3으로 변경.
> 1점 = 기본 개념/정의, 2점 = 기능/비교 이해, 3점 = 응용/설계/복합

---

## 2. 평가 영역 분류 (공식 시험 블루프린트)

| chapter 값 | 평가 영역 | 문항 수 | 배점 | 비율 | 난이도 분포 |
|------------|---------|--------|------|------|------------|
| `01-cloud-overview` | 클라우드 개요·기본 개념 | 13 | 22점 | 22% | 1점×6 / 2점×5 / 3점×2 |
| `02-kakao-services` | 카카오클라우드 서비스 이해 | 16 | 25점 | 25% | 1점×8 / 2점×7 / 3점×1 |
| `03-billing` | 비용 및 요금 | 8 | 13점 | 13% | 1점×4 / 2점×3 / 3점×1 |
| `04-security` | 보안 및 권한 | 9 | 15점 | 15% | 1점×4 / 2점×4 / 3점×1 |
| `05-operations` | 운영·모니터링 | 6 | 10점 | 10% | 1점×3 / 2점×2 / 3점×1 |
| `06-account` | 계정 관리 | 3 | 6점 | 6% | 1점×1 / 2점×1 / 3점×1 |
| `07-complex` | 기타·복합 영역 | 5 | 9점 | 9% | 1점×2 / 2점×2 / 3점×1 |
| **합계** | | **60** | **100점** | **100%** | **1점×28 / 2점×24 / 3점×8** |

### 02-kakao-services 서비스별 서브 폴더

`02-kakao-services` 는 서비스 다양성 때문에 하위 폴더로 세분화합니다.
`build-exam.py` 는 `02-kakao-services/**` 를 모두 수집해 16문항을 구성합니다.

| 서브 폴더 | 서비스 | 공식 문서 경로 |
|----------|--------|--------------|
| `bcs` | Beyond Compute Service (VM, GPU, Bare Metal) | `/service/bcs` |
| `bns` | Beyond Networking Service (VPC, LB, DNS) | `/service/bns` |
| `bss` | Beyond Storage Service (Block, Object, File) | `/service/bss` |
| `container-pack` | Container Pack (Kubernetes, Registry) | `/service/container` |
| `data-store` | Data Store (MySQL, PostgreSQL, Redis, MongoDB) | `/service/datastore` |

### 평가 영역별 목표 문제 풀 크기

시험 1회분 대비 최소 3배 이상의 문제 풀을 확보해야 출제 다양성이 보장됩니다.

| chapter | 시험 출제 수 | 목표 풀 크기 |
|---------|------------|------------|
| 01-cloud-overview | 13 | 40문제 이상 |
| 02-kakao-services (전체) | 16 | 50문제 이상 |
| 03-billing | 8 | 25문제 이상 |
| 04-security | 9 | 27문제 이상 |
| 05-operations | 6 | 18문제 이상 |
| 06-account | 3 | 10문제 이상 |
| 07-complex | 5 | 15문제 이상 |

---

## 3. 인지 유형 분류

`tags` 필드에 인지 유형 태그를 반드시 1개 이상 포함합니다.

| 태그 | 정의 | 난이도 연관 |
|------|------|-----------|
| `definition` | 용어·개념의 정의를 묻는 문제 | 주로 1점 |
| `feature` | 서비스의 주요 기능·특징을 묻는 문제 | 주로 1~2점 |
| `comparison` | 두 서비스/개념의 차이를 묻는 문제 | 주로 2점 |
| `usecase` | 언제/왜 이 서비스를 쓰는지 묻는 문제 | 주로 2점 |
| `architecture` | 여러 서비스 조합의 최적 구성을 묻는 문제 | 주로 3점 |
| `constraint` | 제한사항·한계·비용 조건을 묻는 문제 | 주로 2~3점 |

---

## 4. 평가 영역별 세부 토픽 목록

`topic` 필드에 사용할 수 있는 값의 기준표입니다.

### 01-cloud-overview

| topic | 설명 |
|-------|------|
| `cloud-model` | IaaS / PaaS / SaaS 구분 |
| `deployment-model` | Public / Private / Hybrid 클라우드 |
| `region-az` | 리전과 가용 영역(AZ) 개념 |
| `kakaocloud-overview` | KakaoCloud 서비스 전체 개요, 포지셔닝 |
| `shared-responsibility` | 클라우드 공동 책임 모델 |

### 02-kakao-services / bcs

| topic | 설명 |
|-------|------|
| `vm-overview` | Virtual Machine 개요 및 특징 |
| `instance-type` | 범용/컴퓨팅/메모리/GPU 인스턴스 분류 |
| `image` | 인스턴스 이미지 (OS, 커스텀) |
| `public-ip` | 공인 IP 개념 및 할당 |
| `bare-metal` | Bare Metal Server 특징 및 용도 |
| `gpu` | GPU 인스턴스 용도 및 특징 |

### 02-kakao-services / bns

| topic | 설명 |
|-------|------|
| `vpc` | VPC 개념, 격리, 생성 |
| `subnet` | Subnet 구성 및 CIDR |
| `security-group` | 보안 그룹 인바운드/아웃바운드 |
| `load-balancer` | LB 타입 및 트래픽 분산 |
| `dns` | DNS 도메인 관리 |
| `transit-gateway` | VPC 간 연결, 온프레미스 연결 |

### 02-kakao-services / bss

| topic | 설명 |
|-------|------|
| `block-storage` | Block Storage 특징, 용도 |
| `object-storage` | Object Storage, S3 호환 |
| `file-storage` | 공유 파일 스토리지 |
| `storage-comparison` | 세 스토리지 유형 비교 |
| `backup` | 스냅샷, 백업 정책 |

### 02-kakao-services / container-pack

| topic | 설명 |
|-------|------|
| `kubernetes-overview` | 관리형 쿠버네티스 개요 |
| `cluster` | 클러스터 생성 및 구성 |
| `container-registry` | 컨테이너 이미지 저장소 |
| `node-group` | 노드 그룹 구성 |

### 02-kakao-services / data-store

| topic | 설명 |
|-------|------|
| `mysql` | 관리형 MySQL |
| `postgresql` | 관리형 PostgreSQL |
| `redis` | 관리형 Redis (인메모리) |
| `mongodb` | 관리형 MongoDB |
| `db-comparison` | RDBMS vs NoSQL 비교 |
| `ha-backup` | 고가용성, 자동 백업 |

### 03-billing

| topic | 설명 |
|-------|------|
| `pricing-model` | 종량제, 약정 할인, 크레딧 개념 |
| `service-pricing` | 서비스별 과금 단위 (VM, 스토리지 등) |
| `cost-optimization` | 비용 절감 전략, Reserved vs On-demand |
| `billing-management` | 청구서, 예산 알림, 비용 모니터링 |

### 04-security

| topic | 설명 |
|-------|------|
| `iam-policy` | 정책 설정, 최소 권한 원칙 |
| `network-security` | 보안 그룹, ACL, VPC 격리 |
| `data-encryption` | 저장/전송 데이터 암호화 |
| `compliance` | 규정 준수, 감사 로그 |

### 05-operations

| topic | 설명 |
|-------|------|
| `monitoring` | 메트릭 수집, 대시보드, 경보 |
| `logging` | 활동 로그, 감사 추적 |
| `notification` | 알림 채널 및 조건 설정 |
| `troubleshooting` | 장애 대응, 리소스 상태 확인 |

### 06-account

| topic | 설명 |
|-------|------|
| `iam-overview` | IAM 개요, 사용자/그룹/역할 구조 |
| `account-management` | 계정 생성, 프로젝트, 조직 구조 |
| `mfa` | 다단계 인증 설정 |

### 07-complex

| topic | 설명 |
|-------|------|
| `multi-service` | 복수 서비스를 조합하는 아키텍처 문제 |
| `scenario` | 실제 업무 시나리오 기반 최적 선택 |
| `migration` | 온프레미스 → 클라우드 마이그레이션 |

---

## 5. 태그 조합 규칙

```yaml
# 올바른 태그 예시
tags: [vpc, definition, usecase]
#      ↑서비스  ↑인지유형  ↑인지유형(복수 가능)

# 잘못된 태그 예시
tags: [네트워크]          # 한글 태그 사용 금지
tags: []                  # 빈 태그 금지 (validator가 감점)
tags: [vpc, subnet, load-balancer, dns, transit-gateway, definition, feature, comparison]
#     너무 많은 태그 → 하나의 문제가 너무 많은 개념을 다루고 있다는 신호
```

**태그 수 권장**: 서비스 태그 1~2개 + 인지 유형 태그 1~2개 = 총 2~4개

---

## 6. 챕터 커버리지 추적

각 챕터 디렉토리의 `_index.md` 에서 아래 형식으로 커버리지를 관리합니다.

```markdown
# _index.md — 04-security 챕터

| topic | 목표 문제 수 | 현재 active | 난이도 분포 |
|-------|------------|------------|------------|
| iam-policy | 10 | 0 | — |
| network-security | 8 | 0 | — |
| data-encryption | 5 | 0 | — |
| compliance | 4 | 0 | — |

정답 분포 (A/B/C/D): 0/0/0/0  ← 편향 모니터링
```

---

## 7. 관련 문서

- [`core-beliefs.md`](./core-beliefs.md) — 분류 체계의 철학적 근거
- [`difficulty-rubric.md`](./difficulty-rubric.md) — 난이도 1~3 판단 실전 기준
- [`ARCHITECTURE.md`](../ARCHITECTURE.md) — 전체 시스템 구조
