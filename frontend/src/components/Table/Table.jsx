import { useEffect, useState } from 'react'
import Popup from '../Popup/Popup.jsx'
import mapPositions from '../Map/mapd.json'
import './Table.css'

function Table({ teamName, season, externalPlayer, onClosePlayer }) {
  const [players, setPlayers] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [selectedPlayer, setSelectedPlayer] = useState(null)

  const teamLogo =
    teamName && mapPositions[teamName]
      ? mapPositions[teamName].logo
      : '/static/images/teams/default_logo.png'

  // Fetch team players
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

  // If external player passed in (from search)
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
                const valuationAmount = player.valuations?.[0]?.amount
                const valuation = valuationAmount
                  ? (valuationAmount / 1_000_000).toFixed(1)
                  : null

                return (
                  <tr
                    key={player.id}
                    className="clickable-row"
                    onClick={() => setSelectedPlayer({ ...player, seasonData })}
                  >
                    <td className="player-cell">
                      <img src={teamLogo} alt={teamName} className="player-logo" />
                      <span>{player.name}</span>
                    </td>
                    <td>{seasonData?.position || '—'}</td>
                    <td>{seasonData?.age || '—'}</td>
                    <td className={`valuation ${valuation ? '' : 'valuation-nan'}`}>
                      {valuation ? `€${valuation}M` : 'NaN'}
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
        onClose={() => {
          setSelectedPlayer(null)
          onClosePlayer?.()
        }}
      />
    </>
  )
}

export default Table
