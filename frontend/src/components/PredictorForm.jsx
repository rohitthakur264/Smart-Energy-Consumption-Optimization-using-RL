import React, { useState } from 'react';

export default function PredictorForm({ devices, onPredict, prediction, loading }) {
  const [temperature, setTemperature] = useState(32);
  const [starRating, setStarRating] = useState(3);
  const [deviceType, setDeviceType] = useState('Air Conditioner');
  const [city, setCity] = useState('Mumbai');
  const [usageHours, setUsageHours] = useState(4);

  const handleSubmit = (e) => {
    e.preventDefault();
    onPredict({ temperature, starRating, deviceType, city, usageHours });
  };

  return (
    <div className="predictor-panel card">
      <div className="card__header">
        <span className="card__icon">⚡</span>
        <span className="card__title">Energy Consumption Predictor</span>
      </div>
      <div className="card__body">
        <form onSubmit={handleSubmit} className="predictor-form">
          {/* Device Type */}
          <div className="form-group">
            <label htmlFor="pred-device">Device Type</label>
            <select id="pred-device" value={deviceType} onChange={(e) => setDeviceType(e.target.value)}>
              {(devices || []).map((d) => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>

          {/* City */}
          <div className="form-group">
            <label>City</label>
            <div className="city-toggle">
              <button
                type="button"
                className={`city-btn ${city === 'Mumbai' ? 'city-btn--active' : ''}`}
                onClick={() => setCity('Mumbai')}
              >
                🏙️ Mumbai
              </button>
              <button
                type="button"
                className={`city-btn ${city === 'Satara' ? 'city-btn--active' : ''}`}
                onClick={() => setCity('Satara')}
              >
                🏔️ Satara
              </button>
            </div>
          </div>

          {/* Star Rating */}
          <div className="form-group">
            <label>BEE Star Rating</label>
            <div className="star-selector">
              {[1, 2, 3, 4, 5].map((s) => (
                <button
                  key={s}
                  type="button"
                  className={`star-btn ${starRating === s ? 'star-btn--active' : ''}`}
                  onClick={() => setStarRating(s)}
                >
                  {'★'.repeat(s)}
                </button>
              ))}
            </div>
          </div>

          {/* Temperature */}
          <div className="form-group">
            <label htmlFor="pred-temp">Temperature: <strong>{temperature}°C</strong></label>
            <input
              id="pred-temp"
              type="range"
              min="10"
              max="48"
              step="1"
              value={temperature}
              onChange={(e) => setTemperature(Number(e.target.value))}
            />
            <div className="range-labels">
              <span>10°C</span>
              <span>48°C</span>
            </div>
          </div>

          {/* Usage Hours */}
          <div className="form-group">
            <label htmlFor="pred-usage">Usage: <strong>{usageHours} hrs/day</strong></label>
            <input
              id="pred-usage"
              type="range"
              min="0.5"
              max="24"
              step="0.5"
              value={usageHours}
              onChange={(e) => setUsageHours(Number(e.target.value))}
            />
            <div className="range-labels">
              <span>0.5 hr</span>
              <span>24 hrs</span>
            </div>
          </div>

          <button type="submit" className="btn-run" id="predict-btn" disabled={loading}>
            {loading ? '⏳ Predicting...' : '⚡ Predict Energy'}
          </button>
        </form>

        {/* Result */}
        {prediction && !loading && (
          <div className="prediction-result">
            <div className="prediction-result__value">
              {prediction.energy_consumption_kwh.toFixed(3)}
              <span className="prediction-result__unit">kWh</span>
            </div>
            <div className="prediction-result__details">
              <span>{prediction.device_type}</span>
              <span>•</span>
              <span>{'★'.repeat(prediction.star_rating)} Star</span>
              <span>•</span>
              <span>{prediction.city}</span>
              <span>•</span>
              <span>{prediction.temperature}°C</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
