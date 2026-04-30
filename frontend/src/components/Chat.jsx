import { useState, useRef, useEffect } from 'react'
import { submitAnswer } from '../api'

export default function Chat({ sessionId, messages, onAnswer }) {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function handleSubmit(e) {
    e.preventDefault()
    if (!input.trim() || loading) return

    const answer = input.trim()
    setInput('')
    setLoading(true)

    try {
      const response = await submitAnswer(sessionId, answer)
      onAnswer(answer, response)
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="chat">
      <div className="chat-header">
        <h2>Mock Interview</h2>
        <span className="chat-badge">Session #{sessionId}</span>
      </div>

      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <span className="bubble">{msg.content}</span>
          </div>
        ))}
        {loading && (
          <div className="message agent">
            <span className="bubble typing">Thinking...</span>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form className="input-area" onSubmit={handleSubmit}>
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your answer... (Enter to send, Shift+Enter for new line)"
          rows={3}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  )
}
