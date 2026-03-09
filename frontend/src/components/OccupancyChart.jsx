import Plot from 'react-plotly.js';

const plotLayout = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { color: '#94a3b8', family: 'Inter, sans-serif', size: 12 },
  margin: { t: 50, r: 60, b: 50, l: 60 },
  hovermode: 'x unified',
  legend: { orientation: 'h', y: -0.2, font: { size: 11 } },
  xaxis: { gridcolor: 'rgba(255,255,255,0.05)', zeroline: false },
  yaxis: { gridcolor: 'rgba(255,255,255,0.05)', zeroline: false },
};

export default function OccupancyChart({ data }) {
  if (!data || data.length === 0) return null;

  const x = data.map((d) => d.global_hour);
  const occupancy = data.map((d) => d.occupancy * 100);
  const comfort = data.map((d) => d.comfort);

  return (
    <Plot
      data={[
        {
          x, y: occupancy,
          type: 'bar',
          name: '👥 Occupancy (%)',
          marker: {
            color: 'rgba(245, 158, 11, 0.6)',
            line: { color: 'rgba(245, 158, 11, 0.8)', width: 0.5 },
          },
          hovertemplate: 'Occupancy: %{y:.1f}%<extra></extra>',
        },
        {
          x, y: comfort,
          type: 'scatter', mode: 'lines',
          name: '🌡 Comfort Violation',
          yaxis: 'y2',
          line: { color: '#ef4444', width: 2 },
          fill: 'tozeroy',
          fillcolor: 'rgba(239, 68, 68, 0.08)',
          hovertemplate: 'Violation: %{y:.3f}<extra></extra>',
        },
      ]}
      layout={{
        ...plotLayout,
        title: { text: 'Occupancy & Comfort', font: { size: 15, color: '#f1f5f9' } },
        yaxis: { ...plotLayout.yaxis, title: 'Occupancy (%)', range: [0, 105] },
        yaxis2: {
          title: 'Comfort Violation',
          overlaying: 'y', side: 'right',
          gridcolor: 'rgba(255,255,255,0.03)',
          rangemode: 'tozero',
        },
        xaxis: { ...plotLayout.xaxis, title: 'Hour' },
      }}
      config={{ responsive: true, displayModeBar: false }}
      style={{ width: '100%', height: '100%' }}
    />
  );
}
