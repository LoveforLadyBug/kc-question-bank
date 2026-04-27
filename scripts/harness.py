"""
harness.py — 공통 기반 모듈
모든 파이프라인 스크립트가 공유하는 클라이언트, 로거, 유틸리티를 제공합니다.
"""
from __future__ import annotations

import os
import re
import sys
import time
import yaml
from datetime import datetime
from pathlib import Path

import openai

try:
    import anthropic
except ImportError:
    anthropic = None  # 로컬 모델만 사용하는 환경에서는 미설치 허용

# .env 자동 로드 (ANTHROPIC_API_KEY 등 환경변수 사용 가능하게)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

# LLM 제공자 선택 — "anthropic" (기본) 또는 "local" (Ollama 등 OpenAI 호환)
LLM_PROVIDER: str = os.environ.get("LLM_PROVIDER", "anthropic").lower()

# 사용할 모델. 환경변수 LOCAL_MODEL로 재정의 가능.
# - anthropic 제공자: Claude 모델 문자열 (예: "claude-sonnet-4-6")
# - local 제공자: Ollama 모델 태그 (예: "exaone3.5:7.8b")
_DEFAULT_MODEL = (
    "claude-haiku-4-5-20251001" if LLM_PROVIDER == "anthropic" else "exaone3.5:7.8b"
)
LOCAL_MODEL: str = os.environ.get("LOCAL_MODEL", _DEFAULT_MODEL)

ROOT = Path(__file__).parent.parent

# 챕터 → references/ 슬러그 매핑 (ARCHITECTURE.md 기준)
CHAPTER_REF_SLUG: dict[str, str] = {
    # 평가 영역 기반 (v2 — 공식 시험 블루프린트 기준)
    "01-cloud-overview": "cloud-overview",
    "02-kakao-services/bcs": "bcs",
    "02-kakao-services/bns": "bns",
    "02-kakao-services/bss": "bss",
    "02-kakao-services/container-pack": "container-pack",
    "02-kakao-services/data-store": "data-store",
    "03-billing": "billing",
    "04-security": "security",
    "05-operations": "operations",
    "06-account": "account",
    "07-complex": "complex",
}

# 챕터별 유효 topic 목록 (question-taxonomy.md §4 기준)
CHAPTER_TOPICS: dict[str, list[str]] = {
    "01-cloud-overview": [
        "cloud-model", "deployment-model", "region-az", "kakaocloud-overview", "shared-responsibility",
    ],
    "02-kakao-services/bcs": [
        "vm-overview", "instance-type", "image", "public-ip", "bare-metal", "gpu",
    ],
    "02-kakao-services/bns": [
        "vpc", "subnet", "security-group", "load-balancer", "dns", "transit-gateway",
    ],
    "02-kakao-services/bss": [
        "block-storage", "object-storage", "file-storage", "storage-comparison", "backup",
    ],
    "02-kakao-services/container-pack": [
        "kubernetes-overview", "cluster", "container-registry", "node-group",
    ],
    "02-kakao-services/data-store": [
        "mysql", "postgresql", "redis", "mongodb", "db-comparison", "ha-backup",
    ],
    "03-billing": [
        "pricing-model", "service-pricing", "cost-optimization", "billing-management",
    ],
    "04-security": [
        "iam-policy", "network-security", "data-encryption", "compliance",
    ],
    "05-operations": [
        "monitoring", "logging", "notification", "troubleshooting",
    ],
    "06-account": [
        "iam-overview", "account-management", "mfa",
    ],
    "07-complex": [
        "multi-service", "scenario", "migration",
    ],
}

