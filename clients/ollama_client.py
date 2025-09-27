import requests
import json
from typing import Dict, Any
from .base_client import BaseLLMClient

class OllamaClient(BaseLLMClient):
    def __init__(self, api_key: str = "not_required", model: str = "llama3:8b", base_url: str = "http://localhost:11434"):
        super().__init__(api_key, model, base_url)

    def make_request(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        try:
            headers = {
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.1,
                    "stop": ["```", "---", "###"]
                }
            }

            response = requests.post(
                f"{self.base_url}/api/generate",
                headers=headers,
                json=data,
                timeout=60  # Ollama can be slower
            )

            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

            response_json = response.json()
            content = response_json.get('response', '')

            # Estimate token usage for Ollama (rough approximation)
            prompt_tokens = len(prompt.split()) * 1.3  # rough estimate
            completion_tokens = len(content.split()) * 1.3
            total_tokens = int(prompt_tokens + completion_tokens)

            return {
                'content': content,
                'usage': {
                    'prompt_tokens': int(prompt_tokens),
                    'completion_tokens': int(completion_tokens),
                    'total_tokens': total_tokens
                },
                'model': self.model
            }
        except Exception as e:
            raise Exception(f"Ollama API Error: {str(e)}")

    def is_available(self) -> bool:
        """Check if Ollama server is running and model is available"""
        try:
            # Check if server is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                return False

            # Check if specific model is available
            models = response.json().get('models', [])
            model_names = [m.get('name', '') for m in models]

            return self.model in model_names
        except:
            return False

    def list_available_models(self) -> list:
        """List all available models in Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [m.get('name', '') for m in models]
            return []
        except:
            return []