"""
validate-quality.py — validator 에이전트
QUALITY_SCORE.md 기준으로 문제 품질을 자동 채점합니다.
A·B·C-1·D·E 항목 전부 규칙 기반 코드로 처리합니다 (AI 호출 없음).
AGENTS.md §4 규칙: status→active 변경 금지, 본문 수정 금지.
"""
from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

import requests

from harness import (
    ROOT, CHAPTER_TOPICS, CHAPTER_KEYWORDS,
    AgentLogger, load_question_file, save_question_file,
    extract_sections, parse_choices,
)

REQUIRED_FM_FIELDS = ["id", "chapter", "topic", "difficulty", "type", "tags", "source", "status", "created"]
REQUIRED_SECTIONS  = ["문제", "보기", "정답", "해설", "오답 포인트"]


# ---------------------------------------------------------------------------
# 항목별 채점 함수
# ---------------------------------------------------------------------------

def score_a(fm: dict) -> tuple[int, str | None]:
    """A. 출처 명확성 (20점)"""
    source = str(fm.get("source") or "")
    if not source or not source.startswith("https://docs.kakaocloud.com"):
        return 0, "A_source: source 필드 없음 또는 유효하지 않은 URL"
    try:
        r = requests.head(source, timeout=5, allow_redirects=True)
        if r.status_code == 200:
            return 20, None
        return 10, f"A_source: URL 접근 불가 (HTTP {r.status_code})"
    except Exception:
        return 10, "A_source: URL 접근 타임아웃"


def score_b(fm: dict, sections: dict, choices: dict) -> tuple[int, list[str]]:
    """B. 문제 구조 완결성 (20점) — 섹션 5개 × 4점"""
    issues: list[str] = []
    deduct = 0

    checks = {
        "문제":       lambda: len(sections.get("문제", "").strip().splitlines()) >= 1,
        "보기":       lambda: len(choices) >= 2,
        "정답":       lambda: sections.get("정답", "").strip() in choices,
        "해설":       lambda: len(sections.get("해설", "").strip().splitlines()) >= 2,
        "오답 포인트": lambda: _wrong_point_count(sections.get("오답 포인트", "")) >= len(choices) - 1,
    }
    for sec, check in checks.items():
        if not check():
            deduct += 4
            issues.append(f"B_structure: ## {sec} 섹션 불완전")

    # frontmatter 필수 필드 누락 → 추가 -4점 (최대 20점 한도)
    missing = [f for f in REQUIRED_FM_FIELDS if not fm.get(f)]
    if missing:
        deduct = min(deduct + 4, 20)
        issues.append(f"B_structure: frontmatter 필수 필드 누락: {', '.join(missing)}")

    return max(0, 20 - deduct), issues


def score_c1(fm: dict, sections: dict, choices: dict) -> tuple[int, list[str]]:
    """C-1. 오답 보기 자동 감점 (25점 기준, 각 조건 -5점)"""
    issues: list[str] = []
    deduct = 0
    chapter = str(fm.get("chapter", ""))
    answer_key = sections.get("정답", "").strip()
    answer_text = choices.get(answer_key, "")
    wrong_choices = {k: v for k, v in choices.items() if k != answer_key}

    # C-1-1: 정답과 단어 90% 이상 겹치는 오답 존재
    for v in wrong_choices.values():
        if _token_overlap(answer_text, v) >= 0.9:
            deduct += 5
            issues.append("C_choices: 오답 보기 중 정답과 단어 90% 이상 겹치는 항목 존재 (-5점)")
            break

    # C-1-2: 챕터 키워드가 하나도 없는 오답 존재
    keywords = CHAPTER_KEYWORDS.get(chapter, [])
    if keywords:
        for v in wrong_choices.values():
            if not any(kw.lower() in v.lower() for kw in keywords):
                deduct += 5
                issues.append("C_choices: 오답 보기 중 챕터 키워드 없는 항목 존재 (-5점)")
                break

    # C-1-3: 보기 간 길이 편차 3배 이상
    lengths = [len(v) for v in choices.values() if v]
    if len(lengths) >= 2 and max(lengths) >= min(lengths) * 3:
        deduct += 5
        issues.append("C_choices: 보기 간 길이 편차 3배 이상 (힌트 유출 가능성) (-5점)")

    return max(0, 25 - deduct), issues


def score_d(sections: dict, choices: dict) -> tuple[int, str | None]:
    """D. 해설 충실도 (20점)"""
    explanation = sections.get("해설", "")
    wrong_points = sections.get("오답 포인트", "")
    has_explanation = len(explanation.strip().splitlines()) >= 2
    wrong_count = _wrong_point_count(wrong_points)
    expected = max(len(choices) - 1, 0)

    if not has_explanation:
        return 0, "D_explanation: 해설 없음"
    if wrong_count == 0:
        return 10, "D_explanation: 오답 포인트 없음"
    if wrong_count < expected:
        return 15, f"D_explanation: 오답 포인트 일부 누락 ({wrong_count}/{expected}개)"
    return 20, None