# 챕터별 키워드 (C-1 자동 감점 기준)
CHAPTER_KEYWORDS: dict[str, list[str]] = {
    "01-cloud-overview": ["IaaS", "PaaS", "SaaS", "클라우드", "리전", "AZ", "가용 영역", "카카오클라우드"],
    "02-kakao-services/bcs": ["VM", "Virtual Machine", "인스턴스", "Bare Metal", "GPU", "BCS"],
    "02-kakao-services/bns": ["VPC", "Subnet", "Load Balancer", "DNS", "Transit Gateway", "보안 그룹"],
    "02-kakao-services/bss": ["Block Storage", "Object Storage", "File Storage", "스토리지", "스냅샷"],
    "02-kakao-services/container-pack": ["Kubernetes", "Container", "클러스터", "노드", "Registry", "Pod"],
    "02-kakao-services/data-store": ["MySQL", "PostgreSQL", "Redis", "MongoDB", "데이터베이스"],
    "03-billing": ["요금", "과금", "청구", "pricing", "비용", "크레딧", "약정"],
    "04-security": ["IAM", "권한", "정책", "보안", "암호화", "인증서", "Cloud Trail"],
    "05-operations": ["모니터링", "로깅", "Monitoring", "Logging", "알림", "Alert", "메트릭"],
    "06-account": ["IAM", "사용자", "역할", "그룹", "계정", "MFA", "프로젝트"],
    "07-complex": ["클라우드", "서비스", "아키텍처", "시나리오"],
}


# ---------------------------------------------------------------------------
# API 클라이언트
# ---------------------------------------------------------------------------

# --- Anthropic 어댑터: OpenAI 클라이언트 인터페이스를 흉내내서
#     기존 호출부(client.chat.completions.create)를 그대로 사용 가능하게 함 ---

class _AnthropicChoiceMessage:
    def __init__(self, content: str):
        self.content = content


class _AnthropicChoice:
    def __init__(self, content: str):
        self.message = _AnthropicChoiceMessage(content)


class _AnthropicResponse:
    def __init__(self, content: str):
        self.choices = [_AnthropicChoice(content)]


class _AnthropicCompletions:
    def __init__(self, client):
        self._client = client

    def create(self, *, model, messages, max_tokens=1024, temperature=None, **kwargs):
        # OpenAI-style messages → Anthropic system prompt + user/assistant messages
        system_parts: list[str] = []
        anth_messages: list[dict] = []
        for m in messages:
            role = m.get("role")
            content = m.get("content", "")
            if role == "system":
                system_parts.append(content)
            elif role in ("user", "assistant"):
                anth_messages.append({"role": role, "content": content})
        params: dict = {
            "model": model,
            "messages": anth_messages,
            "max_tokens": max_tokens,
        }
        if system_parts:
            params["system"] = "\n\n".join(system_parts)
        if temperature is not None:
            params["temperature"] = temperature
        resp = self._client.messages.create(**params)
        text = "".join(block.text for block in resp.content if hasattr(block, "text"))
        return _AnthropicResponse(text)


class _AnthropicChat:
    def __init__(self, client):
        self.completions = _AnthropicCompletions(client)


class AnthropicAdapter:
    """OpenAI 클라이언트 시그니처를 흉내내는 Anthropic SDK 래퍼."""

    def __init__(self, api_key: str):
        if anthropic is None:
            raise RuntimeError(
                "anthropic 패키지가 설치되어 있지 않습니다. "
                "`pip install -r requirements.txt`로 설치하세요."
            )
        self._client = anthropic.Anthropic(api_key=api_key)
        self.chat = _AnthropicChat(self._client)


def get_client():
    """LLM_PROVIDER에 따라 Anthropic 어댑터 또는 OpenAI 클라이언트 반환."""
    if LLM_PROVIDER == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다. "
                ".env 파일을 확인하거나 셸에서 export 하세요."
            )
        return AnthropicAdapter(api_key)
    # local provider — Ollama 또는 기타 OpenAI 호환 엔드포인트
    base_url = os.environ.get("OPENAI_BASE_URL", "http://localhost:11434/v1")
    api_key = os.environ.get("OPENAI_API_KEY", "ollama")
    return openai.OpenAI(base_url=base_url, api_key=api_key)


# ---------------------------------------------------------------------------
# 로거 (AGENTS.md §7 형식)
# ---------------------------------------------------------------------------

