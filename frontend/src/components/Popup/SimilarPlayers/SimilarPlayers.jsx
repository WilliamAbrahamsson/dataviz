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

const parseSeasonEndYear = (season) => {
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
    return startYear != null && !Number.isNaN(startYear) ? startYear + 1 : null
  }
  const singleYear = str.match(/\d{4}/)
  if (!singleYear) return null
  const year = Number(singleYear[0])
  return Number.isNaN(year) ? null : year
}

const getSeasonValuation = (valuations = [], season) => {
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

const formatValuation = (player, seasonCode) => {
  const amount = getSeasonValuation(player?.valuations, seasonCode)
  if (!Number.isFinite(Number(amount))) return 'No Valuation Data'
  return `€${(Number(amount) / 1_000_000).toFixed(1)}M`
}

function SimilarPlayers({ players = [], loading = false, season, onSelect }) {
  const rows = Array.isArray(players) ? players.slice(0, 5) : []

  return (
    <div className="similar-players-section">
      <div className="similar-players-header">
        <h4>Similar Player Season Performances</h4>
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
                const targetSeason = p?.matched_season_year_code || season
                const valuation = formatValuation(p, targetSeason)
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
