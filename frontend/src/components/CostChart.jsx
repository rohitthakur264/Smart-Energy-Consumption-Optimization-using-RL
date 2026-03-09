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

export default function CostChart({ data }) {
  if (!data || data.length === 0) return null;

  const x = data.map((d) => d.global_hour);
  const costs = data.map((d) => d.cost);
  const tariffs = data.map((d) => d.tariff);

  // Color code by tariff: Peak=red, Mid=orange, Off-peak=green
  const colors = tariffs.map((t) =>
    t >= 5.0 ? '#ef4444' :
    t >= 3.0 ? '#f59e0b' :
    '#10b981'
  );

  return (
    <Plot
      data={[
        {
          x, y: costs,
          type: 'bar',
          name: 'Hourly Cost',
          marker: { color: colors, opacity: 0.8 },
          hovertemplate: 'Cost: ₹%{y:.3f}<br>Tariff: %{customdata}/kWh<extra></extra>',
          customdata: tariffs.map((t) => `₹${t}`),
        },
      ]}
      layout={{
        ...plotLayout,
        title: { text: 'Tariff-Aware Cost Analysis', font: { size: 15, color: '#f1f5f9' } },
        yaxis: { ...plotLayout.yaxis, title: 'Cost (₹)' },
        xaxis: { ...plotLayout.xaxis, title: 'Hour' },
        showlegend: false,
        annotations: [{
          x: 0.98, y: 0.98, xref: 'paper', yref: 'paper',
          text: '🔴 Peak ₹5/kWh  🟠 Mid ₹3.5/kWh  🟢 Off-Peak ₹2/kWh',
          showarrow: false,
          font: { color: '#94a3b8', size: 10 },
          bgcolor: 'rgba(0,0,0,0.5)',
          borderpad: 6,
          xanchor: 'right',
        }],
      }}
      config={{ responsive: true, displayModeBar: false }}
      style={{ width: '100%', height: '100%' }}
    />
  );
}
