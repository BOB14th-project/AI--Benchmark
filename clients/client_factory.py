from typing import Dict, Any
from .base_client import BaseLLMClient
from .openai_client import OpenAIClient
from .google_client import GoogleClient
from .anthropic_client import AnthropicClient
from .xai_client import XAIClient

class ClientFactory:
    _clients = {
        'openai': OpenAIClient,
        'google': GoogleClient,
        'anthropic': AnthropicClient,
        'xai': XAIClient
    }

    @classmethod
    def create_client(cls, provider: str, config: Dict[str, Any]) -> BaseLLMClient:
        if provider not in cls._clients:
            raise ValueError(f"Unsupported provider: {provider}. Supported providers: {list(cls._clients.keys())}")

        client_class = cls._clients[provider]
        return client_class(
            api_key=config['api_key'],
            model=config['model'],
            base_url=config.get('base_url', '')
        )

    @classmethod
    def get_supported_providers(cls) -> list:
        return list(cls._clients.keys())