/**
 * Smart Energy RL Platform — API Service Layer
 * Communicates with FastAPI backend for real-time simulation data.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

/**
 * Run a building energy simulation.
 * @param {number} numDays - days to simulate (1-30)
 * @param {boolean} useModel - use trained RL model vs baseline
 * @param {string} modelName - which model to use
 * @returns {Promise<{hourly_data: Array, metrics: Object}>}
 */
export async function runSimulation(numDays = 5, useModel = false, modelName = 'enhanced', rates = { peak: 5.0, mid: 3.5, offPeak: 2.0 }) {
  const params = new URLSearchParams({
    num_days: numDays,
    use_model: useModel,
    model_name: modelName,
    peak_rate: rates.peak,
    mid_rate: rates.mid,
    off_peak_rate: rates.offPeak,
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
