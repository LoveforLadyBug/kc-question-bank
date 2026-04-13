import Link from 'next/link'
import { CHAPTERS, getActiveQuestions } from '../lib/questions'

export async function getStaticProps() {
  const chapters = CHAPTERS.map(ch => ({
    ...ch,
    count: getActiveQuestions(ch.id).length,
  }))
  return { props: { chapters } }
}

export default function Home({ chapters }) {
  const total = chapters.reduce((s, c) => s + c.count, 0)

  return (
    <div className="container">
      <div className="header">
        <h1>KakaoCloud 문제은행</h1>
        <p>Essential Basic Course 스터디 퀴즈 &nbsp;·&nbsp; 전체 {total}문제</p>
      </div>

      <div className="chapter-grid">
        {chapters.map(ch => (
          ch.count > 0 ? (
            <Link key={ch.id} href={`/quiz/${ch.id}`}>
              <div className="chapter-card">
                <h2>{ch.name}</h2>
                <p className="count">{ch.count}문제</p>
                <span className="badge ready">시작하기 →</span>
              </div>
            </Link>
          ) : (
            <div key={ch.id} className="chapter-card disabled">
              <h2>{ch.name}</h2>
              <p className="count">0문제</p>
              <span className="badge empty">준비 중</span>
            </div>
          )
        ))}
      </div>
    </div>
  )
}