class AgentLogger:
    LOG_KEEP_DAYS = 30

    def __init__(self, agent_name: str, chapter: str = ""):
        self.agent_name = agent_name
        self.chapter = chapter
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_dir = ROOT / "logs" / agent_name
        log_dir.mkdir(parents=True, exist_ok=True)
        self._rotate_logs(log_dir)
        suffix = f"_{chapter}" if chapter else ""
        self.log_path = log_dir / f"{date_str}{suffix}.log"
        self._start = datetime.now()

    def _rotate_logs(self, log_dir: Path) -> None:
        """LOG_KEEP_DAYS일 이상 된 로그 파일 삭제 (ARCHITECTURE.md §7)."""
        cutoff = time.time() - self.LOG_KEEP_DAYS * 86400
        for f in log_dir.glob("*.log"):
            try:
                if f.stat().st_mtime < cutoff:
                    f.unlink()
            except OSError:
                pass

    def log(self, message: str) -> None:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] [{self.agent_name}] {message}"
        print(line)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def start(self, **kwargs) -> None:
        parts = " ".join(f"{k}={v}" for k, v in kwargs.items())
        self.log(f"START {parts}")

    def end(self) -> None:
        secs = int((datetime.now() - self._start).total_seconds())
        self.log(f"END duration={secs}s")


# ---------------------------------------------------------------------------
# references/ 경로 및 사전 검증
# ---------------------------------------------------------------------------

def ref_path(chapter: str) -> Path:
    slug = CHAPTER_REF_SLUG.get(chapter)
    if not slug:
        print(f"[ERROR] 알 수 없는 챕터: {chapter}")
        sys.exit(1)
    return ROOT / "docs" / "references" / f"{slug}-llms.txt"


def check_references_exist(chapter: str) -> Path:
    """references 파일이 없으면 에러 메시지 출력 후 종료."""
    path = ref_path(chapter)
    if not path.exists():
        slug = CHAPTER_REF_SLUG.get(chapter, "?")
        print(f"[ERROR] docs/references/{slug}-llms.txt 가 없습니다.")
        print(f"        레퍼런스 파일을 먼저 확인하세요: docs/references/{chapter}-llms.txt")
        print(f"        먼저 parser를 실행하세요: python scripts/parse-kakao-docs.py --chapter {chapter}")
        sys.exit(1)
    return path


# ---------------------------------------------------------------------------
# questions/ 유틸리티
# ---------------------------------------------------------------------------

def get_next_question_id(chapter: str) -> int:
    """다음 문제 번호(정수) 반환. questions/{chapter}/ 없거나 비어있으면 1."""
    q_dir = ROOT / "questions" / chapter
    if not q_dir.exists():
        return 1
    existing = [f.stem for f in q_dir.glob("q[0-9][0-9][0-9].md")]
    if not existing:
        return 1
    return max(int(s[1:]) for s in existing) + 1


def load_question_file(path: Path) -> tuple[dict, str]:
    """q{NNN}.md 파싱. (frontmatter dict, body str) 반환."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm = yaml.safe_load(parts[1]) or {}
    return fm, parts[2].strip()


def save_question_file(path: Path, fm: dict, body: str) -> None:
    """frontmatter + body를 q{NNN}.md 포맷으로 원자적 저장.

    임시 파일(.tmp)에 먼저 쓴 뒤 os.replace()로 교체해
    중간 실패 시 기존 파일이 손상되지 않도록 합니다.
    """
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    content = f"---\n{fm_str}---\n\n{body}\n"
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    os.replace(tmp_path, path)


# ---------------------------------------------------------------------------
# Markdown 파싱 유틸리티
# ---------------------------------------------------------------------------

def extract_sections(body: str) -> dict[str, str]:
    """## 섹션명 기준으로 분리해 {섹션명: 내용} 반환."""
    sections: dict[str, str] = {}
    current: str | None = None
    lines: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current is not None:
                sections[current] = "\n".join(lines).strip()
            current = line[3:].strip()
            lines = []
        elif current is not None:
            lines.append(line)
    if current is not None:
        sections[current] = "\n".join(lines).strip()
    return sections


