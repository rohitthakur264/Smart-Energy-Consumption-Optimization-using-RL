import React from 'react';

export default function ModelMetricsCard({ metrics }) {
  if (!metrics) return null;

  const cards = [
    {
      label: 'R² Score',
      value: (metrics.ensemble_r2 * 100).toFixed(2) + '%',
      sub: 'Ensemble Accuracy',
      color: '#06d6a0',
      icon: '🎯',
    },
    {
      label: 'MAE',
      value: metrics.ensemble_mae?.toFixed(4) + ' kWh',
      sub: 'Mean Absolute Error',
      color: '#118ab2',
      icon: '📏',
    },
    {
      label: 'RMSE',
      value: metrics.ensemble_rmse?.toFixed(4) + ' kWh',
      sub: 'Root Mean Sq Error',
      color: '#7c3aed',
      icon: '📐',
    },
    {
      label: 'Samples',
      value: metrics.total_samples?.toLocaleString(),
      sub: 'Training Dataset',
      color: '#f59e0b',
      icon: '📊',
    },
  ];

  return (
    <div className="model-metrics-section">
      <div className="model-metrics-hero">
        <div className="hero-badge">Multi-Modal ML Model</div>
        <h2 className="hero-accuracy">
          {(metrics.ensemble_r2 * 100).toFixed(2)}
          <span className="hero-percent">%</span>
        </h2>
        <p className="hero-label">Prediction Accuracy (R² Score)</p>
        <div className="hero-models">
          <span className="hero-model-tag">
            🌲 Random Forest R² = {(metrics.rf_r2 * 100).toFixed(1)}%
          </span>
          <span className="hero-model-tag">
            🚀 Gradient Boost R² = {(metrics.gbr_r2 * 100).toFixed(1)}%
          </span>
        </div>
      </div>

      <div className="metrics-mini-grid">
        {cards.map((c) => (
          <div key={c.label} className="mini-metric-card" style={{ '--card-accent': c.color }}>
            <span className="mini-metric-icon">{c.icon}</span>
            <div className="mini-metric-value">{c.value}</div>
            <div className="mini-metric-label">{c.label}</div>
            <div className="mini-metric-sub">{c.sub}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
