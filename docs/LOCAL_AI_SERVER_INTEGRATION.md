# 로컬 AI 서버 벤치마크 통합 가이드

이 가이드는 로컬에서 운영 중인 AI 서버를 벤치마크 시스템에 통합하는 방법을 설명합니다.

## 🎯 개요

로컬 AI 서버를 벤치마크에 추가하는 방법은 두 가지입니다:

1. **방법 A**: OpenAI 호환 API를 사용하는 경우 (권장)
2. **방법 B**: 커스텀 API를 사용하는 경우

---

## 방법 A: OpenAI 호환 API 사용 (빠른 설정)

대부분의 로컬 AI 서버 프레임워크는 OpenAI 호환 API를 제공합니다:
- vLLM
- Text Generation Inference (TGI)
- LocalAI
- LM Studio
- Ollama (이미 지원됨)

### 1단계: 로컬 AI 서버 확인

먼저 로컬 AI 서버가 실행 중인지 확인합니다:

```bash
# 예시: 로컬 서버가 http://localhost:8000에서 실행 중인 경우
curl http://localhost:8000/v1/models

# 응답 예시:
# {
#   "data": [
#     {"id": "my-custom-model", "object": "model", ...}
#   ]
# }
```

### 2단계: .env 파일에 설정 추가

`.env` 파일을 열고 로컬 AI 서버 설정을 추가합니다:

```bash
# 로컬 AI 서버 설정 (OpenAI 호환)
LOCAL_AI_API_KEY=not_required
LOCAL_AI_MODEL=your-model-name
LOCAL_AI_BASE_URL=http://localhost:8000/v1
```

**중요**:
- `LOCAL_AI_MODEL`: 서버에서 사용 가능한 모델 이름 (위 curl 명령으로 확인한 이름)
- `LOCAL_AI_BASE_URL`: 서버 주소 + `/v1` (OpenAI API 호환 엔드포인트)
- `LOCAL_AI_API_KEY`: 인증이 필요 없으면 `not_required`, 필요하면 실제 키 입력

### 3단계: config.yaml 파일 수정

`config/config.yaml` 파일을 열고 `llm_providers` 섹션에 로컬 AI 서버를 추가합니다:

```yaml
llm_providers:
  # ... 기존 providers ...

  local_ai:
    api_key_env: "LOCAL_AI_API_KEY"
    model_env: "LOCAL_AI_MODEL"
    base_url_env: "LOCAL_AI_BASE_URL"
```

### 4단계: 벤치마크 실행

이제 로컬 AI 서버로 벤치마크를 실행할 수 있습니다:

```bash
# 방법 1: 모든 모델 테스트 (로컬 AI 포함)
python run_benchmark.py

# 방법 2: 로컬 AI만 테스트
python test_model.py --provider local_ai

# 방법 3: 특정 에이전트만 테스트
python test_agent.py --agent source_code --provider local_ai

# 방법 4: 단일 파일 테스트
python test_single_file.py --file data/test_files/source_code/rsa_example.py --provider local_ai
```

---

## 방법 B: 커스텀 API 사용 (고급 설정)

OpenAI 호환 API가 아닌 경우, 커스텀 클라이언트를 생성해야 합니다.

### 1단계: 로컬 AI 클라이언트 클래스 생성

`clients/local_ai_client.py` 파일을 생성합니다:

