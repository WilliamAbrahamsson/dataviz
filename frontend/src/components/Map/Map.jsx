import { useState, useEffect, useRef } from 'react'
import initialPositions from './mapd.json'
import seasonTeams from './teamsd.json'
import './Map.css'

function Map({ onTeamSelect, season, selectedTeam }) {
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [positions, setPositions] = useState(() => {
    // Normalize to numeric percent values
    const copy = {}
    for (const [team, v] of Object.entries(initialPositions)) {
      copy[team] = {
        logo: v.logo,
        top: parseFloat(String(v.top).replace('%', '')),
        left: parseFloat(String(v.left).replace('%', '')),
      }
    }
    return copy
  })
  const draggingRef = useRef(null) // { team }
  const wrapperRef = useRef(null)

  // Sync with dark mode
  useEffect(() => {
    const updateMode = () =>
      setIsDarkMode(document.body.classList.contains('dark-mode'))
    updateMode()

    const observer = new MutationObserver(updateMode)
    observer.observe(document.body, { attributes: true, attributeFilter: ['class'] })
    return () => observer.disconnect()
  }, [])

  // Select team when season changes; prefer externally selected team, else random.
  useEffect(() => {
    const teams = seasonTeams[season] || []
    if (!teams.length || !onTeamSelect) return

    if (selectedTeam && teams.includes(selectedTeam)) {
      onTeamSelect(selectedTeam)
      return
    }

    const randomTeam = teams[Math.floor(Math.random() * teams.length)]
    onTeamSelect(randomTeam)
  }, [season, onTeamSelect, selectedTeam])

  const teamsInSeason = seasonTeams[season] || []
  const mapImage = isDarkMode
    ? '/static/images/uk_map_dm.png'
    : '/static/images/uk_map_lm.png'

  return (
    <div className="map-container">
      {/* <div className="season-selector">
        <label className="edit-toggle">
          <input
            type="checkbox"
            checked={isEditing}
            onChange={(e) => setIsEditing(e.target.checked)}
          />
          Edit positions
        </label>
      </div> */}

      <div
        className={`map-wrapper${isEditing ? ' editing' : ''}`}
        ref={wrapperRef}
        onMouseMove={(e) => {
          const drag = draggingRef.current
          if (!drag) return
          const rect = wrapperRef.current?.getBoundingClientRect()
          if (!rect) return
          const x = e.clientX - rect.left
          const y = e.clientY - rect.top
          const left = Math.max(0, Math.min(100, (x / rect.width) * 100))
          const top = Math.max(0, Math.min(100, (y / rect.height) * 100))
          setPositions((prev) => ({
            ...prev,
            [drag.team]: { ...prev[drag.team], top, left },
          }))
        }}
        onMouseUp={async () => {
          const drag = draggingRef.current
          if (!drag) return
          draggingRef.current = null
          // Persist to backend
          try {
            const p = positions[drag.team]
            await fetch('/api/map/positions', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ team: drag.team, top: p.top, left: p.left }),
            })
          } catch (err) {
            console.error('Failed to save position', err)
          }
        }}
        onMouseLeave={() => {
          // End drag if cursor leaves wrapper
          draggingRef.current = null
        }}
      >
        <img
          src={mapImage}
          alt="UK Map"
          className="map-image"
          draggable="false"
        />

        {teamsInSeason.map((teamName) => {
          const teamInfo = positions[teamName]
          if (!teamInfo) return null
          return (
            <img
              key={teamName}
              src={teamInfo.logo}
              alt={teamName}
              className="team-logo"
              draggable={false}
              style={{ top: `${teamInfo.top}%`, left: `${teamInfo.left}%`, cursor: isEditing ? 'grab' : 'pointer' }}
              title={teamName}
              onMouseDown={(e) => {
                if (!isEditing) return
                e.preventDefault()
                draggingRef.current = { team: teamName }
              }}
              onClick={() => {
                if (isEditing) return
                onTeamSelect?.(teamName)
              }}
            />
          )
        })}
      </div>
    </div>
  )
}

export default Map
