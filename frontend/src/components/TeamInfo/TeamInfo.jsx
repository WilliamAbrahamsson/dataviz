import { useEffect, useState } from 'react'
import './TeamInfo.css'
import { resolveTeamInfo } from '../../utils/teamLogos.js'

function TeamInfo({ teamName, season, refreshKey = 0 }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [stats, setStats] = useState({
    totalPlayers: 0,
    withValuation: 0,
    totalValue: 0,
    avgValue: 0,
  })

  const teamInfo = teamName ? resolveTeamInfo(teamName) : null

  useEffect(() => {
    if (!teamName || !season) return

    setLoading(true)
    setError(null)

    const url = `/api/players?club=${encodeURIComponent(teamName)}&year_code=${encodeURIComponent(season)}`
    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch team data')
        return res.json()
      })
      .then((data) => {
        const totalPlayers = data.length
        const valuations = data.map((p) => p.valuations?.[0]?.amount || 0)
        const withValuation = valuations.filter((v) => v > 0).length
        const totalValue = valuations.reduce((sum, v) => sum + v, 0)
        const avgValue = withValuation > 0 ? totalValue / withValuation : 0

        setStats({
          totalPlayers,
          withValuation,
          totalValue,
          avgValue,
        })
        setLoading(false)
      })
      .catch((err) => {
        console.error('Team info error:', err)
        setError(err.message)
        setLoading(false)
      })
  }, [teamName, season, refreshKey])

  return (
    <div className="team-info">
      {!teamName && (
        <p className="placeholder-text">Click a team on the map to view details</p>
      )}

      {teamName && loading && (
        <p className="placeholder-text">Loading team info...</p>
      )}

      {teamName && error && (
        <p className="placeholder-text error">Error: {error}</p>
      )}

      {teamInfo && !loading && !error && (
        <>
          <img src={teamInfo.logo} alt={teamName} className="team-logo-card" />
          <div className="team-details">
            <h2 className="team-name">{teamName.toUpperCase()}</h2>
            <div className="value-badges">
              <span className="badge">
                <span className="badge-label">Current Players</span>
                <span className="badge-value">{stats.totalPlayers}</span>
              </span>
              <span className="badge">
                <span className="badge-label">With Valuation</span>
                <span className="badge-value">{stats.withValuation}</span>
              </span>
              <span className="badge">
                <span className="badge-label">Total Squad Value</span>
                <span className="badge-value">
                  {stats.totalValue > 0
                    ? `€${(stats.totalValue / 1_000_000_000).toFixed(3)}B`
                    : '—'}
                </span>
              </span>
              <span className="badge">
                <span className="badge-label">Avg Player Value</span>
                <span className="badge-value">
                  {stats.avgValue > 0
                    ? `€${(stats.avgValue / 1_000_000).toFixed(1)}M`
                    : '—'}
                </span>
              </span>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default TeamInfo
