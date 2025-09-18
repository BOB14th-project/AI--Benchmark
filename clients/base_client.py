from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
import json

class BaseLLMClient(ABC):
    def __init__(self, api_key: str, model: str, base_url: str):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    @abstractmethod
    def make_request(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        pass

    def benchmark_request(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        start_time = time.time()

        try:
            response = self.make_request(prompt, max_tokens)
            end_time = time.time()

            response_time = end_time - start_time
            content = response.get('content', '')

            json_valid = self._is_valid_json(content)

            return {
                'success': True,
                'content': content,
                'response_time': response_time,
                'json_valid': json_valid,
                'error': None,
                'model': self.model
            }
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time

            return {
                'success': False,
                'content': '',
                'response_time': response_time,
                'json_valid': False,
                'error': str(e),
                'model': self.model
            }

    def _is_valid_json(self, content: str) -> bool:
        try:
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()

            json.loads(content)
            return True
        except (json.JSONDecodeError, AttributeError):
            return False