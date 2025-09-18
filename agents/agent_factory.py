from typing import Dict, Any
from .base_agent import BaseAnalysisAgent
from .source_code_agent import SourceCodeAgent
from .assembly_agent import AssemblyBinaryAgent
from .dynamic_analysis_agent import DynamicAnalysisAgent
from .logs_config_agent import LogsConfigAgent

class AgentFactory:
    _agents = {
        'source_code': SourceCodeAgent,
        'assembly_binary': AssemblyBinaryAgent,
        'dynamic_analysis': DynamicAnalysisAgent,
        'logs_config': LogsConfigAgent
    }

    @classmethod
    def create_agent(cls, agent_type: str, config: Dict[str, Any] = None) -> BaseAnalysisAgent:
        if agent_type not in cls._agents:
            raise ValueError(f"Unsupported agent type: {agent_type}. Supported types: {list(cls._agents.keys())}")

        agent_class = cls._agents[agent_type]

        if config and 'prompt_template' in config:
            return agent_class(prompt_template=config['prompt_template'])
        else:
            return agent_class()

    @classmethod
    def get_supported_agents(cls) -> list:
        return list(cls._agents.keys())

    @classmethod
    def get_agent_info(cls, agent_type: str) -> Dict[str, str]:
        if agent_type not in cls._agents:
            raise ValueError(f"Unsupported agent type: {agent_type}")

        agent = cls.create_agent(agent_type)
        return {
            'name': agent.name,
            'description': agent.description,
            'analysis_points': agent.get_analysis_points()
        }