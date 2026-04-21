"""
verify-sources.py — source URL 유효성 검증 스크립트
각 문제 파일의 source 필드 URL에 HTTP GET을 보내 상태 코드를 확인합니다.

사용법:
    python scripts/verify-sources.py --all
    python scripts/verify-sources.py --chapter 02-bcs
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import requests

from harness import ROOT, CHAPTER_TOPICS, load_question_file

ALLOWED_DOMAIN = "docs.kakaocloud.com"
REQUEST_DELAY = 0.3  # 요청 간 딜레이 (초) — 서버 부하 방지


def check_url(url: str) -> int | str:
    """URL의 HTTP 상태 코드를 반환. 접속 실패 시 'ERR' 반환."""
    try:
        r = requests.get(
            url,
            timeout=8,
            headers={"User-Agent": "Mozilla/5.0 (compatible; kc-question-bank/1.0)"},
            allow_redirects=True,
        )
        return r.status_code
    except requests.exceptions.Timeout:
        return "TIMEOUT"
    except Exception as e:
        return f"ERR({e})"


def verify_chapter(chapter: str) -> list[dict]:
    """챕터 내 모든 문제의 source URL을 검증하고 결과 목록 반환."""
    q_dir = ROOT / "questions" / chapter
    if not q_dir.exists():
        print(f"[SKIP] {chapter}: 디렉토리 없음")
        return []

    results = []
    for q_path in sorted(q_dir.glob("q[0-9][0-9][0-9].md")):
        fm, _ = load_question_file(q_path)
        source = str(fm.get("source") or "")
        status_val = fm.get("status", "unknown")

        if not source:
            results.append({
                "file": str(q_path.relative_to(ROOT)),
                "status": status_val,
                "url": "(없음)",
                "http": "NO_SOURCE",
            })
            continue

        if ALLOWED_DOMAIN not in source:
            results.append({
                "file": str(q_path.relative_to(ROOT)),
                "status": status_val,
                "url": source,
                "http": "WRONG_DOMAIN",
            })
            continue

        http_code = check_url(source)
        results.append({
            "file": str(q_path.relative_to(ROOT)),
            "status": status_val,
            "url": source,
            "http": http_code,
        })
        time.sleep(REQUEST_DELAY)

    return results


def print_results(results: list[dict], show_ok: bool = False) -> int:
    """결과를 출력하고 문제 항목 수를 반환."""
    issues = 0
    for r in results:
        http = r["http"]
        is_ok = http == 200
        if is_ok and not show_ok:
            continue
        marker = "✓" if is_ok else "✗"
        print(f"{marker}  {str(http):<10}  {r['status']:<8}  {r['file']}")
        if not is_ok:
            print(f"             URL: {r['url']}")
            issues += 1
    return issues


def main() -> None:
    parser = argparse.ArgumentParser(description="문제 source URL 유효성 검증")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--chapter", help="챕터 지정 (예: 02-bcs)")
    group.add_argument("--all", action="store_true", help="전체 챕터 검증")
    parser.add_argument("--show-ok", action="store_true", help="정상(200) 항목도 출력")
    args = parser.parse_args()

    chapters = list(CHAPTER_TOPICS.keys()) if args.all else [args.chapter]

    total_issues = 0
    for chapter in chapters:
        print(f"\n{'─'*60}")
        print(f"챕터: {chapter}")
        print(f"{'─'*60}")
        results = verify_chapter(chapter)
        issues = print_results(results, show_ok=args.show_ok)
        total_issues += issues
        ok_count = len([r for r in results if r["http"] == 200])
        print(f"\n  소계: 총 {len(results)}개 중 정상 {ok_count}개, 문제 {issues}개")

    print(f"\n{'='*60}")
    print(f"전체 문제 source URL 검증 완료 — 총 이슈: {total_issues}개")
    if total_issues > 0:
        print("  → source URL이 404인 문제는 할루시네이션 의심 대상입니다.")
        print("  → 해당 문제를 공식 문서와 직접 대조하여 수정 또는 폐기하세요.")
    sys.exit(1 if total_issues > 0 else 0)


if __name__ == "__main__":
    main()
