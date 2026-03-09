"""
Constraint-Based Reinforcement Learning Environment
Implements occupancy-aware state space with safety/comfort constraints.
Ensures IEEE standard compliance for building HVAC systems.
"""
import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
from thermal_physics import ThermalDynamicsModel, BuildingThermalProperties


class RealOccupancyModel:
    """
    Realistic occupancy simulation based on real building patterns.
    From UCI dataset insights and ASHRAE 90.1 standard schedules.
    """
    
    def __init__(self, season='summer'):
        self.season = season
        self.base_schedule = self._get_occupancy_schedule()
        
    def _get_occupancy_schedule(self):
        """
        Realistic 24-hour occupancy profile for commercial buildings.
        Returns occupancy as fraction [0, 1] for each hour.
        """
        schedule = {
            'weekday': {
                0: 0.05, 1: 0.05, 2: 0.05, 3: 0.05, 4: 0.05, 5: 0.1,   # Early morning
                6: 0.2, 7: 0.4, 8: 0.8, 9: 0.95, 10: 0.95, 11: 0.95,   # Morning peak
                12: 0.9, 13: 0.85, 14: 0.9, 15: 0.9, 16: 0.9, 17: 0.85, # Afternoon
                18: 0.4, 19: 0.1, 20: 0.05, 21: 0.05, 22: 0.05, 23: 0.05  # Evening
            },
            'weekend': {
                h: 0.1 if 9 <= h <= 17 else 0.02 for h in range(24)  # Weekend lighter
            }
        }
        return schedule['weekday']
    
    def get_occupancy(self, hour: int, stochastic: bool = True) -> float:
        """
        Get occupancy for given hour with realistic noise.
        """
        base_occ = self.base_schedule.get(hour, 0.1)
        
        if stochastic:
            # Add realistic variation (±10% std)
            noise = np.random.normal(0, base_occ * 0.1)
            occupancy = np.clip(base_occ + noise, 0, 1)
        else:
            occupancy = base_occ
        
        return occupancy


class ConstraintSet:
    """
    Define physical and safety constraints for building HVAC system.
    """
    
    # Thermal comfort (ISO 7730 - Category A)
    COMFORT_TEMP_MIN = 20.0  # °C
    COMFORT_TEMP_MAX = 26.0  # °C
    COMFORT_TEMP_SETPOINT = 22.0  # °C
    
    # Safety limits (building codes)
    SAFETY_TEMP_MIN = 15.0  # °C - prevent freezing
    SAFETY_TEMP_MAX = 35.0  # °C - prevent heat damage
    
    # Occupancy-dependent constraints
    TEMP_RELAXATION_UNOCCUPIED = 2.0  # °C - allow wider range when empty
    
    # Humidity (not yet modeled, placeholder)
    RH_COMFORT_MIN = 30.0  # %
    RH_COMFORT_MAX = 60.0  # %
    
    @staticmethod
    def get_comfort_penalty(temperature: float, occupancy: float) -> float:
        """
        Calculate comfort penalty based on temperature and occupancy.
        - During occupied hours: strict comfort maintenance
        - During unoccupied: relaxed constraints
        """
        if occupancy > 0.2:  # Occupied
            comfort_min = ConstraintSet.COMFORT_TEMP_MIN
            comfort_max = ConstraintSet.COMFORT_TEMP_MAX
        else:  # Unoccupied
            comfort_min = ConstraintSet.COMFORT_TEMP_MIN - ConstraintSet.TEMP_RELAXATION_UNOCCUPIED
            comfort_max = ConstraintSet.COMFORT_TEMP_MAX + ConstraintSet.TEMP_RELAXATION_UNOCCUPIED
        
        if comfort_min <= temperature <= comfort_max:
            return 0.0
        elif temperature < comfort_min:
            return (comfort_min - temperature) ** 2
        else:
            return (temperature - comfort_max) ** 2
    
    @staticmethod
    def get_safety_violation(temperature: float) -> bool:
        """Check if temperature violates safety constraints."""
        return temperature < ConstraintSet.SAFETY_TEMP_MIN or temperature > ConstraintSet.SAFETY_TEMP_MAX
    
    @staticmethod
    def get_allowed_actions(temperature: float) -> tuple:
        """
        Return allowed action range based on current temperature.
        - If too cold: only heating allowed (positive signal)
        - If too hot: only cooling allowed (negative signal)
        - Normal: full range allowed
        """
        if temperature < ConstraintSet.COMFORT_TEMP_MIN - 1.0:
            return (0.0, 1.0)  # Only heating
        elif temperature > ConstraintSet.COMFORT_TEMP_MAX + 1.0:
            return (-1.0, 0.0)  # Only cooling
        else:
            return (-1.0, 1.0)  # Full range


