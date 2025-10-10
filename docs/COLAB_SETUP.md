# Google Colab에서 AI Benchmark 실행하기

이 가이드는 Google Colab 환경에서 양자 취약 암호 알고리즘 탐지 벤치마크를 실행하는 방법을 설명합니다.

## 🚀 빠른 시작

### 1. 새 Colab 노트북 생성

1. [Google Colab](https://colab.research.google.com/)에 접속
2. `파일` → `새 노트북` 클릭

### 2. 저장소 클론 및 설치

다음 셀을 순서대로 실행하세요:

```python
# 1. 저장소 클론
!git clone https://github.com/your-username/AI--Benchmark.git
%cd AI--Benchmark

# 2. 필수 패키지 설치
!pip install -q openai google-generativeai anthropic requests pyyaml python-dotenv numpy pandas psutil

# 3. 설치 확인
!python -c "import openai; import google.generativeai as genai; print('설치 완료!')"
```

### 3. API 키 설정

Colab Secrets를 사용하여 안전하게 API 키를 관리합니다:

#### 3-1. Colab Secrets에 API 키 추가

1. 좌측 사이드바에서 **🔑 Secrets** 아이콘 클릭
2. 다음 키들을 추가:
   - `GOOGLE_API_KEY`: Google Gemini API 키
   - `OPENAI_API_KEY`: OpenAI GPT API 키
   - `XAI_API_KEY`: xAI Grok API 키 (선택)
   - `ANTHROPIC_API_KEY`: Anthropic Claude API 키 (선택)

#### 3-2. 환경 변수로 설정

```python
from google.colab import userdata
import os

# API 키 설정
os.environ['GOOGLE_API_KEY'] = userdata.get('GOOGLE_API_KEY')
os.environ['OPENAI_API_KEY'] = userdata.get('OPENAI_API_KEY')

# 선택적 API 키들 (사용하는 경우만)
try:
    os.environ['XAI_API_KEY'] = userdata.get('XAI_API_KEY')
except:
    print("⚠️ XAI API 키가 설정되지 않았습니다 (선택 사항)")

try:
    os.environ['ANTHROPIC_API_KEY'] = userdata.get('ANTHROPIC_API_KEY')
except:
    print("⚠️ Anthropic API 키가 설정되지 않았습니다 (선택 사항)")

# 모델 및 엔드포인트 설정
os.environ['GOOGLE_MODEL'] = 'gemini-2.0-flash-exp'
os.environ['GOOGLE_BASE_URL'] = 'https://generativelanguage.googleapis.com/v1beta'

os.environ['OPENAI_MODEL'] = 'gpt-4.1'
os.environ['OPENAI_BASE_URL'] = 'https://api.openai.com/v1'

os.environ['XAI_MODEL'] = 'grok-3-mini'
os.environ['XAI_BASE_URL'] = 'https://api.x.ai/v1'

print("✅ API 키 설정 완료!")
```

### 4. 테스트 데이터 확인

```python
# 테스트 파일 확인
!ls -la data/test_files/source_code/ | head -10
!ls -la data/test_files/assembly_binary/ | head -10
!ls -la data/test_files/logs_config/ | head -10

print("\n✅ 테스트 데이터 로드 완료!")
```

## 📊 벤치마크 실행

### 옵션 1: 빠른 테스트 (권장 - 처음 실행 시)

```python
# 각 에이전트당 3개 파일만 테스트
!python benchmark_runner.py --providers google --agents source_code --limit 3
```

### 옵션 2: 특정 모델만 테스트

```python
# Google Gemini만 테스트
!python benchmark_runner.py --providers google --agents source_code assembly_binary logs_config --limit 5

# OpenAI GPT만 테스트
!python benchmark_runner.py --providers openai --agents source_code --limit 5
```

### 옵션 3: 전체 벤치마크 (시간 소요)

```python
# 모든 프로바이더와 에이전트 테스트
!python benchmark_runner.py --providers google openai xai --agents source_code assembly_binary logs_config --limit 10
```

### 옵션 4: 병렬 실행 (더 빠름)

```python
# 병렬로 여러 테스트 동시 실행
!python benchmark_runner.py --providers google openai --agents source_code --limit 5 --parallel
```

## 📈 결과 확인

### 실시간 진행 상황

벤치마크 실행 중 다음과 같은 출력이 표시됩니다:

```
🚀 벤치마크 시작
============================================================
✅ google 모델: ['gemini-2.0-flash-exp']
✅ openai 모델: ['gpt-4.1']
📁 source_code: 5개 테스트 파일 로드됨

📋 테스트 1/5: google/gemini-2.0-flash-exp/source_code
    파일: rsa_public_key_system
    ✅ 완료 (12.3초)
    🎯 신뢰도: 0.920
    🔍 탐지된 양자 취약 알고리즘: RSA, SHA-256
```

### 결과 파일 확인

```python
# JSON 결과 확인
import json

with open('benchmark_results_[timestamp].json', 'r') as f:
    results = json.load(f)

print(f"총 테스트: {results['summary']['total_tests']}")
print(f"성공: {results['summary']['successful_tests']}")
print(f"성공률: {results['summary']['success_rate']:.1%}")
```

### 결과 다운로드

```python
from google.colab import files

# JSON 결과 다운로드
files.download('benchmark_results_[timestamp].json')

# CSV 결과 다운로드
files.download('benchmark_results_[timestamp].csv')
```

## 📊 결과 분석 및 시각화

### 기본 분석

```python
# 결과 분석 실행
!python analyze_results.py --compare-models
```

### 시각화 생성

```python
# 에이전트별 성능 비교 그래프
!python visualize_agent_performance.py

# 응답 시간 비교
!python visualize_response_time.py

# 생성된 이미지 확인
from IPython.display import Image, display
display(Image('results/agent_performance_comparison.png'))
display(Image('results/response_time_comparison.png'))
```

### 상세 분석 (Pandas)

```python
import pandas as pd
import matplotlib.pyplot as plt

# CSV 결과 로드
df = pd.read_csv('benchmark_results_[timestamp].csv')

# 모델별 성공률
model_success = df.groupby(['provider', 'model'])['success'].mean()
print("\n모델별 성공률:")
print(model_success)

# 에이전트별 성공률
agent_success = df.groupby('agent_type')['success'].mean()
print("\n에이전트별 성공률:")
print(agent_success)

# 응답 시간 분포
plt.figure(figsize=(10, 6))
df.boxplot(column='response_time', by='provider')
plt.title('프로바이더별 응답 시간 분포')
plt.suptitle('')
plt.ylabel('응답 시간 (초)')
plt.show()

# 탐지된 양자 취약 알고리즘 수 분포
plt.figure(figsize=(10, 6))
df.boxplot(column='detected_quantum_vulnerable_count', by='agent_type')
plt.title('에이전트별 탐지된 양자 취약 알고리즘 수')
plt.suptitle('')
plt.ylabel('탐지 개수')
plt.show()
```

## 🔧 문제 해결

### API 키 오류

```python
# API 키 확인
import os
print("GOOGLE_API_KEY:", "설정됨" if os.getenv('GOOGLE_API_KEY') else "없음")
print("OPENAI_API_KEY:", "설정됨" if os.getenv('OPENAI_API_KEY') else "없음")
```

### 메모리 부족

```python
# 테스트 수 제한
!python benchmark_runner.py --providers google --agents source_code --limit 3
```

### 타임아웃 오류

```python
# config/config.yaml 파일에서 타임아웃 설정 확인
!cat config/config.yaml | grep timeout
```

## 💡 고급 사용법

### 특정 파일만 테스트

```python
# 단일 파일 테스트 스크립트 생성
test_code = """
from clients.client_factory import ClientFactory
from agents.agent_factory import AgentFactory
from config.config_loader import ConfigLoader
import os

# 설정 로드
config = ConfigLoader()
llm_config = config.get_llm_config('google')

# 클라이언트 및 에이전트 생성
client = ClientFactory.create_client('google', llm_config)
agent = AgentFactory.create_agent('source_code')

# 테스트 파일 읽기
with open('data/test_files/source_code/rsa_public_key_system.java', 'r') as f:
    test_data = f.read()

# 프롬프트 생성 및 실행
prompt = agent.create_prompt(test_data)
response = client.benchmark_request(prompt, max_tokens=2000)

# 결과 출력
if response['success']:
    findings = agent.extract_key_findings(response['content'])
    print("탐지 결과:", findings['analysis_results'])
else:
    print("오류:", response['error'])
"""

with open('test_single.py', 'w') as f:
    f.write(test_code)

!python test_single.py
```

### 커스텀 분석

```python
import pandas as pd
import json

# 결과 로드
with open('benchmark_results_[timestamp].json', 'r') as f:
    results = json.load(f)

# 상세 결과 추출
detailed = results['detailed_results']

# 양자 취약 알고리즘별 탐지율 계산
algorithm_detection = {}
for result in detailed:
    if result.get('success') and result.get('valid_json'):
        analysis = result.get('analysis_results', {})
        for category, value in analysis.items():
            if value and value != 'None':
                algorithm_detection[category] = algorithm_detection.get(category, 0) + 1

print("\n카테고리별 탐지 빈도:")
for algo, count in sorted(algorithm_detection.items(), key=lambda x: x[1], reverse=True):
    print(f"{algo}: {count}회")
```

## 📋 체크리스트

실행 전 확인사항:

- [ ] Google Colab 노트북 생성
- [ ] 저장소 클론 완료
- [ ] 필수 패키지 설치 완료
- [ ] API 키 Colab Secrets에 추가
- [ ] 환경 변수 설정 완료
- [ ] 테스트 데이터 확인 완료
- [ ] 벤치마크 실행 명령어 준비

## 🎯 권장 실행 순서

1. **처음 실행 (테스트)**
   ```python
   !python benchmark_runner.py --providers google --agents source_code --limit 3
   ```

2. **정상 작동 확인 후**
   ```python
   !python benchmark_runner.py --providers google openai --agents source_code assembly_binary --limit 5
   ```

3. **전체 벤치마크**
   ```python
   !python benchmark_runner.py --providers google openai xai --agents source_code assembly_binary logs_config --limit 10 --parallel
   ```

## 📞 지원

문제가 발생하면:
1. Colab 노트북 런타임 재시작 (`런타임` → `런타임 다시 시작`)
2. API 키 재확인
3. 타임아웃 설정 조정
4. GitHub Issues에 문의

---

이 가이드를 따라 Google Colab에서 벤치마크를 성공적으로 실행할 수 있습니다. 모든 단계가 정상 작동하면 양자 취약 암호 알고리즘 탐지 성능을 평가할 수 있습니다!
