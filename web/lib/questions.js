import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'

const QUESTIONS_ROOT = path.join(process.cwd(), '..', 'questions')

export const CHAPTERS = [
  { id: '01-cloud-fundamentals', name: 'Cloud Fundamentals' },
  { id: '02-bcs',                name: 'Beyond Compute Service' },
  { id: '03-bns',                name: 'Beyond Networking Service' },
  { id: '04-bss',                name: 'Beyond Storage Service' },
  { id: '05-container-pack',     name: 'Container Pack' },
  { id: '06-data-store',         name: 'Data Store' },
  { id: '07-management-iam',     name: 'Management & IAM' },
]

/** questions/{chapter}/q{NNN}.md 중 status: active만 반환 */
export function getActiveQuestions(chapter) {
  const dir = path.join(QUESTIONS_ROOT, chapter)
  if (!fs.existsSync(dir)) return []

  return fs
    .readdirSync(dir)
    .filter(f => /^q\d{3}\.md$/.test(f))
    .sort()
    .map(f => {
      const { data: fm, content: body } = matter(
        fs.readFileSync(path.join(dir, f), 'utf-8')
      )
      return { fm, body }
    })
    .filter(q => q.fm.status === 'active')
}

/** ## 섹션명 기준으로 분리 */
export function parseSections(body) {
  const sections = {}
  let current = null
  const lines = []
  for (const line of body.split('\n')) {
    if (line.startsWith('## ')) {
      if (current !== null) sections[current] = lines.join('\n').trim()
      current = line.slice(3).trim()
      lines.length = 0
    } else if (current !== null) {
      lines.push(line)
    }
  }
  if (current !== null) sections[current] = lines.join('\n').trim()
  return sections
}

/** 보기 섹션 텍스트 → { A: '...', B: '...', ... } */
export function parseChoices(choicesText) {
  const choices = {}
  for (const line of (choicesText || '').split('\n')) {
    const m = line.trim().match(/^-\s*([A-D])\.\s*(.+)$/)
    if (m) choices[m[1]] = m[2].trim()
  }
  return choices
}
