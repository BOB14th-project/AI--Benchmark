import google.generativeai as genai
from typing import Dict, Any
from .base_client import BaseLLMClient

class GoogleClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = "gemini-pro", base_url: str = ""):
        super().__init__(api_key, model, base_url)
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)

    def make_request(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        try:
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.1
            )

            response = self.client.generate_content(
                prompt,
                generation_config=generation_config
            )

            content = response.text

            return {
                'content': content,
                'usage': {
                    'prompt_tokens': response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
                    'completion_tokens': response.usage_metadata.candidates_token_count if response.usage_metadata else 0,
                    'total_tokens': response.usage_metadata.total_token_count if response.usage_metadata else 0
                },
                'model': self.model
            }
        except Exception as e:
            raise Exception(f"Google API Error: {str(e)}")