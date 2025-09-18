import requests
import json
from typing import Dict, Any
from .base_client import BaseLLMClient

class XAIClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = "grok-beta", base_url: str = "https://api.x.ai/v1"):
        super().__init__(api_key, model, base_url)

    def make_request(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.1
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

            response_json = response.json()
            content = response_json['choices'][0]['message']['content']

            return {
                'content': content,
                'usage': response_json.get('usage', {}),
                'model': response_json.get('model', self.model)
            }
        except Exception as e:
            raise Exception(f"XAI API Error: {str(e)}")