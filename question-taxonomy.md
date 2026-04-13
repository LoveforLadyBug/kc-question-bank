# question-taxonomy.md
# KakaoCloud Essential Basic Course — 문제 분류 체계

> 이 문서는 문제은행 전체의 분류 기준을 정의합니다.
> `generate-questions.py` 가 문제 생성 시 태그와 챕터를 자동 부여할 때,
> 그리고 `build-exam.py` 가 시험 세트를 조립할 때 이 문서를 참조합니다.

---

## 1. 분류 3축

모든 문제는 아래 3축의 교차점에 위치합니다.

```
챕터 (chapter)   ×   난이도 (difficulty 1~5)   ×   인지 유형 (cognitive type)
```

---

## 2. 챕터 분류

| chapter 값 | 이름 | 핵심 서비스 | 공식 문서 경로 |
|------------|------|------------|---------------|
| `01-cloud-fundamentals` | 클라우드 기초 | IaaS/PaaS/SaaS, 리전, AZ, 과금 모델 | `/intro` |
| `02-bcs` | Beyond Compute Service | Virtual Machine, GPU, Bare Metal Server | `/service/bcs` |
| `03-bns` | Beyond Networking Service | VPC, Subnet, Load Balancer, DNS, Transit Gateway | `/service/bns` |
| `04-bss` | Beyond Storage Service | Block Storage, Object Storage, File Storage | `/service/bss` |
| `05-container-pack` | Container Pack | Kubernetes Engine, Container Registry | `/service/container` |
| `06-data-store` | Data Store | MySQL, PostgreSQL, Redis, MongoDB | `/service/datastore` |
| `07-management-iam` | Management & IAM | IAM, Monitoring, Logging, Notification | `/service/management` |

### 챕터별 목표 문제 수 및 출제 비중

| 챕터 | 목표 문제 수 | 모의시험 출제 비중 |
|------|------------|-----------------|
| 01-cloud-fundamentals | 20문제 | 15% (6문제/40문항 기준) |
| 02-bcs | 30문제 | 20% (8문제) |
| 03-bns | 30문제 | 20% (8문제) |
| 04-bss | 20문제 | 15% (6문제) |
| 05-container-pack | 15문제 | 10% (4문제) |
| 06-data-store | 15문제 | 10% (4문제) |
| 07-management-iam | 15문제 | 10% (4문제) |
| **합계** | **145문제** | **100% (40문제)** |

---

## 3. 인지 유형 분류

`tags` 필드에 인지 유형 태그를 반드시 1개 이상 포함합니다.

| 태그 | 정의 | 난이도 연관 |
|------|------|-----------|
| `definition` | 용어·개념의 정의를 묻는 문제 | 주로 1~2 |
| `feature` | 서비스의 주요 기능·특징을 묻는 문제 | 주로 2~3 |
| `comparison` | 두 서비스/개념의 차이를 묻는 문제 | 주로 2~3 |
| `usecase` | 언제/왜 이 서비스를 쓰는지 묻는 문제 | 주로 3~4 |
| `architecture` | 여러 서비스 조합의 최적 구성을 묻는 문제 | 주로 4~5 |
| `constraint` | 제한사항·한계·비용 조건을 묻는 문제 | 주로 4~5 |

---

## 4. 서비스별 세부 토픽 목록

`topic` 필드에 사용할 수 있는 값의 기준표입니다.
`product-specs/*.md` 에서 챕터별로 상세히 정의되며, 여기서는 전체 목록을 관리합니다.

### 01-cloud-fundamentals

| topic | 설명 |
|-------|------|
| `cloud-model` | IaaS / PaaS / SaaS 구분 |
| `deployment-model` | Public / Private / Hybrid 클라우드 |
| `region-az` | 리전과 가용 영역(AZ) 개념 |
| `pricing-model` | 종량제, 약정 할인, 크레딧 |
| `shared-responsibility` | 클라우드 공동 책임 모델 |

### 02-bcs

| topic | 설명 |
|-------|------|
| `vm-overview` | Virtual Machine 개요 및 특징 |
| `instance-type` | 범용/컴퓨팅/메모리/GPU 인스턴스 분류 |
| `image` | 인스턴스 이미지 (OS, 커스텀) |
| `public-ip` | 공인 IP 개념 및 할당 |
| `bare-metal` | Bare Metal Server 특징 및 용도 |
| `gpu` | GPU 인스턴스 용도 및 특징 |
| `storage-attachment` | BCS에 BSS 연결 방식 |

### 03-bns

| topic | 설명 |
|-------|------|
| `vpc` | VPC 개념, 격리, 생성 |
| `subnet` | Subnet 구성 및 CIDR |
| `security-group` | 보안 그룹 인바운드/아웃바운드 |
| `load-balancer` | LB 타입 및 트래픽 분산 |
| `dns` | DNS 도메인 관리 |
| `transit-gateway` | VPC 간 연결, 온프레미스 연결 |
| `direct-connect` | 전용 네트워크 연결 |

### 04-bss

| topic | 설명 |
|-------|------|
| `block-storage` | Block Storage 특징, 용도 |
| `object-storage` | Object Storage, S3 호환 |
| `file-storage` | 공유 파일 스토리지 |
| `storage-comparison` | 세 스토리지 유형 비교 |
| `backup` | 스냅샷, 백업 정책 |

### 05-container-pack

| topic | 설명 |
|-------|------|
| `kubernetes-overview` | 관리형 쿠버네티스 개요 |
| `cluster` | 클러스터 생성 및 구성 |
| `container-registry` | 컨테이너 이미지 저장소 |
| `node-group` | 노드 그룹 구성 |

### 06-data-store

| topic | 설명 |
|-------|------|
| `mysql` | 관리형 MySQL |
| `postgresql` | 관리형 PostgreSQL |
| `redis` | 관리형 Redis (인메모리) |
| `mongodb` | 관리형 MongoDB |
| `db-comparison` | RDBMS vs NoSQL 비교 |
| `ha-backup` | 고가용성, 자동 백업 |

### 07-management-iam

| topic | 설명 |
|-------|------|
| `iam-overview` | IAM 개요, 사용자/역할 |
| `iam-policy` | 정책 설정, 최소 권한 원칙 |
| `monitoring` | 메트릭 수집, 대시보드 |
| `logging` | 활동 로그, 감사 추적 |
| `notification` | 알림 채널 및 조건 |

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
# _index.md — 02-bcs 챕터

| topic | 목표 문제 수 | 현재 active | 난이도 분포 |
|-------|------------|------------|------------|
| vm-overview | 4 | 3 | 1×1, 2×1, 3×1 |
| instance-type | 4 | 4 | 1×1, 2×2, 3×1 |
| image | 3 | 2 | 1×1, 2×1 |
| public-ip | 3 | 0 | — |
| ...  | | | |

정답 분포 (A/B/C/D): 3/2/4/3  ← 편향 모니터링
```

---

## 7. 관련 문서

- [`core-beliefs.md`](./core-beliefs.md) — 분류 체계의 철학적 근거
- [`difficulty-rubric.md`](./difficulty-rubric.md) — 난이도 1~5 판단 실전 기준
- [`../product-specs/`](../product-specs/) — 챕터별 상세 출제 스펙
