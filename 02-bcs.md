# product-specs/02-bcs.md
# 챕터 02 — Beyond Compute Service (BCS) 출제 스펙

> 출제 근거 공식 문서:
> https://docs.kakaocloud.com/service/bcs/bcs-ov
> https://docs.kakaocloud.com/service/bcs/bcs-instance/bcs-instance-overview
> https://docs.kakaocloud.com/en/service/bcs/vm/vm-overview

---

## 1. 챕터 개요

| 항목 | 내용 |
|------|------|
| chapter 값 | `02-bcs` |
| 목표 문제 수 | 30문제 |
| 모의시험 출제 비중 | 20% (40문항 기준 8문제) |
| 레퍼런스 파일 | `docs/references/bcs-llms.txt` |

### 이 챕터가 다루는 범위

BCS는 VM(Virtual Machine), Bare Metal Server, GPU 세 가지 하위 서비스로 구성된
카카오클라우드의 핵심 컴퓨팅 서비스 그룹입니다.
물리 인프라 없이 필요한 만큼 가상 서버를 생성·사용하는 개념과 각 서비스의 특징,
인스턴스 유형 선택 기준을 다룹니다.

---

## 2. 토픽별 출제 명세

### topic: `vm-overview` — Virtual Machine 개요

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 5문제 |
| 난이도 분포 | 1×2, 2×2, 3×1 |
| 핵심 개념 | VM 정의, 하이퍼바이저 기반 가상화, Scale-up vs Scale-out |
| 출제 근거 URL | https://docs.kakaocloud.com/en/service/bcs/vm/vm-overview |

**반드시 포함할 팩트**
- VM은 하이퍼바이저로 물리 하드웨어를 가상화한 컴퓨팅 자원
- Scale-up: 기존 인스턴스의 CPU·메모리 자원 증가
- Scale-out: 인스턴스 수를 늘려 부하 분산
- 보안 그룹(Security Group)과 키 페어(Key Pair)로 접근 제어
- 종량제 과금: 실제 사용 시간 기준 청구

**출제 예시 방향**
```
난이도 1: "카카오클라우드 VM 인스턴스에서 보안 접근 제어에 사용되는 두 가지는?"
난이도 2: "Scale-up과 Scale-out의 차이로 올바른 것은?"
난이도 3: "트래픽이 예측 불가능하게 급증하는 웹 서비스에 적합한 확장 방식은?"
```

---

### topic: `instance-type` — 인스턴스 유형

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 8문제 |
| 난이도 분포 | 1×2, 2×2, 3×3, 4×1 |
| 핵심 개념 | 범용/컴퓨팅 최적화/메모리 최적화/가속 컴퓨팅 인스턴스 유형 |
| 출제 근거 URL | https://docs.kakaocloud.com/en/service/bcs/bcs-instance/bcs-instance-overview |

**인스턴스 유형별 특징 (오답 설계 핵심)**

| 유형 | 특징 | 주요 용도 |
|------|------|----------|
| 범용(General Purpose) | CPU:메모리 균형 | 웹서버, 중소형 DB, 개발/테스트 |
| 컴퓨팅 최적화(Compute Optimized) | 높은 CPU 성능 | 배치처리, HPC, 게임서버, ML 추론 |
| 메모리 최적화(Memory Optimized) | 대용량 메모리 | 인메모리 DB, 대규모 데이터 처리 |
| 가속 컴퓨팅(GPU/NPU) | 하드웨어 가속 | 딥러닝, AI, 데이터 분석 |

**출제 예시 방향**
```
난이도 1: "카카오클라우드 BCS 인스턴스 유형 중 CPU와 메모리를 균형 있게
           제공하는 유형은?"
난이도 2: "딥러닝 모델 학습에 최적화된 인스턴스 유형은?"
난이도 3: "대용량 인메모리 데이터베이스 운영에 적합한 인스턴스 유형은?"
난이도 4: "CPU 집약적인 배치 처리와 ML 추론이 혼합된 워크로드에
           가장 비용 효율적인 인스턴스 조합 전략은?"
```

---

