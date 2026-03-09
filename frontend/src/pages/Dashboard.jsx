import { useState, useEffect } from 'react';
import { runSimulation, getStatus, generateDataset, uploadDataset } from '../api/api';
import ControlPanel from '../components/ControlPanel';
import MetricsCards from '../components/MetricsCards';
import TemperatureChart from '../components/TemperatureChart';
import EnergyChart from '../components/EnergyChart';
import CostChart from '../components/CostChart';
import OccupancyChart from '../components/OccupancyChart';

export default function Dashboard() {
  // State
  const [numDays, setNumDays] = useState(5);
  const [useModel, setUseModel] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [simData, setSimData] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [apiStatus, setApiStatus] = useState(null);
  const [provider, setProvider] = useState('default');
  const [tariffRates, setTariffRates] = useState({ peak: 6.5, mid: 4.5, offPeak: 3.5 });
  const [generatingDataset, setGeneratingDataset] = useState(false);
  const [uploadingDataset, setUploadingDataset] = useState(false);

  // Check API on mount
  useEffect(() => {
    getStatus()
      .then((s) => setApiStatus(s))
      .catch(() => setApiStatus({ status: 'offline' }));
  }, []);

  // Run simulation
  const handleRun = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await runSimulation(numDays, useModel, 'enhanced', tariffRates);
      setSimData(result.hourly_data);
      setMetrics(result.metrics);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Generate Synthetic Dataset
  const handleGenerateDataset = async () => {
    setGeneratingDataset(true);
    setError(null);
    try {
      const res = await generateDataset(100);
      alert(`✅ ${res.message}\n\nSwitching simulation to use this new dataset!`);
      // Optionally re-run simulation automatically
      if (simData) handleRun();
    } catch (err) {
      setError(err.message);
    } finally {
      setGeneratingDataset(false);
    }
  };

  // Upload Custom Dataset
  const handleUploadDataset = async (file) => {
    if (!file) return;
    setUploadingDataset(true);
    setError(null);
    try {
      const res = await uploadDataset(file);
      alert(`✅ ${res.message}\n\nSwitching simulation to use your uploaded dataset!`);
      if (simData) handleRun();
    } catch (err) {
      setError(err.message);
    } finally {
      setUploadingDataset(false);
    }
  };

  return (
    <div className="app">
      {/* ── Header ── */}
      <header className="header">
        <h1 className="header__title">🌱 Smart Energy AI Optimizer</h1>
        <p className="header__subtitle">
          Reduce your building's energy costs in real-time while maintaining perfect thermal comfort using AI.
        </p>
      </header>

      {/* ── Status Bar ── */}
      <div className="status-bar">
        <div className="status-bar__indicator">
          <span className={`status-dot ${
            apiStatus?.status === 'online' ? '' : 
            apiStatus?.status === 'offline' ? 'status-dot--error' : 'status-dot--loading'
          }`} />
          <span>
            API: {apiStatus?.status === 'online' ? 'Connected' : 'Connecting...'}
            {apiStatus?.loaded_models && (
              <> — Models loaded: {apiStatus.loaded_models.join(', ')}</>
            )}
          </span>
        </div>
        <span>
          {metrics ? `Last run: ${metrics.total_hours}h simulated (${metrics.model_used})` : 'Ready'}
        </span>
      </div>

      {/* ── Control Panel ── */}
      <ControlPanel
        numDays={numDays}
        setNumDays={setNumDays}
        useModel={useModel}
        setUseModel={setUseModel}
        onRun={handleRun}
        loading={loading}
        provider={provider}
        setProvider={setProvider}
        tariffRates={tariffRates}
        setTariffRates={setTariffRates}
        onGenerateDataset={handleGenerateDataset}
        generatingDataset={generatingDataset}
        onUploadDataset={handleUploadDataset}
        uploadingDataset={uploadingDataset}
      />

      {/* ── Error ── */}
      {error && (
        <div style={{
          padding: '16px 24px', margin: '16px 0',
          background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '12px', color: '#ef4444', fontSize: '0.9rem',
        }}>
          ⚠️ {error}
        </div>
      )}

      {/* ── Loading ── */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-spinner" />
          <div className="loading-text">
            Running simulation — {numDays} day{numDays > 1 ? 's' : ''} × 24 hours
            {useModel ? ' with PPO model' : ' (baseline)'}...
          </div>
        </div>
      )}

      {/* ── Metrics Cards ── */}
      {metrics && !loading && <MetricsCards metrics={metrics} />}

      {/* ── Charts Grid ── */}
      {simData && !loading && (
        <div className="charts-grid">
          <div className="card chart-card">
            <TemperatureChart data={simData} />
          </div>
          <div className="card chart-card">
            <EnergyChart data={simData} metrics={metrics} />
          </div>
          <div className="card chart-card">
            <CostChart data={simData} />
          </div>
          <div className="card chart-card">
            <OccupancyChart data={simData} />
          </div>
        </div>
      )}

      {/* ── Placeholder when no data ── */}
      {!simData && !loading && (
        <div className="welcome-state">
          <div className="welcome-state__icon">⚡</div>
          <h3>Ready to Optimize?</h3>
          <p>Run a simulation to see the AI in action. It learns your building's thermal properties, electricity rates, and occupancy patterns to minimize costs.</p>
          
          <div className="quick-actions">
            <button 
              className="btn-secondary" 
              onClick={() => { setNumDays(1); setUseModel(false); setTimeout(() => document.getElementById('run-simulation-btn').click(), 50); }}
            >
              📊 Run Baseline (1 Day)
            </button>
            <button 
              className="btn-primary" 
              onClick={() => { setNumDays(7); setUseModel(true); setTimeout(() => document.getElementById('run-simulation-btn').click(), 50); }}
            >
              🤖 Run AI Optimization (7 Days)
            </button>
          </div>
        </div>
      )}

      {/* ── How it Works ── */}
      <section className="tech-section">
        <h2 className="tech-section__title">💡 How the AI Works</h2>
        <div className="tech-grid">
          <div className="tech-card">
            <h4>🌡 Digital Twin Physics</h4>
            <p>Simulates real building temperatures using physics (Newton's cooling law, thermal mass, and solar gains) to accurately predict HVAC energy use.</p>
          </div>
          <div className="tech-card">
            <h4>💰 Smart Cost Savings</h4>
            <p>Learns to pre-cool or pre-heat the building during off-peak hours (₹2.0/kWh) to avoid expensive peak electricity rates (₹5.0/kWh).</p>
          </div>
          <div className="tech-card">
            <h4>🤖 Reinforcement Learning</h4>
            <p>Trains a PPO (Proximal Policy Optimization) agent over millions of steps to find the perfect balance between human comfort and energy cost.</p>
          </div>
          <div className="tech-card">
            <h4>👥 Occupancy Awareness</h4>
            <p>Adjusts temperatures automatically based on estimated occupancy, relaxing constraints when the building is empty to save more power.</p>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="footer">
        <p>Built with React, FastAPI, &amp; Stable Baselines3</p>
        <p style={{ marginTop: '4px' }}>
          Powered by Physics-Based Digital Twins &amp; AI Optimization
        </p>
      </footer>
    </div>
  );
}
