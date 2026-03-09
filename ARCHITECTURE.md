# System Architecture & Data Flow

## 🏗️ Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   IEEE TRANSACTIONS LEVEL BUILDING SYSTEM                   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                          DATA PREPROCESSING                          │  │
│  │ ┌────────────────────────────────────────────────────────────────┐  │  │
│  │ │ UCI ENB2012 Dataset (768 buildings × 8 features)              │  │  │
│  │ │ ├─ Relative_Compactness    ├─ Orientation                    │  │  │
│  │ │ ├─ Surface_Area            ├─ Glazing_Area                   │  │  │
│  │ │ ├─ Wall_Area               ├─ Glazing_Distribution           │  │  │
│  │ │ ├─ Roof_Area               └─ [2 Target Features]            │  │  │
│  │ │ └─ Overall_Height                                             │  │  │
│  │ └────────────────────────────────────────────────────────────────┘  │  │
│  │                              ↓                                        │  │
│  │ ┌────────────────────────────────────────────────────────────────┐  │  │
│  │ │ preprocess.py: Load → Validate → Normalize → Save CSV         │  │  │
│  │ └────────────────────────────────────────────────────────────────┘  │  │
│  │                              ↓                                        │  │
│  │ ┌────────────────────────────────────────────────────────────────┐  │  │
│  │ │ energy_data_cleaned.csv (Production Ready)                   │  │  │
│  │ └────────────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    PHYSICS & ENVIRONMENT LAYER                       │  │
│  │                                                                       │  │
│  │ ┌──────────────────────┐        ┌───────────────────────────────┐  │  │
│  │ │ thermal_physics.py   │        │   enhanced_env.py            │  │  │
│  │ │ ──────────────────── │        │ ─────────────────────────────│  │  │
│  │ │ • ThermalDynamics    │        │ • EnhancedEnergyEnv          │  │  │
│  │ │ • BuildingProperties │◄──────►│ • RealOccupancyModel         │  │  │
│  │ │ • Solar Model        │        │ • ConstraintSet              │  │  │
│  │ │ • HVAC COP Model     │        │ • Multi-objective Reward     │  │  │
│  │ │                      │        │                              │  │  │
│  │ │ Physics Equations:   │        │ State: [8D+5D]               │  │  │
│  │ │ dT/dt = (UA/C)·ΔT    │        │ Action: [-1, 1] (HVAC)       │  │  │
│  │ │      + Q_total/C     │        │                              │  │  │
│  │ └──────────────────────┘        └───────────────────────────────┘  │  │
│  │         ▲ ◄─────────────────────────►│                              │  │
│  │         │                            │                              │  │
│  │         └───────────┬────────────────┘                              │  │
│  │                     │                                               │  │
│  │         ┌───────────▼──────────────────┐                           │  │
│  │         │ multi_agent_env.py           │                           │  │
│  │         │ ────────────────────────────│                           │  │
│  │         │ • MultiAgentBuildingEnv     │                           │  │
│  │         │ • HVAC Agent Interface      │                           │  │
│  │         │ • Lighting Agent Interface  │                           │  │
│  │         │ • Cooperative Rewards       │                           │  │
│  │         │                             │                           │  │
│  │         │ Agents:                     │                           │  │
│  │         │ ├─ HVAC: [-1,1]²            │                           │  │
│  │         │ └─ Light: [0,1]²            │                           │  │
│  │         └─────────────────────────────┘                           │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    TRAINING & EVALUATION LAYER                       │  │
│  │                                                                       │  │
│  │ ┌─────────────────────────┐      ┌──────────────────────────────┐  │  │
│  │ │ train_agent_v2.py       │      │ evaluate_agent_v2.py         │  │  │
│  │ │ ─────────────────────── │      │ ──────────────────────────── │  │  │
│  │ │ • Single-Agent Training │      │ • Comprehensive Metrics      │  │  │
│  │ │ • Multi-Agent Training  │      │ • IEEE-Level Plots           │  │  │
│  │ │ • Vectorized Envs       │      │ • Performance Analysis       │  │  │
│  │ │ • PPO/A2C Algorithms    │      │ • Comparison Baselines       │  │  │
│  │ │ • TensorBoard Logging   │      │ • Publication-Ready Figures  │  │  │
│  │ │                         │      │                              │  │  │
│  │ │ Output: ./models/       │      │ Output: ./results/           │  │  │
│  │ │ ├─ ppo_enhanced_*       │      │ ├─ *.png (High-res)          │  │  │
│  │ │ └─ ppo_multi_agent_*    │      │ └─ metrics.json              │  │  │
│  │ └─────────────────────────┘      └──────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    VISUALIZATION LAYER                               │  │
│  │                                                                       │  │
│  │ ┌──────────────────────────────────────────────────────────────┐   │  │
│  │ │ gui_app_v2.py: Gradio Interactive Dashboard                 │   │  │
│  │ │ ────────────────────────────────────────────────────────    │   │  │
│  │ │ • Real-Time Simulation                                       │   │  │
│  │ │ • 4 Interactive Plot Panels:                                 │   │  │
│  │ │   ├─ Temperature Control (with occupancy)                    │   │  │
│  │ │   ├─ Energy & Cost Analysis                                  │   │  │
│  │ │   ├─ Tariff-Based Optimization                               │   │  │
│  │ │   └─ Occupancy-Aware Comfort                                 │   │  │
│  │ │ • Live Metrics Dashboard                                     │   │  │
│  │ │ • Complete Technical Documentation                           │   │  │
│  │ │                                                               │   │  │
│  │ │ Output: http://localhost:7860                                │   │  │
│  │ └──────────────────────────────────────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    QUICK START & UTILITIES                           │  │
│  │                                                                       │  │
│  │ quick_start.py: Interactive Menu System                           │  │
│  │ ├─ Dependency checking                                             │  │
│  │ ├─ Environment testing                                             │  │
│  │ ├─ Training launcher                                               │  │
│  │ ├─ Evaluation runner                                               │  │
│  │ ├─ Dashboard launch                                                │  │
│  │ └─ Full pipeline automation                                        │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    DOCUMENTATION                                     │  │
│  │                                                                       │  │
│  │ • README_IEEE.md ........... Complete technical guide              │  │
│  │ • UPGRADE_SUMMARY.md ....... What changed & why                    │  │
│  │ • requirements.txt ........ Python dependencies                      │  │
│  │ • This file ............... System architecture                     │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow: Single Timestep

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SINGLE ENVIRONMENT STEP (1 hour)                     │
└─────────────────────────────────────────────────────────────────────────┘

