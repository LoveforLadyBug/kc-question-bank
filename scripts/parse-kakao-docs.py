"""
parse-kakao-docs.py — parser 에이전트
카카오클라우드 공식 문서를 fetch해 llms.txt 포맷으로 저장합니다.
AGENTS.md §2 규칙: docs.kakaocloud.com 외 도메인 fetch 금지, 원문 그대로 저장.
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup

from harness import ROOT, CHAPTER_REF_SLUG, AgentLogger, ref_path, load_question_file

ALLOWED_DOMAIN = "docs.kakaocloud.com"

# 챕터별 크롤링 대상 URL 목록
# 공식 docs 사이드바 기준으로 세부 문서 URL까지 포함
CHAPTER_URLS: dict[str, list[tuple[str, str]]] = {
    "01-cloud-fundamentals": [
        ("https://docs.kakaocloud.com/service", "Cloud Fundamentals"),
        ("https://docs.kakaocloud.com/start", "Cloud Fundamentals"),
    ],
    "02-bcs": [
        ("https://docs.kakaocloud.com/service/bcs", "Beyond Compute Service"),
        ("https://docs.kakaocloud.com/service/bcs/instance-overview", "Beyond Compute Service"),
        ("https://docs.kakaocloud.com/service/bcs/bcs-specifications", "Beyond Compute Service"),
        ("https://docs.kakaocloud.com/service/bcs/vm/vm-overview", "Beyond Compute Service"),
        ("https://docs.kakaocloud.com/service/bcs/vm/vm-main", "Beyond Compute Service"),
        ("https://docs.kakaocloud.com/service/bcs/vm/vm-architecture", "Beyond Compute Service"),
        ("https://docs.kakaocloud.com/service/bcs/vm/vm-monitoring", "Beyond Compute Service"),
        ("https://docs.kakaocloud.com/service/bcs/vm/vm-pricing", "Beyond Compute Service"),
        ("https://docs.kakaocloud.com/service/bcs/bms/bms-overview", "Beyond Compute Service"),
        ("https://docs.kakaocloud.com/service/bcs/bms/bms-main", "Beyond Compute Service"),
        ("https://docs.kakaocloud.com/service/bcs/bms/bms-pricing", "Beyond Compute Service"),
    ],
    "03-bns": [
        ("https://docs.kakaocloud.com/service/networking", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/dns", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/lb", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/tgw", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/vpc", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/vpc/how-to-guides", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/vpc/main/vpc-subnet", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/vpc/vpc-overview", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/vpc/vpc-pricing", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/vpc/vpc-release-note", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/lb/how-to-guides/alb", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/lb/lb-overview", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/lb/lb-pricing", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/lb/lb-release-note", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/lb/lb-troubleshoot", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/lb/main/lb-listener", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/dns/dns-main", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/dns/dns-overview", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/dns/dns-pricing", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/dns/dns-release-note", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/dns/how-to-guides", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/tgw/how-to-guides", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/tgw/tgw-main", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/tgw/tgw-overview", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/tgw/tgw-pricing", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/tgw/tgw-release-note", "Beyond Networking Service"),
        ("https://docs.kakaocloud.com/service/networking/tgw/tgw-sharing", "Beyond Networking Service"),
    ],
    "04-bss": [
        ("https://docs.kakaocloud.com/service/storage", "Beyond Storage Service"),
        ("https://docs.kakaocloud.com/service/storage/file-storage", "Beyond Storage Service"),
        ("https://docs.kakaocloud.com/service/storage/object-storage", "Beyond Storage Service"),
        ("https://docs.kakaocloud.com/service/storage/object-storage/api", "Beyond Storage Service"),
        ("https://docs.kakaocloud.com/service/storage/object-storage/how-to-guides", "Beyond Storage Service"),
        ("https://docs.kakaocloud.com/service/storage/object-storage/object-storage-main", "Beyond Storage Service"),
        ("https://docs.kakaocloud.com/service/storage/object-storage/object-storage-overview", "Beyond Storage Service"),
        ("https://docs.kakaocloud.com/service/storage/object-storage/object-storage-pricing", "Beyond Storage Service"),
        ("https://docs.kakaocloud.com/service/storage/object-storage/object-storage-release-note", "Beyond Storage Service"),
        ("https://docs.kakaocloud.com/service/storage/object-storage/object-storage-troubleshoot", "Beyond Storage Service"),
        ("https://docs.kakaocloud.com/service/storage/file-storage/file-storage-main", "Beyond Storage Service"),
        ("https://docs.kakaocloud.com/service/storage/file-storage/file-storage-overview", "Beyond Storage Service"),
        ("https://docs.kakaocloud.com/service/storage/file-storage/file-storage-pricing", "Beyond Storage Service"),
        ("https://docs.kakaocloud.com/service/storage/file-storage/file-storage-release-note", "Beyond Storage Service"),
        ("https://docs.kakaocloud.com/service/storage/file-storage/file-storage-troubleshoot", "Beyond Storage Service"),
        ("https://docs.kakaocloud.com/service/storage/file-storage/how-to-guides", "Beyond Storage Service"),
    ],
    "05-container-pack": [
        ("https://docs.kakaocloud.com/service/container-pack", "Container Pack"),
        ("https://docs.kakaocloud.com/service/container-pack/cr", "Container Pack"),
        ("https://docs.kakaocloud.com/service/container-pack/k8se", "Container Pack"),
        ("https://docs.kakaocloud.com/service/container-pack/k8se/how-to-guides", "Container Pack"),
        ("https://docs.kakaocloud.com/service/container-pack/k8se/k8se-main", "Container Pack"),
        ("https://docs.kakaocloud.com/service/container-pack/k8se/k8se-overview", "Container Pack"),
        ("https://docs.kakaocloud.com/service/container-pack/k8se/k8se-pricing", "Container Pack"),
        ("https://docs.kakaocloud.com/service/container-pack/k8se/k8se-release-note", "Container Pack"),
        ("https://docs.kakaocloud.com/service/container-pack/k8se/k8se-troubleshoot", "Container Pack"),
        ("https://docs.kakaocloud.com/service/container-pack/cr/cr-main", "Container Pack"),
        ("https://docs.kakaocloud.com/service/container-pack/cr/cr-overview", "Container Pack"),
        ("https://docs.kakaocloud.com/service/container-pack/cr/cr-pricing", "Container Pack"),
        ("https://docs.kakaocloud.com/service/container-pack/cr/cr-release-note", "Container Pack"),
        ("https://docs.kakaocloud.com/service/container-pack/cr/cr-troubleshoot", "Container Pack"),
        ("https://docs.kakaocloud.com/service/container-pack/cr/how-to-guides", "Container Pack"),
    ],
    "06-data-store": [
        ("https://docs.kakaocloud.com/service/data-store", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/memstore", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/mysql", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/postgresql", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/mysql/how-to-guides", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/mysql/mysql-main", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/mysql/mysql-overview", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/mysql/mysql-pricing", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/mysql/mysql-release-note", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/mysql/mysql-troubleshoot", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/postgresql/how-to-guides", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/postgresql/postgresql-main", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/postgresql/postgresql-overview", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/postgresql/postgresql-pricing", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/postgresql/postgresql-release-note", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/postgresql/postgresql-troubleshoot", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/memstore/api", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/memstore/how-to-guides", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/memstore/memstore-cve", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/memstore/memstore-main", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/memstore/memstore-overview", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/memstore/memstore-pricing", "Data Store"),
        ("https://docs.kakaocloud.com/service/data-store/memstore/memstore-release-note", "Data Store"),
    ],
    "07-management-iam": [
        ("https://docs.kakaocloud.com/service/management", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/advanced-managed-prometheus", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/alert-center", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/certificate-manager", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/cloud-trail", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/iam", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/maintenance", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/monitoring", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/monitoring-flow", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/resource-explorer", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/iam/how-to-guides", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/iam/iam-main", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/iam/iam-overview", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/iam/iam-pricing", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/iam/iam-release-note", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/iam/iam-troubleshoot", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/iam/roles", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/monitoring/how-to-guides", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/monitoring/monitoring-main", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/monitoring/monitoring-metric", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/monitoring/monitoring-overview", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/monitoring/monitoring-pricing", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/monitoring/monitoring-release-note", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/monitoring/monitoring-troubleshoot", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/alert-center/alert-center-main", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/alert-center/alert-center-overview", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/alert-center/alert-center-pricing", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/alert-center/alert-center-release-note", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/alert-center/alert-center-troubleshoot", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/alert-center/how-to-guides", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/cloud-trail/cloud-trail-event", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/cloud-trail/cloud-trail-main", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/cloud-trail/cloud-trail-overview", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/cloud-trail/cloud-trail-pricing", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/cloud-trail/cloud-trail-release-note", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/cloud-trail/cloud-trail-troubleshoot", "Management & IAM"),
        ("https://docs.kakaocloud.com/service/management/cloud-trail/how-to-guides", "Management & IAM"),
    ],
}


# ---------------------------------------------------------------------------
# fetch & 텍스트 추출
# ---------------------------------------------------------------------------

def _assert_allowed_domain(url: str) -> None:
    """docs.kakaocloud.com 이외 도메인이면 에러 종료 (AGENTS.md §2)."""
    domain = urlparse(url).netloc
    if ALLOWED_DOMAIN not in domain:
        print(f"[ERROR] 허용되지 않은 도메인: {domain}")
        print(f"        parser는 {ALLOWED_DOMAIN} 도메인만 fetch할 수 있습니다.")
        sys.exit(1)


FETCH_RETRIES = 3
FETCH_RETRY_DELAY = 2  # seconds


def korean_char_ratio(text: str) -> float:
    """텍스트 내 한글(가-힣) 문자 비율을 반환. 0에 가까울수록 인코딩 깨짐 또는 JS 렌더링 필요."""
    if not text:
        return 0.0
    korean = sum(1 for c in text if '\uAC00' <= c <= '\uD7A3')
    return korean / len(text)


def fetch_page(url: str, logger: AgentLogger) -> str | None:
    """URL을 fetch. Playwright를 사용하여 JS 동적 렌더링을 처리합니다."""
    _assert_allowed_domain(url)
    for attempt in range(1, FETCH_RETRIES + 1):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                logger.log(f"FETCH {url} (attempt={attempt})")
                
                page.goto(url, wait_until="networkidle", timeout=15000)
                
                try:
                    page.wait_for_selector("main, article, .content", timeout=5000)
                except PlaywrightTimeoutError:
                    pass
                
                html = page.content()
                browser.close()
                logger.log(f"FETCH {url} OK")
                return html
        except Exception as e:
            logger.log(f"FETCH {url} RETRY ({e}, attempt={attempt}/{FETCH_RETRIES})")
            if attempt < FETCH_RETRIES:
                time.sleep(FETCH_RETRY_DELAY)
    logger.log(f"FETCH {url} FAIL (최대 재시도 횟수 초과)")
    return None


def html_to_text(html: str) -> str:
    """HTML에서 본문 텍스트 추출. Markdown 표 포맷팅 지원."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find("div", class_=re.compile(r"content|main|docs", re.I))
        or soup.body
        or soup
    )
    if not main:
        return ""

    for table in main.find_all("table"):
        md_table = []
        rows = table.find_all("tr")
        for i, row in enumerate(rows):
            cols = row.find_all(["th", "td"])
            col_texts = [c.get_text(separator=" ", strip=True).replace("\n", " ") for c in cols]
            if not col_texts:
                continue
            md_table.append("| " + " | ".join(col_texts) + " |")
            if i == 0 and cols and cols[0].name == "th":
                md_table.append("|" + "|".join(["---"] * len(cols)) + "|")
            elif i == 0 and not table.find("th"):
                 md_table.append("|" + "|".join(["---"] * len(cols)) + "|")

        wrapper = soup.new_tag("pre")
        wrapper.string = "\n" + "\n".join(md_table) + "\n"
        table.replace_with(wrapper)

    lines: list[str] = []
    for el in main.find_all(["h1", "h2", "h3", "h4", "p", "li", "pre", "code"]):
        text = el.get_text(separator=" ", strip=True)
        if not text:
            continue
        if el.name in ("h1", "h2", "h3", "h4"):
            level = int(el.name[1])
            lines.append(f"\n{'#' * level} {text}\n")
        elif el.name == "pre" and text.startswith("|"):
            lines.append("\n" + text + "\n")
        else:
            lines.append(text)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# llms.txt 빌드 및 변경 감지
