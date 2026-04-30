import { useState } from 'react'
import { createSession, uploadCV, uploadJD, startSession } from '../api'
import StudySetup from './StudySetup'

export default function Setup({ onStart }) {
  const [mode, setMode] = useState('cv')
  const [cvFile, setCvFile] = useState(null)
  const [jd, setJd] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleCVSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const { session_id } = await createSession()
      await uploadCV(session_id, cvFile)
      await uploadJD(session_id, jd)
      const response = await startSession(session_id)
      onStart(session_id, response.question)
    } catch (err) {
      setError(err.message || 'Something went wrong. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="setup">
      <div className="setup-card">
        <h1>Interview Coach</h1>
        <p className="subtitle">Practice technical interviews tailored to your profile.</p>

        <div className="mode-toggle">
          <button
            type="button"
            className={mode === 'cv' ? 'active' : ''}
            onClick={() => setMode('cv')}
          >
            CV + Job Description
          </button>
          <button
            type="button"
            className={mode === 'study' ? 'active' : ''}
            onClick={() => setMode('study')}
          >
            Study Mode
          </button>
        </div>

        {mode === 'cv' ? (
          <form onSubmit={handleCVSubmit}>
            <div className="field">
              <label>Your CV (PDF)</label>
              <input
                type="file"
                accept=".pdf"
                onChange={e => setCvFile(e.target.files[0])}
                required
              />
            </div>
            <div className="field">
              <label>Job Description</label>
              <textarea
                placeholder="Paste the job description here..."
                value={jd}
                onChange={e => setJd(e.target.value)}
                rows={8}
                required
              />
            </div>
            {error && <p className="error">{error}</p>}
            <button type="submit" disabled={loading || !cvFile || !jd.trim()}>
              {loading ? 'Preparing your interview...' : 'Start Interview'}
            </button>
          </form>
        ) : (
          <StudySetup onStart={onStart} />
        )}
      </div>
    </div>
  )
}