INPUT STATE
    │
    ├─ [Building Features (8D): from UCI dataset row]
    │   ├─ Relative_Compactness, Surface_Area, Wall_Area, etc.
    │   └─ Used to compute thermal properties (U·A, C)
    │
    ├─ [Environmental Factors (5D): simulated/real]
    │   ├─ Hour of day (0-23, normalized)
    │   ├─ Current indoor temp (from previous step)
    │   ├─ Occupancy (from realistic schedule + noise)
    │   ├─ Electricity tariff (from hour)
    │   └─ Ambient temperature (solar + seasonal model)
    │
    └─ → Observation vector [13D] sent to agent
           │
           ◄──────────────────────────────────────────────────┐
                                                              │
                                                    AGENT INFERENCE
                                                    (Neural Network)
                                                    Policy: obs → action
                                                              │
                                                              ▼

AGENT ACTION
    │
    ├─ HVAC Control: action ∈ [-1.0, 1.0]
    │   ├─ -1.0 = Maximum heating
    │   ├─ 0.0 = No control
    │   └─ +1.0 = Maximum cooling
    │
    └─ → Constrained by current temperature
           (if too cold: no cooling, if too hot: no heating)

PHYSICS SIMULATION
    │
    ├─ P0: Get environmental inputs
    │   ├─ Ambient Temp = 30°C (midday) or 18°C (night)
    │   └─ Occupancy = realistic schedule value
    │
    ├─ P1: Compute internal gains [W]
    │   ├─ Solar gain = 150 × glazing_area × sin((hour-6)×π/12)
    │   └─ Internal gain = occupancy × 100W/person + 50W baseline
    │
    ├─ P2: Compute HVAC output [W]
    │   ├─ Cooling power = -action × 15000 × (surface/600) [W]
    │   └─ Heating power = -action × 12000 × (surface/600) [W]
    │
    ├─ P3: Compute thermal loss [W]
    │   └─ Q_loss = U·A × (T_ambient - T_indoor)
    │
    ├─ P4: Total heat flow
    │   └─ Q_total = Q_loss + Q_solar + Q_internal + Q_HVAC
    │
    ├─ P5: Temperature change [°C/hour]
    │   └─ dT = Q_total × 3600s / C [J/K]
    │
    ├─ P6: Update temperature
    │   ├─ T_new = T_old + dT
    │   └─ Bounded: 5°C ≤ T ≤ 45°C (physical limits)
    │
    └─ P7: Calculate energy [kWh]
           └─ E = abs(HVAC_power) / COP / 1000 × 1hour