# ---------------------------------------------------------------------------

def build_llms_txt(pages: list[tuple[str, str, str]], category: str) -> str:
    """(url, fetched_date, text) 목록으로 llms.txt 포맷 생성."""
    blocks = []
    for url, fetched, text in pages:
        blocks.append(
            f"# SOURCE: {url}\n"
            f"# FETCHED: {fetched}\n"
            f"# CATEGORY: {category}\n\n"
            f"{text.strip()}"
        )
    return "\n\n---\n\n".join(blocks)


def compare_and_warn(chapter: str, new_content: str, logger: AgentLogger) -> None:
    """기존 llms.txt와 비교해 변경 감지 시 영향 가능한 active 문제 목록 출력."""
    out = ref_path(chapter)
    if not out.exists():
        return
    if out.read_text(encoding="utf-8").strip() == new_content.strip():
        return

    q_dir = ROOT / "questions" / chapter
    affected: list[str] = []
    if q_dir.exists():
        for p in q_dir.glob("q[0-9][0-9][0-9].md"):
            fm, _ = load_question_file(p)
            if fm.get("status") == "active":
                affected.append(str(fm.get("id", p.stem)))

    logger.log(f"[WARN] {out.name} 변경 감지")
    if affected:
        logger.log(f"       영향 가능 문제: {', '.join(affected)}")
    logger.log("       → 팀 리뷰 권장. 자동 deprecated 처리는 하지 않습니다.")


