import { useState } from 'react'
import Map from '../../components/Map/Map.jsx'
import TeamInfo from '../../components/TeamInfo/TeamInfo.jsx'
import Table from '../../components/Table/Table.jsx'
import Topbar from '../../components/Topbar/Topbar.jsx'
import './Main.css'

function Main() {
  const [selectedTeam, setSelectedTeam] = useState(null)
  const [selectedSeason, setSelectedSeason] = useState(null)
  const [selectedPlayer, setSelectedPlayer] = useState(null)

  const handlePlayerSelect = (player) => {
    const season = selectedSeason || player.seasons?.[0]?.year_code
    const seasonData =
      player.seasons?.find((s) => s.year_code === season) || player.seasons?.[0]

    if (seasonData?.club) {
      setSelectedTeam(seasonData.club)
      setSelectedPlayer(player)
    }
  }

  return (
    <div className="app-root">
      {/* 👇 pass current season */}
      <Topbar
        onPlayerSelect={handlePlayerSelect}
        selectedSeason={selectedSeason}
      />

      <div className="split-page">
        <div className="left-side">
          <Map
            onTeamSelect={setSelectedTeam}
            onSeasonChange={setSelectedSeason}
          />
        </div>

        <div className="right-side">
          <div className="right-top">
            <TeamInfo teamName={selectedTeam} season={selectedSeason} />
          </div>
          <div className="right-bottom">
            <Table
              teamName={selectedTeam}
              season={selectedSeason}
              externalPlayer={selectedPlayer}
              onClosePlayer={() => setSelectedPlayer(null)}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default Main
