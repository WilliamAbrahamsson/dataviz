import { useState, useEffect } from 'react'
import { X, ArrowLeft, ArrowRight } from 'lucide-react'
import ValuationChart from '../ValuationChart/ValuationChart.jsx'
import './Popup.css'

function Popup({ player, isOpen, onClose }) {
  const [expanded, setExpanded] = useState(false)
  const [age, setAge] = useState(31)
  const [goals, setGoals] = useState(4)
  const [assists, setAssists] = useState(12)
  const [passes, setPasses] = useState(7)
  const [shots, setShots] = useState(20)
  const [tackles, setTackles] = useState(18)
  const [minutes, setMinutes] = useState(1700)
  const [dribbles, setDribbles] = useState(35)
  const [interceptions, setInterceptions] = useState(15)
  const [estimatedValue, setEstimatedValue] = useState(null)

  const valuationData = [
    { date: '2023-08-01', value: 40.0 },
    { date: '2023-12-01', value: 48.2 },
    { date: '2024-04-01', value: 56.1 },
    { date: '2024-08-01', value: 62.4 },
    { date: '2025-02-01', value: 70.8 },
  ]

  useEffect(() => {
    if (!isOpen) {
      setExpanded(false)
      setEstimatedValue(null)
      setAge(31)
      setGoals(4)
      setAssists(12)
      setPasses(7)
      setShots(20)
      setTackles(18)
      setMinutes(1700)
      setDribbles(35)
      setInterceptions(15)
    }
  }, [isOpen])

  if (!isOpen || !player) return null

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) onClose()
  }

  const handleEstimate = () => {
    const baseValue = player.value || 100
    const performanceScore =
      goals * 2.5 +
      assists * 1.8 +
      passes * 0.2 +
      shots * 0.4 +
      tackles * 0.5 +
      dribbles * 0.6 +
      interceptions * 0.5 +
      minutes / 500

    const newVal = (baseValue + (performanceScore * 1.2) / (age / 25)).toFixed(1)
    setEstimatedValue(newVal)
  }

  return (
    <div
      className={`player-drawer-overlay ${expanded ? 'expanded' : ''}`}
      onClick={handleOverlayClick}
    >
      <div className={`player-drawer ${expanded ? 'expanded-layout' : ''}`}>
        {/* === HEADER === */}
        <div className="drawer-header">
          <button
            className="header-icon left"
            onClick={() => {
              if (expanded) setExpanded(false)
              else onClose()
            }}
            title={expanded ? 'Collapse' : 'Close'}
          >
            {expanded ? <ArrowLeft size={28} /> : <X size={28} />}
          </button>

          <h2 className="player-name">{player.name}</h2>

          <button
            className="header-icon right"
            onClick={() => {
              if (expanded) onClose()
              else setExpanded(true)
            }}
            title={expanded ? 'Close' : 'Expand'}
          >
            {expanded ? <X size={28} /> : <ArrowRight size={28} />}
          </button>
        </div>

        {/* === BODY === */}
        <div className={`drawer-body ${expanded ? 'expanded' : ''}`}>
          {/* LEFT PANEL */}
          <div className="left-panel">
            <div className="player-info">
              <img
                src="/static/images/teams/chelsea.webp"
                alt="Chelsea FC Logo"
                className="player-photo"
                draggable="false"
              />
              <h3>{player.name}</h3>
              <p><strong>Age:</strong> {age}</p>
              <p><strong>Position:</strong> {player.position}</p>
              <p><strong>Nationality:</strong> Great Britain</p>
              <p>
                <strong>Market Value:</strong> €
                {estimatedValue ?? player.value}M
              </p>
            </div>

            <div className="chart-section">
              <h4>Valuation Progression</h4>
              <div className="chart-card">
                <ValuationChart data={valuationData} height={250} />
              </div>
            </div>

            {/* 👇 Add Customize Button here when not expanded */}
            {!expanded && (
              <button
                className="customize-btn"
                onClick={() => setExpanded(true)}
              >
                Customize Player
              </button>
            )}
          </div>

          {/* RIGHT PANEL (Only when expanded) */}
          {expanded && (
            <div className="right-panel">
              <h3>Customize Player Stats</h3>
              <div className="form-grid-3x3">
                <div className="form-field">
                  <label>Age</label>
                  <input type="number" value={age} onChange={e => setAge(+e.target.value)} />
                </div>
                <div className="form-field">
                  <label>Goals</label>
                  <input type="number" value={goals} onChange={e => setGoals(+e.target.value)} />
                </div>
                <div className="form-field">
                  <label>Assists</label>
                  <input type="number" value={assists} onChange={e => setAssists(+e.target.value)} />
                </div>
                <div className="form-field">
                  <label>Passes</label>
                  <input type="number" value={passes} onChange={e => setPasses(+e.target.value)} />
                </div>
                <div className="form-field">
                  <label>Shots</label>
                  <input type="number" value={shots} onChange={e => setShots(+e.target.value)} />
                </div>
                <div className="form-field">
                  <label>Tackles</label>
                  <input type="number" value={tackles} onChange={e => setTackles(+e.target.value)} />
                </div>
                <div className="form-field">
                  <label>Minutes</label>
                  <input type="number" value={minutes} onChange={e => setMinutes(+e.target.value)} />
                </div>
                <div className="form-field">
                  <label>Dribbles</label>
                  <input type="number" value={dribbles} onChange={e => setDribbles(+e.target.value)} />
                </div>
                <div className="form-field">
                  <label>Interceptions</label>
                  <input type="number" value={interceptions} onChange={e => setInterceptions(+e.target.value)} />
                </div>
              </div>

              <button className="estimate-btn-green" onClick={handleEstimate}>
                Estimate New Valuation
              </button>

              {estimatedValue && (
                <p className="estimate-result">
                  💰 New Estimated Value: <strong>€{estimatedValue}M</strong>
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Popup
