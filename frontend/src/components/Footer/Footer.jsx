import { useState, useEffect } from 'react'
import './Footer.css'

function Footer() {
  const [darkMode, setDarkMode] = useState(() => {
    return typeof window !== 'undefined' && localStorage.getItem('theme') === 'dark'
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
    <footer className="site-footer" role="contentinfo">
      <div className="footer-content">
        <span className="spacer" />
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
    </footer>
  )
}

export default Footer