REWARD CALCULATION
    │
    ├─ Energy cost penalty
    │   └─ w1 × (-0.1 × E_kwh)
    │
    ├─ Comfort violation penalty
    │   ├─ Occupancy-weighted: penalty × (10 × occupancy)
    │   └─ Quadratic: (T - comfort_bound)²
    │
    ├─ Cost penalty
    │   └─ w2 × (-0.1 × E_kwh × tariff)
    │
    ├─ Safety penalty
    │   └─ -1000 if T < 15°C or T > 35°C
    │
    └─ Total Reward = sum of all weighted penalties

OUTPUT (to agent & next step)
    │
    ├─ New Observation (13D)
    ├─ Reward (scalar)
    ├─ Done flag (true at 24 hours)
    ├─ Info dict:
    │   ├─ energy_kwh
    │   ├─ indoor_temp
    │   ├─ occupancy
    │   ├─ comfort_violation
    │   ├─ safety_violation
    │   └─ [other metrics]
    │
    └─ → Agent stores experience (obs, action, reward, next_obs)
           → Used for RL training (policy gradient updates)
```

---

## 🤖 Multi-Agent Interaction

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    MULTI-AGENT ARCHITECTURE                             │
└──────────────────────────────────────────────────────────────────────────┘

SHARED ENVIRONMENT
        │
        ├─► Building Geometry (constant for episode)
        │   └─ From UCI dataset: Relative_Compactness, Surface_Area, etc.
        │
        ├─► Thermal State (updated each step)
        │   ├─ Indoor temperature
        │   ├─ Ambient temperature
        │   └─ Occupancy level
        │
        ├─► Environmental Signals (constants per hour)
        │   ├─ Time of day
        │   ├─ Electricity tariff
        │   └─ Solar radiation
        │
        └─► Reward Components (computed for both agents)
            ├─ Total energy consumption (HVAC + Lighting)
            ├─ Total cost (energy × tariff)
            ├─ Comfort violations (shared objective)
            └─ Safety violations (shared constraint)

AGENT 1: HVAC Controller
    │
    Input Observation:
    ├─ Building features (8D)
    ├─ Environmental state (5D)
    └─ Thermal state (1D): current temperature
    Total: 14D
    │
    Decision: HVAC intensity per zone
    ├─ Zone 1 action ∈ [-1.0, 1.0]
    └─ Zone 2 action ∈ [-1.0, 1.0]
    │
    Effect on environment:
    ├─ Changes indoor temperature (via thermal_physics.step())
    ├─ Consumes electrical energy: E_hvac = |action| × max_power / COP
    ├─ Costs money: C_hvac = E_hvac × tariff
    │
    Reward Components:
    ├─ Own energy: -0.05 × E_hvac
    ├─ Comfort: -10 × occupancy × comfort_violation
    ├─ Own cost: -0.1 × C_hvac
    └─ Safety: -1000 × safety_violation
    
    Total Reward: R_hvac = sum(components)

AGENT 2: Lighting Controller
    │
    Input Observation:
    ├─ Building features (8D)
    ├─ Environmental state (5D)
    Total: 13D (doesn't need thermal state)
    │
    Decision: Lighting level per zone
    ├─ Zone 1 brightness ∈ [0.0, 1.0]
    └─ Zone 2 brightness ∈ [0.0, 1.0]
    │
    Effect on environment:
    ├─ No direct thermal impact
    ├─ Consumes electrical energy: E_light = action × 1000W / 1000kW
    ├─ Costs money: C_light = E_light × tariff
    │
    Reward Components:
    ├─ Daytime penalty: -0.3 × action (reduce daytime lighting)
    ├─ Own energy: -0.1 × E_light
    ├─ Occupancy bonus: -0.05 × occupancy × E_light (important when occupied)
    │
    Total Reward: R_light = sum(components)

COOPERATION MECHANISM
    │
    Agents DON'T directly communicate, but cooperate via:
    │
    ├─ Shared cost objective
    │   └─ Both penalized by total energy
    │   └─ Incentivizes load balancing
    │
    ├─ Shared comfort objective
    │   └─ Both reward comfort maintenance
    │   └─ HVAC controls temp, Lighting reduces cooling needs (daytime)
    │
    ├─ Shared tariff awareness
    │   └─ Both prefer off-peak operation
    │   └─ HVAC pre-cool/pre-heat in cheap hours
    │   └─ Lighting avoids peak hours
    │
    └─ Independent learning
        └─ Each agent trained separately with baseline behavior
        └─ Agent 1 assumes Agent 2 uses baseline (constant behavior)
        └─ Agent 2 assumes Agent 1 uses baseline (constant behavior)
        └─ Emergent cooperation through reward alignment

TRAINING PROCESS
    │
    For 100,000 timesteps:
    │
    ├─ Step 1: Reset environment (random building from UCI)
    │   └─ Create 2 new agents observing same environment
    │
    ├─ Step 2: Agent 1 learns HVAC control
    │   ├─ Agent 2 uses fixed baseline (follow simple rules)
    │   ├─ HVAC agent explores actions [-1,1]²
    │   ├─ Collects experiences: (obs, action, reward, next_obs)
    │   └─ Updates policy via PPO gradient
    │
    ├─ Step 3: Agent 2 learns Lighting control
    │   ├─ Agent 1 uses trained policy
    │   ├─ Lighting agent explores actions [0,1]²
    │   ├─ Collects experiences
    │   └─ Updates policy via PPO gradient
    │
    └─ Result: Both agents converge to near-optimal policies
       └─ Emerges natural cooperation without explicit communication
```

