import { useState, useEffect } from 'react'
import Link from 'next/link'
import fs from 'fs'
import path from 'path'

export async function getStaticProps() {
  const filePath = path.join(process.cwd(), '..', 'exams', 'weekly', 'mock-exam.json')
  let data = { title: "주간 모의고사", questions: [] }
  if (fs.existsSync(filePath)) {
    const fileContents = fs.readFileSync(filePath, 'utf8')
    data = JSON.parse(fileContents)
  }

  return { 
    props: { 
      chapter: 'weekly', 
      chapterName: data.title, 
      questions: data.questions 
    } 
  }
}

// ---------------------------------------------------------------------------

const CHOICE_COLORS = {
  default: {},
  selected: { borderColor: '#4f46e5', background: '#f5f3ff' },
  correct:  'correct',
  wrong:    'wrong',
  reveal:   'reveal',
}

function QuizScreen({ questions, onFinish }) {
  const [idx, setIdx]           = useState(0)
  const [selected, setSelected] = useState(null)   // 'A' | 'B' | 'C' | 'D' | null
  const [results, setResults]   = useState([])      // { question, selected, answer, isCorrect }

  const q        = questions[idx]
  const revealed = selected !== null
  const progress = ((idx) / questions.length) * 100

  function handleSelect(key) {
    if (revealed) return
    setSelected(key)
  }

  function handleNext() {
    const isCorrect = selected === q.answer
    const newResults = [...results, { question: q, selected, isCorrect }]
    setResults(newResults)

    if (idx + 1 >= questions.length) {
      onFinish(newResults)
    } else {
      setIdx(idx + 1)
      setSelected(null)
    }
  }

  function choiceClass(key) {
    if (!revealed) return ''
    if (key === q.answer) return 'reveal'
    if (key === selected) return 'wrong'
    return ''
  }

  return (
    <div className="quiz-wrap">
      <div className="progress-label">{idx + 1} / {questions.length}</div>
      <div className="progress-bar">
        <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
      </div>

      <div className="question-card">
        <p className="question-text">{q.question}</p>

        <div className="choices">
          {Object.entries(q.choices).map(([key, text]) => (
            <button
              key={key}
              className={`choice-btn ${choiceClass(key)}`}
              onClick={() => handleSelect(key)}
              disabled={revealed}
            >
              <span className="choice-key">{key}</span>
              {text}
            </button>
          ))}
        </div>

        {revealed && (
          <div className="explanation">
            <h4>해설</h4>
            <p>{q.explanation}</p>
            {q.wrongPoints && (
              <div className="wrong-points">
                <h4>오답 포인트</h4>
                <p>{q.wrongPoints}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {revealed && (
        <button className="next-btn" onClick={handleNext}>
          {idx + 1 >= questions.length ? '결과 보기' : '다음 문제 →'}
        </button>
      )}
    </div>
  )
}

function ResultScreen({ results, chapterName, onRetry }) {
  const correct = results.filter(r => r.isCorrect).length
  const total   = results.length
  const pct     = Math.round((correct / total) * 100)

  return (
    <div className="quiz-wrap">
      <div className="result-card">
        <div className="result-score">{pct}점</div>
        <p className="result-label">{total}문제 중 {correct}개 정답</p>
      </div>

      <div className="result-list">
        {results.map((r, i) => (
          <div key={i} className={`result-item ${r.isCorrect ? 'correct' : 'wrong'}`}>
            <h4>{i + 1}. {r.isCorrect ? '✓ 정답' : `✗ 오답 (정답: ${r.question.answer})`}</h4>
            <p>{r.question.question.slice(0, 60)}{r.question.question.length > 60 ? '…' : ''}</p>
          </div>
        ))}
      </div>

      <button className="next-btn" onClick={onRetry} style={{ marginBottom: '0.8rem' }}>
        다시 풀기
      </button>
      <Link href="/">
        <button className="btn-outline">챕터 목록으로</button>
      </Link>
    </div>
  )
}

// ---------------------------------------------------------------------------

export default function WeeklyQuizPage({ chapterName, questions }) {
  const [shuffled, setShuffled]   = useState(null)
  const [results,  setResults]    = useState(null)

  // 클라이언트에서 문제 순서 섞기
  useEffect(() => {
    setShuffled([...questions].sort(() => Math.random() - 0.5))
  }, [questions])

  if (questions.length === 0) {
    return (
      <div className="container">
        <div className="header">
          <h1>{chapterName}</h1>
          <p>모의시험 데이터가 존재하지 않습니다. 스크립트를 먼저 실행하세요.</p>
        </div>
        <Link href="/"><button className="btn-outline">← 챕터 목록</button></Link>
      </div>
    )
  }

  if (!shuffled) return null  // 셔플 전 깜빡임 방지

  if (results) {
    return (
      <ResultScreen
        results={results}
        chapterName={chapterName}
        onRetry={() => {
          setResults(null)
          setShuffled([...questions].sort(() => Math.random() - 0.5))
        }}
      />
    )
  }

  return (
    <div>
      <div style={{ padding: '1rem 1rem 0', maxWidth: 680, margin: '0 auto' }}>
        <Link href="/" style={{ color: '#4f46e5', fontSize: '0.9rem' }}>← 메인으로</Link>
        <h2 style={{ marginTop: '0.4rem', fontSize: '1.1rem' }}>{chapterName}</h2>
      </div>
      <QuizScreen questions={shuffled} onFinish={setResults} />
    </div>
  )
}
