"""
Configuration settings and management
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

@dataclass
class ClassificationConfig:
    """Configuration for feedback classification"""
    confidence_threshold: float = 0.7
    bug_severity_threshold: float = 0.8
    feature_priority_threshold: float = 0.6
    enable_ml_classification: bool = True
    enable_rule_based_fallback: bool = True

@dataclass
class AgentConfig:
    """Configuration for individual agents"""
    csv_reader_timeout: int = 300
    classifier_model: str = "gpt-3.5-turbo"
    bug_analyzer_confidence: float = 0.5
    feature_extractor_impact: float = 0.5
    ticket_creator_auto_approve: bool = False
    quality_critic_min_score: float = 0.7

@dataclass
class SystemConfig:
    """Main system configuration"""
    data_dir: str = "data"
    output_dir: str = "data"
    log_dir: str = "logs"
    models_dir: str = "models"
    max_batch_size: int = 10
    processing_timeout: int = 300
    enable_quality_check: bool = True
    enable_performance_monitoring: bool = True
    classification: ClassificationConfig = None
    agents: AgentConfig = None
    
    def __post_init__(self):
        if self.classification is None:
            self.classification = ClassificationConfig()
        if self.agents is None:
            self.agents = AgentConfig()

class ConfigManager:
    """Configuration management system"""
    
    def __init__(self, config_file: str = "config/settings.json"):
        """
        Initialize configuration manager
        
        Args:
            config_file (str): Path to configuration file
        """
        self.config_file = config_file
        self.config = SystemConfig()
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment"""
        # Load environment variables
        load_dotenv()
        
        # Load from file if exists
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Update config with loaded data
                self._update_config_from_dict(config_data)
                
            except Exception as e:
                print(f"Warning: Could not load config file {self.config_file}: {str(e)}")
                print("Using default configuration")
        
        # Override with environment variables
        self._override_from_env()
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]):
        """Update configuration from dictionary"""
        # Update main config
        for key, value in config_data.items():
            if hasattr(self.config, key):
                if key == 'classification' and isinstance(value, dict):
                    # Update classification config
                    for sub_key, sub_value in value.items():
                        if hasattr(self.config.classification, sub_key):
                            setattr(self.config.classification, sub_key, sub_value)
                elif key == 'agents' and isinstance(value, dict):
                    # Update agents config
                    for sub_key, sub_value in value.items():
                        if hasattr(self.config.agents, sub_key):
                            setattr(self.config.agents, sub_key, sub_value)
                else:
                    setattr(self.config, key, value)
    
    def _override_from_env(self):
        """Override configuration with environment variables"""
        env_mappings = {
            'DATA_DIR': ('data_dir', str),
            'OUTPUT_DIR': ('output_dir', str),
            'LOG_DIR': ('log_dir', str),
            'MODELS_DIR': ('models_dir', str),
            'MAX_BATCH_SIZE': ('max_batch_size', int),
            'PROCESSING_TIMEOUT': ('processing_timeout', int),
            'ENABLE_QUALITY_CHECK': ('enable_quality_check', bool),
            'CLASSIFICATION_CONFIDENCE_THRESHOLD': ('classification.confidence_threshold', float),
            'BUG_SEVERITY_THRESHOLD': ('classification.bug_severity_threshold', float),
            'FEATURE_PRIORITY_THRESHOLD': ('classification.feature_priority_threshold', float),
            'ENABLE_ML_CLASSIFICATION': ('classification.enable_ml_classification', bool),
            'ENABLE_RULE_BASED_FALLBACK': ('classification.enable_rule_based_fallback', bool),
            'CLASSIFIER_MODEL': ('agents.classifier_model', str),
            'TICKET_CREATOR_AUTO_APPROVE': ('agents.ticket_creator_auto_approve', bool),
            'QUALITY_CRITIC_MIN_SCORE': ('agents.quality_critic_min_score', float)
        }
        
        for env_var, (config_path, value_type) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                try:
                    # Parse the value
                    if value_type == bool:
                        parsed_value = env_value.lower() in ('true', '1', 'yes', 'on')
                    elif value_type == int:
                        parsed_value = int(env_value)
                    elif value_type == float:
                        parsed_value = float(env_value)
                    else:
                        parsed_value = env_value
                    
                    # Set the value
                    if '.' in config_path:
                        # Nested attribute
                        obj_name, attr_name = config_path.split('.')
                        obj = getattr(self.config, obj_name)
                        setattr(obj, attr_name, parsed_value)
                    else:
                        # Direct attribute
                        setattr(self.config, config_path, parsed_value)
                        
                except (ValueError, AttributeError) as e:
                    print(f"Warning: Invalid environment variable {env_var}={env_value}: {str(e)}")
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # Convert config to dictionary
            config_dict = asdict(self.config)
            
            # Save to file
            with open(self.config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            print(f"Configuration saved to {self.config_file}")
            
        except Exception as e:
            print(f"Error saving configuration: {str(e)}")
    
    def get_config(self) -> SystemConfig:
        """Get current configuration"""
        return self.config
    
    def update_config(self, updates: Dict[str, Any]):
        """Update configuration with new values"""
        self._update_config_from_dict(updates)
    
    def reset_to_defaults(self):
        """Reset configuration to default values"""
        self.config = SystemConfig()
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return validation results"""
        issues = []
        warnings = []
        
        # Check directories
        directories = [
            (self.config.data_dir, "data_dir"),
            (self.config.output_dir, "output_dir"),
            (self.config.log_dir, "log_dir"),
            (self.config.models_dir, "models_dir")
        ]
        
        for dir_path, dir_name in directories:
            if not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    warnings.append(f"Created missing directory: {dir_name} ({dir_path})")
                except Exception:
                    issues.append(f"Cannot create directory: {dir_name} ({dir_path})")
        
        # Check thresholds
        thresholds = [
            (self.config.classification.confidence_threshold, "classification.confidence_threshold"),
            (self.config.classification.bug_severity_threshold, "classification.bug_severity_threshold"),
            (self.config.classification.feature_priority_threshold, "classification.feature_priority_threshold"),
            (self.config.agents.quality_critic_min_score, "agents.quality_critic_min_score")
        ]
        
        for threshold, name in thresholds:
            if not 0.0 <= threshold <= 1.0:
                issues.append(f"Invalid threshold {name}: {threshold}. Must be between 0.0 and 1.0")
        
        # Check numeric values
        numeric_checks = [
            (self.config.max_batch_size, "max_batch_size", 1, 1000),
            (self.config.processing_timeout, "processing_timeout", 10, 3600),
            (self.config.agents.csv_reader_timeout, "agents.csv_reader_timeout", 10, 3600)
        ]
        
        for value, name, min_val, max_val in numeric_checks:
            if not isinstance(value, int) or not min_val <= value <= max_val:
                issues.append(f"Invalid {name}: {value}. Must be integer between {min_val} and {max_val}")
        
        # Check environment variables
        required_env_vars = ['OPENAI_API_KEY']
        missing_env_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_env_vars:
            issues.append(f"Missing required environment variables: {missing_env_vars}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }

# Global configuration manager instance
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Get or create the global configuration manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def get_config() -> SystemConfig:
    """Get current system configuration"""
    return get_config_manager().get_config()
