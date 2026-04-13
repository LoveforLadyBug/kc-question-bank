# product-specs/05-container-pack.md
# 챕터 05 — Container Pack 출제 스펙

> 출제 근거 공식 문서:
> https://docs.kakaocloud.com/service/container
> https://kakaocloud.com/services

---

## 1. 챕터 개요

| 항목 | 내용 |
|------|------|
| chapter 값 | `05-container-pack` |
| 목표 문제 수 | 15문제 |
| 모의시험 출제 비중 | 10% (40문항 기준 4문제) |
| 레퍼런스 파일 | `docs/references/container-pack-llms.txt` |

### 이 챕터가 다루는 범위

Container Pack은 Kubernetes Engine(관리형 쿠버네티스)과
Container Registry(컨테이너 이미지 저장소)로 구성됩니다.
컨테이너·쿠버네티스 개념을 카카오클라우드 서비스 맥락에서 이해하는 것이 목표입니다.

---

## 2. 토픽별 출제 명세

### topic: `kubernetes-overview` — 관리형 쿠버네티스 개요

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 5문제 |
| 난이도 분포 | 1×2, 2×2, 3×1 |
| 핵심 개념 | 관리형 쿠버네티스 정의, VM 기반 배포와의 차이, VPC 기반 구성 |
| 출제 근거 URL | https://kakaocloud.com/services |

**반드시 포함할 팩트**
- Kubernetes Engine: VPC 기반 관리형 쿠버네티스 서비스
- 클러스터 생성·관리를 카카오클라우드가 담당 (컨트롤 플레인 관리)
- 사용자는 워크로드(Pod/Deployment) 관리에 집중

**출제 예시 방향**
```
난이도 1: "카카오클라우드 Container Pack에서 관리형 쿠버네티스를
           제공하는 서비스는?"
난이도 2: "관리형 쿠버네티스와 직접 설치형 쿠버네티스의 차이는?"
난이도 3: "마이크로서비스를 컨테이너로 배포하고 자동 확장이 필요할 때
           적합한 서비스는?"
```

---

### topic: `cluster` — 클러스터 구성

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 4문제 |
| 난이도 분포 | 2×1, 3×2, 4×1 |
| 핵심 개념 | 클러스터 생성, 노드 그룹, 다중 AZ 배치 |

**반드시 포함할 팩트**
- 클러스터는 VPC 내에 생성
- 노드는 BCS 인스턴스 기반
- 다중 AZ 배치로 고가용성 확보 가능

---

### topic: `container-registry` — Container Registry

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 3문제 |
| 난이도 분포 | 1×1, 2×1, 3×1 |
| 핵심 개념 | 컨테이너 이미지 저장소, 안전한 저장·신속한 배포 |

**반드시 포함할 팩트**
- 컨테이너 이미지를 안전하게 저장하고 신속하게 배포
- Kubernetes Engine과 연동하여 이미지 pull 가능

---

### topic: `node-group` — 노드 그룹

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 3문제 |
| 난이도 분포 | 2×1, 3×1, 4×1 |
| 핵심 개념 | 노드 그룹 정의, 인스턴스 유형 지정, 오토스케일링 |

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
| Kubernetes Engine vs VM 배포 | 관리 주체 차이 혼동 |
| Container Registry vs Object Storage | 이미지 저장 vs 일반 파일 저장 혼동 |
| 노드 vs 파드(Pod) | 인프라 레이어 혼동 |

---

## 5. 관련 문서

- [`docs/references/container-pack-llms.txt`](../references/container-pack-llms.txt)
- [`questions/05-container-pack/_index.md`](../../questions/05-container-pack/_index.md)
