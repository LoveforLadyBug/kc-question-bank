"""
generate-questions.py — generator 에이전트
레퍼런스 문서와 출제 스펙을 바탕으로 문제 초안을 생성합니다.
AGENTS.md §3 규칙을 시스템 프롬프트와 코드 양쪽에서 강제합니다.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import yaml
from datetime import date
from pathlib import Path

from harness import (
    ROOT, CHAPTER_TOPICS, LOCAL_MODEL,
    get_client, AgentLogger,
    check_references_exist, get_next_question_id,
    load_question_file, save_question_file,
    extract_sections, parse_choices, token_jaccard,
    HALLUCINATION_SUSPECT, run_hallucination_checks,
)

MAX_BATCH = 10

# ---------------------------------------------------------------------------
# 시스템 프롬프트 — AGENTS.md §3 규칙을 직접 서술
# ---------------------------------------------------------------------------

# 로컬 LLM 전용 단순화 프롬프트 (exaone 등 소형 모델용)
# - 복잡한 규칙 대신 예시 1개로 포맷을 보여줌
# - YAML 프론트매터를 최소화
LOCAL_SYSTEM_PROMPT = """\
아래 형식을 정확히 따라 사용자가 요청한 수만큼 문제를 생성하세요.
형식 외의 말(인사, 설명, 주석)은 절대 쓰지 마세요. 오직 아래 형식만 출력하세요.

[형식 예시]
---
id: q001
chapter: 01-cloud-overview
topic: region-az
difficulty: 1
type: single
tags: [region-az, definition]
source: https://docs.kakaocloud.com/start/quickstart-guide/create-vpc
status: draft
created: 2026-04-27
reviewed_by: []
quality_score: ~
---

## 문제

카카오클라우드에서 VPC란 무엇인가?

## 보기

- A. 물리 서버를 임대하는 서비스
- B. 조직 전용의 논리적으로 격리된 가상 네트워크
- C. 컨테이너 오케스트레이션 플랫폼
- D. 데이터베이스 관리 서비스

## 정답

B

## 해설

VPC(Virtual Private Cloud)는 조직 전용의 가상 네트워크로, 다른 네트워크와 논리적으로 격리됩니다.
카카오클라우드의 다양한 리소스를 사용하려면 VPC를 먼저 생성해야 합니다.

## 오답 포인트

- A: 물리 서버 임대는 Bare Metal Server 서비스의 설명입니다.
- C: 컨테이너 오케스트레이션은 Container Pack(Kubernetes Engine)의 역할입니다.
- D: 데이터베이스 관리는 Data Store 서비스의 역할입니다.

[예시 끝]

규칙:
1. source는 반드시 아래 레퍼런스 문서에 등장하는 URL 중 하나여야 합니다.
2. status는 반드시 draft입니다.
3. 보기는 A, B, C, D 4개, 정답은 1개입니다.
4. difficulty는 1, 2, 3 중 하나입니다.
5. 문제는 "다음 중 틀린 것은?" 형식을 쓰지 않습니다.
6. 여러 문제 생성 시 각 문제 사이에 빈 줄을 두세요.
"""

SYSTEM_PROMPT = """\
당신은 KakaoCloud Essential Basic Course 문제은행의 generator 에이전트입니다.

역할: 카카오클라우드 공식 문서(llms.txt)와 출제 스펙을 바탕으로 문제 초안을 생성합니다.

출력 형식 (문제 1개):
---
id: {id}
chapter: {chapter}
topic: {topic}
difficulty: {1-3}
type: single
tags: [tag1, tag2]
source: https://docs.kakaocloud.com/...
evidence: |
  [여기에 정답을 뒷받침하는 llms.txt의 원문 문장을 그대로 인용]