```python
import requests
import json
from typing import Dict, Any
from .base_client import BaseLLMClient

class LocalAIClient(BaseLLMClient):
    def __init__(self, api_key: str = "not_required", model: str = "custom-model", base_url: str = "http://localhost:8000"):
        super().__init__(api_key, model, base_url)

    def make_request(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        로컬 AI 서버에 요청을 보내고 응답을 반환합니다.

        이 메서드를 로컬 AI 서버의 API 스펙에 맞게 수정하세요.
        """
        try:
            # ===== 여기를 로컬 AI 서버 API에 맞게 수정 =====
            headers = {
                "Content-Type": "application/json"
            }

            # API 키가 필요한 경우
            if self.api_key and self.api_key != "not_required":
                headers["Authorization"] = f"Bearer {self.api_key}"

            # 요청 데이터 구성 (로컬 서버 API 스펙에 맞게 수정)
            data = {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": 0.1,
                "model": self.model
            }

            # API 엔드포인트 (로컬 서버에 맞게 수정)
            endpoint = f"{self.base_url}/generate"  # 또는 /chat/completions, /inference 등

            response = requests.post(
                endpoint,
                headers=headers,
                json=data,
                timeout=120
            )

            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

            response_json = response.json()

            # 응답에서 텍스트 추출 (로컬 서버 응답 형식에 맞게 수정)
            # 예시 1: OpenAI 스타일
            # content = response_json['choices'][0]['message']['content']

            # 예시 2: 커스텀 형식
            content = response_json.get('generated_text', '')
            # 또는
            # content = response_json.get('response', '')
            # 또는
            # content = response_json.get('output', '')

            # 토큰 사용량 추정 (로컬 서버가 제공하지 않는 경우)
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
            # ===== 수정 끝 =====

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Local AI Error Details: {error_details}")
            raise Exception(f"Local AI API Error: {str(e)}")

    def is_available(self) -> bool:
        """로컬 AI 서버가 실행 중인지 확인"""
        try:
            # 헬스 체크 엔드포인트 (로컬 서버에 맞게 수정)
            response = requests.get(f"{self.base_url}/health", timeout=5)
            # 또는
            # response = requests.get(f"{self.base_url}/v1/models", timeout=5)

            return response.status_code == 200
        except:
            return False
```

### 2단계: ClientFactory에 등록

`clients/client_factory.py` 파일을 수정합니다:

```python
from typing import Dict, Any
from .base_client import BaseLLMClient
from .openai_client import OpenAIClient
from .google_client import GoogleClient
from .anthropic_client import AnthropicClient
from .xai_client import XAIClient
from .ollama_client import OllamaClient
from .local_ai_client import LocalAIClient  # 추가

class ClientFactory:
    _clients = {
        'openai': OpenAIClient,
        'google': GoogleClient,
        'anthropic': AnthropicClient,
        'xai': XAIClient,
        'ollama': OllamaClient,
        'local_ai': LocalAIClient  # 추가
    }

    # ... 나머지 코드는 동일 ...
```

### 3단계: .env 및 config.yaml 설정

방법 A의 2-3단계와 동일하게 설정합니다.

### 4단계: 벤치마크 실행

방법 A의 4단계와 동일합니다.

---

## 🧪 연결 테스트

벤치마크를 실행하기 전에 연결을 테스트할 수 있습니다:

```python
# test_local_connection.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clients.local_ai_client import LocalAIClient  # 또는 OpenAIClient
from dotenv import load_dotenv

load_dotenv()

# 로컬 AI 클라이언트 생성
client = LocalAIClient(
    api_key=os.getenv("LOCAL_AI_API_KEY", "not_required"),
    model=os.getenv("LOCAL_AI_MODEL", "your-model"),
    base_url=os.getenv("LOCAL_AI_BASE_URL", "http://localhost:8000")
)

# 연결 테스트
print("Testing connection...")
if client.is_available():
    print("✅ Server is available!")
else:
    print("❌ Server is not available")
    sys.exit(1)

# 간단한 요청 테스트
print("\nTesting request...")
try:
    response = client.make_request(
        prompt="Analyze this code for RSA encryption: import rsa; key = rsa.generate_private_key(2048)",
        max_tokens=500
    )
    print(f"✅ Request successful!")
    print(f"Response: {response['content'][:200]}...")
    print(f"Tokens: {response['usage']['total_tokens']}")
except Exception as e:
    print(f"❌ Request failed: {e}")
```

실행:
```bash
python test_local_connection.py
```

---

## 📊 RAG 통합 서버의 경우

RAG 시스템을 갖춘 로컬 AI 서버를 테스트하는 경우:

### 1. RAG 참고 문서 활용

벤치마크를 실행하기 전에, 생성한 RAG 참고 문서를 로컬 AI 서버에 로드하세요:

```bash
# RAG 지식 베이스 파일들
data/rag_knowledge/source_code_agent_reference.json
data/rag_knowledge/assembly_binary_agent_reference.json
data/rag_knowledge/logs_config_agent_reference.json
```

