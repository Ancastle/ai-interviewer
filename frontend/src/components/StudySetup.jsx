import { useState, useEffect } from 'react'
import { createSession, getSubjects, getCategories, startStudySession } from '../api'

export default function StudySetup({ onStart }) {
  const [subjects, setSubjects] = useState([])
  const [categories, setCategories] = useState([])
  const [subject, setSubject] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    getSubjects().then(data => {
      setSubjects(data.subjects)
      if (data.subjects.length > 0) setSubject(data.subjects[0].id)
    })
  }, [])

  useEffect(() => {
    if (!subject) return
    setCategoryId('')
    getCategories(subject).then(data => {
      setCategories(data.categories)
      if (data.categories.length > 0) setCategoryId(data.categories[0].id)
    })
  }, [subject])

  async function handleSubmit(e) {
    e.preventDefault()
    if (!subject || !categoryId) return
    setLoading(true)
    setError(null)
    try {
      const { session_id } = await createSession()
      const response = await startStudySession(session_id, subject, categoryId)
      onStart(session_id, response.question)
    } catch (err) {
      setError(err.message || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  const selectedCategory = categories.find(c => c.id === categoryId)

  return (
    <form onSubmit={handleSubmit}>
      <div className="field">
        <label>Subject</label>
        <select value={subject} onChange={e => setSubject(e.target.value)}>
          {subjects.map(s => (
            <option key={s.id} value={s.id}>{s.name}</option>
          ))}
        </select>
      </div>

      <div className="field">
        <label>Category</label>
        <select value={categoryId} onChange={e => setCategoryId(e.target.value)} disabled={!categories.length}>
          {categories.map(c => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>

      {error && <p className="error">{error}</p>}

      <button type="submit" disabled={loading || !subject || !categoryId}>
        {loading ? 'Preparing...' : `Start — ${selectedCategory?.name ?? ''}`}
      </button>
    </form>
  )
}
