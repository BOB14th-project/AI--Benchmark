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
\
#### 3-2. 환경 변수로 설정

```python
from google.colab import userdata
import os

# API 키 설정
os.environ['GOOGLE_API_KEY'] = userdata.get('GOOGLE_API_KEY')
os.environ['OPENAI_API_KEY'] = userdata.get('OPENAI_API_KEY')
os.environ['XAI_API_KEY'] = userdata.get('XAI_API_KEY')




# 모델 및 엔드포인트 설정
os.environ['GOOGLE_MODEL'] = 'gemini-2.5-flash'
os.environ['GOOGLE_BASE_URL'] = 'https://generativelanguage.googleapis.com/v1beta'

os.environ['OPENAI_MODEL'] = 'gpt-4.1'
os.environ['OPENAI_BASE_URL'] = 'https://api.openai.com/v1'

os.environ['XAI_MODEL'] = 'grok-3-mini'
os.environ['XAI_BASE_URL'] = 'https://api.x.ai/v1'

print("✅ API 키 설정 완료!")
```

### 4. Ollama 로컬 모델 설치

Colab Pro/Pro+에서 Ollama를 사용하여 로컬에서 LLM 모델을 실행할 수 있습니다:

#### 4-1. Ollama 설치

```python
# Ollama 설치 (약 2-3분 소요)
!curl -fsSL https://ollama.com/install.sh | sh

# 설치 확인
!ollama --version
```

#### 4-2. Ollama 서버 백그라운드 실행

```python
# 백그라운드에서 Ollama 서버 시작
import subprocess
import time

# Ollama 서버 시작 (백그라운드)
ollama_process = subprocess.Popen(
    ['ollama', 'serve'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# 서버 시작 대기
print("⏳ Ollama 서버 시작 중...")
time.sleep(5)
print("✅ Ollama 서버 시작 완료!")
```

#### 4-3. 모델 다운로드

```python
# 원하는 모델 다운로드 (각 모델은 약 4-8GB)
# 경고: Colab 무료 버전은 디스크 공간 제한이 있으므로 1-2개 모델만 권장

# 옵션 1: LLaMA 3 (약 4.7GB)
!ollama pull llama3:8b

# 옵션 2: Qwen 3 (약 5.2GB)
!ollama pull qwen3:8b

# 옵션 3: Code Llama (약 3.8GB)
!ollama pull codellama:7b

# 다운로드된 모델 확인
!ollama list
```

#### 4-4. Ollama 환경 변수 설정

```python
# 먼저 다운로드한 모든 모델 확인
!ollama list

# 방법 1: 단일 모델 설정
os.environ['OLLAMA_MODEL'] = 'llama3:8b'
os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'
print("✅ Ollama 단일 모델 설정 완료!")

# 방법 2: 여러 모델 사용 - 쉼표로 구분 (권장, 가장 간단)
os.environ['OLLAMA_MODEL'] = 'llama3:8b,qwen3:8b,codellama:7b'
os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'
print("✅ Ollama 다중 모델 설정 완료!")

# 방법 3: JSON 배열 형식 (고급)
import json
ollama_models = ['llama3:8b', 'qwen3:8b', 'codellama:7b']
os.environ['OLLAMA_MODEL'] = json.dumps(ollama_models)
os.environ['OLLAMA_BASE_URL'] = 'http://localhost:11434'
print(f"✅ Ollama 설정 완료! 모델: {ollama_models}")
```

**💡 팁:**
- **가장 권장**: 쉼표 구분 형식 `'llama3:8b,qwen3:8b,codellama:7b'`
- 벤치마크 실행 시 설정한 모든 모델이 순차적으로 테스트됩니다
- JSON 배열 형식은 고급 사용자용 (주의: 이중 인코딩 문제 가능)

#### 4-5. Ollama 연결 테스트