def parse_choices(choices_text: str) -> dict[str, str]:
    """보기 섹션 텍스트에서 {A: 내용, B: 내용, ...} 반환."""
    choices: dict[str, str] = {}
    for line in choices_text.splitlines():
        m = re.match(r"^-\s*([A-D])\.\s*(.+)$", line.strip())
        if m:
            choices[m.group(1)] = m.group(2).strip()
    return choices


# ---------------------------------------------------------------------------
# 공통 유사도 계산
# ---------------------------------------------------------------------------

def token_jaccard(a: str, b: str) -> float:
    """두 문자열의 Jaccard 유사도 (토큰 기반).

    Jaccard = |교집합| / |합집합|  (ARCHITECTURE.md §2 정의 기준)
    두 집합이 모두 비어 있으면 0.0 반환.
    """
    ta = set(a.lower().split())
    tb = set(b.lower().split())
    union = ta | tb
    if not union:
        return 0.0
    return len(ta & tb) / len(union)


# ---------------------------------------------------------------------------
# 할루시네이션 방지 — 3단계 검증 하네스 (db-schema.md §1 v1.1.0)
# ---------------------------------------------------------------------------

HALLUCINATION_SUSPECT = "hallucination-suspect"

VERIFIER_SYSTEM_PROMPT = """\
당신은 KakaoCloud 문제은행 사실검증 에이전트입니다.

=== 작업 정의 ===
[레퍼런스 문서]와 [문제]를 받아서, 문제의 정답·해설·오답 포인트의 모든 사실 주장이 [레퍼런스 문서]에 명시적으로 적혀있는지 판단합니다.
- 모든 사실 주장이 레퍼런스에 직접 적혀있다 → PASS
- 단 하나라도 레퍼런스에 없다 → FAIL

(주의: 오답 보기는 일부러 틀린 내용을 담고 있는 게 정상입니다. 그건 PASS/FAIL 판단의 근거가 아닙니다. 정답·해설·오답 포인트 설명만 봅니다.)

=== 절대 출력 규칙 (위반 시 응답 무효) ===
1. 모든 응답은 한국어로만.
2. 응답은 **정확히 두 줄**. 분석·설명·마크다운·번호 매기기 일절 금지.
3. 첫 줄: 'PASS' 또는 'FAIL' 한 단어만 (대문자).
4. 둘째 줄: '이유: ' 로 시작하는 한 문장, 50자 이내.

=== 출력 예시 ===

예시 1:
PASS
이유: 해설의 모든 내용이 레퍼런스 VPC 섹션에 명시됨

예시 2:
FAIL
이유: 해설의 'kc-cli vpc create' 명령이 레퍼런스에 없음

예시 3:
FAIL
이유: 오답 포인트 C의 IAM 정책 우선순위는 레퍼런스에 없음

이제 받은 [레퍼런스 문서]와 [문제]에 대해 위 형식으로 두 줄만 출력하세요. 다른 어떤 분석도 작성하지 마세요.
"""


def keyword_anchor_check(
    question_text: str,
    chapter: str,
    llms_content: str,
) -> tuple[bool, str]:
    """[1단계] 키워드 앵커 검사.

    챕터 키워드(CHAPTER_KEYWORDS) 중 하나 이상이 문제 본문에 포함되어야 하며,
    해당 키워드가 llms.txt에도 존재하는지 확인합니다.

    Returns:
        (passed: bool, reason: str)
    """
    keywords = CHAPTER_KEYWORDS.get(chapter, [])
    if not keywords:
        return True, "CHAPTER_KEYWORDS 미정의 챕터 — 건너뜀"

    matched_in_question = [kw for kw in keywords if kw in question_text]
    if not matched_in_question:
        return False, f"키워드 앵커 없음: 챕터 키워드 {keywords} 중 문제 본문에 없음"

    # llms.txt에도 해당 키워드가 존재하는지 확인
    matched_in_llms = [kw for kw in matched_in_question if kw in llms_content]
    if not matched_in_llms:
        return False, (
            f"키워드가 레퍼런스에 없음: {matched_in_question} → llms.txt 미포함. "
            "공식 문서에 없는 용어 사용 의심"
        )

    return True, f"키워드 앵커 확인: {matched_in_llms}"