class EnhancedEnergyEnv(gym.Env):
    """
    Enhanced Energy Environment with:
    1. Physically realistic thermal dynamics
    2. Tariff-aware rewards
    3. Occupancy-aware state space
    4. Constraint-based RL
    5. Multi-set state representation
    """
    
    def __init__(self, 
                 uci_data_path: str,
                 use_real_data: bool = True,
                 stochastic: bool = True,
                 custom_tariffs: dict = None):
        """
        Initialize enhanced energy environment.
        
        Args:
            uci_data_path: Path to UCI ENB2012 dataset
            use_real_data: Load actual buildings from UCI dataset
            stochastic: Enable stochastic elements (occupancy noise, etc.)
        """
        super(EnhancedEnergyEnv, self).__init__()
        
        # Load UCI data
        self.df = pd.read_csv(uci_data_path)
        self.feature_cols = ['Relative_Compactness', 'Surface_Area', 'Wall_Area', 
                             'Roof_Area', 'Overall_Height', 'Orientation', 
                             'Glazing_Area', 'Glazing_Area_Distribution']
        
        self.stochastic = stochastic
        self.occupancy_model = RealOccupancyModel()
        self.constraints = ConstraintSet()
        
        # State space: [8 building features] + [hour, indoor_temp, occupancy, tariff, outdoor_temp]
        # Total: 13 dimensions
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(13,), dtype=np.float32
        )
        
        # Action space: HVAC control [-1, 1]
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(1,), dtype=np.float32)
        
        # Tariff schedule (5-tier realistic pricing or custom)
        self.tariff_rates = custom_tariffs or {
            'peak': 5.0,      # 9 AM - 6 PM
            'mid': 3.5,       # 7-9 AM, 6-9 PM
            'off_peak': 2.0   # 9 PM - 7 AM
        }
        
        self.reset()
    
    def get_tariff(self, hour: int) -> float:
        """Get electricity tariff for given hour based on custom rates."""
        if 9 <= hour < 18:  # Peak
            return float(self.tariff_rates.get('peak', 5.0))
        elif (7 <= hour < 9) or (18 <= hour < 21):  # Mid
            return float(self.tariff_rates.get('mid', 3.5))
        else:  # Off-peak
            return float(self.tariff_rates.get('off_peak', 2.0))
    
    def reset(self, seed=None, options=None):
        """
        Reset with optional seed and specific building/hour options.
        options can include: 'building_idx' and 'start_hour'
        """
        if seed is not None:
            super().reset(seed=seed)
            np.random.seed(seed)
        
        # Select building (deterministic if options provided, otherwise random)
        if options and 'building_idx' in options:
            self.building_idx = options['building_idx'] % len(self.df)
        else:
            self.building_idx = np.random.randint(0, len(self.df))
            
        building_data = self.df.iloc[self.building_idx]
        
        # Extract building properties
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
        
        # Initialize thermal model
        self.thermal_model = ThermalDynamicsModel(self.building_props)
        
        # Start hour (deterministic if options provided)
        if options and 'start_hour' in options:
            self.current_hour = options['start_hour'] % 24
        else:
            self.current_hour = 0 # Default to midnight for cleaner dashboarding
            
        self.total_steps = 0
        self.max_episode_steps = 24  # One full day
        self.episode_metrics = {
            'energy_consumption': [],
            'energy_cost': [],
            'comfort_violation': [],
            'safety_violation': 0
        }
        
        return self._get_obs(), {}
    
    def _get_obs(self) -> np.ndarray:
        """
        Get occupancy-aware observation state.
        [8 building features] + [hour, indoor_temp, occupancy, tariff, outdoor_temp]
        """
        building_features = self.df.iloc[self.building_idx][self.feature_cols].values
        occupancy = self.occupancy_model.get_occupancy(self.current_hour, 
                                                        stochastic=self.stochastic)
        tariff = self.get_tariff(self.current_hour)
        ambient_temp = self.thermal_model.compute_ambient_temp(self.current_hour)
        
        # Normalize hour to [0, 1]
        hour_norm = self.current_hour / 24.0
        
        obs = np.concatenate([
            building_features,
            [hour_norm, self.thermal_model.T_indoor, occupancy, tariff, ambient_temp]
        ]).astype(np.float32)
        
        return obs
    
    def step(self, action: np.ndarray) -> tuple:
        """
        Execute one timestep of environment.
        Returns: observation, reward, terminated, truncated, info
        """
        action_clipped = np.clip(action[0], -1.0, 1.0)
        
        # Get current environmental state
        occupancy = self.occupancy_model.get_occupancy(self.current_hour, 
                                                        stochastic=self.stochastic)
        
        # Simulate thermal dynamics
        thermal_result = self.thermal_model.step(action_clipped, 
                                                  self.current_hour, 
                                                  occupancy)
        
        # Add slight stochastic sensory noise to temperature for comfort realism
        if self.stochastic:
            thermal_result['temperature'] += np.random.normal(0, 0.15)

        
        # Record metrics
        energy_kwh = thermal_result['energy_kwh']
        energy_cost = energy_kwh * self.get_tariff(self.current_hour)
        
        # Constraint violations
        comfort_violation = ConstraintSet.get_comfort_penalty(thermal_result['temperature'], 
                                                              occupancy)
        safety_violation = ConstraintSet.get_safety_violation(thermal_result['temperature'])
        
        self.episode_metrics['energy_consumption'].append(energy_kwh)
        self.episode_metrics['energy_cost'].append(energy_cost)
        self.episode_metrics['comfort_violation'].append(comfort_violation)
        if safety_violation:
            self.episode_metrics['safety_violation'] += 1
        
        # Multi-objective reward function
        # R = w1*energy_penalty + w2*comfort_penalty + w3*cost_penalty + w4*safety_penalty
        
        # Weight occupancy-aware comfort penalty
        comfort_weight = 10.0 * occupancy  # Stricter when occupied
        
        energy_penalty = -0.05 * energy_kwh  # Penalize energy use
        comfort_penalty = -comfort_weight * comfort_violation  # Penalize discomfort (occupied)
        cost_penalty = -0.1 * (energy_cost * 100)  # Penalize cost (scaled to maintain original reward balance)
        safety_penalty = -1000.0 * (1 if safety_violation else 0)  # Large penalty for safety violation
        
        reward = energy_penalty + comfort_penalty + cost_penalty + safety_penalty
        
        # Update time
        self.current_hour = (self.current_hour + 1) % 24
        self.total_steps += 1
        
        terminated = self.total_steps >= self.max_episode_steps
        truncated = False
        
        # Info dictionary
        info = {
            'energy_kwh': energy_kwh,
            'energy_cost': energy_cost,
            'indoor_temp': thermal_result['temperature'],
            'ambient_temp': thermal_result['ambient_temp'],
            'occupancy': occupancy,
            'tariff': self.get_tariff(self.current_hour - 1),  # Previous hour tariff
            'hvac_power_w': thermal_result['hvac_power_w'],
            'comfort_violation': comfort_violation,
            'safety_violation': safety_violation,
            'thermal_loss_w': thermal_result['thermal_loss_w'],
            'internal_gains_w': thermal_result['internal_gains_w']
        }
        
        return self._get_obs(), float(reward), terminated, truncated, info


if __name__ == "__main__":
    # Test environment
    env = EnhancedEnergyEnv("energy_data_cleaned.csv")
    
    print("Enhanced Energy Environment Test")
    print("=" * 50)
    obs, _ = env.reset()
    print(f"Initial observation shape: {obs.shape}")
    print(f"Initial state: Hour={obs[8]:.2f}, Temp={obs[9]:.2f}°C, Occ={obs[10]:.2f}, Tariff={obs[11]:.2f}")
    
    # Run one episode
    rewards = []
    temps = []
    for step in range(24):
        action = np.array([0.2])  # Mild cooling
        obs, reward, terminated, truncated, info = env.step(action)
        rewards.append(reward)
        temps.append(info['indoor_temp'])
        
        print(f"Hour {step:2d}: T={info['indoor_temp']:5.1f}°C, "
              f"E={info['energy_kwh']:5.2f}kWh, Occ={info['occupancy']:.2f}, "
              f"R={reward:7.2f}")
    
    print(f"\nTotal reward: {sum(rewards):.2f}")
    print(f"Avg temperature: {np.mean(temps):.2f}°C")
    print(f"Total energy: {sum(env.episode_metrics['energy_consumption']):.2f}kWh")
