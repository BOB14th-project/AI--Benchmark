import requests
import json
import time
import re
from typing import Dict, Any
from .base_client import BaseLLMClient

class OllamaClient(BaseLLMClient):
    def __init__(self, api_key: str = "not_required", model: str = "llama3:8b", base_url: str = "http://localhost:11434"):
        super().__init__(api_key, model, base_url)

    def _clean_response_content(self, content: str) -> str:
        """Clean response content by removing think tags and other unwanted patterns"""
        if not content:
            return content

        # Remove <think>...</think> tags and their content for Qwen3
        if 'qwen3' in self.model:
            # Remove complete think tags with their content
            content = re.sub(r'<think>.*?</think>\s*', '', content, flags=re.DOTALL)

            # Handle unclosed think tags - remove everything from <think> to end if no closing tag
            if '<think>' in content and '</think>' not in content:
                content = re.sub(r'<think>.*', '', content, flags=re.DOTALL)

            # For qwen3, also remove any remaining XML-like tags that might interfere
            content = re.sub(r'</?[a-zA-Z][^>]*>', '', content)

        # Clean up extra whitespace for all models
        content = re.sub(r'\n\s*\n', '\n', content)
        content = content.strip()

        return content

    def make_request(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        try:
            headers = {
                "Content-Type": "application/json"
            }

            # Special options for Qwen3
            options = {
                "num_predict": max_tokens,
                "temperature": 0.1,
                "stop": ["```", "---", "###"]
            }

            if 'qwen3' in self.model:
                # Increase max_tokens for Qwen3 due to think tags
                if max_tokens < 1500:
                    max_tokens = max_tokens * 2  # Double the tokens for qwen3
                options["num_predict"] = max_tokens

                options.update({
                    "num_ctx": 4096,  # Standard context for Qwen3
                    "repeat_penalty": 1.1,  # Standard penalty
                    "top_k": 40,     # Balanced sampling
                    "top_p": 0.9,    # Balanced creativity
                    "temperature": 0.1,  # Low temperature for consistency
                    "seed": 42  # Add seed for consistency
                })

            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": options
            }

            # Different timeout for different models - Qwen3 standard timeout
            timeout = 120 if 'qwen3' in self.model else 60
            response = requests.post(
                f"{self.base_url}/api/generate",
                headers=headers,
                json=data,
                timeout=timeout
            )

            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

            response_json = response.json()
            content = response_json.get('response', '')

            # Debug logging for qwen3
            if 'qwen3' in self.model:
                print(f"    🔧 Debug qwen3 raw response: {content[:200]}...")

            cleaned_content = self._clean_response_content(content)

            if 'qwen3' in self.model:
                print(f"    🔧 Debug qwen3 cleaned response: {cleaned_content[:200]}...")

            content = cleaned_content

            # Qwen3 sometimes returns empty responses - retry once
            if not content and 'qwen3' in self.model:
                print(f"Warning: Empty response from {self.model}, retrying...")
                time.sleep(2)
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    headers=headers,
                    json=data,
                    timeout=timeout
                )
                if response.status_code == 200:
                    response_json = response.json()
                    content = response_json.get('response', '')

                    # Debug logging for qwen3 retry
                    print(f"    🔧 Debug qwen3 retry raw response: {content[:200]}...")

                    cleaned_content = self._clean_response_content(content)
                    print(f"    🔧 Debug qwen3 retry cleaned response: {cleaned_content[:200]}...")

                    content = cleaned_content

                # If still empty after retry, raise an error
                if not content:
                    raise Exception(f"Empty response from {self.model} after retry")

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
            import traceback
            error_details = traceback.format_exc()
            print(f"Ollama Error Details for {self.model}: {error_details}")
            raise Exception(f"Ollama API Error for {self.model}: {str(e)}")

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