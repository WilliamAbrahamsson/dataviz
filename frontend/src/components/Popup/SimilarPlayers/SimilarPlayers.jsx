import mapPositions from '../../Map/mapd.json'
import '../../Table/Table.css'
import './SimilarPlayers.css'

const DEFAULT_LOGO = '/static/images/teams/default_logo.png'

const normalize = (name = '') =>
  name.toLowerCase().replace(/football club|fc|afc|city|united|\.|-/g, '').trim()

const findTeamLogo = (clubName = '') => {
  if (!clubName) return DEFAULT_LOGO
  const normalized = normalize(clubName)

  for (const key of Object.keys(mapPositions)) {
    const nk = normalize(key)
    if (normalized.includes(nk) || nk.includes(normalized)) return mapPositions[key].logo
  }

  return DEFAULT_LOGO
}

const pickSeason = (player = {}, season) => {
  if (!player?.seasons) return null
  if (season) {
    const exact = player.seasons.find((s) => s?.year_code === season)
    if (exact) return exact
  }
  return player.seasons[0] || null
}

const formatValuation = (player) => {
  const amount =
    player?.valuations?.[0]?.amount ??
    player?.valuation ??
    player?.value ??
    player?.market_value ??
    null

  if (!Number.isFinite(Number(amount))) return 'NaN'
  return `€${(Number(amount) / 1_000_000).toFixed(1)}M`
}

function SimilarPlayers({ players = [], loading = false, season, onSelect }) {
  const rows = Array.isArray(players) ? players.slice(0, 5) : []

  return (
    <div className="similar-players-section">
      <div className="similar-players-header">
        <h4>Similar Players</h4>
        <span className="similar-players-caption">Top 5 nearest neighbors</span>
      </div>

      <div className="similar-players-table">
        {loading ? (
          <p className="similar-players-empty">Loading similar players...</p>
        ) : rows.length === 0 ? (
          <p className="similar-players-empty">No similar players available yet.</p>
        ) : (
          <table className="player-table compact">
            <thead>
              <tr>
                <th>Player</th>
                <th>Position</th>
                <th>Season</th>
                <th>Valuation (€M)</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((p, idx) => {
                const seasonInfo = pickSeason(p, season)
                const logo = findTeamLogo(seasonInfo?.club || p.club || p.team || '')
                const valuation = formatValuation(p)
                const displayPosition = seasonInfo?.position || p.position || '—'
                const displaySeason = p?.matched_season_year_code || seasonInfo?.year_code || '—'
                return (
                  <tr
                    key={`${p.id || p.name || 'similar'}-${idx}`}
                    className={onSelect ? 'clickable-row' : ''}
                    onClick={() => {
                      if (!onSelect) return
                      onSelect(p)
                    }}
                  >
                    <td className="player-cell">
                      <img
                        src={logo}
                        alt={seasonInfo?.club || p.club || p.team || 'Club'}
                        className="player-logo"
                      />
                      <span>{p.name || 'Unknown'}</span>
                    </td>
                    <td>{displayPosition}</td>
                    <td>{displaySeason}</td>
                    <td className={`valuation ${valuation === 'NaN' ? 'valuation-nan' : ''}`}>
                      {valuation}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default SimilarPlayers