# ---------------------------------------------------------------------------
# 챕터 파싱 실행
# ---------------------------------------------------------------------------

def run(chapter: str, logger: AgentLogger) -> None:
    urls = CHAPTER_URLS.get(chapter)
    if not urls:
        logger.log(f"[ERROR] 챕터 {chapter}의 URL 목록이 없습니다. CHAPTER_URLS를 확인하세요.")
        sys.exit(1)

    today    = date.today().isoformat()
    category = urls[0][1]
    pages: list[tuple[str, str, str]] = []

    for url, _ in urls:
        html = fetch_page(url, logger)
        if html:
            text = html_to_text(html)
            ratio = korean_char_ratio(text)
            if ratio < 0.03:
                # 한글 비율이 3% 미만 → JS 렌더링 필요 또는 인코딩 문제 의심
                logger.log(f"[WARN] {url} 한글 비율 {ratio:.1%} — JS 렌더링 필요 의심, RAG_NEEDED 표기")
                text = (
                    f"[RAG_NEEDED] 이 페이지는 JS 렌더링이 필요하여 자동 파싱이 불완전합니다.\n"
                    f"원문 URL: {url}\n"
                    f"추후 RAG 검색 데이터 또는 수동 입력으로 보완 필요."
                )
            else:
                logger.log(f"PARSE {url} (한글 비율: {ratio:.1%}, {len(text)} chars)")
            pages.append((url, today, text))
        else:
            logger.log(f"[WARN] {url} 파싱 실패 — 건너뜀")

    if not pages:
        logger.log("[ERROR] 모든 URL fetch 실패. references 업데이트 중단.")
        sys.exit(1)

    new_content = build_llms_txt(pages, category)
    compare_and_warn(chapter, new_content, logger)

    out_path = ref_path(chapter)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # 원자적 쓰기: 임시 파일에 먼저 저장 후 replace (중간 실패 시 기존 파일 보존)
    tmp_path = out_path.with_suffix(".tmp")
    tmp_path.write_text(new_content, encoding="utf-8")
    tmp_path.replace(out_path)
    logger.log(f"WRITE {out_path} ({len(new_content)} chars)")


# ---------------------------------------------------------------------------
# 메인
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="KakaoCloud 공식 문서 파싱")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--chapter", help="챕터 지정 (예: 02-bcs)")
    group.add_argument("--all", action="store_true", help="전체 챕터 파싱")
    args = parser.parse_args()

    chapters = list(CHAPTER_URLS.keys()) if args.all else [args.chapter]
    for chapter in chapters:
        logger = AgentLogger("parser", chapter)
        logger.start(chapter=chapter)
        run(chapter, logger)
        logger.end()


if __name__ == "__main__":
    main()
