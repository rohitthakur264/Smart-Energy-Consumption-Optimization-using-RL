/**
 * Smart Energy RL Platform — API Service Layer
 * Communicates with FastAPI backend for real-time simulation data.
 */

// Use relative URL in production (served from same domain)
const API_BASE = import.meta.env.VITE_API_URL || '/api';

/**
 * Run a building energy simulation.
 * @param {number} numDays - days to simulate (1-30)
 * @param {boolean} useModel - use trained RL model vs baseline
 * @param {string} modelName - which model to use
 * @returns {Promise<{hourly_data: Array, metrics: Object}>}
 */
export async function runSimulation(numDays = 5, useModel = false, modelName = 'enhanced', rates = { peak: 5.0, mid: 3.5, offPeak: 2.0 }, location = 'default') {
  const params = new URLSearchParams({
    num_days: numDays,
    use_model: useModel,
    model_name: modelName,
    peak_rate: rates.peak,
    mid_rate: rates.mid,
    off_peak_rate: rates.offPeak,
    location: location
  });
  
  const res = await fetch(`${API_BASE}/simulate?${params}`);
  if (!res.ok) throw new Error(`Simulation failed: ${res.statusText}`);
  return res.json();
}

/**
 * Run model evaluation over multiple episodes.
 * @param {string} modelName
 * @param {number} numEpisodes
 * @returns {Promise<Object>}
 */
export async function runEvaluation(modelName = 'enhanced', numEpisodes = 5) {
  const params = new URLSearchParams({
    model_name: modelName,
    num_episodes: numEpisodes,
  });
  
  const res = await fetch(`${API_BASE}/evaluate?${params}`);
  if (!res.ok) throw new Error(`Evaluation failed: ${res.statusText}`);
  return res.json();
}

/**
 * Compare RL model vs baseline.
 * @param {number} numDays
 * @returns {Promise<Object>}
 */
export async function compareModels(numDays = 3) {
  const params = new URLSearchParams({ num_days: numDays });
  
  const res = await fetch(`${API_BASE}/compare?${params}`);
  if (!res.ok) throw new Error(`Comparison failed: ${res.statusText}`);
  return res.json();
}

/**
 * Get system status / health.
 * @returns {Promise<Object>}
 */
export async function getStatus() {
  const res = await fetch(`${API_BASE}/status`);
  if (!res.ok) throw new Error(`Status check failed: ${res.statusText}`);
  return res.json();
}

/**
 * Get Previous RL model accuracy metrics.
 * @returns {Promise<Object>}
 */
export async function getAccuracyMetrics() {
  const res = await fetch(`${API_BASE}/metrics`);
  if (!res.ok) return null; // Fallback gracefully if endpoint isn't ready
  return res.json();
}

/**
 * Get Training Convergence progress.
 * @returns {Promise<Object>}
 */
export async function getTrainingProgress() {
  const res = await fetch(`${API_BASE}/training-progress`);
  if (!res.ok) return null;
  return res.json();
}

/**
 * Get today's electricity tariff rates for a given provider.
 * @param {string} provider - 'msedcl' | 'adani' | 'tata' | 'default'
 * @returns {Promise<Object>}
 */
export async function getPriceToday(provider = 'msedcl') {
  const res = await fetch(`${API_BASE}/price-today?provider=${provider}`);
  if (!res.ok) throw new Error(`Price fetch failed: ${res.statusText}`);
  return res.json();
}

/**
 * Generate a synthetic dataset and use it for future simulations.
 * @param {number} numBuildings
 * @returns {Promise<Object>}
 */
export async function generateDataset(numBuildings = 50) {
  const res = await fetch(`${API_BASE}/generate-dataset?num_buildings=${numBuildings}`, { method: 'POST' });
  if (!res.ok) throw new Error(`Failed to generate dataset: ${res.statusText}`);
  return res.json();
}

/**
 * Upload a custom CSV dataset.
 * @param {File} file
 * @returns {Promise<Object>}
 */
export async function uploadDataset(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const res = await fetch(`${API_BASE}/upload-dataset`, {
    method: 'POST',
    body: formData,
  });
  
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.detail || `Upload failed: ${res.statusText}`);
  }
  return res.json();
}


// ═══════════════════════════════════════════════════════════════════
//  Energy Prediction API (Multi-Modal Model)
// ═══════════════════════════════════════════════════════════════════

/**
 * Predict energy consumption for a device.
 */
export async function predictEnergy({ temperature, starRating, deviceType, city, usageHours = 4, humidity = 65, month = 6 }) {
  const params = new URLSearchParams({
    temperature,
    star_rating: starRating,
    device_type: deviceType,
    city,
    usage_hours: usageHours,
    humidity,
    month,
  });
  const res = await fetch(`${API_BASE}/predict?${params}`);
  if (!res.ok) throw new Error(`Prediction failed: ${res.statusText}`);
  return res.json();
}

/**
 * Compare Mumbai vs Satara energy consumption.
 */
export async function compareCities() {
  const res = await fetch(`${API_BASE}/compare-cities`);
  if (!res.ok) throw new Error(`City comparison failed: ${res.statusText}`);
  return res.json();
}

/**
 * Get trained model accuracy metrics (R², MAE, RMSE).
 */
export async function getModelMetrics() {
  const res = await fetch(`${API_BASE}/model-metrics`);
  if (!res.ok) return null;
  return res.json();
}

/**
 * Get energy vs temperature impact for a device.
 */
export async function getTemperatureImpact(deviceType = 'Air Conditioner', city = 'Mumbai') {
  const params = new URLSearchParams({ device_type: deviceType, city });
  const res = await fetch(`${API_BASE}/temperature-impact?${params}`);
  if (!res.ok) return null;
  return res.json();
}

/**
 * Get energy vs star rating for a device.
 */
export async function getStarImpact(deviceType = 'Air Conditioner') {
  const params = new URLSearchParams({ device_type: deviceType });
  const res = await fetch(`${API_BASE}/star-impact?${params}`);
  if (!res.ok) return null;
  return res.json();
}

/**
 * Get list of available device types.
 */
export async function getAvailableDevices() {
  const res = await fetch(`${API_BASE}/available-devices`);
  if (!res.ok) return { devices: [] };
  return res.json();
}
