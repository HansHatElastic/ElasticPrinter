"""Configuration loader for ElasticPrinter."""
import os
import yaml
from typing import Dict, Any


class ConfigLoader:
    """Load and manage configuration settings."""
    
    def __init__(self, config_path: str = None):
        """Initialize config loader.
        
        Args:
            config_path: Path to config file. If None, uses default location.
        """
        if config_path is None:
            # Look for config in multiple locations
            possible_paths = [
                os.path.expanduser("~/.elasticprinter/config.yaml"),
                "/etc/elasticprinter/config.yaml",
                os.path.join(os.path.dirname(__file__), "../../config/config.yaml"),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
            else:
                raise FileNotFoundError(
                    "Config file not found. Please create config.yaml from config.yaml.example"
                )
        
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key.
        
        Args:
            key: Configuration key in dot notation (e.g., 'elasticsearch.host')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    @property
    def elasticsearch(self) -> Dict[str, Any]:
        """Get Elasticsearch configuration."""
        return self.config.get('elasticsearch', {})
    
    @property
    def printer(self) -> Dict[str, Any]:
        """Get printer configuration."""
        return self.config.get('printer', {})
    
    @property
    def processing(self) -> Dict[str, Any]:
        """Get processing configuration."""
        return self.config.get('processing', {})
    
    @property
    def logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.config.get('logging', {})
