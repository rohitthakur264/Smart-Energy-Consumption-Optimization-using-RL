import React from 'react';
import Plot from 'react-plotly.js';

export default function TempImpactChart({ data }) {
  if (!data || !data.temperatures) return null;

  return (
    <div className="card chart-card">
      <div className="card__header">
        <span className="card__icon">🌡️</span>
        <span className="card__title">Temperature Impact — {data.device_type} ({data.city})</span>
      </div>
      <Plot
        data={[
          {
            x: data.temperatures,
            y: data.star_1,
            type: 'scatter',
            mode: 'lines',
            name: '★ 1 Star',
            line: { color: '#ef4444', width: 2.5 },
          },
          {
            x: data.temperatures,
            y: data.star_3,
            type: 'scatter',
            mode: 'lines',
            name: '★★★ 3 Star',
            line: { color: '#f59e0b', width: 2.5 },
          },
          {
            x: data.temperatures,
            y: data.star_5,
            type: 'scatter',
            mode: 'lines',
            name: '★★★★★ 5 Star',
            line: { color: '#06d6a0', width: 2.5 },
          },
        ]}
        layout={{
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          font: { color: '#94a3b8', family: 'Inter' },
          margin: { t: 20, b: 50, l: 60, r: 20 },
          xaxis: {
            title: 'Temperature (°C)',
            gridcolor: 'rgba(255,255,255,0.05)',
          },
          yaxis: {
            title: 'Energy (kWh)',
            gridcolor: 'rgba(255,255,255,0.05)',
          },
          legend: { x: 0.02, y: 0.98, bgcolor: 'rgba(0,0,0,0.3)', font: { size: 11 } },
          autosize: true,
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: '100%', height: '380px' }}
      />
    </div>
  );
}
