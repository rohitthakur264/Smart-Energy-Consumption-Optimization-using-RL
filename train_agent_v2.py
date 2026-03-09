"""
Advanced Multi-Agent RL Training Pipeline
Trains HVAC + Lighting agents with state-of-the-art techniques.
Supports both single-agent (enhanced) and multi-agent variants.
"""
import gymnasium as gym
from stable_baselines3 import PPO, A2C
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.env_util import make_vec_env
import os
import sys
import argparse
import json
from datetime import datetime
import torch

# Import custom environments
from enhanced_env import EnhancedEnergyEnv
from multi_agent_env import MultiAgentBuildingEnv


class MultiAgentTrainer:
    """
    Trainer for multi-agent building control system.
    Trains cooperative HVAC and Lighting agents.
    """
    
    def __init__(self, 
                 data_path: str,
                 model_dir: str = "./models",
                 log_dir: str = "./logs",
                 agent_type: str = "ppo"):
        """
        Initialize multi-agent trainer.
        
        Args:
            data_path: Path to UCI dataset CSV
            model_dir: Directory to save trained models
            log_dir: Directory for tensorboard logs
            agent_type: "ppo" or "a2c"
        """
        self.data_path = data_path
        self.model_dir = model_dir
        self.log_dir = log_dir
        self.agent_type = agent_type
        
        # Create directories
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(log_dir, exist_ok=True)
        
        # Training hyperparameters
        self.config = {
            'learning_rate': 3e-4,
            'n_steps': 2048,
            'batch_size': 64,
            'n_epochs': 10,
            'gamma': 0.99,
            'gae_lambda': 0.95,
            'clip_range': 0.2,
            'ent_coef': 0.01,
            'agent_type': agent_type
        }
    
    def train_single_agent(self, 
                          num_timesteps: int = 100000,
                          num_envs: int = 4,
                          eval_freq: int = 10000):
        """
        Train single agent (enhanced environment).
        Demonstrates baselines for multi-agent comparison.
        """
        print("\n" + "="*70)
        print("Single-Agent Training (Enhanced Environment)")
        print("="*70)
        print(f"Timesteps: {num_timesteps}")
        print(f"Parallel environments: {num_envs}")
        print(f"Configuration: {json.dumps(self.config, indent=2)}\n")
        
        # Create vectorized environment
        env = make_vec_env(
            lambda: EnhancedEnergyEnv(self.data_path, use_real_data=True),
            n_envs=num_envs,
            vec_env_cls=SubprocVecEnv
        )
        
        # Log directory
        log_path = os.path.join(self.log_dir, 
                               f"single_agent_{self.agent_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # Create model
        if self.agent_type == "ppo":
            model = PPO(
                "MlpPolicy",
                env,
                learning_rate=self.config['learning_rate'],
                n_steps=self.config['n_steps'],
                batch_size=self.config['batch_size'],
                n_epochs=self.config['n_epochs'],
                gamma=self.config['gamma'],
                gae_lambda=self.config['gae_lambda'],
                clip_range=self.config['clip_range'],
                ent_coef=self.config['ent_coef'],
                verbose=1,
                tensorboard_log=log_path,
                policy_kwargs={'net_arch': [256, 256]}
            )
        else:
            model = A2C(
                "MlpPolicy",
                env,
                learning_rate=self.config['learning_rate'],
                gamma=self.config['gamma'],
                ent_coef=self.config['ent_coef'],
                verbose=1,
                tensorboard_log=log_path,
                policy_kwargs={'net_arch': [256, 256]}
            )
        
        # Callbacks
        checkpoint_callback = CheckpointCallback(
            save_freq=10000,
            save_path=os.path.join(self.model_dir, 'single_agent_checkpoints'),
            name_prefix='ppo_enhanced'
        )
        
        # Train
        print("Starting training...")
        model.learn(
            total_timesteps=num_timesteps,
            callback=checkpoint_callback,
            progress_bar=True
        )
        
        # Save final model
        model_path = os.path.join(self.model_dir, f'ppo_enhanced_{self.agent_type}_final')
        model.save(model_path)
        print(f"\n✓ Single-agent model saved: {model_path}")
        
        # Save config
        config_path = os.path.join(self.model_dir, 'single_agent_config.json')
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        env.close()
        return model
    
    def train_multi_agent(self, 
                         num_timesteps: int = 100000,
                         num_envs: int = 2):
        """
        Train multi-agent system (HVAC + Lighting).
        Uses independent learners with shared experience.
        """
        print("\n" + "="*70)
        print("Multi-Agent Training (HVAC + Lighting)")
        print("="*70)
        print(f"Timesteps: {num_timesteps}")
        print(f"Parallel environments: {num_envs}")
        print(f"Agents: HVAC Control + Lighting Control")
        print(f"Configuration: {json.dumps(self.config, indent=2)}\n")
        
        # For multi-agent, we train separate agents
        # Agent 1: HVAC Controller
        # Agent 2: Lighting Controller
        
        agents = {}
        
        for agent_name in ['hvac_agent', 'lighting_agent']:
            print(f"\nTraining {agent_name}...")
            
            # Create wrapper environment for single agent
            class SingleAgentWrapper(gym.Env):
                """Wraps multi-agent env to train single agent at a time."""
                
                def __init__(self, data_path, agent_name):
                    self.env = MultiAgentBuildingEnv(data_path, num_zones=2)
                    self.agent_name = agent_name
                    self.other_agent = 'lighting_agent' if agent_name == 'hvac_agent' else 'hvac_agent'
                    
                    # Map observation/action to single agent format
                    self.observation_space = self.env.observation_spaces[agent_name]
                    self.action_space = self.env.action_spaces[agent_name]
                
                def reset(self, seed=None, options=None):
                    obs, _ = self.env.reset(seed=seed, options=options)
                    return obs[self.agent_name], {}
                
                def step(self, action):
                    # Create dummy action for other agent (baseline behavior)
                    if self.agent_name == 'hvac_agent':
                        other_action = np.zeros(2)  # No heating/cooling baseline
                    else:
                        other_action = np.ones(2) * 0.5  # Half brightness baseline (not in training)
                    
                    actions = {self.agent_name: action, self.other_agent: other_action}
                    obs, rewards, terminateds, truncateds, infos = self.env.step(actions)
                    
                    return (obs[self.agent_name], 
                           rewards[self.agent_name],
                           terminateds[self.agent_name],
                           truncateds[self.agent_name],
                           infos[self.agent_name])
            
            # Create vectorized environment
            env = make_vec_env(
                lambda: SingleAgentWrapper(self.data_path, agent_name),
                n_envs=num_envs,
                vec_env_cls=SubprocVecEnv
            )
            
            # Log directory
            log_path = os.path.join(self.log_dir, 
                                   f"multi_agent_{agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # Create model
            model = PPO(
                "MlpPolicy",
                env,
                learning_rate=self.config['learning_rate'],
                n_steps=self.config['n_steps'],
                batch_size=self.config['batch_size'],
                n_epochs=self.config['n_epochs'],
                gamma=self.config['gamma'],
                verbose=1,
                tensorboard_log=log_path,
                policy_kwargs={'net_arch': [128, 128]}
            )
            
            # Train
            print(f"Training {agent_name} for {num_timesteps} timesteps...")
            model.learn(total_timesteps=num_timesteps, progress_bar=True)
            
            # Save model
            model_path = os.path.join(self.model_dir, f'ppo_multi_agent_{agent_name}')
            model.save(model_path)
            print(f"✓ {agent_name} model saved: {model_path}")
            
            agents[agent_name] = model
            env.close()
        
        # Save config
        config_path = os.path.join(self.model_dir, 'multi_agent_config.json')
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        print("\n✓ Multi-agent training complete!")
        return agents


def main():
    """Main training entrypoint."""
    parser = argparse.ArgumentParser(description="Train building energy RL agents")
    parser.add_argument('--data', type=str, default='energy_data_cleaned.csv',
                       help='Path to UCI energy dataset')
    parser.add_argument('--mode', type=str, default='enhanced',
                       choices=['enhanced', 'multi_agent', 'both'],
                       help='Training mode')
    parser.add_argument('--timesteps', type=int, default=100000,
                       help='Number of training timesteps')
    parser.add_argument('--envs', type=int, default=4,
                       help='Number of parallel environments')
    parser.add_argument('--agent-type', type=str, default='ppo',
                       choices=['ppo', 'a2c'],
                       help='RL algorithm')
    
    args = parser.parse_args()
    
    # Check data file exists
    if not os.path.exists(args.data):
        print(f"Error: Data file not found: {args.data}")
        print("Run: python preprocess.py")
        sys.exit(1)
    
    # Initialize trainer
    trainer = MultiAgentTrainer(
        data_path=args.data,
        agent_type=args.agent_type
    )
    
    # Train
    if args.mode in ['enhanced', 'both']:
        trainer.train_single_agent(
            num_timesteps=args.timesteps,
            num_envs=args.envs
        )
    
    if args.mode in ['multi_agent', 'both']:
        trainer.train_multi_agent(
            num_timesteps=args.timesteps,
            num_envs=max(2, args.envs // 2)
        )
    
    print("\n" + "="*70)
    print("Training Complete!")
    print("="*70)
    print(f"Models saved to: ./models/")
    print(f"TensorBoard logs: tensorboard --logdir ./logs/")


if __name__ == "__main__":
    import numpy as np
    main()