```python
# Ollama 서버 연결 테스트
import requests

try:
    response = requests.get('http://localhost:11434/api/tags', timeout=5)
    if response.status_code == 200:
        models = response.json().get('models', [])
        print(f"✅ Ollama 연결 성공! 사용 가능한 모델: {[m['name'] for m in models]}")
    else:
        print(f"❌ Ollama 연결 실패: {response.status_code}")
except Exception as e:
    print(f"❌ Ollama 서버에 연결할 수 없습니다: {e}")
```

**⚠️ 중요 사항:**
- **Colab Pro/Pro+ 권장**: 더 많은 디스크 공간과 메모리 제공
- 런타임 종료 시 Ollama 서버와 모델이 삭제되므로 재시작 필요
- 모델 크기에 따라 다운로드 시간이 5-10분 소요될 수 있습니다

#### 4-6. 추천 모델 조합

```python
# 옵션 1: 빠르고 가벼운 모델 (권장)
!ollama pull llama3:8b
!ollama pull qwen3:8b

# 옵션 2: 코드 특화 모델
!ollama pull codellama:7b

# 옵션 3: 성능 중시 (Colab Pro+ 권장)
!ollama pull llama3:70b
!ollama pull qwen3:14b
```

### 5. Google Drive 마운트 (결과 자동 저장용, 권장)

```python
from google.colab import drive

# Google Drive 마운트
drive.mount('/content/drive')

# 결과 저장 디렉토리 생성
import os
results_dir = '/content/drive/MyDrive/AI_Benchmark_Results'
os.makedirs(results_dir, exist_ok=True)

print(f"✅ Google Drive 마운트 완료!")
print(f"📁 결과 저장 위치: {results_dir}")

# 결과 자동 저장을 위한 환경 변수 설정
os.environ['GDRIVE_RESULTS_DIR'] = results_dir
```

### 6. 테스트 데이터 확인

```python
# 테스트 파일 확인
!ls -la data/test_files/source_code/ | head -10
!ls -la data/test_files/assembly_binary/ | head -10
!ls -la data/test_files/logs_config/ | head -10

print("\n✅ 테스트 데이터 로드 완료!")
```

## 📊 벤치마크 실행

**💡 Google Drive 자동 백업 활성화**

벤치마크 실행 전에 Section 5에서 Google Drive를 마운트하면:
- 테스트 완료 시 결과가 자동으로 Drive에 백업됩니다
- 10개 테스트마다 중간 진행상황이 저장됩니다
- 런타임 종료 시에도 결과가 안전하게 보관됩니다

### 옵션 1: 빠른 테스트 (권장 - 처음 실행 시)

```python
# Ollama 모델만 빠르게 테스트
!python benchmark_runner.py --providers ollama --agents source_code --limit 3

# Google Drive에 자동 백업됨 (GDRIVE_RESULTS_DIR 설정 시)
```

### 옵션 2: API 모델과 비교 테스트

```python
# Google Gemini + Ollama 비교
!python benchmark_runner.py --providers google ollama --agents source_code --limit 5

# OpenAI + Ollama 비교
!python benchmark_runner.py --providers openai ollama --agents source_code assembly_binary --limit 5
```

### 옵션 3: 여러 Ollama 모델 테스트

```python
# config.yaml에 여러 모델 설정 후 실행
# 또는 각 모델을 순차적으로 테스트

# LLaMA 3 테스트
os.environ['OLLAMA_MODEL'] = 'llama3:8b'
!python benchmark_runner.py --providers ollama --agents source_code --limit 5 --output llama3_results

# Qwen 3 테스트
os.environ['OLLAMA_MODEL'] = 'qwen3:8b'
!python benchmark_runner.py --providers ollama --agents source_code --limit 5 --output qwen3_results

# Code Llama 테스트
os.environ['OLLAMA_MODEL'] = 'codellama:7b'
!python benchmark_runner.py --providers ollama --agents source_code --limit 5 --output codellama_results
```

### 옵션 4: 전체 벤치마크 (시간 소요)

```python
# 모든 에이전트와 프로바이더 테스트
!python benchmark_runner.py --providers google openai ollama --agents source_code assembly_binary logs_config --limit 10
```

### 옵션 5: 병렬 실행 (더 빠름)

