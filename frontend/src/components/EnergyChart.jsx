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

export default function EnergyChart({ data, metrics }) {
  if (!data || data.length === 0) return null;

  const x = data.map((d) => d.global_hour);
  const energy = data.map((d) => d.energy);
  const cumEnergy = metrics?.cumulative_energy || [];
  const cumCost = metrics?.cumulative_cost || [];

  return (
    <Plot
      data={[
        {
          x, y: energy,
          type: 'bar',
          name: '⚡ Hourly Energy (kWh)',
          marker: {
            color: energy.map((e) => e > 5 ? '#ef4444' : e > 2 ? '#f59e0b' : '#06d6a0'),
            opacity: 0.7,
          },
          hovertemplate: 'Energy: %{y:.2f} kWh<extra></extra>',
        },
        {
          x, y: cumCost,
          type: 'scatter', mode: 'lines',
          name: '💰 Cumulative Cost (₹)',
          yaxis: 'y2',
          line: { color: '#10b981', width: 2.5 },
          hovertemplate: 'Cost: ₹%{y:.2f}<extra></extra>',
        },
      ]}
      layout={{
        ...plotLayout,
        title: { text: 'Energy Consumption & Cost', font: { size: 15, color: '#f1f5f9' } },
        yaxis: { ...plotLayout.yaxis, title: 'Energy (kWh)' },
        yaxis2: {
          title: 'Cumulative Cost (₹)',
          overlaying: 'y', side: 'right',
          gridcolor: 'rgba(255,255,255,0.03)',
          font: { color: '#10b981' },
        },
        xaxis: { ...plotLayout.xaxis, title: 'Hour' },
        barmode: 'relative',
      }}
      config={{ responsive: true, displayModeBar: false }}
      style={{ width: '100%', height: '100%' }}
    />
  );
}
