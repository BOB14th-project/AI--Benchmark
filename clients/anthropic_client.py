import anthropic
from typing import Dict, Any
from .base_client import BaseLLMClient

class AnthropicClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229", base_url: str = ""):
        super().__init__(api_key, model, base_url)
        self.client = anthropic.Anthropic(api_key=api_key)

    def make_request(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.content[0].text

            return {
                'content': content,
                'usage': {
                    'prompt_tokens': response.usage.input_tokens,
                    'completion_tokens': response.usage.output_tokens,
                    'total_tokens': response.usage.input_tokens + response.usage.output_tokens
                },
                'model': response.model
            }
        except Exception as e:
            raise Exception(f"Anthropic API Error: {str(e)}")