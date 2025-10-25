"""
PQC Inspector AI-Server 클라이언트

RAG 강화 전문 에이전트 시스템을 활용한 파일 분석 클라이언트
"""

import requests
import json
import time
from typing import Dict, Any
from pathlib import Path
from .base_client import BaseLLMClient


class PQCInspectorClient(BaseLLMClient):
    """
    PQC Inspector AI-Server용 클라이언트

    에이전트별로 파일을 업로드하여 분석 결과를 받습니다.
    - SourceCodeAgent: 소스코드 분석
    - AssemblyBinaryAgent: 어셈블리/바이너리 분석
    - LogsConfigAgent: 로그/설정 파일 분석
    """

    def __init__(
        self,
        api_key: str = "not_required",
        model: str = "source_code",  # source_code, assembly_binary, logs_config
        base_url: str = "http://localhost:8000"
    ):
        super().__init__(api_key, model, base_url)

        # 에이전트 타입 매핑
        self.agent_type = model  # model 파라미터를 에이전트 타입으로 사용

        # 유효한 에이전트 타입 확인
        valid_agents = ['source_code', 'assembly_binary', 'logs_config']
        if self.agent_type not in valid_agents:
            raise ValueError(f"Invalid agent type: {self.agent_type}. Must be one of {valid_agents}")

        print(f"✅ PQCInspectorClient 초기화: {self.agent_type} 에이전트")

    def make_request(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        파일 경로를 받아서 PQC Inspector API로 분석 요청

        Args:
            prompt: 실제로는 파일 경로 또는 파일 내용
            max_tokens: 사용하지 않음 (호환성 유지용)

        Returns:
            분석 결과 딕셔너리
        """
        # prompt를 파일 경로로 파싱 시도
        file_path = self._extract_file_path(prompt)

        if file_path and Path(file_path).exists():
            # 파일이 존재하면 파일 업로드
            return self._upload_and_analyze(file_path)
        else:
            # 파일이 없으면 프롬프트 내용을 임시 파일로 저장하여 업로드
            return self._analyze_content(prompt)

    def _extract_file_path(self, prompt: str) -> str:
        """
        프롬프트에서 파일 경로 추출

        예: "FILE_PATH: /path/to/file.py" -> "/path/to/file.py"
        """
        if prompt.startswith("FILE_PATH:"):
            return prompt.replace("FILE_PATH:", "").strip()
        return prompt.strip()

    def _upload_and_analyze(self, file_path: str) -> Dict[str, Any]:
        """
        파일을 업로드하여 분석 요청
        """
        try:
            endpoint = f"{self.base_url}/api/v1/analyze/{self.agent_type}"

            # 파일 열기
            with open(file_path, 'rb') as f:
                files = {'file': (Path(file_path).name, f, 'application/octet-stream')}

                # API 요청
                response = requests.post(
                    endpoint,
                    files=files,
                    timeout=120
                )

            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

            result = response.json()

            # 응답을 표준 형식으로 변환
            content = json.dumps(result, ensure_ascii=False, indent=2)

            # 토큰 사용량 추정 (파일 크기 기반)
            file_size = Path(file_path).stat().st_size
            estimated_tokens = int(file_size / 4)  # 대략 4 bytes per token

            return {
                'content': content,
                'usage': {
                    'prompt_tokens': estimated_tokens,
                    'completion_tokens': len(content) // 4,
                    'total_tokens': estimated_tokens + len(content) // 4
                },
                'model': f"pqc_inspector_{self.agent_type}"
            }

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"PQC Inspector Error ({self.agent_type}): {error_details}")
            raise Exception(f"PQC Inspector API Error: {str(e)}")

    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """
        콘텐츠를 임시 파일로 저장하여 분석
        """
        import tempfile

        try:
            # 임시 파일 생성
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name

            # 파일 업로드 및 분석
            result = self._upload_and_analyze(temp_path)

            # 임시 파일 삭제
            Path(temp_path).unlink()

            return result

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"PQC Inspector Content Analysis Error: {error_details}")
            raise Exception(f"PQC Inspector Content Analysis Error: {str(e)}")

    def is_available(self) -> bool:
        """PQC Inspector 서버가 실행 중인지 확인"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"PQC Inspector availability check failed: {e}")
            return False

    def list_available_models(self) -> list:
        """사용 가능한 에이전트 목록 반환"""
        if self.is_available():
            return ['source_code', 'assembly_binary', 'logs_config']
        return []

    def benchmark_request(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        벤치마크용 요청 (파일 경로 기반)

        프롬프트가 "FILE_PATH: ..." 형식이어야 함
        """
        start_time = time.time()

        try:
            response = self.make_request(prompt, max_tokens)
            end_time = time.time()

            response_time = end_time - start_time
            content = response.get('content', '')

            # JSON 유효성 검사
            json_valid = self._is_valid_json(content)

            return {
                'success': True,
                'content': content,
                'response_time': response_time,
                'json_valid': json_valid,
                'error': None,
                'model': f"pqc_inspector_{self.agent_type}"
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
                'model': f"pqc_inspector_{self.agent_type}"
            }

    def _is_valid_json(self, content: str) -> bool:
        """JSON 유효성 검사"""
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
