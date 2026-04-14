"""
generate-questions.py — generator 에이전트
레퍼런스 문서와 출제 스펙을 바탕으로 문제 초안을 생성합니다.
AGENTS.md §3 규칙을 시스템 프롬프트와 코드 양쪽에서 강제합니다.
"""
from __future__ import annotations

import argparse
import re
import sys
import yaml
from datetime import date
from pathlib import Path

from harness import (
    ROOT, CHAPTER_TOPICS,
    get_client, AgentLogger,
    check_references_exist, get_next_question_id,
    load_question_file, save_question_file,
    extract_sections, parse_choices,
)

MAX_BATCH = 10

# ---------------------------------------------------------------------------
# 시스템 프롬프트 — AGENTS.md §3 규칙을 직접 서술
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
당신은 KakaoCloud Essential Basic Course 문제은행의 generator 에이전트입니다.

역할: 카카오클라우드 공식 문서(llms.txt)와 출제 스펙을 바탕으로 문제 초안을 생성합니다.

출력 형식 (문제 1개):
---
id: {id}
chapter: {chapter}
topic: {topic}
difficulty: {1-5}
type: single
tags: [tag1, tag2]
source: https://docs.kakaocloud.com/...
status: draft
created: {YYYY-MM-DD}
reviewed_by: []
quality_score: ~
---

## 문제

{문제 본문}

## 보기

- A. {보기}
- B. {보기}
- C. {보기}
- D. {보기}

## 정답

{A/B/C/D}

## 해설

{정답 이유 설명, 2줄 이상}

## 오답 포인트

- B: {왜 틀린지}
- C: {왜 틀린지}
- D: {왜 틀린지}

여러 문제 생성 시 각 문제 사이에 빈 줄 하나를 둡니다.

