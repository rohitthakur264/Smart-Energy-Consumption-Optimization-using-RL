export default function ControlPanel({ 
  numDays, setNumDays, 
  useModel, setUseModel, 
  onRun, loading,
  provider, setProvider,
  tariffRates, setTariffRates,
  onGenerateDataset, generatingDataset,
  onUploadDataset, uploadingDataset
}) {
  
  const handleProviderChange = (e) => {
    const val = e.target.value;
    setProvider(val);
    
    if (val === 'default') {
      setTariffRates({ peak: 5.0, mid: 3.5, offPeak: 2.0 });
    } else if (val === 'adani') {
      setTariffRates({ peak: 10.0, mid: 7.5, offPeak: 5.5 });
    } else if (val === 'tata') {
      setTariffRates({ peak: 8.5, mid: 6.0, offPeak: 4.0 });
    }
  };
  return (
    <div className="card control-panel">
      <div className="card__header">
        <span className="card__icon">⚙️</span>
        <span className="card__title">Simulation Controls</span>
      </div>
      <div className="card__body">
        <div className="control-panel__inner">
          {/* Days Slider */}
          <div className="control-group">
            <label htmlFor="days-slider">Simulation Days</label>
            <input
              id="days-slider"
              type="range"
              min={1}
              max={30}
              step={1}
              value={numDays}
              onChange={(e) => setNumDays(parseInt(e.target.value))}
            />
            <span className="slider-value">{numDays} {numDays === 1 ? 'day' : 'days'}</span>
          </div>

          {/* Model Toggle */}
          <div className="control-group">
            <label>RL Model</label>
            <div className="toggle-wrapper">
              <input
                id="model-toggle"
                type="checkbox"
                className="toggle"
                checked={useModel}
                onChange={(e) => setUseModel(e.target.checked)}
              />
              <span className="toggle-label">
                {useModel ? '🤖 PPO Trained Model' : '📊 Baseline (No Control)'}
              </span>
            </div>
          </div>

          {/* Electricity Provider */}
          <div className="control-group">
            <label>Electricity Provider</label>
            <select 
              value={provider} 
              onChange={handleProviderChange}
              style={{
                width: '100%', padding: '10px', 
                background: 'rgba(255,255,255,0.05)', 
                border: '1px solid rgba(255,255,255,0.1)',
                color: '#f1f5f9', borderRadius: '8px', outline: 'none'
              }}
            >
              <option value="default" style={{color: '#000'}}>Standard Universal Rates</option>
              <option value="adani" style={{color: '#000'}}>Adani Electricity Mumbai</option>
              <option value="tata" style={{color: '#000'}}>Tata Power Mumbai</option>
              <option value="custom" style={{color: '#000'}}>Custom Inputs (Advanced)</option>
            </select>
          </div>

          {provider === 'custom' && (
            <div className="control-group" style={{ 
              background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px',
              display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px',
              marginTop: '-12px'
            }}>
              <div>
                <label style={{ fontSize: '10px' }}>Peak (₹)</label>
                <input type="number" step="0.5" value={tariffRates.peak} 
                  onChange={(e) => setTariffRates({...tariffRates, peak: parseFloat(e.target.value) || 0})}
                  style={{ width: '100%', padding: '4px', background: 'transparent', border: '1px solid #333', color: '#fff', outline: 'none', borderRadius: '4px' }} />
              </div>
              <div>
                <label style={{ fontSize: '10px' }}>Mid (₹)</label>
                <input type="number" step="0.5" value={tariffRates.mid} 
                  onChange={(e) => setTariffRates({...tariffRates, mid: parseFloat(e.target.value) || 0})}
                  style={{ width: '100%', padding: '4px', background: 'transparent', border: '1px solid #333', color: '#fff', outline: 'none', borderRadius: '4px' }} />
              </div>
              <div>
                <label style={{ fontSize: '10px' }}>Off-Peak (₹)</label>
                <input type="number" step="0.5" value={tariffRates.offPeak} 
                  onChange={(e) => setTariffRates({...tariffRates, offPeak: parseFloat(e.target.value) || 0})}
                  style={{ width: '100%', padding: '4px', background: 'transparent', border: '1px solid #333', color: '#fff', outline: 'none', borderRadius: '4px' }} />
              </div>
            </div>
          )}

          {provider === 'custom' && (
            <div className="control-group" style={{ 
              background: 'rgba(0,0,0,0.2)', padding: '12px', borderRadius: '8px',
              display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px',
              marginTop: '-12px'
            }}>
              <div>
                <label style={{ fontSize: '10px' }}>Peak (₹)</label>
                <input type="number" step="0.5" value={tariffRates.peak} 
                  onChange={(e) => setTariffRates({...tariffRates, peak: parseFloat(e.target.value) || 0})}
                  style={{ width: '100%', padding: '4px', background: 'transparent', border: '1px solid #333', color: '#fff', outline: 'none', borderRadius: '4px' }} />
              </div>
              <div>
                <label style={{ fontSize: '10px' }}>Mid (₹)</label>
                <input type="number" step="0.5" value={tariffRates.mid} 
                  onChange={(e) => setTariffRates({...tariffRates, mid: parseFloat(e.target.value) || 0})}
                  style={{ width: '100%', padding: '4px', background: 'transparent', border: '1px solid #333', color: '#fff', outline: 'none', borderRadius: '4px' }} />
              </div>
              <div>
                <label style={{ fontSize: '10px' }}>Off-Peak (₹)</label>
                <input type="number" step="0.5" value={tariffRates.offPeak} 
                  onChange={(e) => setTariffRates({...tariffRates, offPeak: parseFloat(e.target.value) || 0})}
                  style={{ width: '100%', padding: '4px', background: 'transparent', border: '1px solid #333', color: '#fff', outline: 'none', borderRadius: '4px' }} />
              </div>
            </div>
          )}

          {/* Dataset Generator & Upload */}
          <div className="control-group">
            <label>Building Dataset</label>
            <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
              <button
                className="btn-secondary"
                onClick={onGenerateDataset}
                disabled={generatingDataset || uploadingDataset}
                style={{ flex: 1, padding: '10px' }}
              >
                {generatingDataset ? '🔄 Gen...' : '🎲 Synthetic'}
              </button>
              
              <label 
                className="btn-secondary" 
                style={{ 
                  flex: 1, padding: '10px', textAlign: 'center', cursor: (generatingDataset || uploadingDataset) ? 'not-allowed' : 'pointer',
                  opacity: (generatingDataset || uploadingDataset) ? 0.5 : 1
                }}
              >
                {uploadingDataset ? '🔄 Up...' : '📂 Upload CSV'}
                <input 
                  type="file" 
                  accept=".csv" 
                  style={{ display: 'none' }} 
                  disabled={generatingDataset || uploadingDataset}
                  onChange={(e) => {
                    const file = e.target.files[0];
                    if (file) {
                      onUploadDataset(file);
                      e.target.value = null; // reset
                    }
                  }}
                />
              </label>
            </div>
          </div>

          {/* Run Button */}
          <div className="control-group" style={{ alignSelf: 'flex-end' }}>
            <button
              id="run-simulation-btn"
              className={`btn-run ${loading ? 'btn-run--loading' : ''}`}
              onClick={onRun}
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="loading-spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />
                  Running Simulation...
                </>
              ) : (
                <>🚀 Run Simulation</>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
