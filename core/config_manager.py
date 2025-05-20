import yaml
import os
import json
from typing import Dict, Any, Optional
import copy

class ConfigManager:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.default_config: Dict[str, Any] = {}
        self.environment_config: Dict[str, Any] = {}
        self.local_config: Dict[str, Any] = {}
        self.runtime_config: Dict[str, Any] = {}
        self.validators: Dict[str, callable] = {}
        
        # Ensure directory exists
        os.makedirs(config_dir, exist_ok=True)
        
        # Load configurations
        self._load_configs()
        
    def _load_configs(self):
        """Load all configuration files"""
        # Default config (always required)
        default_file = os.path.join(self.config_dir, "default.yaml")
        if os.path.exists(default_file):
            with open(default_file, 'r') as f:
                self.default_config = yaml.safe_load(f) or {}
        else:
            # Create a minimal default config
            self.default_config = {
                "system": {
                    "name": "Project-S",
                    "version": "0.1.0",
                    "log_level": "INFO"
                }
            }
            with open(default_file, 'w') as f:
                yaml.dump(self.default_config, f)
                
        # Environment config (optional)
        env = os.environ.get("PROJECT_S_ENV", "development")
        env_file = os.path.join(self.config_dir, f"{env}.yaml")
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                self.environment_config = yaml.safe_load(f) or {}
                
        # Local config (optional, not version controlled)
        local_file = os.path.join(self.config_dir, "local.yaml")
        if os.path.exists(local_file):
            with open(local_file, 'r') as f:
                self.local_config = yaml.safe_load(f) or {}
                
    def get_config(self) -> Dict[str, Any]:
        """Get the merged configuration"""
        # Start with default
        config = copy.deepcopy(self.default_config)
        
        # Override with environment
        self._deep_update(config, self.environment_config)
        
        # Override with local
        self._deep_update(config, self.local_config)
        
        # Override with runtime
        self._deep_update(config, self.runtime_config)
        
        return config
        
    def _deep_update(self, d: Dict[str, Any], u: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively update a dictionary"""
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._deep_update(d[k], v)
            else:
                d[k] = v
        return d
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key (supports dot notation)"""
        config = self.get_config()
        keys = key.split('.')
        
        for k in keys:
            if isinstance(config, dict) and k in config:
                config = config[k]
            else:
                return default
                
        return config
        
    def set_runtime(self, key: str, value: Any):
        """Set a runtime configuration value (not persisted)"""
        # Parse the key path
        keys = key.split('.')
        current = self.runtime_config
        
        # Navigate to the correct position
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
            
        # Set the value
        current[keys[-1]] = value
        
        # Validate if needed
        if key in self.validators:
            self.validators[key](value)
            
    def register_validator(self, key: str, validator: callable):
        """Register a validator function for a configuration key"""
        self.validators[key] = validator
        
    def save_local_config(self):
        """Save the local configuration to disk"""
        local_file = os.path.join(self.config_dir, "local.yaml")
        with open(local_file, 'w') as f:
            yaml.dump(self.local_config, f)
            
    def update_local(self, key: str, value: Any):
        """Update the local configuration"""
        # Parse the key path
        keys = key.split('.')
        current = self.local_config
        
        # Navigate to the correct position
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
            
        # Set the value
        current[keys[-1]] = value
        
        # Validate if needed
        if key in self.validators:
            self.validators[key](value)
            
        # Save to disk
        self.save_local_config()