"""
build-exam-html.py — A/B/C/D 세트 인터랙티브 HTML 모의고사 생성기
draft/review/active 문제 모두 포함 (상태 무관).

세트 구성:
  Set A: q001~q005 (챕터별 5문제 × 11챕터 = 55문제)
  Set B: q006~q010
  Set C: q011~q015
  Set D: q016~q020
"""

from __future__ import annotations
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

# 챕터 순서 및 표시명
CHAPTERS: list[tuple[str, str]] = [
    ("01-cloud-overview",             "Chapter 01 — 클라우드 개요"),
    ("02-kakao-services/bcs",         "Chapter 02 — BCS"),
    ("02-kakao-services/bns",         "Chapter 02 — BNS"),
    ("02-kakao-services/bss",         "Chapter 02 — BSS"),
    ("02-kakao-services/container-pack", "Chapter 02 — Container Pack"),
    ("02-kakao-services/data-store",  "Chapter 02 — Data Store"),
    ("03-billing",                    "Chapter 03 — Billing"),
    ("04-security",                   "Chapter 04 — Security"),
    ("05-operations",                 "Chapter 05 — Operations"),
    ("06-account",                    "Chapter 06 — Account/IAM"),
    ("07-complex",                    "Chapter 07 — 복합"),
]

SETS = {
    "A": (1, 5),
    "B": (6, 10),
    "C": (11, 15),
    "D": (16, 20),
}


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """YAML frontmatter와 본문을 분리."""
    fm: dict = {}
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            yaml_block = text[3:end].strip()
            body = text[end + 3:].strip()
            for line in yaml_block.splitlines():
                m = re.match(r"^(\w[\w-]*):\s*(.*)", line)
                if m:
                    key, val = m.group(1), m.group(2).strip()
                    # 태그 배열 파싱
                    if val.startswith("["):
                        val = [v.strip().strip("\"'") for v in val.strip("[]").split(",")]
                    fm[key] = val
            return fm, body
    return fm, text


