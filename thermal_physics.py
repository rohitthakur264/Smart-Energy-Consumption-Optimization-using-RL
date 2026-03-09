"""
Physically-Realistic Thermal Dynamics Module
Implements proper building thermal response using differential equations.
Based on IEEE standards and ASHRAE guidelines.
"""
import numpy as np
from dataclasses import dataclass
from scipy.integrate import odeint

@dataclass
class BuildingThermalProperties:
    """Building thermal characteristics from UCI ENB2012 dataset."""
    relative_compactness: float  # X1: 0.62 - 0.98
    surface_area: float          # X2: 514.5 - 808.0 m²
    wall_area: float             # X3: 245 - 416.5 m²
    roof_area: float             # X4: 110.25 - 220.5 m²
    overall_height: float        # X5: 3.5 - 7 m
    orientation: float           # X6: 0/90/180/270 degrees
    glazing_area: float          # X7: 0 - 0.4 (fraction)
    glazing_distribution: float  # X8: 0 - 5 (distribution pattern)
    
    def compute_ua(self):
        """
        Compute overall U*A (thermal conductance) from building geometry.
        U*A ~ heat transfer per degree temperature difference [W/K]
        Based on: U*A ≈ perimeter_loss + roof_loss + window_loss
        """
        # Perimeter-based calculation (simplified)
        perimeter = 2 * np.sqrt(self.surface_area / self.relative_compactness)
        wall_u = 0.35  # W/m²K for modern insulation
        roof_u = 0.25  # W/m²K
        window_u = 2.8  # W/m²K (standard double glazing)
        
        # Heat loss through walls (excluding windows)
        wall_loss = self.wall_area * wall_u
        
        # Heat loss through roof
        roof_loss = self.roof_area * roof_u
        
        # Heat loss through windows
        window_area = self.glazing_area * self.wall_area
        window_loss = window_area * window_u
        
        # Total UA [W/K]
        ua_total = wall_loss + roof_loss + window_loss
        return ua_total
    
    def compute_thermal_capacity(self):
        """
        Compute effective thermal mass (capacitance) [J/K]
        Building thermal capacitance ~ 50-100 kJ/K per building
        """
        # Simplified: scaled by surface area
        # Typical range: 50,000 - 100,000 kJ/K ≈ 50-100 MJ/K
        thermal_mass = (self.surface_area / 600) * 75e6  # [J/K]
        return thermal_mass


