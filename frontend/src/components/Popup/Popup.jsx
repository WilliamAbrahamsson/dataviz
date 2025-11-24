import { useState, useEffect } from 'react'
import { X, ArrowLeft, ArrowRight } from 'lucide-react'
import ChartWrapper from './Chart/ChartWrapper/ChartWrapper.jsx'
import mapPositions from '../Map/mapd.json'
import './Popup.css'

const FEATURE_KEYS = [
  'position',
  'club',
  'age',
  'matches_played',
  'matches_started',
  'minutes_played',
  'goals_scored',
  'assists_made',
  'goals_plus_assists',
  'penalty_goals',
  'penalty_attempts',
  'yellow_cards',
  'red_cards',
  'expected_goals',
  'non_penalty_expected_goals',
  'expected_assists',
  'combined_non_penalty_expected_goal_contributions',
  'progressive_carries',
  'progressive_passes',
  'progressive_receptions',
  'passes_completed',
  'passes_attempted',
  'pass_completion_pct',
  'pass_total_distance',
  'pass_progressive_distance',
  'short_passes_completed',
  'short_passes_attempted',
  'medium_passes_completed',
  'medium_passes_attempted',
  'long_passes_completed',
  'long_passes_attempted',
  'key_passes',
  'passes_into_final_third',
  'passes_into_penalty_area',
  'crosses_into_pa',
  'tackles',
  'tackles_won',
  'tackles_def_3rd',
  'tackles_mid_3rd',
  'tackles_att_3rd',
  'challenges_tackles',
  'challenges_attempted',
  'challenges_tackle_pct',
  'challenges_lost',
  'blocks',
  'blocks_shots',
  'blocks_passes',
  'interceptions',
  'tackles_plus_interceptions',
  'clearances',
  'errors_leading_to_shot',
]

const TEXT_FEATURES = new Set(['position', 'club'])

const FEATURE_OPTIONS = FEATURE_KEYS.map((key) => ({
  key,
  label: key
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' '),
  type: TEXT_FEATURES.has(key) ? 'text' : 'number',
}))

const POSITION_OPTIONS = ['GK', 'DF', 'MF', 'FW']
const CLUB_OPTIONS = Object.keys(mapPositions).sort((a, b) => a.localeCompare(b))

const DEFAULT_SELECTED_FEATURES = ['age', 'goals_scored', 'assists_made', 'matches_played']

const buildFeatureValues = (stats = {}) => {
  const values = {}
  FEATURE_OPTIONS.forEach(({ key }) => {
    values[key] = stats[key] ?? ''
  })
  return values
}

