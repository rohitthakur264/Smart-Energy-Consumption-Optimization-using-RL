import React from 'react';
import Plot from 'react-plotly.js';

export default function TrainingChart({ data }) {
  if (!data || !data.episodes) return null;

  return (
    <div className="card chart-card" style={{ gridColumn: '1 / -1', marginBottom: '16px' }}>
      <div className="card__header" style={{ marginBottom: '10px' }}>
        <span className="card__icon">📈</span>
        <span className="card__title">AI Learning Progress (Starting Error vs Final Accuracy)</span>
      </div>
      <div style={{ padding: '0 16px', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '16px' }}>
        Comparing how the agent progressed from Episode 0 (Starting / Baseline) to full convergence.
      </div>
      
      <div style={{ width: '100%', height: '320px', padding: '0 8px' }}>
        <Plot
          data={[
            {
              x: data.episodes,
              y: data.comfort_adherence,
              type: 'scatter',
              mode: 'lines',
              name: 'Thermal Comfort (%)',
              line: { color: '#34d399', width: 2 },
              yaxis: 'y'
            },
            {
              x: data.episodes,
              y: data.energy_savings,
              type: 'scatter',
              mode: 'lines',
              name: 'Energy Savings vs Baseline (%)',
              line: { color: '#60a5fa', width: 2 },
              yaxis: 'y2'
            }
          ]}
          layout={{
            autosize: true,
            margin: { l: 50, r: 50, b: 40, t: 20 },
            paper_bgcolor: 'transparent',
            plot_bgcolor: 'transparent',
            font: { color: '#94a3b8' },
            xaxis: { 
              title: { text: 'Training Episodes', font: { size: 12 } },
              showgrid: true,
              gridcolor: 'rgba(255,255,255,0.1)'
            },
            yaxis: { 
              title: { text: 'Comfort Score (%)', font: { size: 12, color: '#34d399' } },
              showgrid: true,
              gridcolor: 'rgba(255,255,255,0.05)',
              range: [0, 100],
              tickfont: { color: '#34d399' }
            },
            yaxis2: {
              title: { text: 'Energy Savings (%)', font: { size: 12, color: '#60a5fa' } },
              overlaying: 'y',
              side: 'right',
              range: [-20, 50],
              showgrid: false,
              tickfont: { color: '#60a5fa' }
            },
            legend: { 
              orientation: 'h', 
              y: 1.15,
              x: 0.5,
              xanchor: 'center'
            }
          }}
          useResizeHandler={true}
          style={{ width: '100%', height: '100%' }}
          config={{ responsive: true, displayModeBar: false }}
        />
      </div>
    </div>
  );
}
