import openai
from typing import Dict, Any
from .base_client import BaseLLMClient

class OpenAIClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = "gpt-4", base_url: str = "https://api.openai.com/v1"):
        super().__init__(api_key, model, base_url)
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )

    def make_request(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.1
            )

            content = response.choices[0].message.content
            return {
                'content': content,
                'usage': response.usage.dict() if response.usage else {},
                'model': response.model
            }
        except Exception as e:
            raise Exception(f"OpenAI API Error: {str(e)}")