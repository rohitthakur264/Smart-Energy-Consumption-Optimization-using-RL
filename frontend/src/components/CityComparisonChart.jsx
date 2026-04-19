import React from 'react';
import Plot from 'react-plotly.js';

export default function CityComparisonChart({ data }) {
  if (!data || !data.device_comparison) return null;

  const devices = data.device_comparison.map((d) => d.device);
  const mumbaiVals = data.device_comparison.map((d) => d.mumbai_kwh);
  const sataraVals = data.device_comparison.map((d) => d.satara_kwh);

  return (
    <div className="card chart-card">
      <div className="card__header">
        <span className="card__icon">⚖️</span>
        <span className="card__title">Mumbai vs Satara — Energy by Device</span>
      </div>
      <Plot
        data={[
          {
            x: devices,
            y: mumbaiVals,
            type: 'bar',
            name: '🏙️ Mumbai',
            marker: {
              color: 'rgba(6, 214, 160, 0.85)',
              line: { color: 'rgba(6, 214, 160, 1)', width: 1 },
            },
          },
          {
            x: devices,
            y: sataraVals,
            type: 'bar',
            name: '🏔️ Satara',
            marker: {
              color: 'rgba(124, 58, 237, 0.85)',
              line: { color: 'rgba(124, 58, 237, 1)', width: 1 },
            },
          },
        ]}
        layout={{
          barmode: 'group',
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          font: { color: '#94a3b8', family: 'Inter' },
          margin: { t: 20, b: 90, l: 60, r: 20 },
          xaxis: {
            tickangle: -35,
            gridcolor: 'rgba(255,255,255,0.05)',
          },
          yaxis: {
            title: 'Avg Energy (kWh)',
            gridcolor: 'rgba(255,255,255,0.05)',
          },
          legend: { x: 0.7, y: 1.05, orientation: 'h', font: { size: 12 } },
          autosize: true,
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: '100%', height: '380px' }}
      />
    </div>
  );
}