```python
# 병렬로 여러 테스트 동시 실행 (주의: 메모리 사용량 증가)
!python benchmark_runner.py --providers ollama --agents source_code assembly_binary --limit 5 --parallel
```

## 📈 결과 확인

### 실시간 진행 상황

벤치마크 실행 중 다음과 같은 출력이 표시됩니다:

```
🚀 벤치마크 시작
============================================================
✅ google 모델: ['gemini-2.5-flash']
✅ openai 모델: ['gpt-4.1']
📁 source_code: 5개 테스트 파일 로드됨

📋 테스트 1/5: google/gemini-2.5-flash/source_code
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

### 수동으로 결과 백업하기 (실행 중에도 가능)

벤치마크가 실행 중일 때 언제든지 수동으로 백업할 수 있습니다:

```python
# 방법 1: 유틸리티 스크립트 사용 (권장)
!python utils/backup_to_gdrive.py

# 방법 2: 직접 복사
import shutil
import glob

results_dir = os.environ.get('GDRIVE_RESULTS_DIR')
if results_dir:
    # JSON 파일 백업
    for f in glob.glob("benchmark_results_*.json"):
        shutil.copy2(f, results_dir)
        print(f"✅ 백업: {f}")

    # CSV 파일 백업
    for f in glob.glob("benchmark_results_*.csv"):
        shutil.copy2(f, results_dir)
        print(f"✅ 백업: {f}")
```

### Google Drive에서 결과 확인

```python
# Google Drive에 저장된 결과 확인
results_dir = os.environ.get('GDRIVE_RESULTS_DIR', '/content/drive/MyDrive/AI_Benchmark_Results')
!ls -lh {results_dir}

# 백업 목록 자세히 보기
!python utils/backup_to_gdrive.py list

# 가장 최근 결과 파일 찾기
import glob
json_files = glob.glob(f"{results_dir}/benchmark_results_*.json")
if json_files:
    latest_result = max(json_files, key=os.path.getctime)
    print(f"\n📊 최신 결과 파일: {latest_result}")

    # 결과 미리보기
    import json
    with open(latest_result, 'r') as f:
        result_data = json.load(f)
        print(f"\n총 테스트: {result_data['summary']['total_tests']}")
        print(f"성공: {result_data['summary']['successful_tests']}")
        print(f"성공률: {result_data['summary']['success_rate']:.1%}")
else:
    print("❌ 결과 파일이 없습니다.")

# 중간 백업 파일 확인 (진행 중인 테스트)
backup_files = glob.glob(f"{results_dir}/backup_progress_*.json")
if backup_files:
    print(f"\n💾 중간 백업 파일: {len(backup_files)}개")
    latest_backup = max(backup_files, key=os.path.getctime)
    print(f"   최신 백업: {os.path.basename(latest_backup)}")
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

### Ollama 서버 연결 실패

```python
# Ollama 서버 상태 확인
!ps aux | grep ollama

# Ollama 서버 재시작
import subprocess
import time

# 기존 프로세스 종료
!pkill -f "ollama serve"
time.sleep(2)

# 새로 시작
ollama_process = subprocess.Popen(['ollama', 'serve'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(5)
print("✅ Ollama 서버 재시작 완료")

# 연결 테스트
import requests
response = requests.get('http://localhost:11434/api/tags')
print(f"연결 상태: {response.status_code}")
```

### 타임아웃 오류

```python
# config/config.yaml 파일에서 타임아웃 설정 확인
!cat config/config.yaml | grep timeout
```

### Ollama 모델 다운로드 실패

