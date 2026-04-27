import Link from 'next/link'
import { CHAPTERS } from '../lib/constants'

export async function getStaticProps() {
  return { props: {} }
}

export default function Home() {
  return (
    <div className="container">
      <div className="header">
        <h1>KakaoCloud 문제은행</h1>
        <p>Essential Basic Course 스터디 퀴즈</p>
      </div>

      <div className="chapter-grid" style={{ marginBottom: '2rem' }}>
        <a href="/exam.html" style={{ textDecoration: 'none', gridColumn: 'span 2' }}>
          <div className="chapter-card active" style={{ border: '2px solid #FEE500', background: '#FFFDE7', height: '100%' }}>
            <h2>📝 A/B/C/D 세트 모의고사 (전 챕터)</h2>
            <p className="count">세트별 55문제 × 4세트 = 총 220문제</p>
            <span className="badge" style={{ background: '#3B5ADB', color: 'white' }}>응시하기</span>
          </div>
        </a>
        <Link href="/quiz/weekly" style={{ textDecoration: 'none', gridColumn: 'span 2' }}>
          <div className="chapter-card active" style={{ border: '2px solid #4f46e5', background: '#f5f3ff', height: '100%' }}>
            <h2>🔥 주간 모의고사 (Fundamentals & BCS)</h2>
            <p className="count">총 20 문항</p>
            <span className="badge" style={{ background: '#4f46e5', color: 'white' }}>응시하기</span>
          </div>
        </Link>
      </div>

      <div className="chapter-grid">
        {CHAPTERS.map(ch => (
          <div key={ch.id} className="chapter-card disabled">
            <h2>{ch.name}</h2>
            <p className="count">점검 중</p>
            <span className="badge empty">준비 중</span>
          </div>
        ))}
      </div>
    </div>
  )
}
