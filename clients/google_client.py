import google.generativeai as genai
from typing import Dict, Any
from .base_client import BaseLLMClient

class GoogleClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str = "gemini-pro", base_url: str = ""):
        super().__init__(api_key, model, base_url)
        genai.configure(api_key=api_key)

        # Configure safety settings at model initialization for cryptographic analysis
        # Use HarmBlockThreshold enum for explicit setting
        self.safety_settings = {
            genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
            genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
        }

        # Add CIVIC_INTEGRITY if available (newer models)
        try:
            self.safety_settings[genai.types.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY] = genai.types.HarmBlockThreshold.BLOCK_NONE
        except AttributeError:
            pass  # Older API version doesn't have this category

        self.client = genai.GenerativeModel(
            model,
            safety_settings=self.safety_settings
        )

    def make_request(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        try:
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=0.1
            )

            # Safety settings are already configured in model initialization
            response = self.client.generate_content(
                prompt,
                generation_config=generation_config
            )

            # Check if response has valid parts before accessing text
            if not response.candidates:
                raise Exception("No candidates in response")

            candidate = response.candidates[0]

            # Check finish_reason: 1=STOP (normal), 2=SAFETY, 3=RECITATION, 4=OTHER
            if candidate.finish_reason == 2:
                raise Exception(f"Content blocked by safety filters: {candidate.safety_ratings}")
            elif candidate.finish_reason == 3:
                raise Exception("Content blocked due to recitation")
            elif candidate.finish_reason == 4:
                raise Exception("Content generation stopped for other reasons")

            # Check if parts exist
            if not candidate.content.parts:
                raise Exception(f"No content parts in response (finish_reason: {candidate.finish_reason})")

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