# product-specs/04-bss.md
# 챕터 04 — Beyond Storage Service (BSS) 출제 스펙

> 출제 근거 공식 문서:
> https://docs.kakaocloud.com/service/bss/object-storage/object-storage-overview
> https://docs.kakaocloud.com/service/bss/file-storage/file-storage-overview
> https://kakaocloud.com/services/block-storage/intro

---

## 1. 챕터 개요

| 항목 | 내용 |
|------|------|
| chapter 값 | `04-bss` |
| 목표 문제 수 | 20문제 |
| 모의시험 출제 비중 | 15% (40문항 기준 6문제) |
| 레퍼런스 파일 | `docs/references/bss-llms.txt` |

### 이 챕터가 다루는 범위

BSS는 Block Storage, Object Storage, File Storage 세 가지 유형을 제공합니다.
세 스토리지의 특징과 차이점, 적합한 사용 시나리오를 이해하는 것이 핵심입니다.
특히 `storage-comparison` 토픽은 스터디에서 가장 자주 혼동되는 영역입니다.

---

## 2. 토픽별 출제 명세

### topic: `block-storage` — Block Storage

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 4문제 |
| 난이도 분포 | 1×2, 2×1, 3×1 |
| 핵심 개념 | 블록 단위 저장, VM 기본 볼륨, SSD 기반, 단일 인스턴스 연결 |
| 출제 근거 URL | https://docs.kakaocloud.com/service/bss |

**반드시 포함할 팩트**
- 데이터를 고정된 크기의 블록으로 분할 저장
- 서버의 기본(루트) 볼륨으로 사용
- 현재 SSD 블록 스토리지만 지원
- 계층화된 디렉터리 구조를 가짐 (Object Storage와 대비)
- 단일 인스턴스에만 연결 가능 (File Storage와 대비)

---

### topic: `object-storage` — Object Storage

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 6문제 |
| 난이도 분포 | 1×1, 2×2, 3×2, 4×1 |
| 핵심 개념 | Key-Value 평면 구조, 버킷, S3 호환, 비정형 데이터, 무제한 확장 |
| 출제 근거 URL | https://docs.kakaocloud.com/service/bss/object-storage/object-storage-overview |

**반드시 포함할 팩트**
- 데이터를 Key-Value 형태의 객체(Object)로 저장
- 버킷(Bucket): 객체를 담는 컨테이너 단위
- 버킷 용량과 객체 수에 제한 없음 → 무제한 확장
- 계층 구조 없는 평면 구조 → 빠른 접근 속도
- 비정형 데이터(이미지, 비디오, 문서, 백업 등)에 최적화
- Swift API(OpenStack) 사양 지원
- 공개(Public) 버킷은 읽기 전용(Read Only)으로만 제공

**출제 예시 방향**
```
난이도 1: "Object Storage에서 객체를 담는 컨테이너 단위를 무엇이라 하는가?"
난이도 2: "Object Storage가 Block Storage와 다른 데이터 저장 구조는?"
난이도 3: "대용량 이미지·비디오 파일을 저장하고 불특정 다수에게 제공하려 할 때
           가장 적합한 스토리지는?"
난이도 4: "Object Storage의 버킷을 퍼블릭으로 공개했을 때 접근 권한은?"
```

---

### topic: `file-storage` — File Storage

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 4문제 |
| 난이도 분포 | 1×1, 2×1, 3×2 |
| 핵심 개념 | 공유 파일 시스템, 다수 서버 동시 접근, 프로토콜 기반 |
| 출제 근거 URL | https://docs.kakaocloud.com/service/bss/file-storage/file-storage-overview |

**반드시 포함할 팩트**
- 다수의 서버가 동시에 읽기/쓰기 가능한 공유 스토리지
- 프로토콜을 통해 여러 인스턴스가 공동 사용
- Full/Incremental 백업 및 복원 지원
- Object Storage와 달리 파일 공유·협업 환경 제공

---

### topic: `storage-comparison` — 스토리지 유형 비교

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 4문제 |
| 난이도 분포 | 2×1, 3×2, 4×1 |
| 핵심 개념 | 세 스토리지 유형의 차이점 및 적합한 사용 시나리오 |
| 출제 근거 URL | https://docs.kakaocloud.com/service/bss/object-storage/object-storage-overview |

**핵심 비교표 (오답 설계 기준)**

| 구분 | Block Storage | Object Storage | File Storage |
|------|--------------|----------------|-------------|
| 저장 단위 | 블록 | 객체(Key-Value) | 파일 |
| 구조 | 계층(디렉터리) | 평면(Flat) | 계층(디렉터리) |
| 동시 접근 | 단일 인스턴스 | HTTP API | 다수 인스턴스 |
| 주요 용도 | OS/DB 볼륨 | 비정형 대용량 | 공유 파일 시스템 |
| 확장성 | 제한적 | 무제한 | 제한적 |

**출제 예시 방향**
```
난이도 2: "세 스토리지 유형 중 여러 인스턴스가 동시에 읽기/쓰기가
           가능한 것은?"
난이도 3: "VM의 운영체제를 설치할 볼륨으로 사용해야 할 때 적합한
           스토리지 유형은?"
난이도 4: "빅데이터 파이프라인에서 원본 로그를 장기 보관하면서 비용을
           최소화하려 할 때 가장 적합한 스토리지 유형은?"
```

---

### topic: `backup` — 백업 및 스냅샷

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 2문제 |
| 난이도 분포 | 3×1, 4×1 |
| 핵심 개념 | File Storage 백업(Full/Incremental), 스냅샷 개념 |

---

## 3. 전체 난이도 분포 목표

| 난이도 | 목표 문제 수 | 비율 |
|--------|------------|------|
| 1 | 5문제 | 25% |
| 2 | 5문제 | 25% |
| 3 | 7문제 | 35% |
| 4 | 3문제 | 15% |

---

## 4. 챕터 특화 오답 설계 원칙

| 혼동 포인트 | 오답 활용 방법 |
|-------------|--------------|
| Object vs File 공유 기능 | File만 공유 가능, Object는 API 접근 |
| Block vs Object 구조 | 계층 vs 평면 구조 혼동 |
| Object 버킷 공개 시 권한 | 쓰기 가능으로 혼동 유도 |
| 무제한 확장 | Block/File은 제한적, Object만 무제한 |

---

## 5. 관련 문서

- [`docs/references/bss-llms.txt`](../references/bss-llms.txt)
- [`questions/04-bss/_index.md`](../../questions/04-bss/_index.md)
