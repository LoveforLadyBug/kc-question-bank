import argparse
import sys
from pathlib import Path
from datetime import date
import importlib.util

from harness import (
    ROOT, load_question_file, save_question_file, extract_sections,
    AgentLogger, get_client, verify_with_llm, HALLUCINATION_SUSPECT
)

# 동적 임포트 (파일명에 하이픈이 있어서)
vq_spec = importlib.util.spec_from_file_location("validate_quality", str(ROOT / "scripts" / "validate-quality.py"))
validate_quality = importlib.util.module_from_spec(vq_spec)
sys.modules["validate_quality"] = validate_quality
vq_spec.loader.exec_module(validate_quality)

def process_file(client, path: Path, llms_content: str, logger: AgentLogger):
    fm, body = load_question_file(path)
    
    # 2-Pass LLM 검증
    raw_content = path.read_text(encoding="utf-8")
    is_pass, reason = verify_with_llm(client, raw_content, llms_content, logger)
    
    tags = fm.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
        
    sections = extract_sections(body)
    evidence = sections.get("근거 인용", "").strip()
    
    modified = False
    
    if is_pass:
        if HALLUCINATION_SUSPECT in tags:
            tags.remove(HALLUCINATION_SUSPECT)
            modified = True
            
        # 기존 [FAIL] 문구 제거
        new_evidence = "\n".join([line for line in evidence.splitlines() if not line.strip().startswith("[FAIL]")])
        if new_evidence != evidence:
            body = body.replace(f"## 근거 인용\n\n{evidence}", f"## 근거 인용\n\n{new_evidence}")
            modified = True
    else:
        if HALLUCINATION_SUSPECT not in tags:
            tags.append(HALLUCINATION_SUSPECT)
            modified = True
            
        if "[FAIL]" not in evidence:
            fail_msg = f"\n\n[FAIL] {reason}"
            body = body.replace(f"## 근거 인용\n\n{evidence}", f"## 근거 인용\n\n{evidence}{fail_msg}")
            modified = True
            
    if modified:
        fm["tags"] = tags
        save_question_file(path, fm, body)
        logger.log(f"UPDATED {path.name} -> PASS={is_pass} ({reason})")
    else:
        logger.log(f"UNCHANGED {path.name} -> PASS={is_pass}")
        
    # 품질 점수 재계산 (force=True)
    validate_quality.validate_file(path, force=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", help="특정 챕터만 (예: 02-bcs)", action="append")
    args = parser.parse_args()
    
    chapters = args.chapter if args.chapter else ["01-cloud-fundamentals", "02-bcs"]
    
    client = get_client()
    logger = AgentLogger("verifier", "retroactive")
    logger.start(chapters=chapters)
    
    q_root = ROOT / "questions"
    
    for chapter in chapters:
        q_dir = q_root / chapter
        if not q_dir.exists():
            continue
            
        chapter_name = chapter.split("-", 1)[-1]
        llms_path = ROOT / "docs" / "references" / f"{chapter_name}-llms.txt"
        if not llms_path.exists():
            logger.log(f"[WARN] No llms.txt found for {chapter}")
            continue
            
        llms_content = llms_path.read_text(encoding="utf-8")
        paths = sorted(q_dir.glob("q[0-9][0-9][0-9].md"))
        
        logger.log(f"Processing {len(paths)} questions in {chapter}...")
        for p in paths:
            process_file(client, p, llms_content, logger)
            
    logger.end()

if __name__ == "__main__":
    main()
