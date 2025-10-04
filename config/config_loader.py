import yaml
import os
from typing import Dict, Any
from dotenv import load_dotenv

class ConfigLoader:
    def __init__(self, config_path: str = "config/config.yaml"):
        # Load environment variables from .env file
        load_dotenv()

        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)

            config = self._substitute_env_vars(config)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")

    def _substitute_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(config, dict):
            for key, value in config.items():
                if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                    env_var = value[2:-1]
                    config[key] = os.getenv(env_var, value)
                elif isinstance(value, dict):
                    config[key] = self._substitute_env_vars(value)
        return config

    def get_llm_config(self, provider: str, model_name: str = None) -> Dict[str, Any]:
        """Get LLM configuration, resolving environment variable references

        Args:
            provider: Provider name (e.g., 'google', 'openai')
            model_name: Specific model name to use (optional)
        """
        provider_config = self.config.get("llm_providers", {}).get(provider, {})

        # Resolve environment variable references
        resolved_config = {}
        for key, value in provider_config.items():
            if key.endswith('_env'):
                # This is an environment variable reference
                env_var_name = value
                actual_key = key[:-4]  # Remove '_env' suffix
                env_value = os.getenv(env_var_name, f"MISSING_{env_var_name}")

                # Handle model list (comma-separated)
                if actual_key == 'model' and ',' in env_value:
                    if model_name:
                        # Use specific model if provided
                        resolved_config[actual_key] = model_name
                    else:
                        # Return list of models
                        resolved_config[actual_key] = [m.strip() for m in env_value.split(',')]
                        resolved_config['models'] = resolved_config[actual_key]
                else:
                    resolved_config[actual_key] = env_value
            else:
                resolved_config[key] = value

        return resolved_config

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        return self.config.get("agents", {}).get(agent_name, {})

    def get_benchmark_config(self) -> Dict[str, Any]:
        return self.config.get("benchmark", {})

    def get_paths_config(self) -> Dict[str, Any]:
        return self.config.get("paths", {})

    def get_all_llm_providers(self) -> list:
        return list(self.config.get("llm_providers", {}).keys())

    def get_all_agents(self) -> list:
        return list(self.config.get("agents", {}).keys())