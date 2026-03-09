#!/usr/bin/env python3
"""
Quick Start Guide for IEEE Transactions Level Building Energy Management System
Automated setup and demonstration
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run shell command and report status."""
    print(f"\n{'='*70}")
    print(f"▶ {description}")
    print(f"{'='*70}")
    print(f"Command: {cmd}\n")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True)
        print(f"✓ Success: {description}\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {description}")
        print(f"Error: {e}\n")
        return False


def check_dependencies():
    """Check if key packages are installed."""
    print("\n" + "="*70)
    print("Checking Dependencies...")
    print("="*70)
    
    required_packages = {
        'gymnasium': 'gymnasium',
        'stable_baselines3': 'stable-baselines3',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'plotly': 'plotly',
        'gradio': 'gradio'
    }
    
    missing = []
    for import_name, package_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name}")
            missing.append(package_name)
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✓ All dependencies installed!")
    return True


def setup_directories():
    """Create necessary directories."""
    print("\n" + "="*70)
    print("Setting Up Directories...")
    print("="*70)
    
    dirs = ['models', 'logs', 'results']
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
        print(f"✓ Created: {d}/")
    
    print("\n✓ Directories created!")


def preprocess_data():
    """Preprocess UCI dataset."""
    print("\n" + "="*70)
    print("Preprocessing UCI ENB2012 Dataset...")
    print("="*70)
    
    # Check if data file exists
    data_file = Path("energy_data_cleaned.csv")
    if data_file.exists():
        print(f"✓ Dataset already exists: {data_file}")
        return True
    
    # Run preprocessing
    if run_command("python preprocess.py", "Load and process UCI dataset"):
        return True
    else:
        print("\n⚠ Dataset preprocessing failed!")
        print("Make sure ENB2012_data.xlsx exists in energy+efficiency/ directory")
        return False


def test_environments():
    """Test if environments run without errors."""
    print("\n" + "="*70)
    print("Testing Environments...")
    print("="*70)
    
    print("\nTesting thermal physics module...")
    try:
        from thermal_physics import ThermalDynamicsModel, BuildingThermalProperties
        
        props = BuildingThermalProperties(
            relative_compactness=0.82, surface_area=600.0, wall_area=300.0,
            roof_area=100.0, overall_height=5.0, orientation=90.0,
            glazing_area=0.2, glazing_distribution=3.0
        )
        model = ThermalDynamicsModel(props)
        result = model.step(0.3, 12, 0.8)
        
        print(f"✓ Thermal physics working")
        print(f"  - Temperature: {result['temperature']:.1f}°C")
        print(f"  - Energy: {result['energy_kwh']:.2f} kWh")
    except Exception as e:
        print(f"✗ Thermal physics failed: {e}")
        return False
    
    print("\nTesting enhanced environment...")
    try:
        from enhanced_env import EnhancedEnergyEnv
        
        env = EnhancedEnergyEnv("energy_data_cleaned.csv", stochastic=False)
        obs, _ = env.reset()
        
        for _ in range(3):
            obs, reward, term, trunc, info = env.step([0.1])
        
        print(f"✓ Enhanced environment working")
        print(f"  - State shape: {obs.shape}")
        print(f"  - Energy: {info['energy_kwh']:.2f} kWh")
        
        env.close()
    except Exception as e:
        print(f"✗ Enhanced environment failed: {e}")
        return False
    
    print("\nTesting multi-agent environment...")
    try:
        from multi_agent_env import MultiAgentBuildingEnv
        import numpy as np
        
        env = MultiAgentBuildingEnv("energy_data_cleaned.csv")
        obs, _ = env.reset()
        
        actions = {
            'hvac_agent': np.array([0.2, -0.1]),
            'lighting_agent': np.array([0.5, 0.7])
        }
        obs, rew, term, trunc, info = env.step(actions)
        
        print(f"✓ Multi-agent environment working")
        print(f"  - HVAC reward: {rew['hvac_agent']:.4f}")
        print(f"  - Lighting reward: {rew['lighting_agent']:.4f}")
        
        env.close()
    except Exception as e:
        print(f"✗ Multi-agent environment failed: {e}")
        return False
    
    print("\n✓ All environments tested successfully!")
    return True


