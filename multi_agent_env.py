"""
Multi-Agent HVAC + Lighting Control Environment
Decentralized control for building subsystems.
Implements cooperative multi-agent RL using gymnasium's MultiAgentAPI.
"""
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
from typing import Dict, Tuple
from thermal_physics import ThermalDynamicsModel, BuildingThermalProperties
from enhanced_env import RealOccupancyModel, ConstraintSet


class MultiAgentBuildingEnv(gym.Env):
    """
    Multi-agent environment with separate agents for:
    1. HVAC Control Agent (heating/cooling)
    2. Lighting Control Agent (illumination level)
    
    Agents cooperatively optimize building energy while maintaining comfort.
    """
    
    metadata = {'render_modes': ['ansi']}
    
    def __init__(self, 
                 uci_data_path: str,
                 num_zones: int = 2,
                 stochastic: bool = True):
        """
        Initialize multi-agent building environment.
        
        Args:
            uci_data_path: Path to UCI dataset
            num_zones: Number of building zones (for HVAC zoning)
            stochastic: Enable stochastic simulation
        """
        super(MultiAgentBuildingEnv, self).__init__()
        
        self.num_zones = num_zones
        self.stochastic = stochastic
        
        # Load UCI data
        self.df = pd.read_csv(uci_data_path)
        self.feature_cols = ['Relative_Compactness', 'Surface_Area', 'Wall_Area', 
                             'Roof_Area', 'Overall_Height', 'Orientation', 
                             'Glazing_Area', 'Glazing_Area_Distribution']
        
        # Occupancy and constraints
        self.occupancy_model = RealOccupancyModel()
        self.constraints = ConstraintSet()
        
        # Agent identifiers
        self.agents = ['hvac_agent', 'lighting_agent']
        self.possible_agents = self.agents.copy()
        
        # Observation spaces (per agent)
        self.observation_spaces = {
            'hvac_agent': spaces.Box(
                low=-np.inf, high=np.inf, shape=(14,), dtype=np.float32
                # 8 building + 5 environmental + 1 hvac_state
            ),
            'lighting_agent': spaces.Box(
                low=-np.inf, high=np.inf, shape=(13,), dtype=np.float32
                # 8 building + 5 environmental
            )
        }
        
        # Action spaces (per agent)
        self.action_spaces = {
            'hvac_agent': spaces.Box(low=-1.0, high=1.0, shape=(num_zones,), dtype=np.float32),
            # hvac_agent controls: -1 (max heating) to +1 (max cooling), per zone
            
            'lighting_agent': spaces.Box(low=0.0, high=1.0, shape=(num_zones,), dtype=np.float32)
            # lighting_agent controls: 0 (off) to 1 (full brightness), per zone
        }
        
        # Initialize per-agent state
        self.reset()
    
    def reset(self, seed=None, options=None):
        """Reset environment and all agents."""
        super().reset(seed=seed)
        
        # Select random building
        self.building_idx = np.random.randint(0, len(self.df))
        building_data = self.df.iloc[self.building_idx]
        
        self.building_props = BuildingThermalProperties(
            relative_compactness=building_data['Relative_Compactness'],
            surface_area=building_data['Surface_Area'],
            wall_area=building_data['Wall_Area'],
            roof_area=building_data['Roof_Area'],
            overall_height=building_data['Overall_Height'],
            orientation=building_data['Orientation'],
            glazing_area=building_data['Glazing_Area'],
            glazing_distribution=building_data['Glazing_Area_Distribution']
        )
        
        # Thermal model (whole building or can be extended to per-zone)
        self.thermal_model = ThermalDynamicsModel(self.building_props)
        
        # Per-zone state tracking
        self.zone_temps = np.ones(self.num_zones) * 22.0  # Initial temp
        self.zone_lighting = np.zeros(self.num_zones)      # Lighting level
        
        # Episode tracking
        self.current_hour = np.random.randint(0, 24)
        self.total_steps = 0
        self.max_episode_steps = 24
        
        # Metrics
        self.metrics = {
            'hvac_energy': [],
            'lighting_energy': [],
            'total_cost': [],
            'comfort_violations': [],
            'occupancy_comfort': []
        }
        
        observations = {
            'hvac_agent': self._get_obs_hvac(),
            'lighting_agent': self._get_obs_lighting()
        }
        
        return observations, {}
    
    def _get_building_features(self) -> np.ndarray:
        """Get building feature vector from UCI data."""
        return self.df.iloc[self.building_idx][self.feature_cols].values.astype(np.float32)
    
    def _get_environmental_state(self) -> Tuple[float, float, float, float, float]:
        """Get current environmental state: hour_norm, indoor_temp, occupancy, tariff, ambient_temp"""
        occupancy = self.occupancy_model.get_occupancy(self.current_hour, 
                                                        stochastic=self.stochastic)
        tariff = self._get_tariff(self.current_hour)
        ambient_temp = self.thermal_model.compute_ambient_temp(self.current_hour)
        hour_norm = self.current_hour / 24.0
        avg_temp = np.mean(self.zone_temps)
        
        return hour_norm, avg_temp, occupancy, tariff, ambient_temp
    
    def _get_obs_hvac(self) -> np.ndarray:
        """Observation for HVAC agent: includes thermal state."""
        building_features = self._get_building_features()
        env_state = self._get_environmental_state()
        hvac_state = np.array([np.mean(self.zone_temps)])  # Average zone temperature
        
        obs = np.concatenate([
            building_features,
            env_state,
            hvac_state
        ]).astype(np.float32)
        return obs
    
    def _get_obs_lighting(self) -> np.ndarray:
        """Observation for lighting agent: excludes deep thermal state."""
        building_features = self._get_building_features()
        env_state = self._get_environmental_state()
        
        obs = np.concatenate([
            building_features,
            env_state
        ]).astype(np.float32)
        return obs
    
    def _get_tariff(self, hour: int) -> float:
        """Get electricity tariff."""
        if 9 <= hour < 18:
            return 5.0
        elif (7 <= hour < 9) or (18 <= hour < 21):
            return 3.5
        else:
            return 2.0
    
    def step(self, actions: Dict[str, np.ndarray]) -> Tuple[Dict, Dict, Dict, Dict, Dict]:
        """
        Execute one environment step for both agents.
        
        Args:
            actions: {'hvac_agent': action_hvac, 'lighting_agent': action_lighting}
        
        Returns:
            observations, rewards, terminateds, truncateds, infos (per agent)
        """
        action_hvac = np.clip(actions['hvac_agent'], -1.0, 1.0)
        action_lighting = np.clip(actions['lighting_agent'], 0.0, 1.0)
        
        # Get current state
        occupancy = self.occupancy_model.get_occupancy(self.current_hour, 
                                                        stochastic=self.stochastic)
        
        # ==================== HVAC Subsystem ====================
        # Aggregate HVAC actions across zones
        avg_hvac_action = np.mean(action_hvac)
        
        # Simulate thermal dynamics
        thermal_result = self.thermal_model.step(avg_hvac_action, 
                                                  self.current_hour, 
                                                  occupancy)
        
        # Update zone temperatures (simplified: uniform across zones)
        self.zone_temps[:] = thermal_result['temperature']
        
        hvac_energy_kwh = thermal_result['energy_kwh']
        hvac_cost = hvac_energy_kwh * self._get_tariff(self.current_hour) * 100
        
        # ==================== Lighting Subsystem ====================
        # Lighting energy consumption
        # Model: 10 W/m² per zone per unit lighting level
        lighting_power_per_zone = 1000 * action_lighting  # [W] - approximate
        lighting_energy_kwh = np.sum(lighting_power_per_zone) / 1000 * 1  # [kWh for 1 hour]
        lighting_cost = lighting_energy_kwh * self._get_tariff(self.current_hour) * 100
        
        # Lighting improves occupancy comfort (daylighting bonus)
        daylighting_hours = 6 <= self.current_hour <= 18
        lighting_comfort_bonus = 0.5 * occupancy if daylighting_hours else 0.2 * occupancy
        
        self.zone_lighting = action_lighting.copy()
        
        # ==================== Comfort & Constraint Violations ====================
        comfort_violation = ConstraintSet.get_comfort_penalty(thermal_result['temperature'], 
                                                              occupancy)
        safety_violation = ConstraintSet.get_safety_violation(thermal_result['temperature'])
        
        # ==================== Multi-Objective Rewards ====================
        # HVAC Agent Reward
        hvac_reward = (
            -0.05 * hvac_energy_kwh  # Energy efficiency
            - 10.0 * occupancy * comfort_violation  # Thermal comfort (occupancy-weighted)
            - 0.1 * hvac_cost  # Cost optimization
            - 1000.0 * (1 if safety_violation else 0)  # Safety constraint
        )
        
        # Lighting Agent Reward
        # Goal: minimize unnecessary lighting during daytime, optimize nighttime
        daytime_penalty = 0.3 * (1 - daylighting_hours) * action_lighting.mean()
        nighttime_bonus = -0.1 * daylighting_hours * lighting_energy_kwh
        occupancy_bonus = -0.05 * occupancy * lighting_energy_kwh  # More important when occupied
        
        lighting_reward = daytime_penalty + nighttime_bonus + occupancy_bonus
        
        rewards = {
            'hvac_agent': float(hvac_reward),
            'lighting_agent': float(lighting_reward)
        }
        
        # ==================== Termination & Info ====================
        self.total_steps += 1
        self.current_hour = (self.current_hour + 1) % 24
        
        terminated = self.total_steps >= self.max_episode_steps
        terminateds = {agent: terminated for agent in self.agents}
        truncateds = {agent: False for agent in self.agents}
        
        # Shared information
        info = {
            'hvac_agent': {
                'energy_kwh': hvac_energy_kwh,
                'cost': hvac_cost,
                'temperature': thermal_result['temperature'],
                'comfort_violation': comfort_violation,
                'safety_violation': safety_violation
            },
            'lighting_agent': {
                'energy_kwh': lighting_energy_kwh,
                'cost': lighting_cost,
                'occupancy': occupancy,
                'daylighting': daylighting_hours
            }
        }
        
        # Record metrics
        self.metrics['hvac_energy'].append(hvac_energy_kwh)
        self.metrics['lighting_energy'].append(lighting_energy_kwh)
        self.metrics['total_cost'].append(hvac_cost + lighting_cost)
        self.metrics['comfort_violations'].append(comfort_violation)
        
        # Get new observations
        observations = {
            'hvac_agent': self._get_obs_hvac(),
            'lighting_agent': self._get_obs_lighting()
        }
        
        return observations, rewards, terminateds, truncateds, info
    
    def render(self, mode='ansi'):
        """Render current environment state."""
        if mode == 'ansi':
            print(f"Hour: {self.current_hour}, Temps: {self.zone_temps}, "
                  f"Lighting: {self.zone_lighting}")


