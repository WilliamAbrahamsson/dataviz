import { Routes, Route, Navigate } from 'react-router-dom'
import Test from './pages/Test/Test.jsx'
import Main from './pages/Main/Main.jsx'

import Topbar from './components/Topbar/Topbar.jsx'

function App() {
  return (
    <div className="app-container">
      <Topbar />
      <main className="main-content">
        <Routes>
          {/* Redirect root path to /main */}
          <Route path="/" element={<Main />} />

          {/* Main page route */}
          <Route path="/test" element={<Test />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
