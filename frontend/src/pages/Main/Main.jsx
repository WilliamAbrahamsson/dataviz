import { useMemo, useState, useEffect } from 'react'
import Map from '../../components/Map/Map.jsx'
import TeamInfo from '../../components/TeamInfo/TeamInfo.jsx'
import Footer from '../../components/Footer/Footer.jsx'
import Table from '../../components/Table/Table.jsx'
import Topbar from '../../components/Topbar/Topbar.jsx'
import './Main.css'
import seasonTeams from '../../components/Map/teamsd.json'

function Main() {
  const seasons = useMemo(
    () =>
      Object.keys(seasonTeams).sort((a, b) => {
        const ay = parseInt(String(a).slice(0, 4), 10) || 0
        const by = parseInt(String(b).slice(0, 4), 10) || 0
        return by - ay
      }),
    []
  )
  const [selectedTeam, setSelectedTeam] = useState(null)
  const [selectedSeason, setSelectedSeason] = useState(seasons[0] || null)
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

  useEffect(() => {
    if (!selectedSeason) return
    const teams = seasonTeams[selectedSeason] || []
    if (teams.length) {
      const randomTeam = teams[Math.floor(Math.random() * teams.length)]
      setSelectedTeam(randomTeam)
    }
  }, [selectedSeason])

  return (
    <div className="app-root">
      <Topbar
        onPlayerSelect={handlePlayerSelect}
        selectedSeason={selectedSeason}
        onSeasonChange={setSelectedSeason}
      />

      <div className="split-page">
        <div className="left-side">
          <Map
            onTeamSelect={setSelectedTeam}
            season={selectedSeason}
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
              onSelectSeason={setSelectedSeason}
              onClosePlayer={() => setSelectedPlayer(null)}
            />
          </div>
        </div>
      </div>
      <Footer />
    </div>
  )
}

export default Main
