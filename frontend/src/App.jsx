import { Routes, Route, Navigate } from 'react-router-dom'
import Main from './pages/Main/Main.jsx'


function App() {
  return (
    <div className="app-container">
      <main className="main-content">
        <Routes>
          {/* Redirect root path to /main */}
          <Route path="/" element={<Main />} />

        </Routes>
      </main>
    </div>
  )
}

export default App