```python
# 디스크 공간 확인
!df -h

# 불필요한 파일 삭제
!apt-get clean
!rm -rf /root/.cache/*

# 모델 재다운로드
!ollama pull llama3:8b
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

### 기본 설정

- [ ] Google Colab 노트북 생성 (Pro/Pro+ 권장)
- [ ] 저장소 클론 완료
- [ ] 필수 패키지 설치 완료
- [ ] API 키 Colab Secrets에 추가 (선택 사항)
- [ ] 환경 변수 설정 완료

### Ollama 설정 (필수)

- [ ] Ollama 설치 완료
- [ ] Ollama 서버 백그라운드 실행 확인
- [ ] Ollama 모델 다운로드 (최소 1개)
  - [ ] llama3:8b (권장)
  - [ ] qwen3:8b (권장)
  - [ ] codellama:7b (코드 특화)
- [ ] Ollama 환경 변수 설정
- [ ] Ollama 연결 테스트 성공

### 실행 준비

- [ ] 테스트 데이터 확인 완료
- [ ] 벤치마크 실행 명령어 준비
- [ ] 결과 저장 경로 확인

## 🎯 권장 실행 순서

### Ollama 위주 사용 (Colab Pro/Pro+)

1. **처음 실행 (테스트)**
   ```python
   !python benchmark_runner.py --providers ollama --agents source_code --limit 3
   ```

2. **정상 작동 확인 후**
   ```python
   !python benchmark_runner.py --providers ollama --agents source_code assembly_binary --limit 5
   ```

3. **여러 Ollama 모델 비교**
   ```python
   # LLaMA 3
   os.environ['OLLAMA_MODEL'] = 'llama3:8b'
   !python benchmark_runner.py --providers ollama --agents source_code --limit 10

   # Qwen 3
   os.environ['OLLAMA_MODEL'] = 'qwen3:8b'
   !python benchmark_runner.py --providers ollama --agents source_code --limit 10
   ```

4. **전체 벤치마크 (Ollama + API 선택)**
   ```python
   # Ollama만 사용
   !python benchmark_runner.py --providers ollama --agents source_code assembly_binary logs_config --limit 20

   # API와 함께 비교 (선택)
   !python benchmark_runner.py --providers google ollama --agents source_code assembly_binary logs_config --limit 10
   ```

**💡 Colab Pro/Pro+ 사용 팁:**
- 더 많은 GPU/메모리를 활용하여 큰 모델 실행 가능
- llama3:70b 같은 대형 모델도 테스트 가능
- 병렬 실행으로 속도 향상 가능
- 런타임 연결 시간이 길어 장시간 벤치마크 가능

## 📞 지원 및 문제 해결

### 일반적인 문제

1. **Ollama 서버 연결 실패**: 위의 "Ollama 서버 연결 실패" 섹션 참조
2. **메모리 부족**: 테스트 수 제한 (`--limit 3`)
3. **모델 다운로드 실패**: 디스크 공간 확인 및 불필요한 파일 삭제

### 추가 지원

- Colab 노트북 런타임 재시작: `런타임` → `런타임 다시 시작`
- Ollama 서버 재시작: 위의 문제 해결 섹션 참조
- GitHub Issues에 문의

## 💡 Colab Pro/Pro+ 최적화 팁

### 리소스 활용

```python
# GPU 사용 확인
!nvidia-smi

# 메모리 사용량 확인
!free -h

# 디스크 공간 확인
!df -h
```

### 대형 모델 활용

```python
# Colab Pro+에서 70B 모델 사용
!ollama pull llama3:70b
os.environ['OLLAMA_MODEL'] = 'llama3:70b'
!python benchmark_runner.py --providers ollama --agents source_code --limit 5
```

### 장시간 실행

```python
# 백그라운드 실행으로 연결 끊김 방지
import time
from IPython.display import Javascript

# 1시간마다 자동 클릭 (연결 유지)
display(Javascript('''
  setInterval(function() {
    document.querySelector("colab-connect-button").click()
  }, 3600000);
'''))
```

---

## 🎉 완료!

이 가이드를 따라 Google Colab Pro/Pro+에서 Ollama를 사용한 벤치마크를 성공적으로 실행할 수 있습니다.

**핵심 요약:**
1. Ollama 설치 및 서버 실행
2. 원하는 모델 다운로드 (llama3:8b, qwen3:8b 권장)
3. 벤치마크 실행 (`--providers ollama`)
4. 결과 분석 및 시각화

모든 단계가 정상 작동하면 양자 취약 암호 알고리즘 탐지 성능을 평가하고 다양한 LLM 모델을 비교할 수 있습니다!
