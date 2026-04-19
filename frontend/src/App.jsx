import { useState } from 'react';
import './index.css';
import Dashboard from './pages/Dashboard';
import EnergyPredictor from './pages/EnergyPredictor';

function App() {
  const [page, setPage] = useState('predictor');

  return (
    <>
      {/* Navigation Bar */}
      <nav className="nav-bar">
        <div className="nav-bar__inner">
          <div className="nav-bar__brand">🌱 Smart Energy Platform</div>
          <div className="nav-bar__links">
            <button
              className={`nav-link ${page === 'predictor' ? 'nav-link--active' : ''}`}
              onClick={() => setPage('predictor')}
            >
              ⚡ Energy Predictor
            </button>
            <button
              className={`nav-link ${page === 'simulator' ? 'nav-link--active' : ''}`}
              onClick={() => setPage('simulator')}
            >
              🤖 RL Simulator
            </button>
          </div>
        </div>
      </nav>

      {/* Page Content */}
      {page === 'predictor' && <EnergyPredictor />}
      {page === 'simulator' && <Dashboard />}
    </>
  );
}

export default App;