def extract_sections(body: str) -> dict[str, str]:
    """## 헤딩 기준으로 섹션 분리."""
    sections: dict[str, str] = {}
    current = None
    buf: list[str] = []
    for line in body.splitlines():
        m = re.match(r"^## (.+)", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current = m.group(1).strip()
            buf = []
        else:
            if current is not None:
                buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return sections


def load_questions_for_set(set_name: str) -> list[dict]:
    """세트(A~D)에 해당하는 문제 로드."""
    lo, hi = SETS[set_name]
    questions = []
    for chapter_dir, chapter_label in CHAPTERS:
        q_dir = ROOT / "questions" / chapter_dir
        if not q_dir.exists():
            print(f"  [WARN] {q_dir} 없음", file=sys.stderr)
            continue
        for num in range(lo, hi + 1):
            p = q_dir / f"q{num:03d}.md"
            if not p.exists():
                print(f"  [WARN] {p} 없음", file=sys.stderr)
                continue
            text = p.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(text)
            sections = extract_sections(body)
            questions.append({
                "fm": fm,
                "chapter_label": chapter_label,
                "sections": sections,
            })
    return questions


def escape_html(s: str) -> str:
    return (s
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def render_choices(보기: str) -> str:
    """보기 섹션 → HTML 라디오 버튼들."""
    lines = [l.strip() for l in 보기.strip().splitlines() if l.strip()]
    html_parts = []
    for line in lines:
        m = re.match(r"^-?\s*([A-D])\.\s*(.*)", line)
        if m:
            letter, text = m.group(1), m.group(2)
            html_parts.append(
                f'<label class="choice" data-letter="{letter}">'
                f'<input type="radio" name="{{qid}}" value="{letter}"> '
                f'<span class="choice-letter">{letter}.</span> {escape_html(text)}'
                f'</label>'
            )
    return "\n".join(html_parts)


def render_explanation(sections: dict) -> str:
    """해설 + 오답 포인트 → HTML."""
    parts = []
    if "해설" in sections:
        content = sections["해설"].strip()
        # **bold** → <strong>
        content = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", content)
        parts.append(f'<div class="exp-section"><strong>해설</strong><p>{content}</p></div>')
    if "오답 포인트" in sections:
        content = sections["오답 포인트"].strip()
        items = re.split(r"\n- ", content.lstrip("- "))
        bold = lambda s: re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        list_html = "".join(f"<li>{bold(item.strip())}</li>" for item in items if item.strip())
        parts.append(f'<div class="exp-section"><strong>오답 포인트</strong><ul>{list_html}</ul></div>')
    return "\n".join(parts)


def build_question_html(q: dict, idx: int, uid: str) -> str:
    fm = q["fm"]
    sections = q["sections"]
    raw_qid = fm.get("id", f"q{idx:03d}")
    qid = uid  # page-unique id (e.g. "A-01-q003")
    difficulty = fm.get("difficulty", "?")
    chapter_label = q["chapter_label"]
    correct = sections.get("정답", "?").strip()

    문제_text = sections.get("문제", "(문제 없음)").strip()
    문제_text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", 문제_text)

    보기_text = sections.get("보기", "")
    choices_html = render_choices(보기_text).replace("{qid}", qid)
    explanation_html = render_explanation(sections)

    diff_class = f"diff-{difficulty}"
    diff_label = {"1": "기본", "2": "이해", "3": "응용"}.get(str(difficulty), "?")

    return f"""
<div class="question-card" id="{qid}" data-correct="{correct}" data-answered="false">
  <div class="question-header">
    <span class="q-num">{idx}</span>
    <span class="q-id">{raw_qid}</span>
    <span class="q-chapter">{escape_html(chapter_label)}</span>
    <span class="q-diff {diff_class}">난이도 {diff_label}</span>
  </div>
  <div class="question-body">
    <p class="question-text">{문제_text}</p>
    <div class="choices" id="choices-{qid}">
{choices_html}
    </div>
    <div class="question-actions">
      <button class="btn-submit" onclick="submitAnswer('{qid}')">제출</button>
      <button class="btn-explain" onclick="toggleExplanation('{qid}')" style="display:none">해설 보기</button>
    </div>
    <div class="explanation" id="exp-{qid}" style="display:none">
{explanation_html}
    </div>
    <div class="result-badge" id="badge-{qid}" style="display:none"></div>
  </div>
</div>
"""


def build_html(all_sets: dict[str, list[dict]]) -> str:
    # 각 세트의 문제 HTML 생성
    set_panels = ""
    for set_name in ["A", "B", "C", "D"]:
        questions = all_sets[set_name]
        questions_html = "\n".join(
            build_question_html(q, i + 1, f"{set_name}-{i+1:03d}") for i, q in enumerate(questions)
        )
        set_panels += f"""
<div class="set-panel" id="set-{set_name}" style="display:none">
  <div class="set-header">
    <h2>세트 {set_name} — 55문제</h2>
    <div class="set-progress">
      <span id="progress-{set_name}">0 / 55 답변</span>
      <span id="score-{set_name}" style="display:none"></span>
    </div>
    <button class="btn-show-all" onclick="showAllAnswers('{set_name}')">전체 정답 보기</button>
    <button class="btn-reset" onclick="resetSet('{set_name}')">초기화</button>
  </div>
  <div class="questions-container" id="questions-{set_name}">
{questions_html}
  </div>
</div>
"""

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KakaoCloud Essential Basic Course — 모의고사</title>
<style>
  :root {{
    --kakao-yellow: #FEE500;
    --kakao-brown: #3C1E1E;
    --primary: #3B5ADB;
    --correct: #2F9E44;
    --wrong: #E03131;
    --bg: #F8F9FA;
    --card-bg: #FFFFFF;
    --border: #DEE2E6;
    --text: #212529;
    --muted: #868E96;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, 'Noto Sans KR', sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
  }}
  header {{
    background: var(--kakao-yellow);
    padding: 16px 24px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 2px solid var(--kakao-brown);
    position: sticky;
    top: 0;
    z-index: 100;
  }}
  header h1 {{ font-size: 1.2rem; color: var(--kakao-brown); font-weight: 800; }}
  header .subtitle {{ font-size: 0.85rem; color: var(--kakao-brown); opacity: 0.7; }}

  .set-selector {{
    max-width: 900px;
    margin: 32px auto;
    padding: 0 16px;
    text-align: center;
  }}
  .set-selector h2 {{ font-size: 1.4rem; margin-bottom: 8px; }}
  .set-selector p {{ color: var(--muted); margin-bottom: 24px; }}
  .set-buttons {{
    display: flex;
    gap: 16px;
    justify-content: center;
    flex-wrap: wrap;
  }}
  .btn-set {{
    width: 120px;
    height: 120px;
    border-radius: 16px;
    border: 2px solid var(--border);
    background: var(--card-bg);
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 2rem;
    font-weight: 800;
    color: var(--primary);
    transition: all 0.15s;
  }}
  .btn-set:hover {{ border-color: var(--primary); background: #EEF2FF; transform: translateY(-2px); box-shadow: 0 4px 12px rgba(59,90,219,0.2); }}
  .btn-set.active {{ border-color: var(--primary); background: var(--primary); color: white; }}
  .btn-set small {{ font-size: 0.75rem; font-weight: 400; opacity: 0.7; }}

  .set-panel {{
    max-width: 900px;
    margin: 0 auto;
    padding: 0 16px 64px;
  }}
  .set-header {{
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 16px 0;
    border-bottom: 2px solid var(--border);
    margin-bottom: 24px;
    flex-wrap: wrap;
  }}
  .set-header h2 {{ flex: 1; font-size: 1.3rem; }}
  .set-progress {{ color: var(--muted); font-size: 0.9rem; }}
  #score- {{ font-weight: 700; }}

  .btn-show-all, .btn-reset {{
    padding: 6px 14px;
    border-radius: 6px;
    border: 1px solid var(--border);
    background: var(--card-bg);
    cursor: pointer;
    font-size: 0.85rem;
    transition: background 0.1s;
  }}
  .btn-show-all:hover {{ background: #FFF3BF; }}
  .btn-reset:hover {{ background: #FFE3E3; }}

  .question-card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    margin-bottom: 20px;
    overflow: hidden;
    transition: box-shadow 0.2s;
  }}
  .question-card:hover {{ box-shadow: 0 2px 12px rgba(0,0,0,0.08); }}
  .question-card.correct-card {{ border-color: var(--correct); }}
  .question-card.wrong-card {{ border-color: var(--wrong); }}

  .question-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    background: var(--bg);
    border-bottom: 1px solid var(--border);
    flex-wrap: wrap;
  }}
  .q-num {{ font-size: 1.1rem; font-weight: 800; color: var(--primary); min-width: 28px; }}
  .q-id {{ font-size: 0.75rem; color: var(--muted); font-family: monospace; }}
  .q-chapter {{ font-size: 0.8rem; color: var(--muted); flex: 1; }}
  .q-diff {{ font-size: 0.75rem; padding: 2px 8px; border-radius: 20px; font-weight: 600; }}
  .diff-1 {{ background: #D3F9D8; color: #2B8A3E; }}
  .diff-2 {{ background: #FFF3BF; color: #E67700; }}
  .diff-3 {{ background: #FFE3E3; color: #C92A2A; }}

  .question-body {{ padding: 16px; }}
  .question-text {{ font-size: 1rem; font-weight: 500; margin-bottom: 16px; line-height: 1.7; }}

  .choices {{ display: flex; flex-direction: column; gap: 8px; margin-bottom: 16px; }}
  .choice {{
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 10px 14px;
    border: 1.5px solid var(--border);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.1s;
    font-size: 0.95rem;
  }}
  .choice:hover {{ border-color: var(--primary); background: #EEF2FF; }}
  .choice.selected {{ border-color: var(--primary); background: #EEF2FF; }}
  .choice.correct-choice {{ border-color: var(--correct) !important; background: #D3F9D8 !important; }}
  .choice.wrong-choice {{ border-color: var(--wrong) !important; background: #FFE3E3 !important; }}
  .choice input {{ display: none; }}
  .choice-letter {{ font-weight: 700; color: var(--primary); min-width: 20px; }}

  .question-actions {{ display: flex; gap: 10px; margin-bottom: 8px; }}
  .btn-submit {{
    padding: 8px 20px;
    background: var(--primary);
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 600;
    transition: background 0.1s;
  }}
  .btn-submit:hover {{ background: #2F4AC8; }}
  .btn-submit:disabled {{ background: var(--muted); cursor: default; }}
  .btn-explain {{
    padding: 8px 20px;
    background: #FFF3BF;
    color: #E67700;
    border: 1px solid #FFE066;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 600;
  }}
  .btn-explain:hover {{ background: #FFE066; }}

  .result-badge {{
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 700;
    margin-top: 4px;
  }}
  .badge-correct {{ background: var(--correct); color: white; }}
  .badge-wrong {{ background: var(--wrong); color: white; }}

  .explanation {{
    margin-top: 12px;
    padding: 14px;
    background: var(--bg);
    border-radius: 8px;
    font-size: 0.9rem;
    line-height: 1.7;
  }}
  .exp-section {{ margin-bottom: 10px; }}
  .exp-section strong {{ display: block; margin-bottom: 4px; color: var(--primary); }}
  .exp-section p {{ color: #495057; }}
  .exp-section ul {{ padding-left: 20px; color: #495057; }}
  .exp-section ul li {{ margin-bottom: 4px; }}

  .back-btn {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9rem;
    margin: 16px;
    text-decoration: none;
    color: var(--text);
  }}
  .back-btn:hover {{ background: var(--bg); }}

  @media (max-width: 600px) {{
    .set-header {{ flex-direction: column; align-items: flex-start; }}
    .btn-set {{ width: 90px; height: 90px; }}
  }}
</style>
</head>
<body>

<header>
  <div>
    <h1>☁️ KakaoCloud Essential Basic Course</h1>
    <div class="subtitle">모의고사 — A/B/C/D 세트 각 55문제</div>
  </div>
</header>

<div id="home">
  <div class="set-selector">
    <h2>세트를 선택하세요</h2>
    <p>세트별로 챕터당 5문제씩 총 55문제가 출제됩니다. 세트끼리 문제가 겹치지 않습니다.</p>
    <div class="set-buttons">
      <button class="btn-set" onclick="selectSet('A')">A<small>q001~005</small></button>
      <button class="btn-set" onclick="selectSet('B')">B<small>q006~010</small></button>
      <button class="btn-set" onclick="selectSet('C')">C<small>q011~015</small></button>
      <button class="btn-set" onclick="selectSet('D')">D<small>q016~020</small></button>
    </div>
  </div>
</div>

{set_panels}

<script>
let currentSet = null;

function selectSet(name) {{
  document.getElementById('home').style.display = 'none';
  document.querySelectorAll('.set-panel').forEach(p => p.style.display = 'none');
  document.querySelectorAll('.btn-set').forEach(b => b.classList.remove('active'));
  document.getElementById('set-' + name).style.display = 'block';
  currentSet = name;
  updateProgress(name);
}}

function goHome() {{
  document.getElementById('home').style.display = 'block';
  document.querySelectorAll('.set-panel').forEach(p => p.style.display = 'none');
  currentSet = null;
}}

function submitAnswer(qid) {{
  const card = document.getElementById(qid);
  const correct = card.dataset.correct;
  const selected = document.querySelector(`input[name="${{qid}}"]:checked`);
  if (!selected) {{ alert('선택지를 고르세요.'); return; }}

  const answer = selected.value;
  const isCorrect = answer === correct;

  // 선택지 스타일 적용
  card.querySelectorAll('.choice').forEach(label => {{
    label.style.pointerEvents = 'none';
    const letter = label.dataset.letter;
    if (letter === correct) label.classList.add('correct-choice');
    else if (letter === answer && !isCorrect) label.classList.add('wrong-choice');
  }});

  // 결과 배지
  const badge = document.getElementById('badge-' + qid);
  badge.style.display = 'inline-block';
  badge.textContent = isCorrect ? '✅ 정답!' : `❌ 오답 (정답: ${{correct}})`;
  badge.className = 'result-badge ' + (isCorrect ? 'badge-correct' : 'badge-wrong');

  // 카드 테두리
  card.classList.add(isCorrect ? 'correct-card' : 'wrong-card');
  card.dataset.answered = isCorrect ? 'correct' : 'wrong';

  // 버튼 상태
  card.querySelector('.btn-submit').disabled = true;
  card.querySelector('.btn-explain').style.display = 'inline-block';

  if (currentSet) updateProgress(currentSet);
}}

function toggleExplanation(qid) {{
  const exp = document.getElementById('exp-' + qid);
  const btn = document.querySelector(`#${{qid}} .btn-explain`);
  if (exp.style.display === 'none') {{
    exp.style.display = 'block';
    btn.textContent = '해설 닫기';
  }} else {{
    exp.style.display = 'none';
    btn.textContent = '해설 보기';
  }}
}}

function showAllAnswers(setName) {{
  const panel = document.getElementById('set-' + setName);
  panel.querySelectorAll('.question-card').forEach(card => {{
    if (card.dataset.answered !== 'false') return;
    const qid = card.id;
    const correct = card.dataset.correct;
    card.querySelectorAll('.choice').forEach(label => {{
      label.style.pointerEvents = 'none';
      if (label.dataset.letter === correct) label.classList.add('correct-choice');
    }});
    card.dataset.answered = 'shown';
    card.querySelector('.btn-submit').disabled = true;
    card.querySelector('.btn-explain').style.display = 'inline-block';
    const badge = document.getElementById('badge-' + qid);
    badge.style.display = 'inline-block';
    badge.textContent = `정답: ${{correct}}`;
    badge.className = 'result-badge badge-correct';
  }});
  updateProgress(setName);
}}

function resetSet(setName) {{
  if (!confirm('이 세트의 모든 답변을 초기화할까요?')) return;
  const panel = document.getElementById('set-' + setName);
  panel.querySelectorAll('.question-card').forEach(card => {{
    card.dataset.answered = 'false';
    card.classList.remove('correct-card', 'wrong-card');
    card.querySelectorAll('.choice').forEach(label => {{
      label.style.pointerEvents = '';
      label.classList.remove('correct-choice', 'wrong-choice', 'selected');
    }});
    card.querySelectorAll('input[type=radio]').forEach(r => r.checked = false);
    card.querySelector('.btn-submit').disabled = false;
    card.querySelector('.btn-explain').style.display = 'none';
    const expId = 'exp-' + card.id;
    const exp = document.getElementById(expId);
    if (exp) exp.style.display = 'none';
    const badge = document.getElementById('badge-' + card.id);
    if (badge) badge.style.display = 'none';
  }});
  updateProgress(setName);
}}

function updateProgress(setName) {{
  const panel = document.getElementById('set-' + setName);
  const cards = panel.querySelectorAll('.question-card');
  const total = cards.length;
  let answered = 0, correct = 0;
  cards.forEach(card => {{
    if (card.dataset.answered !== 'false') {{
      answered++;
      if (card.dataset.answered === 'correct') correct++;
    }}
  }});
  document.getElementById('progress-' + setName).textContent = `${{answered}} / ${{total}} 답변`;
  const scoreEl = document.getElementById('score-' + setName);
  if (answered > 0) {{
    scoreEl.textContent = ` | 정답률 ${{Math.round(correct/answered*100)}}% (${{correct}}/${{answered}})`;
    scoreEl.style.display = 'inline';
  }}
}}

// 선택지 클릭 → 라디오 선택 효과
document.addEventListener('click', function(e) {{
  const label = e.target.closest('.choice');
  if (!label) return;
  const card = label.closest('.question-card');
  if (!card || card.dataset.answered !== 'false') return;
  card.querySelectorAll('.choice').forEach(l => l.classList.remove('selected'));
  label.classList.add('selected');
  label.querySelector('input').checked = true;
}});
</script>
</body>
</html>
"""


def main() -> None:
    print("KakaoCloud 모의고사 HTML 생성 중...")
    all_sets: dict[str, list[dict]] = {}
    for set_name in ["A", "B", "C", "D"]:
        print(f"  세트 {set_name} 로드 중...")
        questions = load_questions_for_set(set_name)
        print(f"    → {len(questions)}문제 로드됨")
        all_sets[set_name] = questions

    html = build_html(all_sets)

    out = ROOT / "exams" / "exam.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    total = sum(len(q) for q in all_sets.values())
    print(f"\n✅ 완료: {out}")
    print(f"   총 {total}문제 (세트별 {total//4}문제)")


if __name__ == "__main__":
    main()
