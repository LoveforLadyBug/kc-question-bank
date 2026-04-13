# product-specs/03-bns.md
# 챕터 03 — Beyond Networking Service (BNS) 출제 스펙

> 출제 근거 공식 문서:
> https://docs.kakaocloud.com/en/service/bns/bns-ov
> https://kakaocloud.com/services/load-balancing/intro

---

## 1. 챕터 개요

| 항목 | 내용 |
|------|------|
| chapter 값 | `03-bns` |
| 목표 문제 수 | 30문제 |
| 모의시험 출제 비중 | 20% (40문항 기준 8문제) |
| 레퍼런스 파일 | `docs/references/bns-llms.txt` |

### 이 챕터가 다루는 범위

BNS는 VPC, Load Balancing, DNS, Transit Gateway, Direct Connect 등
네트워크 관련 필수 서비스를 포함합니다.
클라우드 네트워크 설계의 기본이 되는 챕터로, 출제 비중이 가장 높습니다.

---

## 2. 토픽별 출제 명세

### topic: `vpc` — VPC (Virtual Private Cloud)

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 7문제 |
| 난이도 분포 | 1×2, 2×2, 3×2, 4×1 |
| 핵심 개념 | VPC 정의, 논리적 격리, 리전 단위 생성, 무료 서비스 |
| 출제 근거 URL | https://docs.kakaocloud.com/en/service/bns/bns-ov |

**반드시 포함할 팩트**
- VPC는 논리적으로 격리된 가상 네트워크 공간
- VPC는 무료 서비스
- VPC 내에서 Subnet, Route Table, Security Group 구성
- 리소스는 VPC 기반으로 생성·관리됨

**출제 예시 방향**
```
난이도 1: "카카오클라우드에서 논리적으로 격리된 가상 네트워크 공간을
           제공하는 서비스는?"
난이도 2: "VPC를 사용하는 주요 이유로 올바른 것은?"
난이도 3: "외부 인터넷과 차단된 내부 전용 네트워크를 구성하려 할 때
           첫 번째로 생성해야 하는 리소스는?"
난이도 4: "두 개의 VPC에 배치된 서비스가 서로 통신해야 할 때
           사용할 수 있는 서비스는?"
```

---

### topic: `subnet` — 서브넷

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 5문제 |
| 난이도 분포 | 1×1, 2×2, 3×2 |
| 핵심 개념 | 서브넷 정의, VPC 내 IP 범위 분할, Public/Private Subnet 구분 |
| 출제 근거 URL | https://docs.kakaocloud.com/en/service/bns/bns-ov |

**반드시 포함할 팩트**
- 서브넷은 VPC 내에서 CIDR로 IP 범위를 분할한 단위
- AZ 단위로 서브넷 배치 가능
- 인스턴스 생성 시 리전 → VPC → 서브넷(AZ) 순으로 선택

---

### topic: `security-group` — 보안 그룹

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 4문제 |
| 난이도 분포 | 2×2, 3×2 |
| 핵심 개념 | 인바운드/아웃바운드 규칙, IP/포트 기반 패킷 필터링 |
| 출제 근거 URL | https://docs.kakaocloud.com/en/service/bcs/vm/vm-overview |

**반드시 포함할 팩트**
- 보안 그룹: IP 주소 및 포트 번호 기반 패킷 필터링
- 인스턴스 레벨에서 동작 (서브넷 레벨 아님)
- 인바운드(수신): 외부 → 인스턴스 / 아웃바운드(발신): 인스턴스 → 외부

---

### topic: `load-balancer` — Load Balancer

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 7문제 |
| 난이도 분포 | 1×1, 2×2, 3×3, 4×1 |
| 핵심 개념 | LB 타입(ALB/NLB/DSRNLB), 트래픽 분산, 헬스 체크 |
| 출제 근거 URL | https://kakaocloud.com/services/load-balancing/intro |

**LB 타입별 특징 (오답 설계 핵심)**

| 타입 | 프로토콜 | 특징 |
|------|---------|------|
| ALB (Application LB) | HTTP/HTTPS | URL 기반 분기, SSL 처리 |
| NLB (Network LB) | TCP | 고성능 L4 트래픽 처리 |
| DSRNLB (Direct Server Return NLB) | TCP | 서버가 클라이언트에 직접 응답 |

**반드시 포함할 팩트**
- 헬스 체크로 장애 서버 자동 제외 → 무중단 서비스
- 액세스 로그 및 모니터링 대시보드 제공
- HTTPS 트래픽 암호화/복호화(SSL Termination)는 ALB가 처리

**출제 예시 방향**
```
난이도 1: "Load Balancer의 주요 역할로 올바른 것은?"
난이도 2: "HTTP/HTTPS 기반 웹 서비스에서 URL 경로별로 다른 서버로
           트래픽을 분산하려 할 때 적합한 LB 타입은?"
난이도 3: "헬스 체크 기능이 서비스 가용성에 기여하는 방식은?"
난이도 4: "대용량 TCP 트래픽을 처리하되 서버가 클라이언트에 직접
           응답해야 하는 경우 적합한 LB 타입은?"
```

---

### topic: `dns` — DNS

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 3문제 |
| 난이도 분포 | 1×1, 2×1, 3×1 |
| 핵심 개념 | DNS 역할, 도메인 관리, 웹사이트 속도·가용성 |
| 출제 근거 URL | https://kakaocloud.com/services |

---

### topic: `transit-gateway` — Transit Gateway

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 4문제 |
| 난이도 분포 | 2×1, 3×1, 4×2 |
| 핵심 개념 | TGW 정의, VPC 간 연결, 온프레미스 연결, 확장성 |
| 출제 근거 URL | https://docs.kakaocloud.com/en/service/bns/bns-ov |

**반드시 포함할 팩트**
- Transit Gateway: VPC와 온프레미스 네트워크를 통합 연결·관리
- 다수의 AZ/VPC 간 복잡한 연결을 단순화
- 클릭 몇 번으로 성능 저하 없이 유연한 연결 구성 가능

---

## 3. 전체 난이도 분포 목표

| 난이도 | 목표 문제 수 | 비율 |
|--------|------------|------|
| 1 | 6문제 | 20% |
| 2 | 8문제 | 27% |
| 3 | 11문제 | 37% |
| 4 | 4문제 | 13% |
| 5 | 1문제 | 3% |

---

## 4. 챕터 특화 오답 설계 원칙

| 혼동 포인트 | 오답 활용 방법 |
|-------------|--------------|
| VPC vs Subnet | 격리 단위 혼동 유도 |
| ALB vs NLB | 프로토콜 레이어 혼동 유도 |
| 보안 그룹 vs 네트워크 ACL | 적용 레벨(인스턴스 vs 서브넷) 혼동 |
| Transit Gateway vs Direct Connect | 연결 대상(VPC 간 vs 전용선) 혼동 |

---

## 5. 관련 문서

- [`docs/references/bns-llms.txt`](../references/bns-llms.txt)
- [`questions/03-bns/_index.md`](../../questions/03-bns/_index.md)
