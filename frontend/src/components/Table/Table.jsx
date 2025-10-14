import { useState } from 'react'
import Popup from '../Popup/Popup.jsx'
import './Table.css'

function Table() {
  const teamLogo = '/static/images/teams/chelsea.webp'
  const data = [
    { name: 'Cole Palmer', position: 'Forward', shirt: 20, value: 130.2 },
    { name: 'Nicolas Jackson', position: 'Forward', shirt: 15, value: 100.7 },
    { name: 'Moisés Caicedo', position: 'Midfielder', shirt: 25, value: 92.4 },
    { name: 'Reece James', position: 'Defender', shirt: 24, value: 76.7 },
    { name: 'Levi Colwill', position: 'Defender', shirt: 26, value: 51.3 },
    { name: 'Benoît Badiashile', position: 'Defender', shirt: 5, value: 42.5 },
    { name: 'Noni Madueke', position: 'Forward', shirt: 11, value: 35.1 },
    { name: 'Robert Sánchez', position: 'Goalkeeper', shirt: 1, value: 25.3 },
    { name: 'Mykhailo Mudryk', position: 'Forward', shirt: 10, value: 20.7 },
    { name: 'Christopher Nkunku', position: 'Forward', shirt: 18, value: 19.2 },
    { name: 'Reece James', position: 'Defender', shirt: 24, value: 76.7 },
    { name: 'Levi Colwill', position: 'Defender', shirt: 26, value: 51.3 },
    { name: 'Benoît Badiashile', position: 'Defender', shirt: 5, value: 42.5 },
    { name: 'Noni Madueke', position: 'Forward', shirt: 11, value: 35.1 },
    { name: 'Robert Sánchez', position: 'Goalkeeper', shirt: 1, value: 25.3 },
    { name: 'Mykhailo Mudryk', position: 'Forward', shirt: 10, value: 20.7 },
  ]

  const [selectedPlayer, setSelectedPlayer] = useState(null)

  return (
    <>
      <div className="table-wrapper">
        <table className="player-table">
          <thead>
            <tr>
              <th>Player</th>
              <th>Position</th>
              <th>Shirt No.</th>
              <th>Valuation</th>
            </tr>
          </thead>
          <tbody>
            {data.map((player, index) => (
              <tr
                key={index}
                className="clickable-row"
                onClick={() => setSelectedPlayer(player)}
              >
                <td className="player-cell">
                  <img
                    src={teamLogo}
                    alt="Team Logo"
                    className="player-logo"
                    draggable="false"
                  />
                  <span>{player.name}</span>
                </td>
                <td>{player.position}</td>
                <td>{player.shirt}</td>
                <td className="valuation">€{player.value.toFixed(1)}M</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Popup
        player={selectedPlayer}
        isOpen={!!selectedPlayer}
        onClose={() => setSelectedPlayer(null)}
      />
    </>
  )
}

export default Table
