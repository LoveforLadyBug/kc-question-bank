#!/usr/bin/env python3
"""
setup.py — 프로젝트 초기 디렉토리 구조 생성 스크립트

처음 저장소를 클론한 뒤 한 번만 실행합니다.
questions/, exams/, logs/ 디렉토리와 각 챕터의 _index.md를 생성합니다.

사용법:
    python scripts/setup.py
    python scripts/setup.py --dry-run   # 실제로 만들지 않고 무엇을 만들지만 출력
"""

import argparse
from pathlib import Path

ROOT = Path(__file__).parent.parent

CHAPTERS = [
    "01-cloud-fundamentals",
    "02-bcs",
    "03-bns",
    "04-bss",
    "05-container-pack",
    "06-data-store",
    "07-management-iam",
]

# 챕터별 토픽 목록 (question-taxonomy.md §4 기준)
CHAPTER_TOPICS = {
    "01-cloud-fundamentals": ["cloud-model", "deployment-model", "region-az", "pricing-model", "shared-responsibility"],
    "02-bcs":               ["vm-overview", "instance-type", "image", "public-ip", "bare-metal", "gpu", "storage-attachment"],
    "03-bns":               ["vpc", "subnet", "security-group", "load-balancer", "dns", "transit-gateway", "direct-connect"],
    "04-bss":               ["block-storage", "object-storage", "file-storage", "storage-comparison", "backup"],
    "05-container-pack":    ["kubernetes-overview", "cluster", "container-registry", "node-group"],
    "06-data-store":        ["mysql", "postgresql", "redis", "mongodb", "db-comparison", "ha-backup"],
    "07-management-iam":    ["iam-overview", "iam-policy", "monitoring", "logging", "notification"],
}

INDEX_TEMPLATE = """\
# _index.md — {chapter} 챕터 커버리지 현황

> 이 파일은 챕터 내 문제 현황을 추적합니다.
> `validate-quality.py` 실행 후 자동으로 갱신됩니다.
> 수동으로 수정하지 마세요.

## 현황 요약

| topic | 목표 문제 수 | 현재 active | 난이도 분포 |
|-------|------------|------------|------------|
{topic_rows}

## 정답 위치 분포 (편향 모니터링)

| A | B | C | D |
|---|---|---|---|
| 0 | 0 | 0 | 0 |

> 특정 위치에 정답이 몰리면 `generate-questions.py` 실행 시 자동으로 조정됩니다.
"""


def make_topic_rows(chapter: str) -> str:
    topics = CHAPTER_TOPICS.get(chapter, [])
    rows = []
    for topic in topics:
        rows.append(f"| `{topic}` | — | 0 | — |")
    return "\n".join(rows)


def create_structure(dry_run: bool = False):
    created = []
    skipped = []

    def makedirs(path: Path):
        if path.exists():
            skipped.append(str(path.relative_to(ROOT)))
        else:
            if not dry_run:
                path.mkdir(parents=True, exist_ok=True)
            created.append(f"📁 {path.relative_to(ROOT)}/")

    def write_file(path: Path, content: str):
        if path.exists():
            skipped.append(str(path.relative_to(ROOT)))
        else:
            if not dry_run:
                path.write_text(content, encoding="utf-8")
            created.append(f"📄 {path.relative_to(ROOT)}")

    # questions/ 챕터 디렉토리 + _index.md
    for chapter in CHAPTERS:
        chapter_dir = ROOT / "questions" / chapter
        makedirs(chapter_dir)
        index_path = chapter_dir / "_index.md"
        content = INDEX_TEMPLATE.format(
            chapter=chapter,
            topic_rows=make_topic_rows(chapter),
        )
        write_file(index_path, content)

    # exams/ 디렉토리
    makedirs(ROOT / "exams" / "weekly")
    makedirs(ROOT / "exams" / "archived")

    # logs/ 디렉토리 + .gitkeep
    for agent in ["parser", "generator", "validator"]:
        log_dir = ROOT / "logs" / agent
        makedirs(log_dir)
        gitkeep = log_dir / ".gitkeep"
        write_file(gitkeep, "")

    # .gitignore 업데이트 확인
    gitignore_path = ROOT / ".gitignore"
    required_entries = ["logs/", "*.tmp", ".env"]
    if gitignore_path.exists():
        existing = gitignore_path.read_text()
        missing = [e for e in required_entries if e not in existing]
        if missing and not dry_run:
            with gitignore_path.open("a") as f:
                f.write("\n# 문제은행 자동 추가\n")
                for entry in missing:
                    f.write(f"{entry}\n")
            created.append(f"✏️  .gitignore에 추가: {missing}")
    else:
        content = "# 문제은행\nlogs/\n*.tmp\n.env\n"
        write_file(gitignore_path, content)

    # 결과 출력
    prefix = "[DRY RUN] " if dry_run else ""
    print(f"\n{prefix}생성됨 ({len(created)}개):")
    for item in created:
        print(f"  + {item}")

    if skipped:
        print(f"\n{prefix}이미 존재하여 건너뜀 ({len(skipped)}개):")
        for item in skipped[:5]:
            print(f"  - {item}")
        if len(skipped) > 5:
            print(f"  ... 외 {len(skipped) - 5}개")

    print(f"\n{'[DRY RUN] ' if dry_run else ''}완료.")
    if dry_run:
        print("실제로 생성하려면 --dry-run 없이 실행하세요.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="프로젝트 초기 디렉토리 구조 생성")
    parser.add_argument("--dry-run", action="store_true", help="실제로 만들지 않고 미리 보기")
    args = parser.parse_args()

    print("KakaoCloud Essential 문제은행 — 초기 설정")
    print("=" * 45)
    create_structure(dry_run=args.dry_run)
