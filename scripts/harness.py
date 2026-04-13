"""
harness.py — 공통 기반 모듈
모든 파이프라인 스크립트가 공유하는 클라이언트, 로거, 유틸리티를 제공합니다.
"""
from __future__ import annotations

import os
import re
import sys
import yaml
from datetime import datetime
from pathlib import Path

import anthropic

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
    def __init__(self, agent_name: str, chapter: str = ""):
        self.agent_name = agent_name
        self.chapter = chapter
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_dir = ROOT / "logs" / agent_name
        log_dir.mkdir(parents=True, exist_ok=True)
        suffix = f"_{chapter}" if chapter else ""
        self.log_path = log_dir / f"{date_str}{suffix}.log"
        self._start = datetime.now()

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
    """frontmatter + body를 q{NNN}.md 포맷으로 저장."""
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    path.write_text(f"---\n{fm_str}---\n\n{body}\n", encoding="utf-8")


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
