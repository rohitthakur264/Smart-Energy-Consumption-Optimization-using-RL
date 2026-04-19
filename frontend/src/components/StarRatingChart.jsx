import React from 'react';
import Plot from 'react-plotly.js';

export default function StarRatingChart({ data }) {
  if (!data || !data.star_ratings) return null;

  return (
    <div className="card chart-card">
      <div className="card__header">
        <span className="card__icon">⭐</span>
        <span className="card__title">Star Rating Impact — {data.device_type}</span>
      </div>
      <Plot
        data={[
          {
            x: data.star_ratings.map((s) => `${s} Star`),
            y: data.mumbai_kwh,
            type: 'bar',
            name: '🏙️ Mumbai',
            marker: {
              color: data.star_ratings.map((_, i) => {
                const colors = ['#ef4444', '#f97316', '#f59e0b', '#84cc16', '#06d6a0'];
                return colors[i] || '#06d6a0';
              }),
              line: { color: 'rgba(255,255,255,0.2)', width: 1 },
            },
          },
          {
            x: data.star_ratings.map((s) => `${s} Star`),
            y: data.satara_kwh,
            type: 'bar',
            name: '🏔️ Satara',
            marker: {
              color: data.star_ratings.map((_, i) => {
                const colors = [
                  'rgba(239,68,68,0.5)',
                  'rgba(249,115,22,0.5)',
                  'rgba(245,158,11,0.5)',
                  'rgba(132,204,22,0.5)',
                  'rgba(6,214,160,0.5)',
                ];
                return colors[i] || 'rgba(6,214,160,0.5)';
              }),
              line: { color: 'rgba(255,255,255,0.15)', width: 1 },
            },
          },
        ]}
        layout={{
          barmode: 'group',
          paper_bgcolor: 'transparent',
          plot_bgcolor: 'transparent',
          font: { color: '#94a3b8', family: 'Inter' },
          margin: { t: 20, b: 50, l: 60, r: 20 },
          xaxis: {
            gridcolor: 'rgba(255,255,255,0.05)',
          },
          yaxis: {
            title: 'Avg Energy (kWh)',
            gridcolor: 'rgba(255,255,255,0.05)',
          },
          legend: { x: 0.65, y: 1.05, orientation: 'h', font: { size: 12 } },
          autosize: true,
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: '100%', height: '380px' }}
      />
    </div>
  );
}
