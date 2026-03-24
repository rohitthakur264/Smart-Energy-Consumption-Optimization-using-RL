/**
 * Today's electricity price card
 * Shows real MSEDCL/Adani/Tata ToD tariff data.
 */
export default function PriceTodayCard({ priceData, loading }) {
  if (loading) {
    return (
      <div className="card price-today-card">
        <div className="card__header">
          <span className="card__icon">⚡</span>
          <span className="card__title">Today's Electricity Prices</span>
        </div>
        <div className="card__body" style={{ textAlign: 'center', padding: '24px', color: '#94a3b8' }}>
          Loading live rates...
        </div>
      </div>
    );
  }

  if (!priceData) return null;

  const { zones, current_rate, current_zone, provider_full, tariff_year, unit, note, all_providers } = priceData;

  const zoneColors = { peak: '#ef4444', mid: '#eab308', off_peak: '#22c55e' };
  const zoneLabels = { peak: '🔴 Peak', mid: '🟡 Mid', off_peak: '🟢 Off-Peak' };

  return (
    <div className="card price-today-card">
      <div className="card__header">
        <span className="card__icon">⚡</span>
        <span className="card__title">Today's Electricity Prices</span>
        <span style={{
          marginLeft: 'auto', fontSize: '0.7rem', color: '#94a3b8',
          background: 'rgba(255,255,255,0.06)', padding: '2px 8px', borderRadius: '4px'
        }}>
          {tariff_year} Tariff Order
        </span>
      </div>

      <div className="card__body">
        {/* Current Rate Banner */}
        <div style={{
          background: `linear-gradient(135deg, rgba(99,102,241,0.15), rgba(139,92,246,0.1))`,
          border: '1px solid rgba(99,102,241,0.25)',
          borderRadius: '12px', padding: '16px 20px',
          marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '16px'
        }}>
          <div>
            <div style={{ fontSize: '0.72rem', color: '#94a3b8', marginBottom: '2px' }}>Current Rate (this hour)</div>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: zoneColors[current_zone] || '#f1f5f9' }}>
              ₹{current_rate.toFixed(2)}
              <span style={{ fontSize: '0.85rem', fontWeight: 400, color: '#94a3b8', marginLeft: 4 }}>/ kWh</span>
            </div>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '2px' }}>{provider_full}</div>
          </div>
          <div style={{ marginLeft: 'auto', textAlign: 'right' }}>
            <div style={{
              fontSize: '0.78rem', fontWeight: 700,
              color: zoneColors[current_zone] || '#f1f5f9',
              background: `${zoneColors[current_zone] || '#f1f5f9'}20`,
              padding: '4px 10px', borderRadius: '20px',
              border: `1px solid ${zoneColors[current_zone] || '#f1f5f9'}40`
            }}>
              {zoneLabels[current_zone] || current_zone}
            </div>
          </div>
        </div>

        {/* Zone Breakdown */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px', marginBottom: '16px' }}>
          {Object.entries(zones).map(([key, z]) => (
            <div key={key} style={{
              background: `${z.color}10`,
              border: `1px solid ${z.color}30`,
              borderRadius: '8px', padding: '10px 12px',
              borderTop: `3px solid ${z.color}`,
            }}>
              <div style={{ fontSize: '0.68rem', color: '#94a3b8', marginBottom: '4px' }}>{z.hours}</div>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: z.color }}>₹{z.rate.toFixed(2)}</div>
              <div style={{ fontSize: '0.65rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                {key === 'off_peak' ? 'Off-Peak' : key.charAt(0).toUpperCase() + key.slice(1)}
              </div>
            </div>
          ))}
        </div>

        {/* Provider Comparison Table */}
        {all_providers && (
          <div>
            <div style={{ fontSize: '0.72rem', color: '#64748b', marginBottom: '8px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Provider Comparison (₹/kWh)
            </div>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.78rem' }}>
              <thead>
                <tr style={{ color: '#64748b' }}>
                  <th style={{ textAlign: 'left', padding: '4px 6px', fontWeight: 600 }}>Provider</th>
                  <th style={{ textAlign: 'right', padding: '4px 6px', color: '#ef4444', fontWeight: 600 }}>Peak</th>
                  <th style={{ textAlign: 'right', padding: '4px 6px', color: '#eab308', fontWeight: 600 }}>Mid</th>
                  <th style={{ textAlign: 'right', padding: '4px 6px', color: '#22c55e', fontWeight: 600 }}>Off-Peak</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(all_providers)
                  .filter(([k]) => k !== 'default')
                  .map(([k, v]) => (
                  <tr key={k} style={{
                    borderTop: '1px solid rgba(255,255,255,0.05)',
                    background: k === priceData.provider ? 'rgba(99,102,241,0.08)' : 'transparent'
                  }}>
                    <td style={{ padding: '6px 6px', color: '#f1f5f9' }}>
                      {k === priceData.provider ? '▶ ' : ''}{v.full_name?.split('–')[0]?.trim() || k.toUpperCase()}
                    </td>
                    <td style={{ textAlign: 'right', padding: '6px 6px', color: '#fca5a5' }}>₹{v.peak.toFixed(2)}</td>
                    <td style={{ textAlign: 'right', padding: '6px 6px', color: '#fde68a' }}>₹{v.mid.toFixed(2)}</td>
                    <td style={{ textAlign: 'right', padding: '6px 6px', color: '#86efac' }}>₹{v.off_peak.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div style={{ fontSize: '0.65rem', color: '#475569', marginTop: '8px' }}>
              📋 {note || 'Based on 2024-25 Indian tariff orders'}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
