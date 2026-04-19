import { useState, useEffect } from 'react';
import {
  predictEnergy,
  compareCities,
  getModelMetrics,
  getTemperatureImpact,
  getStarImpact,
  getAvailableDevices,
} from '../api/api';
import ModelMetricsCard from '../components/ModelMetricsCard';
import PredictorForm from '../components/PredictorForm';
import CityComparisonChart from '../components/CityComparisonChart';
import TempImpactChart from '../components/TempImpactChart';
import StarRatingChart from '../components/StarRatingChart';

export default function EnergyPredictor() {
  const [metrics, setMetrics] = useState(null);
  const [cityData, setCityData] = useState(null);
  const [tempData, setTempData] = useState(null);
  const [starData, setStarData] = useState(null);
  const [devices, setDevices] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [predLoading, setPredLoading] = useState(false);
  const [selectedDevice, setSelectedDevice] = useState('Air Conditioner');
  const [selectedCity, setSelectedCity] = useState('Mumbai');

  // Load initial data
  useEffect(() => {
    getModelMetrics().then(setMetrics);
    compareCities().then(setCityData);
    getAvailableDevices().then((r) => r && setDevices(r.devices || []));
    getTemperatureImpact('Air Conditioner', 'Mumbai').then(setTempData);
    getStarImpact('Air Conditioner').then(setStarData);
  }, []);

  // Update charts when device or city changes
  const handleChartDeviceChange = (device) => {
    setSelectedDevice(device);
    getTemperatureImpact(device, selectedCity).then(setTempData);
    getStarImpact(device).then(setStarData);
  };

  const handleChartCityChange = (city) => {
    setSelectedCity(city);
    getTemperatureImpact(selectedDevice, city).then(setTempData);
  };

  // Predict
  const handlePredict = async (params) => {
    setPredLoading(true);
    try {
      const result = await predictEnergy(params);
      setPrediction(result);
    } catch (err) {
      console.error(err);
    } finally {
      setPredLoading(false);
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <h1 className="header__title">⚡ Smart Energy Predictor</h1>
        <p className="header__subtitle">
          Multi-modal ML model predicting energy consumption based on temperature &amp; BEE star rating — Mumbai vs Satara
        </p>
      </header>

      {/* Model Accuracy */}
      <ModelMetricsCard metrics={metrics} />

      {/* Predictor + City Summary */}
      <div className="predictor-layout">
        <PredictorForm
          devices={devices}
          onPredict={handlePredict}
          prediction={prediction}
          loading={predLoading}
        />

        {/* City Summary Cards */}
        {cityData && (
          <div className="city-summary-cards">
            <div className="city-summary-card city-summary-card--mumbai">
              <div className="city-summary-card__badge">🏙️ Coastal</div>
              <h3>Mumbai</h3>
              <div className="city-summary-stat">
                <span className="city-summary-stat__value">{cityData.mumbai_summary.avg_energy_kwh}</span>
                <span className="city-summary-stat__unit">kWh avg</span>
              </div>
              <div className="city-summary-details">
                <div><span>Avg Temp:</span> <strong>{cityData.mumbai_summary.avg_temperature}°C</strong></div>
                <div><span>Humidity:</span> <strong>{cityData.mumbai_summary.avg_humidity}%</strong></div>
                <div><span>Samples:</span> <strong>{cityData.mumbai_summary.total_samples.toLocaleString()}</strong></div>
              </div>
            </div>

            <div className="city-summary-card city-summary-card--satara">
              <div className="city-summary-card__badge">🏔️ Inland</div>
              <h3>Satara</h3>
              <div className="city-summary-stat">
                <span className="city-summary-stat__value">{cityData.satara_summary.avg_energy_kwh}</span>
                <span className="city-summary-stat__unit">kWh avg</span>
              </div>
              <div className="city-summary-details">
                <div><span>Avg Temp:</span> <strong>{cityData.satara_summary.avg_temperature}°C</strong></div>
                <div><span>Humidity:</span> <strong>{cityData.satara_summary.avg_humidity}%</strong></div>
                <div><span>Samples:</span> <strong>{cityData.satara_summary.total_samples.toLocaleString()}</strong></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* City Comparison Bar Chart */}
      <CityComparisonChart data={cityData} />

      {/* Chart Controls */}
      <div className="chart-controls card">
        <div className="card__header">
          <span className="card__icon">🔧</span>
          <span className="card__title">Chart Controls</span>
        </div>
        <div className="card__body" style={{ display: 'flex', gap: '24px', flexWrap: 'wrap', alignItems: 'center' }}>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label htmlFor="chart-device">Device</label>
            <select id="chart-device" value={selectedDevice} onChange={(e) => handleChartDeviceChange(e.target.value)}>
              {devices.map((d) => <option key={d} value={d}>{d}</option>)}
            </select>
          </div>
          <div className="form-group" style={{ marginBottom: 0 }}>
            <label>City (for temp chart)</label>
            <div className="city-toggle">
              <button
                type="button"
                className={`city-btn ${selectedCity === 'Mumbai' ? 'city-btn--active' : ''}`}
                onClick={() => handleChartCityChange('Mumbai')}
              >
                Mumbai
              </button>
              <button
                type="button"
                className={`city-btn ${selectedCity === 'Satara' ? 'city-btn--active' : ''}`}
                onClick={() => handleChartCityChange('Satara')}
              >
                Satara
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="charts-grid">
        <TempImpactChart data={tempData} />
        <StarRatingChart data={starData} />
      </div>

      {/* Device Breakdown Table */}
      {cityData && cityData.device_comparison && (
        <div className="card" style={{ marginTop: '20px' }}>
          <div className="card__header">
            <span className="card__icon">📋</span>
            <span className="card__title">Detailed Device Comparison</span>
          </div>
          <div className="card__body" style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Device</th>
                  <th>Mumbai (kWh)</th>
                  <th>Satara (kWh)</th>
                  <th>Difference</th>
                  <th>Higher In</th>
                </tr>
              </thead>
              <tbody>
                {cityData.device_comparison.map((d) => (
                  <tr key={d.device}>
                    <td>{d.device}</td>
                    <td className="mono">{d.mumbai_kwh.toFixed(3)}</td>
                    <td className="mono">{d.satara_kwh.toFixed(3)}</td>
                    <td className="mono" style={{ color: d.difference_kwh > 0 ? '#ef4444' : '#06d6a0' }}>
                      {d.difference_kwh > 0 ? '+' : ''}{d.difference_kwh.toFixed(3)} ({d.difference_pct > 0 ? '+' : ''}{d.difference_pct}%)
                    </td>
                    <td>
                      <span className={`table-badge ${d.difference_kwh > 0 ? 'table-badge--mumbai' : 'table-badge--satara'}`}>
                        {d.difference_kwh > 0 ? '🏙️ Mumbai' : '🏔️ Satara'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="footer">
        <p>Multi-Modal Energy Prediction — Random Forest + Gradient Boosting Ensemble</p>
        <p style={{ marginTop: '4px' }}>Dataset: Mumbai &amp; Satara Appliance Energy Consumption (BEE Star Ratings)</p>
      </footer>
    </div>
  );
}
