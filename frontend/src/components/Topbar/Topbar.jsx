import { useState, useEffect } from 'react'
import './Topbar.css'
import Search from '../Search/Search.jsx'

function Topbar({ onPlayerSelect, selectedSeason }) {
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem('theme') === 'dark'
  })

  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode')
      localStorage.setItem('theme', 'dark')
    } else {
      document.body.classList.remove('dark-mode')
      localStorage.setItem('theme', 'light')
    }
  }, [darkMode])

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

          <button
            className={`theme-toggle-btn ${darkMode ? 'dark' : 'light'}`}
            onClick={() => setDarkMode((v) => !v)}
            title="Toggle theme"
          >
            <div className="toggle-track">
              <div className="toggle-thumb">
                {darkMode ? '🌙' : '☀️'}
              </div>
            </div>
          </button>
        </div>
      </div>
    </header>
  )
}

export default Topbar