### 2. 벤치마크 실행 시 주의사항

RAG 시스템은 추가 처리 시간이 필요할 수 있습니다. `config/config.yaml`에서 타임아웃을 조정하세요:

```yaml
benchmark:
  timeout_seconds: 90  # RAG 처리 시간을 고려하여 증가
  max_retries: 3
```

### 3. 성능 비교

RAG가 있는 모델과 없는 모델의 성능을 비교하려면:

```bash
# RAG 없는 로컬 모델
python test_model.py --provider ollama --model llama3:8b

# RAG 있는 로컬 모델
python test_model.py --provider local_ai --model your-rag-model

# 결과 비교
python analyze_and_visualize.py benchmark_results.json
```

---

## 🔧 문제 해결

### 1. 연결 오류
```
Error: Connection refused
```

**해결 방법**:
- 로컬 AI 서버가 실행 중인지 확인
- 포트 번호가 올바른지 확인
- 방화벽 설정 확인

```bash
# 서버 상태 확인
curl http://localhost:8000/health

# 또는
netstat -an | grep 8000
```

### 2. 모델을 찾을 수 없음
```
Error: Model 'your-model' not found
```

**해결 방법**:
- 사용 가능한 모델 목록 확인
```bash
curl http://localhost:8000/v1/models
```
- `.env` 파일의 `LOCAL_AI_MODEL`을 정확한 모델 이름으로 수정

### 3. 타임아웃 오류
```
Error: Request timeout
```

**해결 방법**:
- `config/config.yaml`에서 타임아웃 증가
- 로컬 서버의 하드웨어 리소스 확인 (GPU 메모리, CPU 사용률)

### 4. JSON 파싱 오류
```
Error: Invalid JSON response
```

**해결 방법**:
- 로컬 AI 서버의 응답 형식 확인
- `local_ai_client.py`의 응답 파싱 로직 수정
- 프롬프트에 JSON 형식 요청 추가

---

## 📈 예상 결과

로컬 AI 서버를 벤치마크에 추가한 후:

1. **results/** 디렉토리에 결과 JSON 생성
2. **분석 도구** 실행:
   ```bash
   python analyze_and_visualize.py benchmark_results.json
   ```

3. **생성되는 분석 결과**:
   - `COMPREHENSIVE_REPORT.txt`: 종합 보고서
   - `model_f1_comparison.png`: 모델별 F1 Score
   - `precision_recall_f1.png`: Precision, Recall, F1 비교
   - `agent_performance.png`: 에이전트별 성능
   - `model_response_time.png`: 응답 시간 비교

---

## 🎯 RAG 성능 평가 팁

RAG 시스템의 효과를 평가하려면:

1. **Before/After 비교**:
   - RAG 없이: 기본 오픈소스 모델 (Ollama llama3:8b)
   - RAG 있음: 로컬 RAG AI 서버

2. **주요 지표**:
   - **Recall (재현율)**: RAG가 누락된 알고리즘을 탐지하는가?
   - **Precision (정밀도)**: RAG가 오탐을 줄이는가?
   - **Korean Algorithm Detection**: 한국 알고리즘 탐지율 개선?
   - **Response Time**: RAG 추가로 인한 속도 저하?

3. **에이전트별 분석**:
   ```bash
   python test_agent.py --agent source_code --provider local_ai
   python test_agent.py --agent assembly_binary --provider local_ai
   python test_agent.py --agent logs_config --provider local_ai
   ```

---

## 📚 추가 리소스

- **OpenAI API 호환 서버 예시**:
  - [vLLM](https://github.com/vllm-project/vllm)
  - [Text Generation Inference](https://github.com/huggingface/text-generation-inference)
  - [LocalAI](https://github.com/go-skynet/LocalAI)

- **벤치마크 커스터마이징**:
  - `config/config.yaml`: 벤치마크 설정
  - `agents/`: 에이전트 프롬프트 수정
  - `utils/metrics_calculator.py`: 평가 지표 추가

---

궁금한 점이 있으면 언제든 질문하세요!