function Popup({ player, season, isOpen, onClose }) {
  const [expanded, setExpanded] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [playerData, setPlayerData] = useState(null)
  const [seasonData, setSeasonData] = useState(null)
  const [estimatedValue, setEstimatedValue] = useState(null)

  const [featureValues, setFeatureValues] = useState({})
  const [selectedFeatures, setSelectedFeatures] = useState(DEFAULT_SELECTED_FEATURES)
  const [clubLogo, setClubLogo] = useState('/static/images/teams/default_logo.png')
  const [isFeatureDropdownOpen, setIsFeatureDropdownOpen] = useState(false)

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
        setFeatureValues(buildFeatureValues(s))
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
      setFeatureValues({})
      setIsFeatureDropdownOpen(false)
    }
  }, [isOpen])

  useEffect(() => {
    if (!expanded) setIsFeatureDropdownOpen(false)
  }, [expanded])

  if (!isOpen || !player) return null

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) onClose()
  }

  const valuations = playerData?.valuations || []
  const valuationData = valuations.map((v) => ({
    date: v.date,
    value: v.amount ? v.amount / 1_000_000 : 0,
  }))

  const formatDisplayValue = (key, fallback) => {
    const value = featureValues?.[key]
    if (value === 0) return 0
    if (value === '' || value === undefined || value === null) return fallback ?? '—'
    return value
  }

  const handleFeatureChange = (featureKey, value) => {
    const option = FEATURE_OPTIONS.find((opt) => opt.key === featureKey)
    const parsedValue =
      option?.type === 'number' ? (value === '' ? '' : Number(value)) : value
    setFeatureValues((prev) => ({
      ...prev,
      [featureKey]: parsedValue,
    }))
  }

  const toggleFeatureSelection = (featureKey) => {
    setSelectedFeatures((prev) =>
      prev.includes(featureKey)
        ? prev.filter((key) => key !== featureKey)
        : [...prev, featureKey]
    )
  }

  const renderFeatureInput = (featureKey, option) => {
    if (!option) return null

    if (featureKey === 'club') {
      const clubValue = featureValues[featureKey] || ''
      const includeFallback = clubValue && !CLUB_OPTIONS.includes(clubValue)

      return (
        <select value={clubValue} onChange={(e) => handleFeatureChange(featureKey, e.target.value)}>
          <option value="">Select Club</option>
          {includeFallback && (
            <option value={clubValue}>{clubValue}</option>
          )}
          {CLUB_OPTIONS.map((club) => (
            <option key={club} value={club}>
              {club}
            </option>
          ))}
        </select>
      )
    }

    if (featureKey === 'position') {
      const positionValue = featureValues[featureKey] || ''
      const includeFallback = positionValue && !POSITION_OPTIONS.includes(positionValue)

      return (
        <select
          value={positionValue}
          onChange={(e) => handleFeatureChange(featureKey, e.target.value)}
        >
          <option value="">Select Position</option>
          {includeFallback && (
            <option value={positionValue}>{positionValue}</option>
          )}
          {POSITION_OPTIONS.map((position) => (
            <option key={position} value={position}>
              {position}
            </option>
          ))}
        </select>
      )
    }

    return (
      <input
        type={option.type === 'number' ? 'number' : 'text'}
        value={
          featureValues[featureKey] === '' || featureValues[featureKey] === undefined
            ? ''
            : featureValues[featureKey]
        }
        onChange={(e) => handleFeatureChange(featureKey, e.target.value)}
      />
    )
  }

  const handleEstimate = () => {
    if (!player) return

    const payload = {
      featureValues
    }

    fetch('http://127.0.0.1:5000/api/estimate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then((response) => response.json())
      .then((data) => {
        setEstimatedValue(data.estimated_value)
      })
      .catch((error) => {
        console.error('Error estimating value:', error)
      })
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
                  <p><strong>Club:</strong> {formatDisplayValue('club', seasonData?.club)}</p>
                  <p><strong>Season:</strong> {season}</p>
                  <p><strong>Age:</strong> {formatDisplayValue('age')}</p>
                  <p><strong>Position:</strong> {formatDisplayValue('position', seasonData?.position)}</p>
                  <p><strong>Goals:</strong> {formatDisplayValue('goals_scored')}</p>
                  <p><strong>Assists:</strong> {formatDisplayValue('assists_made')}</p>
                  <p><strong>Minutes:</strong> {formatDisplayValue('minutes_played')}</p>
                </div>

                <ChartWrapper
                  valuations={playerData?.valuations || []}
                  season={season}
                />

                {!expanded && (
                  <button className="customize-btn" onClick={() => setExpanded(true)}>
                    Customize Player
                  </button>
                )}
              </div>

              {expanded && (
                <div className="right-panel">
                  <h3>Customize Stats</h3>
                  <div className="form-field">
                    <label>Select Features</label>
                    <div className="feature-selector">
                      <button
                        type="button"
                        className="feature-dropdown-toggle"
                        onClick={() => setIsFeatureDropdownOpen((open) => !open)}
                      >
                        {isFeatureDropdownOpen ? 'Hide Feature List' : 'Open Feature List'}
                      </button>
                      {isFeatureDropdownOpen && (
                        <div className="feature-dropdown-list">
                          {FEATURE_OPTIONS.map((feature) => (
                            <label key={feature.key} className="feature-option">
                              <input
                                type="checkbox"
                                checked={selectedFeatures.includes(feature.key)}
                                onChange={() => toggleFeatureSelection(feature.key)}
                              />
                              {feature.label}
                            </label>
                          ))}
                        </div>
                      )}
                    </div>
                    <small>Checked features appear below until you uncheck them.</small>
                  </div>

                  {selectedFeatures.length === 0 ? (
                    <p>Select at least one feature to customize.</p>
                  ) : (
                    <div className="form-grid-3x3">
                      {selectedFeatures.map((featureKey) => {
                        const option = FEATURE_OPTIONS.find((opt) => opt.key === featureKey)
                        if (!option) return null

                        return (
                          <div className="form-field" key={featureKey}>
                            <label>{option.label}</label>
                            {renderFeatureInput(featureKey, option)}
                          </div>
                        )
                      })}
                    </div>
                  )}

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
