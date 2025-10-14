import { useState, useEffect } from 'react'
import { X, ArrowLeft, ArrowRight } from 'lucide-react'
import ValuationChart from '../ValuationChart/ValuationChart.jsx'
import mapPositions from '../Map/mapd.json'
import './Popup.css'

function Popup({ player, season, isOpen, onClose }) {
  const [expanded, setExpanded] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [playerData, setPlayerData] = useState(null)
  const [seasonData, setSeasonData] = useState(null)
  const [estimatedValue, setEstimatedValue] = useState(null)

  const [age, setAge] = useState(0)
  const [goals, setGoals] = useState(0)
  const [assists, setAssists] = useState(0)
  const [minutes, setMinutes] = useState(0)
  const [clubLogo, setClubLogo] = useState('/static/images/teams/default_logo.png')

  const normalize = (name) =>
    name?.toLowerCase().replace(/football club|fc|afc|city|united|\.|-/g, '').trim()

  const findTeamLogo = (clubName) => {
    if (!clubName) return '/static/images/teams/default_logo.png'
    const n = normalize(clubName)
    for (const key of Object.keys(mapPositions)) {
      const nk = normalize(key)
      if (n.includes(nk) || nk.includes(n)) return mapPositions[key].logo
    }
    return '/static/images/teams/default_logo.png'
  }

  useEffect(() => {
    if (!isOpen || !player) return
    setLoading(true)
    setError(null)

    const url = `http://127.0.0.1:5000/api/players/${player.id}?year_code=${encodeURIComponent(season)}`
    fetch(url)
      .then((res) => {
        if (!res.ok) throw new Error('Failed to fetch player data')
        return res.json()
      })
      .then((data) => {
        setPlayerData(data)
        const s = data.seasons?.find((x) => x.year_code === season) || player.seasonData || {}
        setSeasonData(s)
        setAge(s.age || 0)
        setGoals(s.goals_scored || 0)
        setAssists(s.assists_made || 0)
        setMinutes(s.minutes_played || 0)
        setClubLogo(findTeamLogo(s.club))
        setLoading(false)
      })
      .catch((err) => {
        setError(err.message)
        setLoading(false)
      })
  }, [player, season, isOpen])

  useEffect(() => {
    if (!isOpen) {
      setExpanded(false)
      setEstimatedValue(null)
      setPlayerData(null)
      setSeasonData(null)
    }
  }, [isOpen])

  if (!isOpen || !player) return null

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) onClose()
  }

  const valuations = playerData?.valuations || []
  const valuationData = valuations.map((v) => ({
    date: v.date,
    value: v.amount ? v.amount / 1_000_000 : 0,
  }))

  const handleEstimate = () => {
    const baseValue = playerData?.valuations?.[0]?.amount / 1_000_000 || 5
    const perf = goals * 2 + assists * 1.5 + minutes / 400
    const newVal = (baseValue + perf / ((age || 25) / 25)).toFixed(1)
    setEstimatedValue(newVal)
  }

  return (
    <div
      className={`player-drawer-overlay ${expanded ? 'expanded' : ''}`}
      onClick={handleOverlayClick}
    >
      <div className={`player-drawer ${expanded ? 'expanded-layout' : ''}`}>
        <div className="drawer-header">
          <button className="header-icon left" onClick={() => (expanded ? setExpanded(false) : onClose())}>
            {expanded ? <ArrowLeft size={28} /> : <X size={28} />}
          </button>

          <h2 className="player-name">{playerData?.name || player.name}</h2>

          <button className="header-icon right" onClick={() => setExpanded((e) => !e)}>
            {expanded ? <X size={28} /> : <ArrowRight size={28} />}
          </button>
        </div>

        <div className={`drawer-body ${expanded ? 'expanded' : ''}`}>
          {error ? (
            <p className="error-text">Error: {error}</p>
          ) : loading ? (
            <p className="loading-text">Loading player...</p>
          ) : (
            <>
              <div className="left-panel">
                <div className="player-info">
                  <img src={clubLogo} alt={seasonData?.club || 'Club'} className="player-photo" />
                  <h3>{playerData?.name}</h3>
                  <p><strong>Club:</strong> {seasonData?.club || '—'}</p>
                  <p><strong>Season:</strong> {season}</p>
                  <p><strong>Age:</strong> {age}</p>
                  <p><strong>Position:</strong> {seasonData?.position || '—'}</p>
                  <p><strong>Goals:</strong> {goals}</p>
                  <p><strong>Assists:</strong> {assists}</p>
                  <p><strong>Minutes:</strong> {minutes}</p>
                </div>

                <div className="chart-section">
                  <h4>Valuation History</h4>
                  <div className="chart-card">
                    <ValuationChart data={valuationData} height={250} />
                  </div>
                </div>

                {!expanded && (
                  <button className="customize-btn" onClick={() => setExpanded(true)}>
                    Customize Player
                  </button>
                )}
              </div>

              {expanded && (
                <div className="right-panel">
                  <h3>Customize Stats</h3>
                  <div className="form-grid-3x3">
                    <div className="form-field">
                      <label>Age</label>
                      <input type="number" value={age} onChange={(e) => setAge(+e.target.value)} />
                    </div>
                    <div className="form-field">
                      <label>Goals</label>
                      <input type="number" value={goals} onChange={(e) => setGoals(+e.target.value)} />
                    </div>
                    <div className="form-field">
                      <label>Assists</label>
                      <input type="number" value={assists} onChange={(e) => setAssists(+e.target.value)} />
                    </div>
                    <div className="form-field">
                      <label>Minutes</label>
                      <input type="number" value={minutes} onChange={(e) => setMinutes(+e.target.value)} />
                    </div>
                  </div>

                  <button className="estimate-btn-green" onClick={handleEstimate}>
                    Estimate New Value
                  </button>

                  {estimatedValue && (
                    <p className="estimate-result">💰 Estimated Value: €{estimatedValue}M</p>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default Popup
