import requests
import json
from typing import Dict, Any
from .base_client import BaseLLMClient

class LocalAIClient(BaseLLMClient):
    """
    로컬 AI 서버용 클라이언트

    OpenAI 호환 API 또는 커스텀 API를 지원합니다.
    사용하는 로컬 서버의 API 스펙에 맞게 수정하세요.
    """

    def __init__(self, api_key: str = "not_required", model: str = "custom-model", base_url: str = "http://localhost:8000"):
        super().__init__(api_key, model, base_url)

        # API 타입 자동 감지 (OpenAI 호환 vs 커스텀)
        self.api_type = self._detect_api_type()

    def _detect_api_type(self) -> str:
        """
        API 타입을 자동으로 감지합니다.

        Returns:
            'openai': OpenAI 호환 API
            'custom': 커스텀 API
        """
        # base_url에 '/v1'이 포함되어 있으면 OpenAI 호환으로 간주
        if '/v1' in self.base_url:
            return 'openai'

        # /v1/models 엔드포인트가 있는지 확인
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=2)
            if response.status_code == 200:
                return 'openai'
        except:
            pass

        return 'custom'

    def make_request(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        로컬 AI 서버에 요청을 보내고 응답을 반환합니다.
        """
        if self.api_type == 'openai':
            return self._make_openai_compatible_request(prompt, max_tokens)
        else:
            return self._make_custom_request(prompt, max_tokens)

    def _make_openai_compatible_request(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        OpenAI 호환 API 요청
        vLLM, TGI, LocalAI, LM Studio 등에서 사용
        """
        try:
            headers = {
                "Content-Type": "application/json"
            }

            if self.api_key and self.api_key != "not_required":
                headers["Authorization"] = f"Bearer {self.api_key}"

            # OpenAI API 형식
            data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.1
            }

            # 엔드포인트 결정
            if '/v1' in self.base_url:
                endpoint = f"{self.base_url}/chat/completions"
            else:
                endpoint = f"{self.base_url}/v1/chat/completions"

            response = requests.post(
                endpoint,
                headers=headers,
                json=data,
                timeout=120
            )

            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

            response_json = response.json()

            # OpenAI 형식 응답 파싱
            content = response_json['choices'][0]['message']['content']

            # 토큰 사용량
            usage = response_json.get('usage', {})
            if not usage:
                # 사용량 정보가 없으면 추정
                prompt_tokens = len(prompt.split()) * 1.3
                completion_tokens = len(content.split()) * 1.3
                total_tokens = int(prompt_tokens + completion_tokens)
                usage = {
                    'prompt_tokens': int(prompt_tokens),
                    'completion_tokens': int(completion_tokens),
                    'total_tokens': total_tokens
                }

            return {
                'content': content,
                'usage': usage,
                'model': self.model
            }

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Local AI (OpenAI-compatible) Error: {error_details}")
            raise Exception(f"Local AI API Error: {str(e)}")

    def _make_custom_request(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        커스텀 API 요청

        이 메서드를 로컬 AI 서버의 실제 API 스펙에 맞게 수정하세요.
        """
        try:
            headers = {
                "Content-Type": "application/json"
            }

            if self.api_key and self.api_key != "not_required":
                headers["Authorization"] = f"Bearer {self.api_key}"

            # ===== 여기를 로컬 서버 API에 맞게 수정하세요 =====

            # 예시 1: 간단한 생성 API
            data = {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": 0.1,
                "model": self.model
            }

            endpoint = f"{self.base_url}/generate"

            # 예시 2: RAG 통합 API (필요시 주석 해제)
            # data = {
            #     "query": prompt,
            #     "max_length": max_tokens,
            #     "temperature": 0.1,
            #     "model": self.model,
            #     "use_rag": True,  # RAG 활성화
            #     "top_k": 5  # RAG 검색 결과 수
            # }
            # endpoint = f"{self.base_url}/api/inference"

            # ===== 수정 끝 =====

            response = requests.post(
                endpoint,
                headers=headers,
                json=data,
                timeout=120
            )

            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

            response_json = response.json()

            # ===== 응답 파싱 (로컬 서버 응답 형식에 맞게 수정) =====

            # 예시 1: 직접 텍스트 반환
            content = response_json.get('generated_text', '')

            # 예시 2: 중첩된 구조
            # content = response_json.get('output', {}).get('text', '')

            # 예시 3: 배열 형식
            # content = response_json.get('results', [{}])[0].get('text', '')

            # 예시 4: RAG 응답
            # content = response_json.get('answer', '')
            # rag_sources = response_json.get('sources', [])  # RAG 소스 정보

            # ===== 수정 끝 =====

            # 토큰 사용량 추정
            prompt_tokens = len(prompt.split()) * 1.3
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
            print(f"Local AI (Custom) Error: {error_details}")
            raise Exception(f"Local AI Custom API Error: {str(e)}")

    def is_available(self) -> bool:
        """로컬 AI 서버가 실행 중인지 확인"""
        try:
            # OpenAI 호환 API 체크
            if self.api_type == 'openai':
                if '/v1' in self.base_url:
                    response = requests.get(f"{self.base_url}/models", timeout=5)
                else:
                    response = requests.get(f"{self.base_url}/v1/models", timeout=5)
                return response.status_code == 200

            # 커스텀 API 체크
            # ===== 헬스 체크 엔드포인트를 로컬 서버에 맞게 수정 =====
            else:
                # 예시 1: /health 엔드포인트
                response = requests.get(f"{self.base_url}/health", timeout=5)

                # 예시 2: /status 엔드포인트
                # response = requests.get(f"{self.base_url}/status", timeout=5)

                # 예시 3: 루트 엔드포인트
                # response = requests.get(f"{self.base_url}/", timeout=5)

                return response.status_code == 200
            # ===== 수정 끝 =====

        except Exception as e:
            print(f"Availability check failed: {e}")
            return False

    def list_available_models(self) -> list:
        """사용 가능한 모델 목록 반환 (OpenAI 호환 API만)"""
        if self.api_type != 'openai':
            return [self.model]  # 커스텀 API는 설정된 모델만 반환

        try:
            if '/v1' in self.base_url:
                response = requests.get(f"{self.base_url}/models", timeout=5)
            else:
                response = requests.get(f"{self.base_url}/v1/models", timeout=5)

            if response.status_code == 200:
                models_data = response.json()

                # OpenAI 형식
                if 'data' in models_data:
                    return [m['id'] for m in models_data['data']]

                # 다른 형식
                elif 'models' in models_data:
                    return models_data['models']

            return [self.model]
        except:
            return [self.model]