def show_menu():
    """Show interactive menu."""
    print("\n" + "="*70)
    print("🏢 IEEE TRANSACTIONS LEVEL BUILDING ENERGY MANAGEMENT SYSTEM")
    print("="*70)
    print("""
📊 Quick Start Options:

1. 🏋️  Train Single-Agent (Enhanced Environment)
   - Physics-based HVAC control
   - Occupancy-aware comfort
   - Tariff optimization
   - Time: ~30 minutes (4 parallel envs)
   
2. 🤖 Train Multi-Agent (HVAC + Lighting)
   - Cooperative HVAC + Lighting agents
   - Independent learning with shared objectives
   - Time: ~45 minutes
   
3. 📊 Evaluate Trained Models
   - Generate IEEE-level metrics
   - Create publication-quality plots
   - Performance comparison
   
4. 📺 Launch Interactive Dashboard
   - Real-time visualizations
   - Tariff-aware optimization display
   - Occupancy comfort analysis
   
5. 📚 View Comprehensive Documentation
   - Technical deep dive
   - Equations and formulations
   - Integration guide
   
6. ⚡ Run All (Setup + Train + Evaluate + Dashboard)
   - Complete pipeline (2-3 hours)
   
0. ❌ Exit

    """)


def main():
    """Main quick start menu."""
    print("\n" + "="*70)
    print("INITIALIZING IEEE TRANSACTIONS LEVEL SYSTEM")
    print("="*70)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Step 2: Setup directories
    setup_directories()
    
    # Step 3: Preprocess data
    if not preprocess_data():
        sys.exit(1)
    
    # Step 4: Test environments
    if not test_environments():
        print("\n⚠ Environment tests failed. Check implementation.")
        sys.exit(1)
    
    # Step 5: Show menu
    while True:
        show_menu()
        choice = input("Select option (0-6): ").strip()
        
        if choice == "0":
            print("\n👋 Goodbye!")
            break
        
        elif choice == "1":
            print("\n" + "="*70)
            print("TRAINING SINGLE-AGENT MODEL")
            print("="*70)
            timesteps = input("Enter training timesteps (default 100000): ").strip() or "100000"
            envs = input("Enter parallel environments (default 4): ").strip() or "4"
            
            cmd = f"python train_agent_v2.py --mode enhanced --timesteps {timesteps} --envs {envs}"
            run_command(cmd, "Single-agent training")
        
        elif choice == "2":
            print("\n" + "="*70)
            print("TRAINING MULTI-AGENT SYSTEM")
            print("="*70)
            timesteps = input("Enter training timesteps (default 100000): ").strip() or "100000"
            
            cmd = f"python train_agent_v2.py --mode multi_agent --timesteps {timesteps}"
            run_command(cmd, "Multi-agent training")
        
        elif choice == "3":
            print("\n" + "="*70)
            print("EVALUATING MODELS")
            print("="*70)
            
            model_path = input("Enter model path (or press Enter to skip): ").strip()
            if model_path:
                cmd = f'python evaluate_agent_v2.py --single-model "{model_path}" --episodes 10'
                run_command(cmd, "Model evaluation")
        
        elif choice == "4":
            print("\n" + "="*70)
            print("LAUNCHING DASHBOARD")
            print("="*70)
            print("Starting Gradio server...")
            print("Dashboard will open at: http://localhost:7860\n")
            
            try:
                import subprocess
                subprocess.run(["python", "gui_app_v2.py"])
            except KeyboardInterrupt:
                print("Dashboard stopped.")
        
        elif choice == "5":
            print("\n" + "="*70)
            print("OPENING DOCUMENTATION")
            print("="*70)
            
            readme_path = Path("README_IEEE.md")
            if readme_path.exists():
                print(f"✓ Documentation: {readme_path}")
                print("\nOpening in default viewer...\n")
                
                # Try to open with default application
                try:
                    if sys.platform == 'win32':
                        os.startfile(readme_path)
                    elif sys.platform == 'darwin':
                        subprocess.run(['open', str(readme_path)])
                    else:
                        subprocess.run(['xdg-open', str(readme_path)])
                except:
                    print(f"Could not open file. Read manually: {readme_path}")
            else:
                print("✗ README_IEEE.md not found")
        
        elif choice == "6":
            print("\n" + "="*70)
            print("RUNNING COMPLETE PIPELINE")
            print("="*70)
            print("This will: Train models → Evaluate → Launch dashboard")
            print("Estimated time: 2-3 hours\n")
            
            confirm = input("Continue? (y/n): ").strip().lower()
            if confirm == 'y':
                run_command(
                    "python train_agent_v2.py --mode enhanced --timesteps 100000 --envs 4",
                    "Complete training"
                )
                run_command(
                    'python evaluate_agent_v2.py --single-model "models/ppo_enhanced_ppo_final.zip" --episodes 10',
                    "Evaluation"
                )
                print("\n✓ Pipeline complete! Launch dashboard with option 4.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
        sys.exit(0)
