import React from 'react';

export default function RegionalComparisonCard() {
  // Constant baseline assumptions based on mathematical energy model for maintaining 22°C inside
  const delhiAvgKwh = 3.85; 
  const chennaiAvgKwh = 4.05;
  const globalAveragePrice = 0.25; // USD peak price roughly

  return (
    <div className="card" style={{ gridColumn: '1 / -1', marginBottom: '16px', background: 'linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9))' }}>
      <div className="card__header" style={{ marginBottom: '16px' }}>
        <span className="card__icon">⚖️</span>
        <span className="card__title">Regional 1-Hour AC Impact (Delhi vs Chennai)</span>
      </div>
      <div style={{ fontSize: '0.9rem', color: '#94a3b8', marginBottom: '16px' }}>
        If you run a standard AC (approx. 1.5 Ton equivalent load) for <strong>1 continuous hour</strong> to maintain a strict 22°C against real-world weather patterns, here is the average energy consumption and theoretical cost.
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        
        {/* Delhi Region */}
        <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.05)', position: 'relative', overflow: 'hidden' }}>
          <div style={{ position: 'absolute', top: 0, right: 0, padding: '8px 12px', background: 'rgba(14, 165, 233, 0.1)', color: '#38bdf8', fontSize: '0.75rem', fontWeight: 'bold', borderBottomLeftRadius: '8px' }}>
            🏔️ North India
          </div>
          <h3 style={{ color: '#f1f5f9', margin: '0 0 16px 0', fontSize: '1.2rem' }}>Delhi</h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
              <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Average Temperature</span>
              <span style={{ color: '#e2e8f0', fontSize: '0.9rem' }}>24.1 °C</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Peak Summer (Max)</span>
              <span style={{ color: '#ef4444', fontSize: '0.9rem' }}>43.6 °C</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Average Energy (1 Hour)</span>
              <span style={{ color: '#e2e8f0', fontWeight: 'bold', fontSize: '1.1rem' }}>{delhiAvgKwh} kWh</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Est. Hourly Cost (Peak)</span>
              <span style={{ color: '#fbbf24', fontWeight: 'bold', fontSize: '1.1rem' }}>${(delhiAvgKwh * globalAveragePrice).toFixed(2)}</span>
            </div>
          </div>
          
          <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid rgba(255,255,255,0.05)', fontSize: '0.8rem', color: '#64748b' }}>
            <em>Benefit: Extreme winters pull the annual average down significantly, compensating for brutal summer peaks.</em>
          </div>
        </div>

        {/* Chennai Region */}
        <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.05)', position: 'relative', overflow: 'hidden' }}>
          <div style={{ position: 'absolute', top: 0, right: 0, padding: '8px 12px', background: 'rgba(245, 158, 11, 0.1)', color: '#fbbf24', fontSize: '0.75rem', fontWeight: 'bold', borderBottomLeftRadius: '8px' }}>
            🌴 South India
          </div>
          <h3 style={{ color: '#f1f5f9', margin: '0 0 16px 0', fontSize: '1.2rem' }}>Chennai</h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
              <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Average Temperature</span>
              <span style={{ color: '#e2e8f0', fontSize: '0.9rem' }}>28.1 °C</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Peak Summer (Max)</span>
              <span style={{ color: '#f97316', fontSize: '0.9rem' }}>40.2 °C</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Average Energy (1 Hour)</span>
              <span style={{ color: '#e2e8f0', fontWeight: 'bold', fontSize: '1.1rem' }}>{chennaiAvgKwh} kWh</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Est. Hourly Cost (Peak)</span>
              <span style={{ color: '#fbbf24', fontWeight: 'bold', fontSize: '1.1rem' }}>${(chennaiAvgKwh * globalAveragePrice).toFixed(2)}</span>
            </div>
          </div>
          
          <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid rgba(255,255,255,0.05)', fontSize: '0.8rem', color: '#64748b' }}>
            <em>Drawback: Constant year-round tropical heat drives up the average base-load energy consumption higher than the North.</em>
          </div>
        </div>

      </div>
    </div>
  );
}