if __name__ == "__main__":
    # Test multi-agent environment
    env = MultiAgentBuildingEnv("energy_data_cleaned.csv", num_zones=2)
    
    print("Multi-Agent Building Control Environment Test")
    print("=" * 60)
    
    obs, _ = env.reset()
    print(f"HVAC Agent observation shape: {obs['hvac_agent'].shape}")
    print(f"Lighting Agent observation shape: {obs['lighting_agent'].shape}")
    
    # Run one episode with random agents
    hvac_energies = []
    lighting_energies = []
    
    for step in range(24):
        # Random actions
        actions = {
            'hvac_agent': np.array([np.random.uniform(-0.3, 0.3), np.random.uniform(-0.3, 0.3)]),
            'lighting_agent': np.array([np.random.uniform(0, 1), np.random.uniform(0, 1)])
        }
        
        obs, rewards, terminateds, truncateds, infos = env.step(actions)
        
        hvac_energies.append(infos['hvac_agent']['energy_kwh'])
        lighting_energies.append(infos['lighting_agent']['energy_kwh'])
        
        print(f"Hour {step:2d}: HVAC_E={infos['hvac_agent']['energy_kwh']:5.2f}kWh, "
              f"Light_E={infos['lighting_agent']['energy_kwh']:5.2f}kWh, "
              f"HVAC_R={rewards['hvac_agent']:7.2f}, Light_R={rewards['lighting_agent']:7.2f}")
    
    print(f"\nTotal HVAC energy: {sum(hvac_energies):.2f} kWh")
    print(f"Total Lighting energy: {sum(lighting_energies):.2f} kWh")
    print(f"Total energy: {sum(hvac_energies) + sum(lighting_energies):.2f} kWh")
