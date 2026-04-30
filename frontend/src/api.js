const BASE = 'http://localhost:8000'

export async function createSession() {
  const res = await fetch(`${BASE}/session`, { method: 'POST' })
  if (!res.ok) throw new Error('Failed to create session')
  return res.json()
}

export async function uploadCV(sessionId, file) {
  const form = new FormData()
  form.append('session_id', sessionId)
  form.append('file', file)
  const res = await fetch(`${BASE}/documents/cv`, { method: 'POST', body: form })
  if (!res.ok) throw new Error('Failed to upload CV')
  return res.json()
}

export async function uploadJD(sessionId, text) {
  const form = new FormData()
  form.append('session_id', sessionId)
  form.append('text', text)
  const res = await fetch(`${BASE}/documents/jd`, { method: 'POST', body: form })
  if (!res.ok) throw new Error('Failed to upload job description')
  return res.json()
}

export async function startSession(sessionId) {
  const res = await fetch(`${BASE}/session/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId }),
  })
  if (!res.ok) throw new Error('Failed to start session')
  return res.json()
}

export async function submitAnswer(sessionId, answer) {
  const res = await fetch(`${BASE}/session/${sessionId}/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ answer }),
  })
  if (!res.ok) throw new Error('Failed to submit answer')
  return res.json()
}
