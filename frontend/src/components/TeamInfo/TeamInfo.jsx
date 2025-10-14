import './TeamInfo.css'

function TeamInfo() {
  return (
    <div className="team-info">
      {/* Left: Club logo */}
      <img
        src="/static/images/teams/chelsea.webp"
        alt="Chelsea FC"
        className="team-logo-card"
      />

      {/* Right: Club information */}
      <div className="team-details">
        <h2 className="team-name">CHELSEA FC</h2>
        <p>Current Players: 58 (With valuation: 50)</p>
        <p>Total Squad Value: EUR 1.193B</p>
        <p>Average Player Value: EUR 23.5M</p>
      </div>
    </div>
  )
}

export default TeamInfo