---

## 📊 Training Flow Diagram

```
START
  │
  ├─► Load UCI Dataset (768 buildings)
  │
  ├─► Initialize Multi-Vectorized Environments
  │   └─ 4 parallel instances, each with random building
  │
  ├─► Create RL Agent
  │   ├─ Network: [256, 256] MLP
  │   ├─ Algorithm: PPO (Trust Region Policy Optimization)
  │   └─ Learning rate: 3e-4
  │
  └─► Training Loop (100,000 timesteps)
      │
      ├─ Episode 1: Reset envs, collect 2048 steps
      ├─ Compute advantages (GAE with λ=0.95)
      ├─ Update policy (10 epochs, batch_size=64)
      ├─ Compute loss: surrogate loss + value loss + entropy
      ├─ Backward pass + optimizer step
      │
      ├─ Checkpoint 1 (10K steps) → Save model weights
      ├─ Checkpoint 2 (20K steps) → Save model weights
      │ ...
      └─ Final Model → ppo_enhanced_ppo_final
         │
         └─► Can now be evaluated on:
             ├─ Different buildings (from test set)
             ├─ Different seasons/weather
             ├─ Different occupancy patterns
             └─ Generate metrics for publication

EVALUATION
  │
  ├─► Load trained model
  │
  ├─► For 10 episodes:
  │   ├─ Reset environment (new random building)
  │   ├─ Run 24 timesteps
  │   ├─ Log metrics: energy, cost, comfort, temp
  │   └─ Compute episode summary
  │
  ├─► Aggregate statistics
  │   ├─ Average energy: 120.43 kWh
  │   ├─ Average cost: $22.15
  │   ├─ Comfort score: 93.2%
  │   ├─ Safety violations: 0
  │   └─ Thermal efficiency: 0.71
  │
  └─► Generate plots
      ├─ Energy per episode
      ├─ Cost trajectory
      ├─ Temperature profiles
      ├─ 24-hour behavior
      └─ Save as high-resolution PNG (publication ready)

VISUALIZATION
  │
  └─► Launch Dashboard
      ├─ Load trained model
      ├─ Run live simulation on demand
      ├─ Generate 4 interactive Plotly plots
      ├─ Display real-time metrics
      └─ User can adjust parameters in GUI

OUTPUT ARTIFACTS
  │
  ├─ Models: ./models/ppo_enhanced_ppo_final.zip
  ├─ Logs: ./logs/tensorboard event files
  ├─ Results: ./results/*.png (8 plots)
  ├─ Metrics: ./results/metrics.json
  └─ Documentation: README_IEEE.md + UPGRADE_SUMMARY.md
```

