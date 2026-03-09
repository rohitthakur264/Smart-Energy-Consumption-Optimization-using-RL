export default function MetricsCards({ metrics }) {
  if (!metrics) return null;

  const cards = [
    {
      icon: '⚡',
      value: `${metrics.total_energy.toFixed(1)}`,
      unit: 'kWh',
      label: 'Total Energy',
      type: 'energy',
    },
    {
      icon: '💰',
      value: `₹${metrics.total_cost.toFixed(2)}`,
      unit: '',
      label: 'Operating Cost',
      type: 'cost',
    },
    {
      icon: '📉',
      value: `${metrics.energy_reduction_pct.toFixed(1)}%`,
      unit: '',
      label: 'Energy Reduction',
      type: 'reduction',
    },
    {
      icon: '🌡',
      value: `${metrics.avg_temperature.toFixed(1)}°`,
      unit: 'C',
      label: 'Avg Temperature',
      type: 'temp',
    },
    {
      icon: '😊',
      value: `${metrics.comfort_score.toFixed(0)}`,
      unit: '%',
      label: 'Comfort Score',
      type: 'comfort',
    },
    {
      icon: '🏢',
      value: `${metrics.days_simulated}`,
      unit: 'days',
      label: 'Simulated',
      type: 'efficiency',
    },
  ];

  return (
    <div className="metrics-grid">
      {cards.map((card, i) => (
        <div key={i} className={`metric-card metric-card--${card.type}`}>
          <div className="metric-card__icon">{card.icon}</div>
          <div className="metric-card__value">
            {card.value}
            {card.unit && <span style={{ fontSize: '0.6em', opacity: 0.7 }}> {card.unit}</span>}
          </div>
          <div className="metric-card__label">{card.label}</div>
        </div>
      ))}
    </div>
  );
}
