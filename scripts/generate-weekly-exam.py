import json
import random
from pathlib import Path
from datetime import date
from harness import ROOT, load_question_file, save_question_file, extract_sections, token_jaccard
import sys

def parse_choices(choices_text: str) -> dict[str, str]:
    choices = {}
    for line in choices_text.splitlines():
        line = line.strip()
        if line.startswith("- A.") or line.startswith("- A:"):
            choices["A"] = line[4:].strip()
        elif line.startswith("- B.") or line.startswith("- B:"):
            choices["B"] = line[4:].strip()
        elif line.startswith("- C.") or line.startswith("- C:"):
            choices["C"] = line[4:].strip()
        elif line.startswith("- D.") or line.startswith("- D:"):
            choices["D"] = line[4:].strip()
    return choices

def select_and_activate(chapter: str, count: int, global_selected_texts: list[str], global_seen_topics: set) -> list[dict]:
    q_dir = ROOT / "questions" / chapter
    if not q_dir.exists():
        print(f"[WARN] {chapter} dir not found")
        return []

    paths = sorted(q_dir.glob("q[0-9][0-9][0-9].md"))
    candidates = []
    
    for p in paths:
        fm, body = load_question_file(p)
        score = fm.get("quality_score", 0)
        # 80점 이상이면서 hallucination 태그가 없는 문제 (소급 검증 통과본)
        tags = fm.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
            
        if score >= 80 and "hallucination-suspect" not in tags:
            candidates.append((p, fm, body))
            
    if len(candidates) < count:
        print(f"[ERROR] {chapter}에서 {count}개를 뽑기에 유효한 문제가 부족합니다 (현재 {len(candidates)}개).")
        sys.exit(1)
        
    random.shuffle(candidates)
    selected = []
    
    for p, fm, body in candidates:
        topic = fm.get("topic", "").strip()
        if topic and topic in global_seen_topics:
            continue
            
        sections = extract_sections(body)
        combined_text = sections.get("문제", "").strip() + " " + sections.get("보기", "").strip()
        
        is_duplicate = False
        for s_combined in global_selected_texts:
            if token_jaccard(combined_text, s_combined) >= 0.6:
                is_duplicate = True
                break
                
        if not is_duplicate:
            selected.append((p, fm, body))
            global_selected_texts.append(combined_text)
            if topic:
                global_seen_topics.add(topic)
            if len(selected) == count:
                break
                
    if len(selected) < count:
        print(f"[ERROR] {chapter}에서 중복을 제외하고 나니 {count}개를 채우지 못했습니다 (현재 {len(selected)}개).")
        sys.exit(1)
        
    results = []
    
    for p, fm, body in selected:
        # 상태 업데이트 (Active로 승격)
        fm["status"] = "active"
        if "reviewed_by" not in fm or not fm["reviewed_by"]:
            fm["reviewed_by"] = ["admin"]
        elif "admin" not in fm["reviewed_by"]:
            fm["reviewed_by"].append("admin")
            
        save_question_file(p, fm, body)
        
        # JSON용 구조화 데이터 생성
        sections = extract_sections(body)
        choices = parse_choices(sections.get("보기", ""))
        
        results.append({
            "id": fm.get("id"),
            "chapter": fm.get("chapter"),
            "topic": fm.get("topic"),
            "difficulty": fm.get("difficulty"),
            "question": sections.get("문제", "").strip(),
            "choices": choices,
            "answer": sections.get("정답", "").strip(),
            "explanation": sections.get("해설", "").strip(),
            "wrongPoints": sections.get("오답 포인트", "").strip()
        })
        
    return results

def main():
    print("문제 선별 및 Active 승격 시작...")
    
    global_selected_texts = []
    global_seen_topics = set()
    
    # 배분 비율: Fundamentals 65% (13문제), BCS 35% (7문제)
    fundamentals = select_and_activate("01-cloud-fundamentals", 13, global_selected_texts, global_seen_topics)
    bcs = select_and_activate("02-bcs", 7, global_selected_texts, global_seen_topics)
    
    all_selected = fundamentals + bcs
    random.shuffle(all_selected)
    
    out_dir = ROOT / "exams" / "weekly"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. JSON 내보내기 (웹앱용)
    json_path = out_dir / "mock-exam.json"
    json_data = {
        "title": "주간 모의고사 (Fundamentals & BCS)",
        "generatedAt": date.today().isoformat(),
        "total": len(all_selected),
        "questions": all_selected
    }
    json_path.write_text(json.dumps(json_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[{json_path}] 저장 완료.")
    
    # 2. 마크다운 내보내기 (문서 보관용)
    md_lines = [
        f"# 주간 모의고사 (Fundamentals & BCS)",
        f"생성일: {json_data['generatedAt']} | 문제 수: {json_data['total']}",
        ""
    ]
    
    for i, q in enumerate(all_selected, 1):
        md_lines.append(f"## {i}. {q['question']}\n")
        for key in ["A", "B", "C", "D"]:
            if key in q["choices"]:
                md_lines.append(f"- {key}. {q['choices'][key]}")
        md_lines.append("\n<br>\n")
        
    md_lines.extend(["---", "", "## 정답 및 해설", ""])
    for i, q in enumerate(all_selected, 1):
        md_lines.append(f"### {i}. {q['answer']}")
        md_lines.append(f"**해설**: {q['explanation']}")
        if q['wrongPoints']:
            md_lines.append(f"**오답 포인트**:\n{q['wrongPoints']}")
        md_lines.append("\n<br>\n")
        
    md_path = out_dir / "mock-exam.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    print(f"[{md_path}] 저장 완료.")

if __name__ == "__main__":
    main()
