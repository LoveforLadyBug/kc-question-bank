"""
build-exam.py — 시험 세트 조립 스크립트
AI를 사용하지 않는 순수 조립 스크립트입니다.
status: active 문제만 포함, deprecated 문제 자동 제외.
"""
from __future__ import annotations

import argparse
import random
from datetime import date
from pathlib import Path

from harness import ROOT, AgentLogger, load_question_file, extract_sections

# 모의시험 챕터별 출제 문항 수 (40문항 기준, question-taxonomy.md §2)
MOCK_DISTRIBUTION: dict[str, int] = {
    "01-cloud-fundamentals": 6,
    "02-bcs":                8,
    "03-bns":                8,
    "04-bss":                6,
    "05-container-pack":     4,
    "06-data-store":         4,
    "07-management-iam":     4,
}


# ---------------------------------------------------------------------------
# 문제 로드
# ---------------------------------------------------------------------------

def load_active_questions(
    chapters: list[str] | None = None,
    tags: list[str] | None = None,
) -> list[dict]:
    """active 문제를 로드. chapter/tags 필터 적용."""
    q_root = ROOT / "questions"
    if not q_root.exists():
        return []

    target_chapters = chapters or sorted(d.name for d in q_root.iterdir() if d.is_dir())
    result: list[dict] = []

    for chapter in target_chapters:
        q_dir = q_root / chapter
        if not q_dir.exists():
            continue
        for p in sorted(q_dir.glob("q[0-9][0-9][0-9].md")):
            fm, body = load_question_file(p)
            if fm.get("status") != "active":
                continue
            if tags:
                q_tags = fm.get("tags") or []
                if not any(t in q_tags for t in tags):
                    continue
            result.append({"fm": fm, "body": body})

    return result


# ---------------------------------------------------------------------------
# 문제 포맷
# ---------------------------------------------------------------------------

def format_question(q: dict, index: int) -> str:
    """문제 본문 + 보기만 출력 (정답/해설 미포함)."""
    fm       = q["fm"]
    sections = extract_sections(q["body"])
    lines = [
        f"### {index}. [{fm.get('id')}] 난이도 {fm.get('difficulty', '?')}",
        "",
        sections.get("문제", "(문제 없음)"),
        "",
        sections.get("보기", "(보기 없음)"),
        "",
    ]
    return "\n".join(lines)


def format_answer_key(questions: list[dict]) -> str:
    """정답표 포맷."""
    lines = ["## 정답표", ""]
    for i, q in enumerate(questions, 1):
        fm       = q["fm"]
        sections = extract_sections(q["body"])
        answer   = sections.get("정답", "?").strip()
        lines.append(f"{i}. {fm.get('id')} — {answer}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 모드별 빌드
# ---------------------------------------------------------------------------

def build_weekly(chapter: str, count: int = 10) -> tuple[str, Path]:
    questions = load_active_questions(chapters=[chapter])
    if not questions:
        print(f"[ERROR] {chapter}에 active 문제가 없습니다.")
        return "", ROOT / "exams" / "weekly" / f"{chapter}.md"

    selected = random.sample(questions, min(count, len(questions)))
    lines = [
        f"# 주차별 스터디 — {chapter}",
        f"생성일: {date.today().isoformat()} | 문제 수: {len(selected)}",
        "",
    ]
    for i, q in enumerate(selected, 1):
        lines.append(format_question(q, i))

    lines += ["---", "", format_answer_key(selected)]
    out = ROOT / "exams" / "weekly" / f"{chapter}.md"
    return "\n".join(lines), out


def build_random(tags: list[str], count: int = 10) -> tuple[str, Path]:
    questions = load_active_questions(tags=tags)
    if not questions:
        print(f"[ERROR] 태그 {tags}에 해당하는 active 문제가 없습니다.")
        return "", ROOT / "exams" / f"random-{'-'.join(tags[:2])}.md"

    selected = random.sample(questions, min(count, len(questions)))
    tag_str  = ", ".join(tags)
    lines = [
        f"# 랜덤 출제 — [{tag_str}]",
        f"생성일: {date.today().isoformat()} | 문제 수: {len(selected)}",
        "",
    ]
    for i, q in enumerate(selected, 1):
        lines.append(format_question(q, i))

    lines += ["---", "", format_answer_key(selected)]
    out = ROOT / "exams" / f"random-{'-'.join(tags[:2])}.md"
    return "\n".join(lines), out


def build_mock(count: int = 40) -> tuple[str, Path]:
    all_selected: list[dict] = []

    for chapter, target in MOCK_DISTRIBUTION.items():
        questions = load_active_questions(chapters=[chapter])
        if not questions:
            print(f"[WARN] {chapter}: active 문제 없음 — 건너뜀")
            continue
        # 난이도 3 이상 우선 포함 (core-beliefs.md §4 분포 권장)
        hi = [q for q in questions if (q["fm"].get("difficulty") or 0) >= 3]
        lo = [q for q in questions if (q["fm"].get("difficulty") or 0) < 3]
        pool = hi + lo
        all_selected.extend(random.sample(pool, min(target, len(pool))))

    random.shuffle(all_selected)

    lines = [
        "# 모의시험",
        f"생성일: {date.today().isoformat()} | 총 {len(all_selected)}문항",
        "",
    ]
    for i, q in enumerate(all_selected, 1):
        lines.append(format_question(q, i))

    lines += ["---", "", format_answer_key(all_selected)]

    existing = list((ROOT / "exams").glob("mock-exam-*.md"))
    next_num = len(existing) + 1
    out = ROOT / "exams" / f"mock-exam-{next_num:02d}.md"
    return "\n".join(lines), out


# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="KakaoCloud 시험 세트 생성")
    parser.add_argument("--mode", required=True, choices=["weekly", "random", "mock"])
    parser.add_argument("--chapter", default=None, help="챕터 지정 (weekly 모드 필수)")
    parser.add_argument("--tags", default=None, help="콤마 구분 태그 (random 모드 필수, 예: vpc,load-balancer)")
    parser.add_argument("--count", type=int, default=None, help="문제 수 (기본: weekly=10, mock=40)")
    parser.add_argument("--output", default=None, help="출력 파일 경로 지정")
    args = parser.parse_args()

    logger = AgentLogger("build-exam")
    logger.start(mode=args.mode)

    if args.mode == "weekly":
        if not args.chapter:
            logger.log("[ERROR] --mode weekly 는 --chapter 가 필요합니다.")
            return
        content, out = build_weekly(args.chapter, args.count or 10)

    elif args.mode == "random":
        if not args.tags:
            logger.log("[ERROR] --mode random 은 --tags 가 필요합니다.")
            return
        tags = [t.strip() for t in args.tags.split(",")]
        content, out = build_random(tags, args.count or 10)

    else:  # mock
        content, out = build_mock(args.count or 40)

    if args.output:
        out = Path(args.output)

    if content:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        logger.log(f"WRITE {out}")

    logger.end()


if __name__ == "__main__":
    main()
