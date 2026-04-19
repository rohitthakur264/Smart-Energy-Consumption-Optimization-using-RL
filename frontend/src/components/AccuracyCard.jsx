import React from 'react';

export default function AccuracyCard({ accuracyMetrics }) {
  if (!accuracyMetrics) return null;

  return (
    <div className="card accuracy-card" style={{ gridColumn: '1 / -1', marginBottom: '16px' }}>
      <div className="card__header" style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', paddingBottom: '12px', marginBottom: '16px' }}>
        <span className="card__icon">🏆</span>
        <span className="card__title">Previous RL Model Accuracy (Training Stats)</span>
      </div>
      <div className="card__body" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
        
        <div className="metric-box" style={{ background: 'rgba(52, 211, 153, 0.1)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(52, 211, 153, 0.3)' }}>
          <div style={{ fontSize: '0.8rem', color: '#a7f3d0', textTransform: 'uppercase', letterSpacing: '1px' }}>Thermal Comfort Adherence</div>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#34d399', margin: '8px 0' }}>{accuracyMetrics.thermal_comfort_adherence}</div>
          <div style={{ fontSize: '0.8rem', color: '#6ee7b7' }}>Target: Category A (ISO 7730)</div>
        </div>

        <div className="metric-box" style={{ background: 'rgba(96, 165, 250, 0.1)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(96, 165, 250, 0.3)' }}>
          <div style={{ fontSize: '0.8rem', color: '#bfdbfe', textTransform: 'uppercase', letterSpacing: '1px' }}>Avg Energy Savings</div>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#60a5fa', margin: '8px 0' }}>{accuracyMetrics.avg_energy_savings_pct}%</div>
          <div style={{ fontSize: '0.8rem', color: '#93c5fd' }}>Compared to standard thermostat</div>
        </div>

        <div className="metric-box" style={{ background: 'rgba(192, 132, 252, 0.1)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(192, 132, 252, 0.3)' }}>
          <div style={{ fontSize: '0.8rem', color: '#e9d5ff', textTransform: 'uppercase', letterSpacing: '1px' }}>Convergence Rate</div>
          <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#c084fc', margin: '8px 0' }}>{accuracyMetrics.convergence_rate}</div>
          <div style={{ fontSize: '0.8rem', color: '#d8b4fe' }}>Over {accuracyMetrics.episodes_trained.toLocaleString()} episodes</div>
        </div>
        
      </div>
    </div>
  );
}