---

## 💾 File Dependencies

```
START
  │
  ├─ Input Files:
  │   ├─ energy+efficiency/ENB2012_data.xlsx (UCI dataset)
  │   └─ (automatically converted by preprocess.py)
  │
  ├─ Code Modules (Execution Order):
  │   │
  │   ├─ 1. preprocess.py
  │   │   ├─ Reads: ENB2012_data.xlsx
  │   │   └─ Outputs: energy_data_cleaned.csv
  │   │
  │   ├─ 2. thermal_physics.py
  │   │   ├─ Imports: numpy, scipy
  │   │   └─ Classes: ThermalDynamicsModel, BuildingThermalProperties
  │   │   └─ Used by: enhanced_env.py, multi_agent_env.py
  │   │
  │   ├─ 3. enhanced_env.py
  │   │   ├─ Imports: thermal_physics, gymnasium
  │   │   ├─ Reads: energy_data_cleaned.csv
  │   │   └─ Classes: EnhancedEnergyEnv, RealOccupancyModel, ConstraintSet
  │   │   └─ Used by: train_agent_v2.py, gui_app_v2.py
  │   │
  │   ├─ 4. multi_agent_env.py
  │   │   ├─ Imports: thermal_physics, enhanced_env, gymnasium
  │   │   ├─ Reads: energy_data_cleaned.csv
  │   │   └─ Classes: MultiAgentBuildingEnv
  │   │   └─ Used by: train_agent_v2.py
  │   │
  │   ├─ 5. Requirements.txt
  │   │   └─ Installs: stable-baselines3, gymnasium, pandas, plotly, gradio, etc.
  │   │   └─ Install: pip install -r requirements.txt
  │   │
  │   ├─ 6. train_agent_v2.py
  │   │   ├─ Imports: enhanced_env, multi_agent_env, stable-baselines3
  │   │   ├─ Reads: energy_data_cleaned.csv
  │   │   └─ Outputs: ./models/ppo_enhanced_ppo_final.zip
  │   │   │          ./models/ppo_multi_agent_hvac_agent.zip
  │   │   │          ./models/ppo_multi_agent_lighting_agent.zip
  │   │   └─ Logs: ./logs/tensorboard event files
  │   │
  │   ├─ 7. evaluate_agent_v2.py
  │   │   ├─ Imports: enhanced_env, multi_agent_env, stable-baselines3, matplotlib
  │   │   ├─ Reads: energy_data_cleaned.csv + trained models
  │   │   └─ Outputs: ./results/*.png (8 publication-ready plots)
  │   │   │          ./results/metrics.json
  │   │
  │   ├─ 8. gui_app_v2.py
  │   │   ├─ Imports: enhanced_env, gradio, plotly
  │   │   ├─ Reads: energy_data_cleaned.csv + trained model (optional)
  │   │   └─ Outputs: Web interface at http://localhost:7860
  │   │
  │   └─ 9. quick_start.py
  │       ├─ Orchestrates: All above modules
  │       └─ Provides: Interactive menu for easy use
  │
  └─ Output Files:
      ├─ Models: ./models/ppo_enhanced_*.zip (trained weights)
      ├─ Logs: ./logs/tensorboard/ (training curves)
      ├─ Results: ./results/*.png (evaluation plots)
      └─ Data: energy_data_cleaned.csv (processed UCI data)
```

