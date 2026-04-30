import { useState } from 'react'
import Setup from './components/Setup'
import Chat from './components/Chat'
import Report from './components/Report'

export default function App() {
  const [phase, setPhase] = useState('setup')
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [result, setResult] = useState(null)

  function onInterviewStart(sid, firstQuestion) {
    setSessionId(sid)
    setMessages([{ role: 'agent', content: firstQuestion }])
    setPhase('interview')
  }

  function onAnswerResult(answer, response) {
    const updated = [...messages, { role: 'user', content: answer }]
    if (response.done) {
      setMessages(updated)
      setResult(response)
      setPhase('report')
    } else {
      setMessages([...updated, { role: 'agent', content: response.question }])
    }
  }

  function onRestart() {
    setPhase('setup')
    setSessionId(null)
    setMessages([])
    setResult(null)
  }

  return (
    <div className="app">
      {phase === 'setup' && <Setup onStart={onInterviewStart} />}
      {phase === 'interview' && (
        <Chat sessionId={sessionId} messages={messages} onAnswer={onAnswerResult} />
      )}
      {phase === 'report' && <Report result={result} onRestart={onRestart} />}
    </div>
  )
}
