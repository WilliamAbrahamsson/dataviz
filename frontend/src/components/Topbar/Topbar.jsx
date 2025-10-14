import './Topbar.css'

function Topbar() {
  return (
    <header className="topbar">
      <div className="topbar-content">
        {/* Left: Logo / Title */}
        <div className="topbar-left">
          <h1 className="topbar-title">⚽ DataViz Dashboard</h1>
        </div>

        {/* Center: Navigation */}
        <nav className="topbar-center">
          <a href="/">Home</a>
          <a href="/test">Test Fetch</a>
          {/* <a href="/about">About</a> */}
        </nav>

        {/* Right: Search bar */}
        <div className="topbar-right">
          <input
            type="text"
            className="search-input"
            placeholder="Search..."
          />
        </div>
      </div>
    </header>
  )
}

export default Topbar
