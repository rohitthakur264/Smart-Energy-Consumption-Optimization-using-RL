import Plot from 'react-plotly.js';

const plotLayout = {
  paper_bgcolor: 'rgba(0,0,0,0)',
  plot_bgcolor: 'rgba(0,0,0,0)',
  font: { color: '#94a3b8', family: 'Inter, sans-serif', size: 12 },
  margin: { t: 50, r: 30, b: 50, l: 60 },
  hovermode: 'x unified',
  legend: { orientation: 'h', y: -0.2, font: { size: 11 } },
  xaxis: { gridcolor: 'rgba(255,255,255,0.05)', zeroline: false },
  yaxis: { gridcolor: 'rgba(255,255,255,0.05)', zeroline: false },
};

export default function TemperatureChart({ data }) {
  if (!data || data.length === 0) return null;

  const x = data.map((d) => d.global_hour);
  const indoor = data.map((d) => d.temperature);
  const ambient = data.map((d) => d.ambient);

  return (
    <Plot
      data={[
        {
          x, y: indoor,
          type: 'scatter', mode: 'lines',
          name: '🏠 Indoor',
          line: { color: '#ef4444', width: 2.5 },
          hovertemplate: 'Indoor: %{y:.1f}°C<extra></extra>',
        },
        {
          x, y: ambient,
          type: 'scatter', mode: 'lines',
          name: '🌤 Ambient',
          line: { color: '#3b82f6', width: 2, dash: 'dash' },
          hovertemplate: 'Ambient: %{y:.1f}°C<extra></extra>',
        },
        {
          x, y: Array(x.length).fill(26),
          type: 'scatter', mode: 'lines',
          name: 'Comfort Max',
          line: { color: 'rgba(16,185,129,0.3)', width: 1, dash: 'dot' },
          showlegend: false,
        },
        {
          x, y: Array(x.length).fill(20),
          type: 'scatter', mode: 'lines',
          name: 'Comfort Min',
          line: { color: 'rgba(16,185,129,0.3)', width: 1, dash: 'dot' },
          fill: 'tonexty',
          fillcolor: 'rgba(16,185,129,0.06)',
          showlegend: false,
        },
      ]}
      layout={{
        ...plotLayout,
        title: { text: 'Temperature Control', font: { size: 15, color: '#f1f5f9' } },
        yaxis: { ...plotLayout.yaxis, title: 'Temperature (°C)' },
        xaxis: { ...plotLayout.xaxis, title: 'Hour' },
        shapes: [{
          type: 'rect', x0: x[0], x1: x[x.length - 1], y0: 20, y1: 26,
          fillcolor: 'rgba(16,185,129,0.04)', line: { width: 0 }, layer: 'below',
        }],
        annotations: [{
          x: x[Math.floor(x.length * 0.02)], y: 25.5,
          text: '✅ Comfort Zone', showarrow: false,
          font: { color: '#10b981', size: 10 },
        }],
      }}
      config={{ responsive: true, displayModeBar: false }}
      style={{ width: '100%', height: '100%' }}
    />
  );
}
