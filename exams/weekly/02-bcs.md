# 주차별 스터디 — 02-bcs
생성일: 2026-04-13 | 문제 수: 10

### 1. [q018] 난이도 2

카카오클라우드 BCS의 가속 컴퓨팅(GPU/NPU) 인스턴스에서 사용할 수 있는 이미지에 관한 설명으로 옳은 것은?

- A. 범용 인스턴스와 동일한 표준 이미지를 공유하며 별도 이미지는 없다
- B. 가속 컴퓨팅 인스턴스는 드라이버가 사전 설치된 전용 이미지를 제공한다
- C. GPU 인스턴스에는 반드시 Windows 이미지만 사용 가능하다
- D. 가속 컴퓨팅 인스턴스에서는 커스텀 이미지 사용이 금지되어 있다

### 2. [q014] 난이도 1

카카오클라우드 BCS에서 CPU와 메모리 자원을 균형 있게 제공하여 웹 서버, 중소형 데이터베이스, 개발·테스트 환경에 적합한 인스턴스 유형은?

- A. 범용(General Purpose) 인스턴스
- B. 컴퓨팅 최적화(Compute Optimized) 인스턴스
- C. 메모리 최적화(Memory Optimized) 인스턴스
- D. 가속 컴퓨팅(Accelerated Computing) 인스턴스

### 3. [q002] 난이도 2

카카오클라우드 VM에서 Scale-up과 Scale-out의 차이로 올바른 것은?

- A. Scale-up은 인스턴스 수를 늘리고, Scale-out은 인스턴스 사양을 높인다
- B. Scale-up은 기존 인스턴스의 CPU·메모리를 증가시키고, Scale-out은 인스턴스 수를 늘린다
- C. Scale-up과 Scale-out은 모두 인스턴스 수를 조정하는 방식이다
- D. Scale-out은 단일 인스턴스의 성능을 극대화하는 방식이다

### 4. [q016] 난이도 3

수십 GB 이상의 데이터를 메모리에 상주시키며 실시간 조회 응답 속도를 극대화해야 하는 인메모리 데이터베이스 운영에 가장 적합한 BCS 인스턴스 유형은?

- A. 컴퓨팅 최적화(Compute Optimized) 인스턴스
- B. 범용(General Purpose) 인스턴스
- C. 메모리 최적화(Memory Optimized) 인스턴스
- D. 가속 컴퓨팅(Accelerated Computing) 인스턴스

### 5. [q003] 난이도 3

딥러닝 모델 학습처럼 대규모 병렬 연산이 필요한 워크로드에 가장 적합한 카카오클라우드 BCS 인스턴스 유형은?

- A. 범용(General Purpose) 인스턴스
- B. 메모리 최적화(Memory Optimized) 인스턴스
- C. GPU 인스턴스
- D. Bare Metal Server

### 6. [q022] 난이도 3

카카오클라우드 BCS의 Bare Metal Server와 Virtual Machine(VM)을 비교한 설명으로 옳은 것은?

- A. VM은 Bare Metal보다 성능이 높으며, 하이퍼바이저 없이 운영된다
- B. Bare Metal은 하이퍼바이저 오버헤드 없이 물리 서버 성능을 그대로 활용하므로 VM보다 성능이 높다
- C. Bare Metal Server와 VM 인스턴스는 서로 동일한 요금제를 사용한다
- D. VM은 물리 서버를 단독 점유하고, Bare Metal은 여러 사용자가 공유한다

### 7. [q023] 난이도 2

카카오클라우드 BCS GPU 인스턴스에서 지원하는 NVIDIA 라이브러리로 올바른 것은?

- A. TensorRT, cuDNN, NCCL
- B. BCS GPU 인스턴스에서 OpenMP, MKL, BLAS를 지원한다
- C. BCS 가속 컴퓨팅 인스턴스에서 Spark, Hadoop, Hive를 활용한다
- D. BCS GPU 인스턴스는 Ansible, Terraform, Docker 라이브러리를 지원한다

### 8. [q015] 난이도 2

딥러닝 모델 학습 작업을 위해 카카오클라우드 BCS 인스턴스를 선택할 때 가장 적합한 인스턴스 유형은?

- A. 범용(General Purpose) 인스턴스
- B. 메모리 최적화(Memory Optimized) 인스턴스
- C. 가속 컴퓨팅(Accelerated Computing) 인스턴스
- D. 컴퓨팅 최적화(Compute Optimized) 인스턴스

### 9. [q020] 난이도 2

카카오클라우드 BCS에서 공인 IP 주소를 인스턴스 간에 이동시키는 방법으로 올바른 것은?

- A. BCS 공인 IP는 최초 할당 후 변경이 불가능하므로 새 IP를 재발급받아야 한다
- B. 기존 BCS 인스턴스에서 detach한 뒤 다른 인스턴스에 attach하는 방식으로 재사용 가능하다
- C. BCS 공인 IP 이동은 동일 가용 영역(AZ) 내 인스턴스에서만 가능하다
- D. BCS 인스턴스 종료 없이 공인 IP를 이동할 수 없으며, 반드시 인스턴스를 먼저 삭제해야 한다

### 10. [q019] 난이도 1

카카오클라우드 BCS에서 공인 IP 주소를 인스턴스에 할당할 때 발생하는 비용에 관한 설명으로 옳은 것은?

- A. 공인 IP는 BCS 인스턴스에 자동 할당되며 무료이고 할당 개수에 제한이 없다
- B. 공인 IP는 BCS 인스턴스 실행 여부와 관계없이 할당 시 별도 비용이 발생한다
- C. 공인 IP는 BCS 인스턴스가 실행(running) 중일 때만 요금이 부과된다
- D. 공인 IP는 BCS VPC 생성 시 자동으로 1개가 무료 제공된다

---

## 정답표

1. q018 — B
2. q014 — A
3. q002 — B
4. q016 — C
5. q003 — C
6. q022 — B
7. q023 — A
8. q015 — C
9. q020 — B
10. q019 — B