class ThermalDynamicsModel:
    """
    Newton's Law of Cooling with HVAC system model.
    dT/dt = (U*A/C) * (T_ambient - T_indoor) + (Q_internal + Q_HVAC) / C
    
    Where:
    - T_indoor: room temperature [°C]
    - T_ambient: ambient temperature [°C]
    - U*A: thermal conductance [W/K]
    - C: thermal capacitance [J/K]
    - Q_internal: internal heat gains [W]
    - Q_HVAC: HVAC system output [W]
    """
    
    def __init__(self, building_props: BuildingThermalProperties):
        self.props = building_props
        self.ua = building_props.compute_ua()  # [W/K]
        self.capacity = building_props.compute_thermal_capacity()  # [J/K]
        self.T_indoor = 22.0  # Initial indoor temperature [°C]
        self.dt = 3600  # Timestep: 1 hour [seconds]
        
    def compute_solar_gain(self, hour: int, occupancy: float) -> float:
        """
        Compute solar heat gain and internal heat gains.
        Returns heat gain in [W]
        """
        # Solar gain: peaks at noon, depends on orientation
        solar_peak = 150 * self.props.glazing_area  # [W] - window area effect
        solar_gain = solar_peak * max(0, np.sin((hour - 6) * np.pi / 12))
        
        # Internal gains: occupants (100W/person), equipment (lighting, appliances)
        occupants_in_space = max(int(occupancy * 10), 0)  # 0-10 people
        internal_gains = occupants_in_space * 100 + 50  # [W] - base equipment
        
        return solar_gain + internal_gains
    
    def compute_ambient_temp(self, hour: int, day: int = 0) -> float:
        """
        Realistic ambient temperature profile.
        Sinusoidal day-night cycle with seasonal variation.
        """
        # Base ambient temp pattern: min at 6 AM, max at 2 PM
        temp_min = 10.0  # Min ambient [°C]
        temp_max = 32.0  # Max ambient [°C]
        ambient = ((temp_max + temp_min) / 2 + 
                   (temp_max - temp_min) / 2 * np.sin((hour - 6) * np.pi / 12))
        return ambient
    
    def hvac_power_output(self, control_signal: float, mode: str = "cooling") -> float:
        """
        HVAC system power output as function of control signal.
        control_signal ∈ [-1, 1]
        - Positive: cooling (removes heat)
        - Negative: heating (adds heat)
        Returns power in [W]
        """
        max_cooling_power = 15000 * (self.props.surface_area / 600)  # [W]
        max_heating_power = 12000 * (self.props.surface_area / 600)  # [W]
        
        if control_signal > 0:
            # Cooling: Q_HVAC < 0 (removes heat)
            power = -control_signal * max_cooling_power
        else:
            # Heating: Q_HVAC > 0 (adds heat)
            power = -control_signal * max_heating_power  # Note: signal is negative
        
        return power
    
    def compute_energy_consumption(self, hvac_power: float) -> float:
        """
        Calculate electrical energy consumption from HVAC power output.
        COP (Coefficient of Performance):
        - Cooling COP ~= 3.5 (modern air conditioning)
        - Heating COP ~= 3.0 (heat pump) or 0.95 (resistance, less efficient)
        
        Returns energy in [kWh] for 1-hour timestep
        """
        if hvac_power > 0:  # Heating
            cop = 3.0
        elif hvac_power < 0:  # Cooling
            cop = 3.5
        else:
            return 0.0
        
        # Electrical power = thermal power / COP
        electrical_power = abs(hvac_power) / cop  # [W]
        energy_kwh = electrical_power / 1000 * 1  # [kWh] for 1 hour
        return energy_kwh
    
    def step(self, control_signal: float, hour: int, occupancy: float) -> dict:
        """
        Single timestep thermal simulation.
        Returns state, energy consumption, and thermal comfort metrics.
        """
        # Compute environmental inputs
        ambient_temp = self.compute_ambient_temp(hour)
        internal_gains = self.compute_solar_gain(hour, occupancy)
        hvac_power = self.hvac_power_output(control_signal)
        
        # Total heat gain/loss
        q_ambient = self.ua * (ambient_temp - self.T_indoor)  # [W] - ambient effect
        q_total = q_ambient + internal_gains + hvac_power  # [W]
        
        # Temperature change: dT = Q * dt / C
        dT = q_total * self.dt / self.capacity  # [°C]
        self.T_indoor += dT
        
        # Ensure temperature stays in physical bounds
        self.T_indoor = np.clip(self.T_indoor, 5, 45)  # Physical bounds
        
        # Energy metrics
        energy_consumption = self.compute_energy_consumption(hvac_power)
        
        return {
            'temperature': self.T_indoor,
            'ambient_temp': ambient_temp,
            'energy_kwh': energy_consumption,
            'hvac_power_w': hvac_power,
            'internal_gains_w': internal_gains,
            'thermal_loss_w': q_ambient,
            'total_heat_gain_w': q_total
        }
    
    def reset(self, initial_temp: float = 22.0):
        """Reset thermal model to initial conditions."""
        self.T_indoor = initial_temp


if __name__ == "__main__":
    # Example: Test thermal model with a specific building
    props = BuildingThermalProperties(
        relative_compactness=0.82,
        surface_area=600.0,
        wall_area=300.0,
        roof_area=100.0,
        overall_height=5.0,
        orientation=90.0,
        glazing_area=0.2,
        glazing_distribution=3.0
    )
    
    model = ThermalDynamicsModel(props)
    print(f"Building UA: {model.ua:.1f} W/K")
    print(f"Building Thermal Capacity: {model.capacity/1e6:.1f} MJ/K\n")
    
    # Simulate 24-hour cycle with varying HVAC control
    temperatures = []
    energies = []
    
    for hour in range(24):
        occupancy = max(0, np.sin((hour - 8 - 24) * np.pi / 12)) * 0.5 + 0.5
        # Simple control: cool when too hot, heat when too cold
        if model.T_indoor > 23:
            control = 0.3  # Cooling
        elif model.T_indoor < 21:
            control = -0.3  # Heating
        else:
            control = 0.0
        
        result = model.step(control, hour, occupancy)
        temperatures.append(result['temperature'])
        energies.append(result['energy_kwh'])
        
        print(f"Hour {hour:2d}: Indoor={result['temperature']:6.2f}°C, "
              f"Ambient={result['ambient_temp']:6.2f}°C, "
              f"Energy={result['energy_kwh']:6.2f} kWh")
    
    print(f"\nTotal daily energy: {sum(energies):.2f} kWh")
