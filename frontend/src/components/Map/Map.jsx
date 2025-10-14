import { useState, useEffect } from 'react'
import mapPositions from './mapd.json'
import seasonTeams from './teamsd.json'
import './Map.css'

function Map({ onTeamSelect, onSeasonChange }) {
  const allSeasons = Object.keys(seasonTeams)
  const [season, setSeason] = useState(allSeasons[0])
  const [isDarkMode, setIsDarkMode] = useState(false)

  // Sync with dark mode
  useEffect(() => {
    const updateMode = () =>
      setIsDarkMode(document.body.classList.contains('dark-mode'))
    updateMode()

    const observer = new MutationObserver(updateMode)
    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] })
    return () => observer.disconnect()
  }, [])

  // Notify parent and select a random team
  useEffect(() => {
    onSeasonChange?.(season)
    const teams = seasonTeams[season] || []
    if (teams.length && onTeamSelect) {
      const randomTeam = teams[Math.floor(Math.random() * teams.length)]
      onTeamSelect(randomTeam)
    }
  }, [season, onSeasonChange, onTeamSelect])

  const teamsInSeason = seasonTeams[season] || []
  const mapImage = isDarkMode
    ? '/static/images/uk_map_dm.png'
    : '/static/images/uk_map_lm.png'

  return (
    <div className="map-container">
      <div className="season-selector">
        <label htmlFor="season">Season:</label>
        <select
          id="season"
          value={season}
          onChange={(e) => setSeason(e.target.value)}
        >
          {allSeasons.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      <div className="map-wrapper">
        <img
          src={mapImage}
          alt="UK Map"
          className="map-image"
          draggable="false"
        />

        {teamsInSeason.map((teamName) => {
          const teamInfo = mapPositions[teamName]
          if (!teamInfo) return null
          return (
            <img
              key={teamName}
              src={teamInfo.logo}
              alt={teamName}
              className="team-logo"
              draggable="false"
              style={{ top: teamInfo.top, left: teamInfo.left }}
              title={teamName}
              onClick={() => onTeamSelect?.(teamName)}
            />
          )
        })}
      </div>
    </div>
  )
}

export default Map
