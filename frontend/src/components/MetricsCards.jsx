export default function MetricsCards({ metrics }) {
  if (!metrics) return null;

  const cards = [];
  
  cards.push({
    icon: '⚡',
    value: `${metrics.total_energy.toFixed(1)}`,
    unit: 'kWh',
    label: 'AI Energy (New)',
    type: 'energy',
  });

  if (metrics.baseline_energy !== undefined) {
    cards.push({
      icon: '🏢',
      value: `${metrics.baseline_energy.toFixed(1)}`,
      unit: 'kWh',
      label: 'Baseline Energy (Old)',
      type: 'energy',
    });
  }

  if (metrics.baseline_cost !== undefined) {
    cards.push({
      icon: '🏛',
      value: `₹${metrics.baseline_cost.toFixed(2)}`,
      unit: '',
      label: 'Baseline Cost (Old)',
      type: 'reduction',
    });
  }

  cards.push({
    icon: '💰',
    value: `₹${metrics.total_cost.toFixed(2)}`,
    unit: '',
    label: metrics.baseline_cost !== undefined ? 'AI Cost (New)' : 'Operating Cost',
    type: 'cost',
  });

  if (metrics.savings !== undefined) {
    cards.push({
      icon: '🏆',
      value: `₹${metrics.savings.toFixed(2)}`,
      unit: '',
      label: 'Total Savings',
      type: 'comfort',
    });
  }

  cards.push(
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
      icon: '🏢',
      value: `${metrics.days_simulated}`,
      unit: 'days',
      label: 'Simulated',
      type: 'efficiency',
    }
  );

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
