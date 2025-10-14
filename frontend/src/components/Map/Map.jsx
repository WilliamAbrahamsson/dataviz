import { useState } from 'react'
import './Map.css'

function Map() {
  const [season, setSeason] = useState('2024/25')

  const seasons = ['2024/25', '2023/24', '2022/23', '2021/22', '2020/21']

  return (
    <div className="map-container">
      {/* 🔽 Season selector */}
      <div className="season-selector">
        <label htmlFor="season">Season:</label>
        <select
          id="season"
          value={season}
          onChange={(e) => setSeason(e.target.value)}
        >
          {seasons.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      {/* 🗺️ UK Map */}
      <img
        src="/static/images/uk_map.png"
        alt="UK Map"
        className="map-image"
        draggable="false"
      />

      {/* ⚽ Example team logos */}
      <img
        src="/static/images/teams/newcastle.webp"
        alt="Newcastle"
        className="team-logo"
        draggable="false"
        style={{ top: '25%', left: '60%' }}
      />

      <img
        src="/static/images/teams/liverpool.png"
        alt="Liverpool"
        className="team-logo"
        draggable="false"
        style={{ top: '35%', left: '35%' }}
      />

      <img
        src="/static/images/teams/mancity.png"
        alt="Manchester City"
        className="team-logo"
        draggable="false"
        style={{ top: '42%', left: '47%' }}
      />

      <img
        src="/static/images/teams/arsenal.webp"
        alt="Arsenal"
        className="team-logo"
        draggable="false"
        style={{ top: '62%', left: '53%' }}
      />

      <img
        src="/static/images/teams/chelsea.webp"
        alt="Chelsea"
        className="team-logo"
        draggable="false"
        style={{ top: '60%', left: '55%' }}
      />
    </div>
  )
}

export default Map
