import { useMemo, useState } from 'react'
import ValuationChart from '../ValuationChart/ValuationChart.jsx'
import ChartDropdown from '../ChartDropdown.jsx'
import './ChartWrapper.css'

function parseSeasonEndYear(season) {
  if (!season) return null
  const str = String(season)

  // Handle formats like "2019/20", "2019-20", "2019/2020"
  const rangeMatch = str.match(/(\d{4})\s*[/\-]\s*(\d{2,4})/)
  if (rangeMatch) {
    const startYear = Number(rangeMatch[1]) || null
    const second = rangeMatch[2]

    if (second.length === 4) {
      const endYear = Number(second)
      return Number.isNaN(endYear) ? null : endYear
    }

    // For "2019/20" style codes, end year is startYear + 1
    return startYear != null && !Number.isNaN(startYear)
      ? startYear + 1
      : null
  }

  // Fallback: single 4‑digit year like "2020"
  const singleYear = str.match(/\d{4}/)
  if (!singleYear) return null
  const year = Number(singleYear[0])
  return Number.isNaN(year) ? null : year
}

function ChartWrapper({ valuations = [], season }) {
  const [pointWindow, setPointWindow] = useState('4')

  const valuationData = useMemo(() => {
    if (!valuations || valuations.length === 0) return []

    const endYear = parseSeasonEndYear(season)
    const seasonFiltered = endYear
      ? valuations.filter((v) => {
          if (!v.date) return false
          const d = new Date(v.date)
          const year = d.getFullYear()
          return !Number.isNaN(year) && year <= endYear
        })
      : valuations

    if (seasonFiltered.length === 0) return []

    const sorted = [...seasonFiltered].sort(
      (a, b) => new Date(a.date) - new Date(b.date),
    )

    let seasonWindow = sorted
    if (endYear) {
      const juneCutoff = new Date(endYear, 5, 30)
      const firstAfterJuneIdx = sorted.findIndex((v) => {
        const d = new Date(v.date)
        return d > juneCutoff && d.getFullYear() === endYear
      })

      if (firstAfterJuneIdx !== -1) {
        seasonWindow = sorted.slice(0, firstAfterJuneIdx + 1)
      }
    }

    const sliced =
      pointWindow === 'all'
        ? seasonWindow
        : seasonWindow.slice(-Number(pointWindow) || seasonWindow.length)

    return sliced.map((v) => ({
      date: v.date,
      value: v.amount ? v.amount / 1_000_000 : 0,
    }))
  }, [valuations, pointWindow, season])

  return (
    <div className="chart-section">
      <div className="chart-header">
        <h4>Valuation History</h4>
        <ChartDropdown value={pointWindow} onChange={setPointWindow} />
      </div>

      <div className="chart-card">
        <ValuationChart data={valuationData} height={250} />
      </div>
    </div>
  )
}

export default ChartWrapper
