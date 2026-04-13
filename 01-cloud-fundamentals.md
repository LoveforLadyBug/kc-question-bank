# product-specs/01-cloud-fundamentals.md
# 챕터 01 — Cloud Fundamentals 출제 스펙

> 이 문서는 `generate-questions.py` 가 문제를 생성할 때 참조하는 출제 명세서입니다.
> "무엇을 얼마나, 어떤 수준으로 출제할지"를 정의합니다.
>
> 출제 근거 공식 문서: https://docs.kakaocloud.com/start/cloud-intro
>                      https://docs.kakaocloud.com/start/region-az
>                      https://docs.kakaocloud.com/start/resource

---

## 1. 챕터 개요

| 항목 | 내용 |
|------|------|
| chapter 값 | `01-cloud-fundamentals` |
| 목표 문제 수 | 20문제 |
| 모의시험 출제 비중 | 15% (40문항 기준 6문제) |
| 레퍼런스 파일 | `docs/references/cloud-fundamentals-llms.txt` |

### 이 챕터가 다루는 범위

카카오클라우드 서비스를 사용하기 위한 **기반 개념**을 다룹니다.
특정 서비스의 기능을 묻기 전에, 클라우드 자체를 이해하고 있는지 확인합니다.
카카오클라우드 고유 개념(리전 코드, AZ 코드 등)은 공식 문서 기준으로 출제합니다.

---

## 2. 토픽별 출제 명세

### topic: `cloud-model` — 클라우드 서비스 모델

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 4문제 |
| 난이도 분포 | 1×2문제, 2×1문제, 3×1문제 |
| 핵심 개념 | IaaS / PaaS / SaaS 정의 및 구분, 카카오클라우드 서비스의 모델 분류 |
| 출제 포인트 | IaaS·PaaS·SaaS 각각의 정의와 책임 범위, 카카오클라우드 서비스가 어느 모델에 해당하는지 |
| 출제 제외 | FaaS, CaaS 등 Essential 범위 외 모델 |

**출제 예시 방향**
```
난이도 1: "IaaS의 정의로 올바른 것은?"
난이도 2: "다음 중 PaaS에 해당하는 카카오클라우드 서비스는?"
난이도 3: "애플리케이션 런타임 관리를 클라우드 제공자에게 위임하고 싶을 때
           적합한 서비스 모델은?"
```

**좋은 오답 보기 풀**
- IaaS 문제의 오답: PaaS, SaaS, On-premise
- 서비스 분류 문제의 오답: 같은 카테고리의 다른 서비스명 (예: VM vs Kubernetes Engine)

---

### topic: `deployment-model` — 클라우드 배포 모델

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 3문제 |
| 난이도 분포 | 1×1문제, 2×1문제, 3×1문제 |
| 핵심 개념 | Public / Private / Hybrid 클라우드 정의 및 차이 |
| 출제 포인트 | 각 모델의 특징, 카카오클라우드가 제공하는 배포 형태(Public/Private/Installable) |
| 출제 근거 URL | https://kakaoenterprise.com/service/kakaocloud/ |

**출제 예시 방향**
```
난이도 1: "퍼블릭 클라우드의 특징으로 올바른 것은?"
난이도 2: "온프레미스 환경에 퍼블릭 클라우드 경험을 제공하는 배포 형태는?"
난이도 3: "보안 규제로 인해 데이터를 외부로 반출할 수 없는 금융기관에
           가장 적합한 카카오클라우드 배포 형태는?"
```

---

### topic: `region-az` — 리전과 가용 영역

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 5문제 |
| 난이도 분포 | 1×2문제, 2×1문제, 3×1문제, 4×1문제 |
| 핵심 개념 | 리전/AZ 정의, 카카오클라우드 리전 코드(`kr-central-2`), AZ 코드(`kr-central-2-a/b`) |
| 출제 포인트 | 리전 vs AZ 구분, 다중 AZ 구성의 목적(고가용성), 리전 간 리소스 자동 복제 여부 |
| 출제 근거 URL | https://docs.kakaocloud.com/start/region-az |

**반드시 포함해야 할 팩트 (공식 문서 기준)**
- 카카오클라우드의 현재 리전: `kr-central-2` (대한민국 수도권)
- AZ 코드 형식: `{리전코드}-{문자}` (예: `kr-central-2-a`)
- 리전 간 리소스 자동 복제 없음 → 사용자가 직접 구성해야 함
- 다중 AZ 배치 → 고가용성(HA) 및 내결함성 확보

**출제 예시 방향**
```
난이도 1: "카카오클라우드 리전과 가용 영역(AZ)의 관계로 올바른 것은?"
난이도 2: "카카오클라우드 AZ 코드 'kr-central-2-a'에서 'kr-central-2'가 의미하는 것은?"
난이도 3: "단일 AZ 장애 시에도 서비스를 지속하려면 어떻게 구성해야 하는가?"
난이도 4: "재해 복구(DR) 목적으로 리소스를 배치할 때, 다중 AZ와 다중 리전 구성의
           차이점으로 올바른 것은?"
```