status: draft
created: {YYYY-MM-DD}
reviewed_by: []
quality_score: ~
verify_result: ~
verify_reason: ~
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
2. evidence는 반드시 llms.txt의 원문 문장을 한 문장 이상 그대로 인용합니다. 요약, 파라프레이즈, 생략 금지.
3. status는 반드시 draft입니다. 절대 변경하지 않습니다.
4. type은 반드시 single, 보기 4개(A/B/C/D), 정답은 반드시 1개입니다.
5. "다음 중 틀린 것은?" 형식의 부정 문항을 사용하지 않습니다.
6. 보기에 "모두 맞다", "모두 틀리다", "해당 없음"을 포함하지 않습니다.
7. 오답 포인트는 오답 보기 개수(3개)만큼 반드시 작성합니다.
8. tags는 영문 소문자만 사용합니다. 서비스 태그 1~2개 + 인지 유형 태그 1~2개 = 총 2~4개.
9. 정답 보기가 다른 보기보다 3배 이상 길지 않도록 합니다 (힙트 유출 방지).
10. 공식 문서 문장을 그대로 복사하지 않습니다.
11. quality_score는 반드시 ~ (null)로 설정합니다.
12. topic은 반드시 사용자가 제공한 출제 스펙의 topic 목록 중 하나를 사용합니다. 임의로 만들지 않습니다.
13. 해설은 반드시 2줄 이상 작성합니다. 첫 번째 줄은 정답의 핵심 근거, 두 번째 줄은 보충 설명 또는 관련 개념을 추가합니다. 한 문장으로 끝내지 않습니다.
14. verify_result와 verify_reason은 반드시 ~ (null)로 설정합니다. (검증 시스템이 자동 기록)
"""


# ---------------------------------------------------------------------------
# 중복 감지
# ---------------------------------------------------------------------------

def is_duplicate(topic: str, choices_text: str, existing_paths: list[Path]) -> bool:
    """기존 active/review 문제와 topic + 보기의 Jaccard 유사도가 80% 이상이면 True."""
    for p in existing_paths:
        fm, body = load_question_file(p)
        if fm.get("status") not in ("active", "review"):
            continue
        if fm.get("topic") != topic:
            continue
        sections = extract_sections(body)
        if token_jaccard(choices_text, sections.get("보기", "")) >= 0.8:
            return True
    return False


# ---------------------------------------------------------------------------
# AI 응답 파싱
# ---------------------------------------------------------------------------

def parse_question_blocks(text: str) -> list[str]:
    """AI 응답 텍스트에서 문제 블록(YAML frontmatter + 본문) 목록 추출.

    AI 출력 형식 편차를 모두 처리:
    - 표준:          ---\\nYAML\\n---\\nbody
    - 빈줄 포함:     ---\\n\\nYAML\\n---\\n\\nbody
    - 종료선 없음:   ---\\nYAML\\n\\n## 문제\\nbody

    핵심 전략: frontmatter 시작은 --- 다음에 id: 필드가 오는 패턴으로 식별.
    이 방식이 닫는 ---와 여는 ---를 구별하는 가장 안정적인 방법.
    """
    blocks: list[str] = []

    # --- 다음에 (빈줄 선택적으로) id: 가 오는 위치에서 분리
    # 이 패턴이 매칭되는 --- 만이 frontmatter 시작
    split_pattern = re.compile(
        r"(?m)(?:^|\n)(?=---[ \t]*\n(?:[ \t]*\n)*[ \t]*id:)"
    )
    chunks = split_pattern.split(text)

    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk.startswith("---") or "## 문제" not in chunk:
            continue

        inner = chunk[3:]  # 첫 --- 제거

        # frontmatter 종료 --- 탐색 (본문 시작 전)
        closing = re.search(r"(?m)^---[ \t]*$", inner)
        if closing:
            yaml_part = inner[: closing.start()].strip()
            body_part = inner[closing.end() :].strip()
        else:
            # 닫는 --- 없을 때: 첫 ## 헤더 직전까지가 YAML
            first_header = re.search(r"(?m)^##\s+", inner)
            if not first_header:
                continue
            yaml_part = inner[: first_header.start()].strip()
            body_part = inner[first_header.start() :].strip()

        if not yaml_part or "## 문제" not in body_part:
            continue

        blocks.append(f"---\n{yaml_part}\n---\n\n{body_part}")

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

    # 로컬 LLM은 단순화된 프롬프트 + 레퍼런스 앞 4000자만 전달 (컨텍스트 과부하 방지)
    is_local = os.environ.get("LLM_PROVIDER", "anthropic").lower() == "local"
    if is_local:
        active_system_prompt = LOCAL_SYSTEM_PROMPT
        llms_for_prompt = llms_content[:4000]
        ids = ", ".join(f"q{next_id + i:03d}" for i in range(count))
        topics_list = ", ".join(CHAPTER_TOPICS.get(chapter, []))
        user_prompt = (
            f"chapter: {chapter}\n"
            f"사용 가능한 topic 목록: {topics_list}\n"
            f"생성할 문제 수: {count}개\n"
            f"부여할 ID: {ids}\n"
            f"오늘 날짜: {date.today().isoformat()}\n\n"
            f"[레퍼런스 문서]\n{llms_for_prompt}\n\n"
            f"위 레퍼런스를 바탕으로 {count}개의 문제를 형식에 맞게 생성하세요."
        )
        logger.log("[LOCAL] 단순화 프롬프트 + 레퍼런스 4000자 사용")
    else:
        active_system_prompt = SYSTEM_PROMPT
        user_prompt = build_user_prompt(
            chapter, topic, count, next_id, llms_content, spec_content, existing_summaries
        )

    client = get_client()
    logger.log(f"CALL {'local' if is_local else 'anthropic'} LLM API (count={count})")
    message = client.chat.completions.create(
        model=LOCAL_MODEL,
        max_tokens=8192,
        messages=[
            {"role": "system", "content": active_system_prompt},
            {"role": "user", "content": user_prompt}
        ],
    )
    response_text = message.choices[0].message.content
    logger.log(f"RECV {len(response_text)} chars")

    # --debug 플래그 시 raw 응답을 logs/에 저장
    import sys
    if "--debug" in sys.argv:
        debug_path = ROOT / "logs" / f"debug_raw_{chapter.replace('/', '_')}.txt"
        debug_path.write_text(response_text, encoding="utf-8")
        logger.log(f"[DEBUG] raw 응답 저장: {debug_path}")

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

        # Post-check 3: status / quality_score / verify 강제 (AGENTS.md §3)
        fm["status"] = "draft"
        fm["quality_score"] = None
        fm["verify_result"] = None
        fm["verify_reason"] = None

        # ── 할루시네이션 방지 3단계 검증 ────────────────────────────────────
        question_block = (
            f"---\n{yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)}"
            f"---\n\n{body}"
        )
        passed, failed_stage, reason = run_hallucination_checks(
            client=client,
            fm=fm,
            body=body,
            question_block=question_block,
            chapter=chapter,
            llms_content=llms_content,
            logger=logger,
        )

        if not passed:
            fm["status"] = HALLUCINATION_SUSPECT
            fm["verify_result"] = "FAIL"
            fm["verify_reason"] = f"[{failed_stage}] {reason}"
            logger.log(f"[HALLUCINATION-SUSPECT] {fm.get('id')} → {fm['verify_reason']}")
        else:
            fm["verify_result"] = "PASS"
            fm["verify_reason"] = None
        # ─────────────────────────────────────────────────────────────

        out_path = q_dir / f"{fm['id']}.md"
        save_question_file(out_path, fm, body)
        logger.log(f"WRITE {out_path} [verify={fm['verify_result']}]")
        existing_paths.append(out_path)
        saved += 1
    logger.log(f"DONE saved={saved}/{len(blocks)}")
    logger.end()


def main() -> None:
    parser = argparse.ArgumentParser(description="KakaoCloud 문제 초안 생성")
    parser.add_argument("--chapter", required=True, help="챕터 (예: 02-bcs)")
    parser.add_argument("--topic", default=None, help="토픽 지정 (예: vpc)")
    parser.add_argument("--count", type=int, default=5, help="생성 개수 (기본: 5, 최대: 10)")
    parser.add_argument("--debug", action="store_true", help="raw LLM 응답을 logs/에 저장")
    args = parser.parse_args()
    generate(args.chapter, args.topic, args.count)


if __name__ == "__main__":
    main()
