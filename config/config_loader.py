import yaml
import os
from typing import Dict, Any

class ConfigLoader:
    def __init__(self, config_path: str = "config/config.yaml"):
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

    def get_llm_config(self, provider: str) -> Dict[str, Any]:
        return self.config.get("llm_providers", {}).get(provider, {})

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