### topic: `image` — 인스턴스 이미지

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 4문제 |
| 난이도 분포 | 1×1, 2×2, 3×1 |
| 핵심 개념 | 공식 이미지 vs 커스텀 이미지, 지원 OS, 가속 컴퓨팅 전용 이미지 |
| 출제 근거 URL | https://docs.kakaocloud.com/en/service/bcs/vm/vm-overview |

**반드시 포함할 팩트**
- 지원 OS: Ubuntu, CentOS (Linux 계열), Microsoft Windows
- 가속 컴퓨팅 인스턴스는 드라이버가 설치된 전용 이미지 제공
- 볼륨 크기 제한은 선택한 OS 이미지에 따라 다름

---

### topic: `public-ip` — 공인 IP

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 4문제 |
| 난이도 분포 | 1×1, 2×2, 3×1 |
| 핵심 개념 | 공인 IP 개념, 인스턴스 이동 시 IP 재사용, 과금 여부 |
| 출제 근거 URL | https://docs.kakaocloud.com/en/service/bcs/vm/vm-main |

**반드시 포함할 팩트**
- 공인 IP는 별도 비용 발생
- 인스턴스 간 detach/attach로 재할당 가능
- 인스턴스 종료(terminate) 시 IP 반환

---

### topic: `bare-metal` — Bare Metal Server

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 5문제 |
| 난이도 분포 | 1×1, 2×2, 3×1, 4×1 |
| 핵심 개념 | Bare Metal의 정의, VM과의 차이(하이퍼바이저 유무), 용도 |
| 출제 근거 URL | https://docs.kakaocloud.com/en/service/bcs/bcs-ov |

**반드시 포함할 팩트**
- Bare Metal: 가상화 계층(하이퍼바이저) 없이 물리 서버를 직접 사용
- 인스턴스 이름에 `.baremetal` 접미사 (예: `r2a.baremetal`)
- VM 대비 높은 성능, 낮은 격리성

**좋은 오답 포인트**
- "Bare Metal은 가상화를 사용한다" → 금지 사실
- "VM과 Bare Metal의 가격은 동일하다" → 틀린 정보

---

### topic: `gpu` — GPU 인스턴스

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 4문제 |
| 난이도 분포 | 1×1, 2×1, 3×2 |
| 핵심 개념 | GPU/NPU 인스턴스 용도, NVIDIA 라이브러리 지원 |
| 출제 근거 URL | https://docs.kakaocloud.com/en/service/bcs/bcs-ov |

**반드시 포함할 팩트**
- GPU 인스턴스는 TensorRT, cuDNN, NCCL 등 NVIDIA 라이브러리 지원
- GPU와 NPU 인스턴스 제공 (AI/ML 분산 컴퓨팅 환경 구축용)

---

### topic: `storage-attachment` — BCS에 BSS 연결

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 없음 (question-taxonomy 등록 토픽이나 Essential 범위 외) |
| 비고 | Block Storage 연결 개념은 `04-bss` 챕터의 `block-storage` 토픽에서 다룸. BCS product-spec에서는 별도 출제하지 않으며, 필요 시 `04-bss`와 연계 문제로 작성 |

---

## 3. 전체 난이도 분포 목표

| 난이도 | 목표 문제 수 | 비율 |
|--------|------------|------|
| 1 | 8문제 | 27% |
| 2 | 9문제 | 30% |
| 3 | 9문제 | 30% |
| 4 | 3문제 | 10% |
| 5 | 1문제 | 3% |

---

## 4. 챕터 특화 오답 설계 원칙

| 혼동 포인트 | 오답 활용 방법 |
|-------------|--------------|
| VM vs Bare Metal | 하이퍼바이저 유무 혼동 유도 |
| Scale-up vs Scale-out | 방향 혼동 유도 |
| 인스턴스 유형 간 용도 | 유사 워크로드에 다른 유형 배치 |
| GPU vs 컴퓨팅 최적화 | AI 워크로드 문제에서 혼동 유도 |

---

## 5. 관련 문서

- [`docs/references/bcs-llms.txt`](../references/bcs-llms.txt)
- [`questions/02-bcs/_index.md`](../../questions/02-bcs/_index.md)
