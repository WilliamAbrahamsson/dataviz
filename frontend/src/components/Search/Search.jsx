import { useState, useEffect, useRef } from 'react'
import './Search.css'

function Search({ onSelect, currentSeason }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef(null)

  // Fetch players from backend (filtered by season)
  useEffect(() => {
    const fetchPlayers = async () => {
      const trimmed = query.trim()
      if (!trimmed || !currentSeason) {
        setResults([])
        setIsOpen(false)
        return
      }

      try {
        const url = `/api/players?year_code=${encodeURIComponent(
          currentSeason
        )}&name=${encodeURIComponent(trimmed)}`
        const res = await fetch(url)
        if (!res.ok) throw new Error('Failed to fetch players')
        const data = await res.json()

        // ✅ Only include players who have a valid PlayerSeason for this season
        const filtered = data
          .filter((p) =>
            p.seasons?.some((s) => s.year_code === currentSeason && s.club)
          )
          .filter((p) =>
            p.name.toLowerCase().includes(trimmed.toLowerCase())
          )
          .slice(0, 8)

        setResults(filtered)
        setIsOpen(filtered.length > 0)
      } catch (err) {
        console.error('Search error:', err)
        setResults([])
        setIsOpen(false)
      }
    }

    const timeout = setTimeout(fetchPlayers, 250) // debounce
    return () => clearTimeout(timeout)
  }, [query, currentSeason])

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSelect = (player) => {
    setQuery(player.name)
    setIsOpen(false)
    onSelect?.(player)
  }

  return (
    <div className="search-wrapper" ref={dropdownRef}>
      <input
        type="text"
        className="search-input"
        placeholder={
          currentSeason
            ? `Search players (season ${currentSeason})`
            : 'Select season first...'
        }
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => results.length > 0 && setIsOpen(true)}
        disabled={!currentSeason}
      />

      {isOpen && (
        <ul className="search-dropdown">
          {results.map((player) => {
            const seasonData = player.seasons.find(
              (s) => s.year_code === currentSeason && s.club
            )
            if (!seasonData) return null // 🚫 skip players without club/season data
            return (
              <li key={player.id} onClick={() => handleSelect(player)}>
                <div className="player-result">
                  <span className="player-name">{player.name}</span>
                  <span className="player-meta">{seasonData.club}</span>
                </div>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}

export default Search
