import { useEffect } from 'react'
import './Topbar.css'
import Search from '../Search/Search.jsx'

function Topbar({ onPlayerSelect, selectedSeason }) {
  // Topbar no longer manages theme; Footer contains theme toggle
  useEffect(() => {}, [])

  return (
    <header className="topbar">
      <div className="topbar-content">
        <div className="topbar-left">
          <h1 className="topbar-logo">
            <span className="logo-accent">Footballer</span>Valuation Tool
          </h1>
        </div>

        <div className="topbar-right">
          <Search onSelect={onPlayerSelect} currentSeason={selectedSeason} />
        </div>
      </div>
    </header>
  )
}

export default Topbar
