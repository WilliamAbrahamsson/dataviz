import { useEffect, useState } from 'react'
import Popup from '../Popup/Popup.jsx'
import mapPositions from '../Map/mapd.json'
import './Table.css'

function parseSeasonEndYear(season) {
  if (!season) return null
  const str = String(season)

  const rangeMatch = str.match(/(\d{4})\s*[/\-]\s*(\d{2,4})/)
  if (rangeMatch) {
    const startYear = Number(rangeMatch[1]) || null
    const second = rangeMatch[2]

    if (second.length === 4) {
      const endYear = Number(second)
      return Number.isNaN(endYear) ? null : endYear
    }

    return startYear != null && !Number.isNaN(startYear)
      ? startYear + 1
      : null
  }

  const singleYear = str.match(/\d{4}/)
  if (!singleYear) return null
  const year = Number(singleYear[0])
  return Number.isNaN(year) ? null : year
}

function getSeasonValuation(valuations = [], season) {
  if (!Array.isArray(valuations) || valuations.length === 0) return null

  const endYear = parseSeasonEndYear(season)
  const seasonFiltered = endYear
    ? valuations.filter((v) => {
        if (!v?.date) return false
        const d = new Date(v.date)
        const year = d.getFullYear()
        return !Number.isNaN(year) && year <= endYear
      })
    : valuations.filter((v) => v?.date)

  if (seasonFiltered.length === 0) return null

  const sorted = [...seasonFiltered].sort((a, b) => new Date(a.date) - new Date(b.date))

  let seasonWindow = sorted
  if (endYear) {
    const juneCutoff = new Date(endYear, 5, 30)
    const firstAfterJuneIdx = sorted.findIndex((v) => {
      const d = new Date(v.date)
      return d > juneCutoff && d.getFullYear() === endYear
    })

    if (firstAfterJuneIdx !== -1) {
      seasonWindow = sorted.slice(0, firstAfterJuneIdx + 1)
    }
  }

  if (seasonWindow.length === 0) return null

  const latest = seasonWindow[seasonWindow.length - 1]
  const amount = Number(latest?.amount)
  return Number.isFinite(amount) ? amount : null
}

function Table({ teamName, season, externalPlayer, onClosePlayer }) {
  const [players, setPlayers] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedPlayer, setSelectedPlayer] = useState(null)

  const teamLogo =
    teamName && mapPositions[teamName]
      ? mapPositions[teamName].logo
      : '/static/images/teams/default_logo.png'

  useEffect(() => {
    if (!teamName || !season) return
    setLoading(true)
    setError(null)

    const url = `/api/players?club=${encodeURIComponent(teamName)}&year_code=${encodeURIComponent(season)}`
    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch players')
        return res.json()
      })
      .then((data) => {
        setPlayers(data)
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [teamName, season])

  useEffect(() => {
    if (externalPlayer) {
      setSelectedPlayer(externalPlayer)
    }
  }, [externalPlayer])

  return (
    <>
      <div className="table-wrapper">
        {!teamName && <p className="status">Select a team on the map to view players.</p>}
        {loading && <p className="status">Loading players...</p>}
        {error && <p className="status error">Error: {error}</p>}

        {!loading && !error && teamName && players.length > 0 && (
          <table className="player-table">
            <thead>
              <tr>
                <th>Player</th>
                <th>Position</th>
                <th>Age</th>
                <th>Valuation (€M)</th>
              </tr>
            </thead>
            <tbody>
              {players.map((player) => {
                const seasonData = player.seasons?.find((s) => s.year_code === season)
                const valuationAmount = getSeasonValuation(player.valuations, season)
                const hasValuation = Number.isFinite(valuationAmount)
                const valuation = hasValuation
                  ? (valuationAmount / 1_000_000).toFixed(1)
                  : null
                const rowDisabled = !hasValuation

                return (
                  <tr
                    key={player.id}
                    className={`clickable-row${rowDisabled ? ' row-disabled' : ''}`}
                    onClick={() => {
                      if (rowDisabled) return
                      setSelectedPlayer({ ...player, seasonData })
                    }}
                  >
                    <td className="player-cell">
                      <img src={teamLogo} alt={teamName} className="player-logo" />
                      <span>{player.name}</span>
                    </td>
                    <td>{seasonData?.position || '—'}</td>
                    <td>{seasonData?.age || '—'}</td>
                    <td className={`valuation ${valuation ? '' : 'valuation-nan'}`}>
                      {valuation ? `€${valuation}M` : 'No Valuation Data'}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}

        {!loading && !error && teamName && players.length === 0 && (
          <p className="status">No players found for {teamName} in {season}.</p>
        )}
      </div>

      <Popup
        player={selectedPlayer}
        season={season}
        isOpen={!!selectedPlayer}
        onSelectPlayer={(p) => setSelectedPlayer(p)}
        onClose={() => {
          setSelectedPlayer(null)
          onClosePlayer?.()
        }}
      />
    </>
  )
}

export default Table
