import { useEffect, useState } from "react";
import "./Test.css";

function Test() {
  const [players, setPlayers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("http://127.0.0.1:5000/api/players/")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch players");
        return res.json();
      })
      .then((data) => {
        setPlayers(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="page">
      <div className="content">
        <h1 className="title">⚽ Player Dashboard</h1>
        <p className="subtitle">Data from your Flask backend</p>

        {loading && <p className="status">Loading players...</p>}
        {error && <p className="status error">Error: {error}</p>}

        {!loading && !error && (
          <div className="cards">
            {players.length === 0 ? (
              <p className="status">No players found.</p>
            ) : (
              players.map((p) => (
                <div key={p.id} className="card">
                  <h2 className="card-title">{p.name || "Unnamed Player"}</h2>
                  <p className="card-club">
                    {p.seasons?.[0]?.club || "Unknown Club"}
                  </p>
                  <div className="card-body">
                    <p>
                      <strong>Nationality:</strong> {p.nationality || "N/A"}
                    </p>
                    <p>
                      <strong>Born:</strong> {p.birth_year || "N/A"}
                    </p>
                    <p>
                      <strong>Valuations:</strong> {p.valuations?.length || 0}
                    </p>
                    <p>
                      <strong>Seasons:</strong> {p.seasons?.length || 0}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default Test;
