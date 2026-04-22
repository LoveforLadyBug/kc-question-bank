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

import anthropic

# 사용할 Claude 모델. 환경변수 CLAUDE_MODEL로 재정의 가능.
CLAUDE_MODEL: str = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")

ROOT = Path(__file__).parent.parent

# 챕터 → references/ 슬러그 매핑 (ARCHITECTURE.md 기준)
CHAPTER_REF_SLUG: dict[str, str] = {
    "01-cloud-fundamentals": "cloud-fundamentals",
    "02-bcs": "bcs",
    "03-bns": "bns",
    "04-bss": "bss",
    "05-container-pack": "container-pack",
    "06-data-store": "data-store",
    "07-management-iam": "management",
}

# 챕터별 유효 topic 목록 (question-taxonomy.md §4 기준)
CHAPTER_TOPICS: dict[str, list[str]] = {
    "01-cloud-fundamentals": [
        "cloud-model", "deployment-model", "region-az", "pricing-model", "shared-responsibility",
    ],
    "02-bcs": [
        "vm-overview", "instance-type", "image", "public-ip", "bare-metal", "gpu", "storage-attachment",
    ],
    "03-bns": [
        "vpc", "subnet", "security-group", "load-balancer", "dns", "transit-gateway", "direct-connect",
    ],
    "04-bss": [
        "block-storage", "object-storage", "file-storage", "storage-comparison", "backup",
    ],
    "05-container-pack": [
        "kubernetes-overview", "cluster", "container-registry", "node-group",
    ],
    "06-data-store": [
        "mysql", "postgresql", "redis", "mongodb", "db-comparison", "ha-backup",
    ],
    "07-management-iam": [
        "iam-overview", "iam-policy", "monitoring", "logging", "notification",
    ],
}

# 챕터별 키워드 (C-1 자동 감점 기준)
CHAPTER_KEYWORDS: dict[str, list[str]] = {
    "01-cloud-fundamentals": ["IaaS", "PaaS", "SaaS", "클라우드", "리전", "AZ", "가용", "공동 책임"],
    "02-bcs": ["VM", "Virtual Machine", "인스턴스", "Bare Metal", "GPU", "하이퍼바이저", "BCS"],
    "03-bns": ["VPC", "Subnet", "Load Balancer", "DNS", "Transit Gateway", "보안 그룹", "Security Group"],
    "04-bss": ["Block Storage", "Object Storage", "File Storage", "스토리지", "스냅샷", "BSS"],
    "05-container-pack": ["Kubernetes", "Container", "클러스터", "노드", "Registry", "Pod"],
    "06-data-store": ["MySQL", "PostgreSQL", "Redis", "MongoDB", "데이터베이스", "고가용성"],
    "07-management-iam": ["IAM", "모니터링", "로깅", "Monitoring", "Logging", "알림", "정책"],
}


# ---------------------------------------------------------------------------
# API 클라이언트
# ---------------------------------------------------------------------------

def get_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
        sys.exit(1)
    return anthropic.Anthropic(api_key=api_key)


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
당신은 KakaoCloud 문제은행의 엄격한 검증(verifier) 에이전트입니다.
제공된 [레퍼런스 문서]와 [문제]를 비교하여 할루시네이션 여부를 판단합니다.

중요: 제공된 레퍼런스 문서는 상세한 공식 기술 문서입니다.
문제의 내용이 레퍼런스 문서에 명확히 기반하고 있는지 엄격하게 검증해야 합니다.

FAIL 로 판단해야 하는 경우:
1. 정답, 해설, 오답 포인트의 내용 중 하나라도 레퍼런스 문서에서 명시적인 근거를 찾을 수 없거나 조금이라도 의심스러운 경우
2. 레퍼런스에 존재하지 않는 커맨드/URL/기능/스펙을 만들어낸 경우 (할루시네이션)
3. 일반적인 클라우드 지식이라 할지라도, 카카오클라우드 레퍼런스 문서에 언급되어 있지 않은 내용을 단정적으로 설명하는 경우

PASS 해야 하는 경우:
- 문제의 모든 내용(정답, 해설, 오답 포인트)이 레퍼런스 문서의 내용과 완벽하게 일치하고 명시적인 근거가 존재하는 경우

조금이라도 의심스럽거나 레퍼런스에서 명확한 근거를 찾을 수 없다면 무조건 FAIL로 판단하세요.

출력 형식 (정확히 두 줄, 다른 내용 없이):
PASS 또는 FAIL
이유: (한 줄, 50자 이내)

첫 번째 줄이 반드시 PASS 또는 FAIL 단어로 시작해야 합니다.
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
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=256,
            system=VERIFIER_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_content}],
        )
        response = message.content[0].text.strip()
        logger.log(f"VERIFY response: {response[:120]!r}")

        lines = [l.strip() for l in response.splitlines() if l.strip()]
        # 첫 번째 또는 마지막 줄에서 PASS/FAIL 탐색
        verdict = ""
        for line in lines:
            upper = line.upper()
            if "PASS" in upper and not "FAIL" in upper:
                verdict = "PASS"
                break
            elif "FAIL" in upper:
                verdict = "FAIL"
                break
        reason_line = next((l for l in lines if l.startswith("이유:") or l.startswith("reason:")), "이유: 불명")
        reason = reason_line.split(":", 1)[-1].strip()

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

