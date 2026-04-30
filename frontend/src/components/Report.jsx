export default function Report({ result, onRestart }) {
  const { report, scores } = result

  function avg(key) {
    if (!scores?.length) return 0
    if (key === 'overall') {
      return scores.reduce((sum, s) => sum + s.overall, 0) / scores.length
    }
    return scores.reduce((sum, s) => sum + s.scores[key], 0) / scores.length
  }

  const metrics = ['accuracy', 'depth', 'clarity', 'relevance']

  return (
    <div className="report">
      <div className="report-card">
        <h2>Interview Complete</h2>
        <p className="report-subtitle">Here's how you did across {scores?.length ?? 0} questions.</p>

        <div className="scores">
          {metrics.map(m => (
            <div key={m} className="score-item">
              <span className="score-label">{m}</span>
              <div className="score-bar">
                <div className="score-fill" style={{ width: `${(avg(m) / 5) * 100}%` }} />
              </div>
              <span className="score-value">{avg(m).toFixed(1)}</span>
            </div>
          ))}
          <div className="score-item overall">
            <span className="score-label">Overall</span>
            <div className="score-bar">
              <div className="score-fill" style={{ width: `${(avg('overall') / 5) * 100}%` }} />
            </div>
            <span className="score-value">{avg('overall').toFixed(1)}</span>
          </div>
        </div>

        <div className="report-text">
          <h3>Coach Feedback</h3>
          <p>{report}</p>
        </div>

        <button onClick={onRestart}>Start New Interview</button>
      </div>
    </div>
  )
}