필수 규칙:
1. source는 반드시 사용자가 제공한 llms.txt의 SOURCE URL 중 하나여야 합니다. 추측하거나 만들지 않습니다.
2. status는 반드시 draft입니다. 절대 변경하지 않습니다.
3. type은 반드시 single, 보기 4개(A/B/C/D), 정답은 반드시 1개입니다.
4. "다음 중 틀린 것은?" 형식의 부정 문항을 사용하지 않습니다.
5. 보기에 "모두 맞다", "모두 틀리다", "해당 없음"을 포함하지 않습니다.
6. 오답 포인트는 오답 보기 개수(3개)만큼 반드시 작성합니다.
7. tags는 영문 소문자만 사용합니다. 서비스 태그 1~2개 + 인지 유형 태그 1~2개 = 총 2~4개.
8. 정답 보기가 다른 보기보다 3배 이상 길지 않도록 합니다 (힌트 유출 방지).
9. 공식 문서 문장을 그대로 복사하지 않습니다.
10. quality_score는 반드시 ~ (null)로 설정합니다.
11. topic은 반드시 사용자가 제공한 출제 스펙의 topic 목록 중 하나를 사용합니다. 임의로 만들지 않습니다.
12. 해설은 반드시 2줄 이상 작성합니다. 첫 번째 줄은 정답의 핵심 근거, 두 번째 줄은 보충 설명 또는 관련 개념을 추가합니다. 한 문장으로 끝내지 않습니다.
"""


# ---------------------------------------------------------------------------
# 중복 감지
# ---------------------------------------------------------------------------

def _token_similarity(a: str, b: str) -> float:
    ta = set(a.lower().split())
    tb = set(b.lower().split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(len(ta), len(tb))


def is_duplicate(topic: str, choices_text: str, existing_paths: list[Path]) -> bool:
    """기존 active/review 문제와 topic + 보기가 80% 이상 유사하면 True."""
    for p in existing_paths:
        fm, body = load_question_file(p)
        if fm.get("status") not in ("active", "review"):
            continue
        if fm.get("topic") != topic:
            continue
        sections = extract_sections(body)
        if _token_similarity(choices_text, sections.get("보기", "")) >= 0.8:
            return True
    return False


# ---------------------------------------------------------------------------
# AI 응답 파싱
# ---------------------------------------------------------------------------

def parse_question_blocks(text: str) -> list[str]:
    """AI 응답 텍스트에서 문제 블록(YAML frontmatter + 본문) 목록 추출."""
    blocks: list[str] = []
    # 빈 줄로 구분된 블록 분리, --- 로 시작하는 블록만 선택
    raw = re.split(r"\n{2,}(?=---\n)", text.strip())
    for block in raw:
        block = block.strip()
        if block.startswith("---") and "## 문제" in block:
            blocks.append(block)
    return blocks


# ---------------------------------------------------------------------------
# 유저 프롬프트
# ---------------------------------------------------------------------------

def build_user_prompt(
    chapter: str,
    topic: str | None,
    count: int,
    next_id: int,
    llms_content: str,
    spec_content: str,
    existing_summaries: list[str],
) -> str:
    topic_line = f"- topic: {topic}" if topic else "- topic: 출제 스펙에 정의된 토픽을 균형있게 선택"
    ids = ", ".join(f"q{next_id + i:03d}" for i in range(count))

    dup_section = ""
    if existing_summaries:
        dup_section = (
            "\n## 중복 방지: 기존 문제 요약\n"
            "아래 문제들과 topic+보기가 80% 이상 유사한 문제는 생성하지 마세요.\n\n"
            + "\n".join(existing_summaries)
            + "\n"
        )

    return (
        f"## 생성 요청\n"
        f"- chapter: {chapter}\n"
        f"{topic_line}\n"
        f"- 생성 개수: {count}개\n"
        f"- 부여할 ID: {ids}\n"
        f"- 오늘 날짜: {date.today().isoformat()}\n"
        f"{dup_section}\n"
        f"## 출제 스펙\n{spec_content}\n\n"
        f"## 레퍼런스 문서 (공식 문서 원문)\n{llms_content}\n\n"
        f"위 레퍼런스와 출제 스펙을 바탕으로 {count}개 문제를 생성하세요."
    )


# ---------------------------------------------------------------------------
# 메인 로직
# ---------------------------------------------------------------------------

def generate(chapter: str, topic: str | None, count: int) -> None:
    logger = AgentLogger("generator", chapter)
    logger.start(chapter=chapter, topic=topic or "all", count=count)

    # Pre-check 1: references 존재 여부 (없으면 에러 종료)
    ref = check_references_exist(chapter)

    # Pre-check 2: 배치 상한
    if count > MAX_BATCH:
        logger.log(f"[ERROR] 배치 상한 초과: {count} > {MAX_BATCH}. --count 10 이하로 지정하세요.")
        sys.exit(1)

    # Pre-check 3: topic 유효성
    if topic and topic not in CHAPTER_TOPICS.get(chapter, []):
        valid = ", ".join(CHAPTER_TOPICS.get(chapter, []))
        logger.log(f"[ERROR] 알 수 없는 topic: {topic}. 유효한 값: {valid}")
        sys.exit(1)

    llms_content = ref.read_text(encoding="utf-8")
    logger.log(f"READ {ref} ({len(llms_content)} chars)")

    spec_path = ROOT / "docs" / "product-specs" / f"{chapter}.md"
    spec_content = spec_path.read_text(encoding="utf-8") if spec_path.exists() else "(출제 스펙 파일 없음)"
    logger.log(f"READ {spec_path}")

    # 기존 문제 로드 (중복 감지용)
    q_dir = ROOT / "questions" / chapter
    existing_paths = sorted(q_dir.glob("q[0-9][0-9][0-9].md")) if q_dir.exists() else []
    existing_summaries = []
    for p in existing_paths:
        fm, body = load_question_file(p)
        if fm.get("status") in ("active", "review"):
            sections = extract_sections(body)
            existing_summaries.append(
                f"[{fm.get('id')}] topic={fm.get('topic')} 보기: {sections.get('보기', '')[:80]}"
            )

    next_id = get_next_question_id(chapter)
    user_prompt = build_user_prompt(
        chapter, topic, count, next_id, llms_content, spec_content, existing_summaries
    )

    client = get_client()
    logger.log(f"CALL claude API (count={count})")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    response_text = message.content[0].text
    logger.log(f"RECV {len(response_text)} chars")

    blocks = parse_question_blocks(response_text)
    logger.log(f"PARSED {len(blocks)} question block(s)")

    q_dir.mkdir(parents=True, exist_ok=True)
    saved = 0
    for block in blocks:
        # YAML frontmatter + body 분리
        try:
            parts = block.split("---", 2)
            if len(parts) < 3:
                logger.log(f"[WARN] frontmatter 구분선 없음, 건너뜀: {block[:60]!r}")
                continue
            fm = yaml.safe_load(parts[1]) or {}
            body = parts[2].strip()
        except Exception as e:
            logger.log(f"[WARN] YAML 파싱 실패 ({e}), 건너뜀")
            continue

        # Post-check 1: source 검증 (AGENTS.md §3 — source 없으면 에러)
        source = str(fm.get("source") or "")
        if not source or not source.startswith("https://docs.kakaocloud.com"):
            logger.log(f"[ERROR] source 필드가 없거나 유효하지 않습니다: id={fm.get('id')}")
            logger.log(f"        레퍼런스 파일을 먼저 확인하세요: {ref}")
            continue

        # Post-check 2: 중복 감지
        sections = extract_sections(body)
        if is_duplicate(str(fm.get("topic", "")), sections.get("보기", ""), existing_paths):
            logger.log(f"[SKIP] 중복 감지: {fm.get('id')} topic={fm.get('topic')}")
            continue

        # Post-check 3: status / quality_score 강제 (AGENTS.md §3)
        fm["status"] = "draft"
        fm["quality_score"] = None

        out_path = q_dir / f"{fm['id']}.md"
        save_question_file(out_path, fm, body)
        logger.log(f"WRITE {out_path}")
        existing_paths.append(out_path)
        saved += 1

    logger.log(f"DONE saved={saved}/{len(blocks)}")
    logger.end()


def main() -> None:
    parser = argparse.ArgumentParser(description="KakaoCloud 문제 초안 생성")
    parser.add_argument("--chapter", required=True, help="챕터 (예: 02-bcs)")
    parser.add_argument("--topic", default=None, help="토픽 지정 (예: vpc)")
    parser.add_argument("--count", type=int, default=5, help="생성 개수 (기본: 5, 최대: 10)")
    args = parser.parse_args()
    generate(args.chapter, args.topic, args.count)


if __name__ == "__main__":
    main()
