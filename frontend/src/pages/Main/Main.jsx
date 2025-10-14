import Map from '../../components/Map/Map.jsx'
import TeamInfo from '../../components/TeamInfo/TeamInfo.jsx'
import Table from '../../components/Table/Table.jsx'
import './Main.css'

function Main() {
  return (
    <div className="split-page">
      {/* Left: Map */}
      <div className="left-side">
        <Map />
      </div>

      {/* Right: Two stacked sections */}
      <div className="right-side">
        {/* Top section — Team info card */}
        <div className="right-top">
          <TeamInfo />
        </div>

        {/* Bottom section — Player table */}
        <div className="right-bottom">
          <Table />
        </div>
      </div>
    </div>
  )
}

export default Main