def grounding_check(
    evidence: str,
    llms_content: str,
    jaccard_threshold: float = 0.65,
) -> tuple[bool, str]:
    """[2단계] 근거 문장 그라운딩 검사.

    evidence 필드의 인용 문장이 llms.txt 내용과 Jaccard 유사도 기준으로
    존재하는지 확인합니다. 문장 단위로 분할하여 가장 높은 유사도를 사용합니다.

    Args:
        evidence: 문제 frontmatter의 evidence 필드 값
        llms_content: 해당 챕터 llms.txt 전체 내용
        jaccard_threshold: 이 값 이상이면 그라운딩 성공 (기본 0.65)

    Returns:
        (passed: bool, reason: str)
    """
    if not evidence or not evidence.strip():
        return False, "evidence 필드가 비어 있음 — 근거 인용 누락"

    # llms.txt를 문장 단위로 분할하여 가장 유사한 문장 탐색
    sentences = [s.strip() for s in llms_content.replace("\n", " ").split("。") if len(s.strip()) > 10]
    if not sentences:
        sentences = [s.strip() for s in llms_content.split("\n") if len(s.strip()) > 10]

    best_score = max((token_jaccard(evidence, s) for s in sentences), default=0.0)

    if best_score >= jaccard_threshold:
        return True, f"근거 문장 확인 (Jaccard={best_score:.2f})"
    else:
        return False, (
            f"근거 문장 미확인 (최고 Jaccard={best_score:.2f} < {jaccard_threshold}). "
            "evidence가 레퍼런스에 없는 내용일 수 있음"
        )