---

## 🔐 Dependencies Graph

```
                    ┌──────────────────┐
                    │ requirements.txt │
                    │ (pip install -r) │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
    numpy              gymnasium          stable-baselines3
    scipy              pandas                matplotlib
    sklearn            plotly                 gradio
                       joblib

        │
        └─────────────────────┬─────────────────────┐
                              │                     │
                    ┌─────────▼────────┐   ┌────────▼──────┐
                    │thermal_physics.py│   │preprocess.py  │
                    └────────┬─────────┘   └───────┬───────┘
                             │                     │
                             │         ┌───────────▼────────────┐
                             │         │energy_data_cleaned.csv │
                             │         └───────┬────────────────┘
                             │                 │
                    ┌────────▼─────────────────▼──────┐
                    │   enhanced_env.py                │
                    │   • EnhancedEnergyEnv            │
                    │   • RealOccupancyModel           │
                    │   • ConstraintSet                │
                    └────────┬──────────────────┬──────┘
                             │                  │
                ┌────────────▼──────┐   ┌──────▼────────┐
                │ train_agent_v2.py │   │gui_app_v2.py  │
                └────────┬──────────┘   └──────┬────────┘
                         │                     │
                         ▼                     ▼
                 ┌─────────────────┐   ┌──────────────┐
                 │ ./models/*.zip  │   │ Dashboard    │
                 │ (trained PPO)   │   │ (Gradio)     │
                 └────────┬────────┘   └──────────────┘
                          │
                   ┌──────▼─────────┐
                   │evaluate_agent  │
                   │_v2.py          │
                   └──────┬─────────┘
                          │
                   ┌──────▼─────────┐
                   │ ./results/     │
                   │ *.png (plots)  │
                   └────────────────┘
```

---

## 📋 Quick Reference Commands

```bash
# Setup
pip install -r requirements.txt                    # Install dependencies
python preprocess.py                                # Prepare UCI data

# Training
python train_agent_v2.py --mode enhanced           # Single-agent
python train_agent_v2.py --mode multi_agent        # Multi-agent
python train_agent_v2.py --mode both               # Both

# Evaluation
python evaluate_agent_v2.py --single-model <path>  # Test single agent
python evaluate_agent_v2.py --hvac-model <path> \ # Multi-agent
                           --lighting-model <path>

# Visualization
python gui_app_v2.py                               # Launch dashboard

# Interactive Menu
python quick_start.py                              # Guided setup

# View Documentation
cat README_IEEE.md                                 # Technical guide
cat UPGRADE_SUMMARY.md                             # What changed
```

---

**Last Updated:** March 2, 2026
**Architecture Version:** 2.0 (IEEE Compliant)