**주의: 출제 금지 항목**
- 특정 AZ의 물리적 위치(데이터센터 주소) → 공식 문서에 미공개
- 리전 수 또는 AZ 수 → 변경될 수 있으므로 숫자 고정 출제 금지

---

### topic: `pricing-model` — 과금 모델

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 4문제 |
| 난이도 분포 | 1×1문제, 2×1문제, 3×1문제, 5×1문제 |
| 핵심 개념 | 종량제(Pay-as-you-go), 약정 할인, 크레딧, 무료 서비스 |
| 출제 포인트 | 종량제의 특징, 약정 vs 종량제 비용 비교, 무료 서비스 목록(VPC, IAM 등) |
| 출제 근거 URL | https://kakaocloud.com/pricing/overview |

**반드시 포함해야 할 팩트**
- 종량제: 실제 사용한 리소스에 대해서만 비용 청구
- 무료 서비스: VPC, IAM 등 일부 서비스는 무료
- 약정 할인: 장기 사용 약정 시 할인 적용

**출제 예시 방향**
```
난이도 1: "카카오클라우드 종량제 과금의 특징으로 올바른 것은?"
난이도 2: "카카오클라우드에서 무료로 제공되는 서비스는?"
난이도 3: "단기간 대규모 컴퓨팅이 필요할 때 비용 효율적인 과금 방식은?"
난이도 5: "이벤트성 트래픽이 연 2회 발생하는 서비스의 인프라 비용을
           최소화하는 전략으로 가장 올바른 것은?"
```

---

### topic: `shared-responsibility` — 공동 책임 모델

| 항목 | 내용 |
|------|------|
| 목표 문제 수 | 4문제 |
| 난이도 분포 | 2×2문제, 3×2문제 |
| 핵심 개념 | 클라우드 제공자 책임 vs 사용자 책임 범위, IaaS/PaaS/SaaS별 책임 차이 |
| 출제 포인트 | 물리 인프라·하이퍼바이저는 제공자 책임, 데이터·애플리케이션은 사용자 책임 |

**출제 예시 방향**
```
난이도 2: "IaaS 모델에서 클라우드 제공자의 책임 범위에 해당하는 것은?"
난이도 3: "SaaS 모델과 IaaS 모델을 비교할 때, 사용자의 책임 범위가
           더 넓은 모델은? 그 이유는?"
```

---

## 3. 전체 난이도 분포 목표

| 난이도 | 목표 문제 수 | 비율 |
|--------|------------|------|
| 1 (기초 I) | 6문제 | 30% |
| 2 (기초 II) | 5문제 | 25% |
| 3 (응용) | 6문제 | 30% |
| 4 (심화 I) | 2문제 | 10% |
| 5 (심화 II) | 1문제 | 5% |
| **합계** | **20문제** | **100%** |

---

## 4. 인지 유형 분포 목표

| 인지 유형 | 목표 문제 수 |
|-----------|------------|
| `definition` | 6문제 |
| `feature` | 5문제 |
| `comparison` | 4문제 |
| `usecase` | 4문제 |
| `constraint` | 1문제 |

---

## 5. 오답 설계 원칙 (이 챕터 특화)

Cloud Fundamentals는 개념이 추상적이어서 오답 설계가 특히 중요합니다.

**흔한 혼동 포인트 → 좋은 오답 소재**

| 혼동 포인트 | 오답으로 활용 방법 |
|-------------|-----------------|
| IaaS vs PaaS 책임 경계 | 서로를 오답 보기로 배치 |
| 리전 vs AZ 격리 수준 | "AZ 장애 시 리전 전체 장애" vs "AZ만 장애" |
| 다중 AZ vs 다중 리전 | 고가용성(HA) vs 재해복구(DR) 혼동 |
| 종량제 vs 약정 | 단기 vs 장기 사용 맥락에 따라 오답 배치 |
| 리소스 자동 복제 여부 | "자동 복제됨"을 오답으로 활용 |

---

## 6. generate-questions.py 실행 가이드

```bash
# 이 챕터 전체 생성 (최대 10개)
python scripts/generate-questions.py --chapter 01-cloud-fundamentals

# 특정 토픽만 생성
python scripts/generate-questions.py --chapter 01-cloud-fundamentals --topic region-az

# 특정 난이도만 생성
python scripts/generate-questions.py --chapter 01-cloud-fundamentals --difficulty 3
```

**생성 전 필수 확인 사항**
```
□ docs/references/cloud-fundamentals-llms.txt 존재 여부
□ llms.txt 내 SOURCE 헤더가 docs.kakaocloud.com 기준인지
□ 기존 questions/01-cloud-fundamentals/ 의 문제 수 및 난이도 분포 확인
  → _index.md 참조
```

---

## 7. 관련 문서

- [`docs/references/cloud-fundamentals-llms.txt`](../references/cloud-fundamentals-llms.txt) — 파싱된 공식 문서
- [`questions/01-cloud-fundamentals/_index.md`](../../questions/01-cloud-fundamentals/_index.md) — 현재 문제 현황
- [`docs/design-docs/difficulty-rubric.md`](../design-docs/difficulty-rubric.md) — 난이도 판단 기준
- [`docs/design-docs/question-taxonomy.md`](../design-docs/question-taxonomy.md) — 토픽 분류 체계