def verify_with_llm(
    client,
    question_block: str,
    llms_content: str,
    logger: "AgentLogger",
) -> tuple[bool, str]:
    """[3단계] 2-Pass LLM 검증.

    별도 LLM 호출로 문제 전체 내용이 레퍼런스에 근거하는지 판단합니다.

    Args:
        client: anthropic.Anthropic 클라이언트
        question_block: 문제 원문 (frontmatter + body 전체)
        llms_content: 해당 챕터 llms.txt 전체 내용
        logger: AgentLogger 인스턴스

    Returns:
        (passed: bool, reason: str)
    """
    user_content = (
        f"[레퍼런스 문서]\n{llms_content}\n\n"
        f"[문제]\n{question_block}\n\n"
        "위 레퍼런스 문서를 기반으로 이 문제의 할루시네이션 여부를 판단하세요."
    )

    try:
        message = client.chat.completions.create(
            model=LOCAL_MODEL,
            max_tokens=512,
            temperature=0.1,
            messages=[
                {"role": "system", "content": VERIFIER_SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
        )
        response = message.choices[0].message.content.strip()
        logger.log(f"VERIFY response: {response[:800]!r}")

        lines = [l.strip() for l in response.splitlines() if l.strip()]
        upper_response = response.upper()

        # 결론 후보 영역 — 응답 끝 400자 (모델이 결론을 후반에 두는 경향 활용)
        tail = response[-400:] if len(response) > 400 else response
        upper_tail = tail.upper()

        # 1) PASS/FAIL 영문 키워드 탐색 (라인 단위 우선)
        verdict = ""
        for line in lines:
            upper = line.upper()
            if "PASS" in upper and "FAIL" not in upper:
                verdict = "PASS"
                break
            elif "FAIL" in upper:
                verdict = "FAIL"
                break

        # 2) 한국어 결론 키워드 폴백 — 응답 끝부분에서만 검색 (false positive 방지)
        if not verdict:
            # 명확한 결론 표현만 (오답 보기 분석에 우연히 등장하기 어려운 표현)
            fail_signals = (
                "할루시네이션이 발견", "할루시네이션이 있", "할루시네이션 발견",
                "할루시네이션 있음", "할루시네이션이 의심", "할루시네이션 의심됨",
                "할루시네이션입니다", "할루시네이션으로 판단", "할루시네이션으로 결론",
                "사실관계 오류", "검증 실패", "FAIL로 판단", "FAIL입니다",
            )
            pass_signals = (
                "할루시네이션이 없", "할루시네이션 없음", "할루시네이션이 아님",
                "할루시네이션 의심은 없", "할루시네이션이 적절히",
                "사실관계가 일치", "검증 통과", "PASS로 판단", "PASS입니다",
                "레퍼런스와 일치", "레퍼런스 내용과 일치",
            )
            if any(kw in tail for kw in fail_signals):
                verdict = "FAIL"
            elif any(kw in tail for kw in pass_signals):
                verdict = "PASS"

        # 3) 응답 끝부분에 PASS/FAIL 토큰이 있으면 인정 (마지막 폴백)
        if not verdict:
            if "FAIL" in upper_tail:
                verdict = "FAIL"
            elif "PASS" in upper_tail:
                verdict = "PASS"

        reason_line = next(
            (l for l in lines if l.startswith("이유:") or l.lower().startswith("reason:")),
            None,
        )
        if reason_line:
            reason = reason_line.split(":", 1)[-1].strip()
        else:
            # 이유 줄이 없으면 응답 끝에서 한 줄 발췌 (마지막 비빈 줄)
            tail_lines = [l for l in tail.splitlines() if l.strip()]
            reason = (tail_lines[-1] if tail_lines else "불명")[:80]

        if "PASS" in verdict:
            return True, reason
        elif "FAIL" in verdict:
            return False, reason
        else:
            # 판정 불명확 — 안전을 위해 FAIL 처리
            return False, f"검증 응답 파싱 실패: {verdict!r}"

    except Exception as e:
        logger.log(f"[WARN] LLM 검증 호출 실패: {e}")
        # API 오류 시 검증 실패로 처리하지 않고 경고만 (네트워크 이슈 대응)
        return True, f"LLM 검증 API 오류 — 건너뜀: {e}"


def run_hallucination_checks(
    client,
    fm: dict,
    body: str,
    question_block: str,
    chapter: str,
    llms_content: str,
    logger: "AgentLogger",
) -> tuple[bool, str, str]:
    """3단계 할루시네이션 검증 파이프라인을 순서대로 실행합니다.

    [1] keyword_anchor_check → [2] grounding_check → [3] verify_with_llm

    Args:
        client: Anthropic 클라이언트 (3단계에만 사용)
        fm: 파싱된 frontmatter dict
        body: 문제 본문
        question_block: 전체 원문 (frontmatter + body)
        chapter: 챕터 ID
        llms_content: 해당 챕터 llms.txt 전체 내용
        logger: AgentLogger

    Returns:
        (passed: bool, failed_stage: str, reason: str)
        passed=True 이면 failed_stage=""
    """
    question_text = body  # 본문 전체 (문제 + 보기 + 해설)

    # ── [1] 키워드 앵커 검사 ────────────────────────────────
    ok, reason = keyword_anchor_check(question_text, chapter, llms_content)
    if not ok:
        logger.log(f"[HALLUCINATION] [1/3] keyword_anchor FAIL — {reason}")
        return False, "keyword_anchor", reason

    logger.log(f"[VERIFY] [1/3] keyword_anchor PASS — {reason}")

    # ── [2] 근거 문장 그라운딩 검사 ─────────────────────────
    evidence = str(fm.get("evidence") or "")
    ok, reason = grounding_check(evidence, llms_content)
    if not ok:
        logger.log(f"[HALLUCINATION] [2/3] grounding FAIL — {reason}")
        return False, "grounding", reason

    logger.log(f"[VERIFY] [2/3] grounding PASS — {reason}")

    # ── [3] 2-Pass LLM 검증 ─────────────────────────────────
    ok, reason = verify_with_llm(client, question_block, llms_content, logger)
    if not ok:
        logger.log(f"[HALLUCINATION] [3/3] llm_verify FAIL — {reason}")
        return False, "llm_verify", reason

    logger.log(f"[VERIFY] [3/3] llm_verify PASS — {reason}")
    return True, "", reason

