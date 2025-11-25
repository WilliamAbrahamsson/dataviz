import { useState, useEffect, useMemo, useCallback, Fragment } from 'react'
import { X, ArrowLeft, ArrowRight } from 'lucide-react'
import ChartWrapper from './Chart/ChartWrapper/ChartWrapper.jsx'
import mapPositions from '../Map/mapd.json'
import './Popup.css'

const API_BASE_URL = 'http://localhost:5000'

const STATIC_FIELDS = ['position','club']
const GK_FALLBACK_ORDER = [
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

const POSITION_TO_GROUP = {
  FW: 'attackers',
  'FW/MF': 'attackers',
  MF: 'midfielders',
  'MF/DF': 'midfielders',
  'MF/FW': 'midfielders',
  DF: 'defenders',
  'DF/MF': 'defenders',
}

const TEXT_FEATURES = new Set(STATIC_FIELDS)

const labelize = (key) =>
  key
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')

const buildFeatureOrder = (position = '', featureLists = {}) => {
  const normalized = position?.toUpperCase?.() || ''
  const group = POSITION_TO_GROUP[normalized]
  const positionFeatures = group ? featureLists[group] : null
  const ordered = Array.isArray(positionFeatures) && positionFeatures.length
    ? positionFeatures.map((item) => item.feature)
    : GK_FALLBACK_ORDER
  const merged = [...STATIC_FIELDS, ...ordered]
  return Array.from(new Set(merged))
}

const POSITION_OPTIONS = ['GK', 'DF', 'MF', 'FW']
const CLUB_OPTIONS = Object.keys(mapPositions).sort((a, b) => a.localeCompare(b))

function Popup({ player, season, isOpen, onClose }) {
  const [expanded, setExpanded] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [playerData, setPlayerData] = useState(null)
  const [seasonData, setSeasonData] = useState(null)
  const [estimatedValue, setEstimatedValue] = useState(null)
  const [defaultPrediction, setDefaultPrediction] = useState(null)
  const [customPrediction, setCustomPrediction] = useState(null)
  const [latestChartValue, setLatestChartValue] = useState(null)

  const [featureValues, setFeatureValues] = useState({})
  const [initialFeatureValues, setInitialFeatureValues] = useState({})
  const [selectedFeatures, setSelectedFeatures] = useState([])
  const [clubLogo, setClubLogo] = useState('/static/images/teams/default_logo.png')
  const [isFeatureDropdownOpen, setIsFeatureDropdownOpen] = useState(false)
  const [featureLists, setFeatureLists] = useState({
    attackers: [],
    defenders: [],
    midfielders: [],
  })

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

  const currentPosition = seasonData?.position || playerData?.position || player?.position || ''

  const featureOrder = useMemo(
    () => buildFeatureOrder(currentPosition, featureLists),
    [currentPosition, featureLists]
  )

  const featureOptions = useMemo(
    () =>
      featureOrder.map((key) => ({
        key,
        label: labelize(key),
        type: TEXT_FEATURES.has(key) ? 'text' : 'number',
      })),
    [featureOrder]
  )

  const buildFeatureValues = useCallback(
    (stats = {}) => {
      const values = {}
      featureOrder.forEach((key) => {
        values[key] = stats[key] ?? ''
      })
      return values
    },
    [featureOrder]
  )

  useEffect(() => {
    if (!isOpen || !player) return
    setLoading(true)
    setError(null)
    setEstimatedValue(null)
    setDefaultPrediction(null)
    setCustomPrediction(null)

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
        setCustomPrediction(null)
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
      setInitialFeatureValues({})
      setIsFeatureDropdownOpen(false)
      setDefaultPrediction(null)
      setCustomPrediction(null)
      setLatestChartValue(null)
    }
  }, [isOpen])

  useEffect(() => {
    if (!seasonData) return
    const baseValues = buildFeatureValues(seasonData)
    setFeatureValues(baseValues)
    setInitialFeatureValues(baseValues)
  }, [seasonData, buildFeatureValues])

  useEffect(() => {
    let cancelled = false
    const fetchGroup = async (group) => {
      const response = await fetch(`${API_BASE_URL}/api/feature-importance/${group}`)
      if (!response.ok) throw new Error(`Failed to fetch ${group} feature importance`)
      return response.json()
    }

    const loadFeatureLists = async () => {
      try {
        const [attackers, midfielders, defenders] = await Promise.all([
          fetchGroup('attackers'),
          fetchGroup('midfielders'),
          fetchGroup('defenders'),
        ])
        if (cancelled) return
        setFeatureLists({
          attackers: attackers || [],
          defenders: defenders || [],
          midfielders: midfielders || [],
        })
      } catch (err) {
        if (cancelled) return
        console.error('Failed to load feature importance from backend:', err)
      }
    }

    loadFeatureLists()
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (!featureOrder.length) return
    setSelectedFeatures((prev) => {
      const validPrev = prev.filter((key) => featureOrder.includes(key))
      if (validPrev.length) return validPrev
      const defaults = featureOrder.filter((key) => !STATIC_FIELDS.includes(key)).slice(0, 6)
      if (defaults.length) return defaults
      return featureOrder.slice(0, Math.min(6, featureOrder.length))
    })
  }, [featureOrder])

  useEffect(() => {
    if (!expanded) setIsFeatureDropdownOpen(false)
  }, [expanded])

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) onClose()
  }

  const valuations = playerData?.valuations || []

  const formatDisplayValue = (key, fallback) => {
    const value = initialFeatureValues?.[key]
    if (value === 0) return 0
    if (value === '' || value === undefined || value === null) return fallback ?? '—'
    return value
  }

  const hasCustomChanges = useMemo(() => {
    const numberKeys = new Set(featureOptions.filter((o) => o.type === 'number').map((o) => o.key))

    return featureOrder.some((key) => {
      const initial = initialFeatureValues?.[key]
      const current = featureValues?.[key]
      if (numberKeys.has(key)) {
        const a = initial === '' || initial === undefined || initial === null ? null : Number(initial)
        const b = current === '' || current === undefined || current === null ? null : Number(current)
        if (a === null && b === null) return false
        if (a === null || b === null) return true
        return a !== b
      }
      return (initial ?? '') !== (current ?? '')
    })
  }, [featureValues, initialFeatureValues, featureOrder, featureOptions])

  const handleFeatureChange = (featureKey, value) => {
    const option = featureOptions.find((opt) => opt.key === featureKey)
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

  const handleResetAll = () => {
    setFeatureValues(initialFeatureValues || {})
    setCustomPrediction(null)
    setEstimatedValue(defaultPrediction)
  }

  const handleResetFeature = (featureKey) => {
    setFeatureValues((prev) => ({
      ...prev,
      [featureKey]:
        initialFeatureValues && Object.prototype.hasOwnProperty.call(initialFeatureValues, featureKey)
          ? initialFeatureValues[featureKey]
          : '',
    }))
  }

  const isFieldChanged = (featureKey) => {
    const option = featureOptions.find((opt) => opt.key === featureKey)
    const isNumber = option?.type === 'number'
    const initial = initialFeatureValues?.[featureKey]
    const current = featureValues?.[featureKey]
    if (isNumber) {
      const a = initial === '' || initial === undefined || initial === null ? null : Number(initial)
      const b = current === '' || current === undefined || current === null ? null : Number(current)
      if (a === null && b === null) return false
      if (a === null || b === null) return true
      return a !== b
    }
    return (initial ?? '') !== (current ?? '')
  }

  const renderFeatureInput = (featureKey, option) => {
    if (!option) return null

    if (featureKey === 'club') {
      const clubValue = featureValues[featureKey] || ''
      const includeFallback = clubValue && !CLUB_OPTIONS.includes(clubValue)

      return (
        <div className="input-reset-row">
          <select
            value={clubValue}
            onChange={(e) => handleFeatureChange(featureKey, e.target.value)}
            className={isFieldChanged(featureKey) ? 'field-changed' : ''}
          >
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
          <button
            type="button"
            className="field-reset-btn"
            onClick={() => handleResetFeature(featureKey)}
            disabled={!isFieldChanged(featureKey)}
          >
            Reset
          </button>
        </div>
      )
    }

    if (featureKey === 'position') {
      const positionValue = featureValues[featureKey] || ''
      const includeFallback = positionValue && !POSITION_OPTIONS.includes(positionValue)

      return (
        <div className="input-reset-row">
          <select
            value={positionValue}
            onChange={(e) => handleFeatureChange(featureKey, e.target.value)}
            className={isFieldChanged(featureKey) ? 'field-changed' : ''}
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
          <button
            type="button"
            className="field-reset-btn"
            onClick={() => handleResetFeature(featureKey)}
            disabled={!isFieldChanged(featureKey)}
          >
            Reset
          </button>
        </div>
      )
    }

    return (
      <div className="input-reset-row">
        <input
          type={option.type === 'number' ? 'number' : 'text'}
          value={
            featureValues[featureKey] === '' || featureValues[featureKey] === undefined
              ? ''
              : featureValues[featureKey]
          }
          onChange={(e) => handleFeatureChange(featureKey, e.target.value)}
          className={isFieldChanged(featureKey) ? 'field-changed' : ''}
        />
        <button
          type="button"
          className="field-reset-btn"
          onClick={() => handleResetFeature(featureKey)}
          disabled={!isFieldChanged(featureKey)}
        >
          Reset
        </button>
      </div>
    )
  }

  const callModel = (values) =>
    fetch('http://127.0.0.1:5000/api/estimate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ featureValues: values }),
    }).then((response) => response.json())

  useEffect(() => {
    if (!isOpen) return
    if (!initialFeatureValues || Object.keys(initialFeatureValues).length === 0) return

    let cancelled = false
    setCustomPrediction(null)

    callModel(initialFeatureValues)
      .then((res) => {
        if (cancelled) return
        const raw = Number(res?.estimated_value)
        const val = Number.isFinite(raw) ? raw / 1_000_000 : null
        setDefaultPrediction(val)
        setEstimatedValue(val)
      })
      .catch((error) => {
        console.error('Error estimating default value:', error)
      })

    return () => {
      cancelled = true
    }
  }, [initialFeatureValues, isOpen])

  const handleEstimate = () => {
    if (!player) return
    if (!hasCustomChanges) return

    callModel(featureValues)
      .then((customRes) => {
        const custRaw = Number(customRes?.estimated_value)
        const custVal = Number.isFinite(custRaw) ? custRaw / 1_000_000 : null
        setCustomPrediction(custVal)
        setEstimatedValue(custVal)
      })
      .catch((error) => {
        console.error('Error estimating value:', error)
      })
  }

  if (!isOpen || !player) return null

  return (
    <div
      className={`player-drawer-overlay ${expanded ? 'expanded' : ''}`}
      onClick={handleOverlayClick}
    >
      <div className={`player-drawer ${expanded ? 'expanded-layout' : ''}`}>
        <div className="drawer-header">
          <button className="header-icon left" onClick={() => (expanded ? setExpanded(false) : onClose())}>
            {expanded ? <ArrowLeft size={20} /> : <X size={20} />}
            <span className="header-label">{expanded ? 'Back' : 'Close'}</span>
          </button>

          <h2 className="player-name">{playerData?.name || player.name}</h2>

          <button className="header-icon right" onClick={() => setExpanded((e) => !e)}>
            {expanded ? <X size={20} /> : <ArrowRight size={20} />}
            <span className="header-label">{expanded ? 'Close' : 'Expand'}</span>
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
                  defaultPrediction={defaultPrediction}
                  customPrediction={customPrediction}
                  onDataChange={(vals) => {
                    if (!vals || !vals.length) {
                      setLatestChartValue(null)
                      return
                    }
                    setLatestChartValue(vals[vals.length - 1].value)
                  }}
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
                          {featureOptions.map((feature, idx) => {
                            const showDivider = idx === STATIC_FIELDS.length && featureOptions.length > STATIC_FIELDS.length
                            return (
                              <Fragment key={feature.key}>
                                {showDivider && <div className="feature-separator" aria-hidden="true" />}
                                <label className="feature-option">
                                  <input
                                    type="checkbox"
                                    checked={selectedFeatures.includes(feature.key)}
                                    onChange={() => toggleFeatureSelection(feature.key)}
                                  />
                                  {feature.label}
                                </label>
                              </Fragment>
                            )
                          })}
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
                        const option = featureOptions.find((opt) => opt.key === featureKey)
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

                  <div className="reset-all-row">
                    <button
                      type="button"
                      className="reset-all-btn"
                      onClick={handleResetAll}
                      disabled={!hasCustomChanges}
                    >
                      Reset All
                    </button>
                  </div>

                  <button
                    className={`estimate-btn ${hasCustomChanges ? 'estimate-btn-green' : ''}`}
                    onClick={handleEstimate}
                    disabled={!hasCustomChanges}
                  >
                    Estimate New Value
                  </button>
                  {!hasCustomChanges && (
                    <p className="estimate-helper">Modify values to make custom prediction</p>
                  )}

                  {(latestChartValue != null || defaultPrediction != null || customPrediction != null) && (
                    <div className="estimate-results">
                      {latestChartValue != null && (
                        <div className="estimate-card estimate-card-market">
                          <div className="estimate-title">
                            <img
                              src="/static/images/Transfermarkt_logo.png"
                              alt="Transfermarkt"
                              className="estimate-icon"
                            />
                            <span className="estimate-label">Valuation</span>
                          </div>
                          <span className="estimate-value">€{latestChartValue.toFixed(1)}M</span>
                        </div>
                      )}
                      {defaultPrediction != null && (
                        <div className="estimate-card estimate-card-default">
                          <span className="estimate-label">Default prediction</span>
                          <span className="estimate-value">€{defaultPrediction.toFixed(1)}M</span>
                        </div>
                      )}
                      {customPrediction != null && (
                        <div className="estimate-card estimate-card-custom">
                          <span className="estimate-label">Latest custom prediction</span>
                          <span className="estimate-value">€{customPrediction.toFixed(1)}M</span>
                        </div>
                      )}
                    </div>
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
