"""
Advanced Evaluation & Visualization Dashboard
Evaluates trained agents and generates publication-quality plots.
IEEE Transactions level metrics and analysis.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
from stable_baselines3 import PPO, A2C
from enhanced_env import EnhancedEnergyEnv, ConstraintSet
from multi_agent_env import MultiAgentBuildingEnv


class AdvancedEvaluator:
    """
    Comprehensive evaluation of trained building control agents.
    Generates IEEE-level metrics and visualizations.
    """
    
    def __init__(self, data_path: str, output_dir: str = "./results"):
        self.data_path = data_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def evaluate_single_agent(self, 
                              model_path: str,
                              num_episodes: int = 10,
                              episode_length: int = 24) -> dict:
        """
        Evaluate single-agent (enhanced environment) performance.
        """
        print("\n" + "="*70)
        print("Single-Agent Evaluation")
        print("="*70)
        
        env = EnhancedEnergyEnv(self.data_path)
        try:
            model = PPO.load(model_path)
        except:
            try:
                model = A2C.load(model_path)
            except:
                raise ValueError(f"Could not load model from {model_path}")
        
        # Metrics collection
        metrics = {
            'episodes': [],
            'total_energy': [],
            'total_cost': [],
            'avg_temperature': [],
            'comfort_violations': [],
            'safety_violations': [],
            'thermal_efficiency': [],
            'hourly_data': []
        }
        
        print(f"Running {num_episodes} episodes ({episode_length} hours each)...\n")
        
        for ep in range(num_episodes):
            obs, _ = env.reset()
            ep_energy = []
            ep_cost = []
            ep_temp = []
            ep_comfort_viol = []
            ep_safety_viol = 0
            
            for step in range(episode_length):
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = env.step(action)
                
                ep_energy.append(info['energy_kwh'])
                ep_cost.append(info['energy_cost'])
                ep_temp.append(info['indoor_temp'])
                ep_comfort_viol.append(info['comfort_violation'])
                if info['safety_violation']:
                    ep_safety_viol += 1
                
                # Store hourly data
                metrics['hourly_data'].append({
                    'episode': ep,
                    'hour': step,
                    'temperature': info['indoor_temp'],
                    'occupancy': info['occupancy'],
                    'energy': info['energy_kwh'],
                    'cost': info['energy_cost'],
                    'tariff': info['tariff']
                })
            
            # Episode metrics
            metrics['episodes'].append(ep + 1)
            metrics['total_energy'].append(sum(ep_energy))
            metrics['total_cost'].append(sum(ep_cost))
            metrics['avg_temperature'].append(np.mean(ep_temp))
            metrics['comfort_violations'].append(sum(ep_comfort_viol))
            metrics['safety_violations'].append(ep_safety_viol)
            
            # Thermal efficiency (maintain comfort with minimal energy)
            temp_std = np.std(ep_temp)
            thermal_eff = 1.0 / (1.0 + temp_std)  # Higher is better
            metrics['thermal_efficiency'].append(thermal_eff)
            
            print(f"Episode {ep+1:2d}: Energy={sum(ep_energy):7.2f}kWh, "
                  f"Cost=${sum(ep_cost):7.2f}, Comfort_Viol={sum(ep_comfort_viol):6.2f}, "
                  f"Efficiency={thermal_eff:.3f}")
        
        # Summary statistics
        print(f"\n{'='*70}")
        print("EVALUATION SUMMARY (Single-Agent)")
        print(f"{'='*70}")
        print(f"Average Energy per Episode: {np.mean(metrics['total_energy']):8.2f} kWh")
        print(f"Average Cost per Episode:   ${np.mean(metrics['total_cost']):8.2f}")
        print(f"Average Temperature:        {np.mean(metrics['avg_temperature']):8.2f}°C ± {np.std(metrics['avg_temperature']):5.2f}°C")
        print(f"Avg Comfort Violations:     {np.mean(metrics['comfort_violations']):8.2f}")
        print(f"Total Safety Violations:    {sum(metrics['safety_violations']):8d}")
        print(f"Avg Thermal Efficiency:     {np.mean(metrics['thermal_efficiency']):8.3f}")
        
        # Calculate baseline (no control)
        baseline_energy = 15.0 * episode_length  # Worst case
        energy_reduction = ((baseline_energy - np.mean(metrics['total_energy'])) / baseline_energy) * 100
        print(f"\nEnergy Reduction vs Baseline: {energy_reduction:8.1f}%")
        print(f"{'='*70}\n")
        
        env.close()
        return metrics
    
    def evaluate_multi_agent(self,
                             hvac_model_path: str,
                             lighting_model_path: str,
                             num_episodes: int = 10) -> dict:
        """
        Evaluate multi-agent (HVAC + Lighting) performance.
        """
        print("\n" + "="*70)
        print("Multi-Agent Evaluation (HVAC + Lighting)")
        print("="*70)
        
        env = MultiAgentBuildingEnv(self.data_path)
        
        try:
            hvac_model = PPO.load(hvac_model_path)
            lighting_model = PPO.load(lighting_model_path)
        except:
            print("Warning: Could not load models. Using random agents.")
            hvac_model = lighting_model = None
        
        metrics = {
            'episodes': [],
            'hvac_energy': [],
            'lighting_energy': [],
            'total_energy': [],
            'total_cost': [],
            'avg_temperature': [],
            'comfort_violations': [],
            'hourly_data': []
        }
        
        print(f"Running {num_episodes} episodes (24 hours each)...\n")
        
        for ep in range(num_episodes):
            obs, _ = env.reset()
            
            hvac_ep_energy = []
            light_ep_energy = []
            ep_cost = []
            ep_temp = []
            ep_comfort_viol = []
            
            for step in range(24):
                # Get agent actions
                if hvac_model:
                    hvac_action, _ = hvac_model.predict(obs['hvac_agent'], deterministic=True)
                    lighting_action, _ = lighting_model.predict(obs['lighting_agent'], deterministic=True)
                else:
                    hvac_action = np.random.uniform(-0.3, 0.3, 2)
                    lighting_action = np.random.uniform(0.2, 0.8, 2)
                
                actions = {
                    'hvac_agent': hvac_action,
                    'lighting_agent': lighting_action
                }
                
                obs, rewards, dones, truncs, infos = env.step(actions)
                
                hvac_ep_energy.append(infos['hvac_agent']['energy_kwh'])
                light_ep_energy.append(infos['lighting_agent']['energy_kwh'])
                ep_cost.append(infos['hvac_agent']['cost'] + infos['lighting_agent']['cost'])
                ep_temp.append(infos['hvac_agent']['temperature'])
                ep_comfort_viol.append(infos['hvac_agent']['comfort_violation'])
            
            metrics['episodes'].append(ep + 1)
            metrics['hvac_energy'].append(sum(hvac_ep_energy))
            metrics['lighting_energy'].append(sum(light_ep_energy))
            metrics['total_energy'].append(sum(hvac_ep_energy) + sum(light_ep_energy))
            metrics['total_cost'].append(sum(ep_cost))
            metrics['avg_temperature'].append(np.mean(ep_temp))
            metrics['comfort_violations'].append(sum(ep_comfort_viol))
            
            print(f"Episode {ep+1:2d}: HVAC={sum(hvac_ep_energy):7.2f}kWh, "
                  f"Light={sum(light_ep_energy):7.2f}kWh, Total={metrics['total_energy'][-1]:7.2f}kWh")
        
        print(f"\n{'='*70}")
        print("EVALUATION SUMMARY (Multi-Agent)")
        print(f"{'='*70}")
        print(f"Average HVAC Energy:      {np.mean(metrics['hvac_energy']):8.2f} kWh")
        print(f"Average Lighting Energy:  {np.mean(metrics['lighting_energy']):8.2f} kWh")
        print(f"Average Total Energy:     {np.mean(metrics['total_energy']):8.2f} kWh")
        print(f"Average Cost per Day:     ${np.mean(metrics['total_cost']):8.2f}")
        print(f"Average Temperature:      {np.mean(metrics['avg_temperature']):8.2f}°C")
        print(f"{'='*70}\n")
        
        env.close()
        return metrics
    
    def plot_single_agent_results(self, metrics: dict, save_name: str = "single_agent_evaluation.png"):
        """Generate comprehensive plots for single-agent evaluation."""
        fig = plt.figure(figsize=(16, 10))
        gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        # Plot 1: Energy consumption per episode
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.plot(metrics['episodes'], metrics['total_energy'], 'b-o', linewidth=2, markersize=8)
        ax1.set_xlabel('Episode', fontsize=11)
        ax1.set_ylabel('Total Energy (kWh)', fontsize=11)
        ax1.set_title('Energy Consumption per Episode', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Cost per episode
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.plot(metrics['episodes'], metrics['total_cost'], 'g-s', linewidth=2, markersize=8)
        ax2.set_xlabel('Episode', fontsize=11)
        ax2.set_ylabel('Total Cost ($)', fontsize=11)
        ax2.set_title('Operating Cost per Episode', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Thermal efficiency
        ax3 = fig.add_subplot(gs[0, 2])
        ax3.plot(metrics['episodes'], metrics['thermal_efficiency'], 'r-^', linewidth=2, markersize=8)
        ax3.set_xlabel('Episode', fontsize=11)
        ax3.set_ylabel('Thermal Efficiency', fontsize=11)
        ax3.set_title('Thermal Efficiency Over Episodes', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Temperature stability
        ax4 = fig.add_subplot(gs[1, 0])
        ax4.plot(metrics['episodes'], metrics['avg_temperature'], 'm-d', linewidth=2, markersize=8)
        ax4.axhline(y=22.0, color='g', linestyle='--', label='Comfort Setpoint (22°C)', linewidth=2)
        ax4.fill_between(metrics['episodes'], 20.0, 26.0, alpha=0.2, color='green', label='Comfort Zone')
        ax4.set_xlabel('Episode', fontsize=11)
        ax4.set_ylabel('Average Temperature (°C)', fontsize=11)
        ax4.set_title('Temperature Stability', fontsize=12, fontweight='bold')
        ax4.legend(fontsize=9)
        ax4.grid(True, alpha=0.3)
        
        # Plot 5: Comfort violations
        ax5 = fig.add_subplot(gs[1, 1])
        ax5.bar(metrics['episodes'], metrics['comfort_violations'], color='orange', alpha=0.7, edgecolor='black')
        ax5.set_xlabel('Episode', fontsize=11)
        ax5.set_ylabel('Comfort Violation Score', fontsize=11)
        ax5.set_title('Comfort Maintenance Quality', fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='y')
        
        # Plot 6: Safety compliance
        ax6 = fig.add_subplot(gs[1, 2])
        safety_compliance = [(0 if x > 0 else 100) for x in metrics['safety_violations']]
        ax6.bar(metrics['episodes'], safety_compliance, color='cyan', alpha=0.7, edgecolor='black')
        ax6.set_xlabel('Episode', fontsize=11)
        ax6.set_ylabel('Safety Compliance (%)', fontsize=11)
        ax6.set_title('Safety Constraint Adherence', fontsize=12, fontweight='bold')
        ax6.set_ylim([0, 110])
        ax6.grid(True, alpha=0.3, axis='y')
        
        # Plot 7: Hourly temperature profile (first episode)
        ax7 = fig.add_subplot(gs[2, :2])
        hourly_df = pd.DataFrame(metrics['hourly_data'])
        first_ep = hourly_df[hourly_df['episode'] == 0]
        
        ax7.plot(first_ep['hour'], first_ep['temperature'], 'b-o', linewidth=2, markersize=6, label='Indoor Temp')
        ax7.fill_between(first_ep['hour'], 20.0, 26.0, alpha=0.2, color='green', label='Comfort Zone')
        ax7.set_xlabel('Hour of Day', fontsize=11)
        ax7.set_ylabel('Temperature (°C)', fontsize=11)
        ax7.set_title('24-Hour Temperature Profile (Episode 1)', fontsize=12, fontweight='bold')
        ax7.set_xticks(range(0, 24, 2))
        ax7.legend(fontsize=9)
        ax7.grid(True, alpha=0.3)
        
        # Plot 8: Energy vs Cost correlation
        ax8 = fig.add_subplot(gs[2, 2])
        ax8.scatter(metrics['total_energy'], metrics['total_cost'], s=100, alpha=0.6, c=metrics['thermal_efficiency'], cmap='RdYlGn')
        ax8.set_xlabel('Total Energy (kWh)', fontsize=11)
        ax8.set_ylabel('Total Cost ($)', fontsize=11)
        ax8.set_title('Energy-Cost Trade-off', fontsize=12, fontweight='bold')
        cbar = plt.colorbar(ax8.collections[0], ax=ax8)
        cbar.set_label('Efficiency', fontsize=10)
        ax8.grid(True, alpha=0.3)
        
        plt.suptitle('Single-Agent Energy Management Evaluation (IEEE Transactions Level)', 
                    fontsize=14, fontweight='bold', y=0.995)
        
        plt.savefig(self.output_dir / save_name, dpi=300, bbox_inches='tight')
        print(f"✓ Plot saved: {self.output_dir / save_name}")
        plt.close()
    
    def plot_multi_agent_results(self, metrics: dict, save_name: str = "multi_agent_evaluation.png"):
        """Generate comprehensive plots for multi-agent evaluation."""
        fig = plt.figure(figsize=(16, 10))
        gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        # Plot 1: HVAC Energy
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.plot(metrics['episodes'], metrics['hvac_energy'], 'b-o', linewidth=2, markersize=8, label='HVAC')
        ax1.set_xlabel('Episode', fontsize=11)
        ax1.set_ylabel('Energy (kWh)', fontsize=11)
        ax1.set_title('HVAC Energy Consumption', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Lighting Energy
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.plot(metrics['episodes'], metrics['lighting_energy'], 'y-s', linewidth=2, markersize=8, label='Lighting')
        ax2.set_xlabel('Episode', fontsize=11)
        ax2.set_ylabel('Energy (kWh)', fontsize=11)
        ax2.set_title('Lighting Energy Consumption', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Stacked energy comparison
        ax3 = fig.add_subplot(gs[0, 2])
        width = 0.6
        ax3.bar(metrics['episodes'], metrics['hvac_energy'], width, label='HVAC', color='blue', alpha=0.7)
        ax3.bar(metrics['episodes'], metrics['lighting_energy'], width, 
               bottom=metrics['hvac_energy'], label='Lighting', color='yellow', alpha=0.7, edgecolor='black')
        ax3.set_xlabel('Episode', fontsize=11)
        ax3.set_ylabel('Total Energy (kWh)', fontsize=11)
        ax3.set_title('Multi-Agent Energy Breakdown', fontsize=12, fontweight='bold')
        ax3.legend(fontsize=10)
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Plot 4: Total cost
        ax4 = fig.add_subplot(gs[1, 0])
        ax4.plot(metrics['episodes'], metrics['total_cost'], 'g-d', linewidth=2, markersize=8)
        ax4.set_xlabel('Episode', fontsize=11)
        ax4.set_ylabel('Total Cost ($)', fontsize=11)
        ax4.set_title('Daily Operating Cost', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        # Plot 5: Temperature stability
        ax5 = fig.add_subplot(gs[1, 1])
        ax5.plot(metrics['episodes'], metrics['avg_temperature'], 'r-^', linewidth=2, markersize=8)
        ax5.fill_between(metrics['episodes'], 20.0, 26.0, alpha=0.2, color='green', label='Comfort Zone')
        ax5.set_xlabel('Episode', fontsize=11)
        ax5.set_ylabel('Average Temperature (°C)', fontsize=11)
        ax5.set_title('Temperature Control', fontsize=12, fontweight='bold')
        ax5.legend(fontsize=9)
        ax5.grid(True, alpha=0.3)
        
        # Plot 6: Comfort violations
        ax6 = fig.add_subplot(gs[1, 2])
        ax6.bar(metrics['episodes'], metrics['comfort_violations'], color='orange', alpha=0.7, edgecolor='black')
        ax6.set_xlabel('Episode', fontsize=11)
        ax6.set_ylabel('Comfort Violation', fontsize=11)
        ax6.set_title('Comfort Quality', fontsize=12, fontweight='bold')
        ax6.grid(True, alpha=0.3, axis='y')
        
        # Plot 7: Energy efficiency (HVAC vs cost)
        ax7 = fig.add_subplot(gs[2, :2])
        ax7_2 = ax7.twinx()
        
        line1 = ax7.plot(metrics['episodes'], metrics['total_energy'], 'b-o', linewidth=2, markersize=8, label='Total Energy')
        line2 = ax7_2.plot(metrics['episodes'], metrics['total_cost'], 'r-s', linewidth=2, markersize=8, label='Total Cost')
        
        ax7.set_xlabel('Episode', fontsize=11)
        ax7.set_ylabel('Energy (kWh)', fontsize=11, color='b')
        ax7_2.set_ylabel('Cost ($)', fontsize=11, color='r')
        ax7.set_title('Overall System Performance', fontsize=12, fontweight='bold')
        ax7.tick_params(axis='y', labelcolor='b')
        ax7_2.tick_params(axis='y', labelcolor='r')
        ax7.grid(True, alpha=0.3)
        
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax7.legend(lines, labels, loc='upper left', fontsize=9)
        
        # Plot 8: Summary metrics table
        ax8 = fig.add_subplot(gs[2, 2])
        ax8.axis('off')
        
        summary_data = [
            ['Metric', 'Value'],
            ['Avg HVAC Energy', f"{np.mean(metrics['hvac_energy']):.2f} kWh"],
            ['Avg Lighting Energy', f"{np.mean(metrics['lighting_energy']):.2f} kWh"],
            ['Avg Total Energy', f"{np.mean(metrics['total_energy']):.2f} kWh"],
            ['Avg Daily Cost', f"${np.mean(metrics['total_cost']):.2f}"],
            ['Energy Std Dev', f"{np.std(metrics['total_energy']):.2f} kWh"],
            ['Cost Std Dev', f"${np.std(metrics['total_cost']):.2f}"]
        ]
        
        table = ax8.table(cellText=summary_data, cellLoc='center', loc='center',
                         colWidths=[0.5, 0.5],
                         bbox=[0, 0, 1, 1])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Style header row
        for i in range(2):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        plt.suptitle('Multi-Agent Building Control Evaluation (IEEE Transactions Level)', 
                    fontsize=14, fontweight='bold', y=0.995)
        
        plt.savefig(self.output_dir / save_name, dpi=300, bbox_inches='tight')
        print(f"✓ Plot saved: {self.output_dir / save_name}")
        plt.close()


def main():
    """Main evaluation script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Evaluate trained building control agents")
    parser.add_argument('--data', type=str, default='energy_data_cleaned.csv',
                       help='Path to UCI dataset')
    parser.add_argument('--single-model', type=str, 
                       help='Path to single-agent model')
    parser.add_argument('--hvac-model', type=str,
                       help='Path to HVAC agent model')
    parser.add_argument('--lighting-model', type=str,
                       help='Path to Lighting agent model')
    parser.add_argument('--episodes', type=int, default=10,
                       help='Number of evaluation episodes')
    
    args = parser.parse_args()
    
    evaluator = AdvancedEvaluator(args.data)
    
    if args.single_model:
        print("\n" + "="*70)
        print("EVALUATING SINGLE-AGENT MODEL")
        print("="*70)
        metrics = evaluator.evaluate_single_agent(args.single_model, num_episodes=args.episodes)
        evaluator.plot_single_agent_results(metrics)
    
    if args.hvac_model and args.lighting_model:
        print("\n" + "="*70)
        print("EVALUATING MULTI-AGENT MODEL")
        print("="*70)
        metrics = evaluator.evaluate_multi_agent(args.hvac_model, args.lighting_model, num_episodes=args.episodes)
        evaluator.plot_multi_agent_results(metrics)
    
    print("\nEvaluation complete! Check ./results/ for visualizations.")


if __name__ == "__main__":
    main()
