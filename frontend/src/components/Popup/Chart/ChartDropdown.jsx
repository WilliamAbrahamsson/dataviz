import './ChartDropdown.css'

const OPTIONS = [
  { value: '4', label: 'Last 4 points' },
  { value: '10', label: 'Last 10 points' },
  { value: 'all', label: 'All points' },
]

function ChartDropdown({ value, onChange }) {
  return (
    <div className="chart-dropdown">
      <label className="chart-dropdown-label">
        Points
        <select
          className="chart-dropdown-select"
          value={value}
          onChange={(e) => onChange(e.target.value)}
        >
          {OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </label>
    </div>
  )
}

export default ChartDropdown
