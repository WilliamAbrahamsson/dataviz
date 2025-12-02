import { useEffect, useMemo, useRef } from 'react'
import './Topbar.css'
import Search from '../Search/Search.jsx'
import seasonTeams from '../Map/teamsd.json'

function Topbar({ onPlayerSelect, selectedSeason, onSeasonChange }) {
  // Topbar no longer manages theme; Footer contains theme toggle
  useEffect(() => {}, [])

  const seasons = useMemo(() => {
    return Object.keys(seasonTeams)
      .sort((a, b) => {
        const ay = parseInt(String(a).slice(0, 4), 10) || 0
        const by = parseInt(String(b).slice(0, 4), 10) || 0
        return by - ay
      })
  }, [])

  const seasonSelectRef = useRef(null)

  const handleSeasonPickerClick = (e) => {
    if (e.target?.tagName?.toLowerCase() === 'select') return
    if (seasonSelectRef.current) {
      seasonSelectRef.current.focus()
      if (seasonSelectRef.current.showPicker) {
        seasonSelectRef.current.showPicker()
      } else if (seasonSelectRef.current.click) {
        seasonSelectRef.current.click()
      }
    }
  }

  return (
    <header className="topbar">
      <div className="topbar-content">
        <div className="topbar-left">
          <h1 className="topbar-logo">
            <span className="logo-accent">PL EVALUATION LAB</span>
            <span className="logo-tail">Deluxe Edition</span>
          </h1>
        </div>

        <div className="topbar-right">
          <div className="season-picker" onClick={handleSeasonPickerClick}>
            <label htmlFor="topbar-season" className="season-label">Season</label>
            <select
              id="topbar-season"
              className="season-select"
              ref={seasonSelectRef}
              value={selectedSeason || ''}
              onChange={(e) => onSeasonChange?.(e.target.value)}
            >
              <option value="" disabled>Select</option>
              {seasons.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
            <span className="season-caret" aria-hidden="true">▾</span>
          </div>
          <Search onSelect={onPlayerSelect} currentSeason={selectedSeason} />
        </div>
      </div>
    </header>
  )
}

export default Topbar