def score_e(fm: dict) -> tuple[int, str | None]:
    """E. 챕터 적합성 (15점)"""
    chapter = str(fm.get("chapter", ""))
    topic   = str(fm.get("topic", ""))
    tags    = fm.get("tags") or []

    if chapter not in CHAPTER_TOPICS:
        return 0, f"E_chapter: chapter 값 '{chapter}'이 유효하지 않음"

    valid_topics = CHAPTER_TOPICS[chapter]
    if topic in valid_topics:
        return 15, None

    # topic 없지만 tags 중 하나가 챕터 키워드와 매칭
    keywords = [kw.lower() for kw in CHAPTER_KEYWORDS.get(chapter, [])]
    if any(any(k in t.lower() for k in keywords) for t in tags):
        return 10, f"E_chapter: topic '{topic}' 불일치, tags로 부분 매칭"

    return 5, f"E_chapter: topic '{topic}'이 출제 스펙 목록에 없음"


# ---------------------------------------------------------------------------
# 파일 단위 검증
# ---------------------------------------------------------------------------

def validate_file(path: Path, force: bool = False) -> dict | None:
    """단일 문제 파일 채점. 결과 dict 반환 (스킵 시 None)."""
    fm, body = load_question_file(path)
    status = fm.get("status", "")

    if status == "deprecated":
        return None
    # active 문제는 --force 없이 스킵 (AGENTS.md §4)
    if status == "active" and not force:
        return None

    sections = extract_sections(body)
    choices  = parse_choices(sections.get("보기", ""))

    s_a, issue_a   = score_a(fm)
    s_b, issues_b  = score_b(fm, sections, choices)
    s_c, issues_c  = score_c1(fm, sections, choices)
    s_d, issue_d   = score_d(sections, choices)
    s_e, issue_e   = score_e(fm)

    total      = s_a + s_b + s_c + s_d + s_e
    all_issues = [i for i in [issue_a, *issues_b, *issues_c, issue_d, issue_e] if i]

    # frontmatter 업데이트 (본문은 건드리지 않음 — AGENTS.md §4)
    fm["quality_score"] = total
    fm["quality_breakdown"] = {
        "A_source":      s_a,
        "B_structure":   s_b,
        "C_choices":     s_c,
        "D_explanation": s_d,
        "E_chapter":     s_e,
    }
    fm["quality_checked_at"] = date.today().isoformat()

    if all_issues:
        fm["quality_issues"] = all_issues
    elif "quality_issues" in fm:
        del fm["quality_issues"]

    # 75점 미만이면 draft → review 강등 (active로는 절대 변경 안 함)
    if total < 75 and status == "draft":
        fm["status"] = "review"

    save_question_file(path, fm, body)
    return {"id": fm.get("id"), "score": total, "status": fm["status"], "issues": all_issues}


# ---------------------------------------------------------------------------
# 리뷰 노트 생성
# ---------------------------------------------------------------------------

def write_review_notes(chapter: str, results: list[dict]) -> None:
    q_dir = ROOT / "questions" / chapter
    notes_path = q_dir / "_review-notes.md"
    today = date.today().isoformat()
    lines = [
        f"# _review-notes.md",
        f"# {chapter} 챕터 리뷰 노트 — {today}",
        "",
        "| 문제 ID | 점수 | 주요 이슈 | 담당자 |",
        "|---------|------|-----------|--------|",
    ]
    for r in results:
        issue_summary = r["issues"][0] if r["issues"] else "—"
        lines.append(f"| {r['id']} | {r['score']} | {issue_summary} | (미배정) |")
    notes_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------

def _wrong_point_count(wrong_points_text: str) -> int:
    return len([l for l in wrong_points_text.splitlines() if re.match(r"^-\s*[A-D]:", l.strip())])


def _token_overlap(a: str, b: str) -> float:
    ta = set(a.lower().split())
    tb = set(b.lower().split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(len(ta), len(tb))


# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="KakaoCloud 문제 품질 검증")
    parser.add_argument("--chapter", default=None, help="챕터 지정 (예: 02-bcs). 미지정 시 전체")
    parser.add_argument("--status", default=None, help="특정 status만 검증 (예: draft)")
    parser.add_argument("--force", action="store_true", help="active 문제 강제 재채점")
    args = parser.parse_args()

    logger = AgentLogger("validator", args.chapter or "all")
    logger.start(chapter=args.chapter or "all", status=args.status or "all", force=args.force)

    q_root = ROOT / "questions"
    if args.chapter:
        chapters = [args.chapter]
    else:
        chapters = sorted(d.name for d in q_root.iterdir() if d.is_dir()) if q_root.exists() else []

    for chapter in chapters:
        q_dir = q_root / chapter
        if not q_dir.exists():
            continue

        paths = sorted(q_dir.glob("q[0-9][0-9][0-9].md"))
        if args.status:
            paths = [p for p in paths if load_question_file(p)[0].get("status") == args.status]

        results: list[dict] = []
        for p in paths:
            result = validate_file(p, force=args.force)
            if result is None:
                continue
            logger.log(f"SCORE {p.name}: {result['score']}점 status={result['status']}")
            results.append(result)

        if results:
            write_review_notes(chapter, results)
            logger.log(f"WRITE questions/{chapter}/_review-notes.md ({len(results)}건)")

    logger.end()


if __name__ == "__main__":
    main()
