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

      <div className="maintenance-banner">
        <div className="maintenance-icon">🔍</div>
        <h2 className="maintenance-title">문제 점검 중입니다.</h2>
        <p className="maintenance-desc">
          현재 문제 품질 검토가 진행 중입니다.<br />
          점검이 완료되는 대로 다시 이용하실 수 있습니다.<br />
          이용에 불편을 드려 죄송합니다.
        </p>
      </div>

      <div className="chapter-grid" style={{ marginBottom: '2rem' }}>
        <Link href="/quiz/weekly" style={{ textDecoration: 'none' }}>
          <div className="chapter-card active" style={{ border: '2px solid #4f46e5', background: '#f5f3ff' }}>
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
