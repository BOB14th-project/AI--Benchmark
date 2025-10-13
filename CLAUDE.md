# AI Benchmark - 양자 취약 암호 알고리즘 탐지 벤치마크

이 시스템은 다양한 LLM 모델들의 양자 취약 암호 알고리즘 탐지 성능을 평가하는 벤치마크 도구입니다.

## 🎯 목표

포스트 양자 암호(Post-Quantum Cryptography) 전환을 위한 기존 시스템의 **양자 취약 암호 알고리즘** 식별 능력을 LLM 모델별로 비교 평가합니다.

### 🔍 탐지 대상: 양자 취약 알고리즘

**Shor's Algorithm에 취약한 공개키 암호**:
- RSA (모든 키 길이)
- 타원곡선 암호 (ECC, ECDSA, ECDH)
- 이산대수 기반 암호 (DSA, DH, ElGamal)
- 한국 공개키 알고리즘 (KCDSA, EC-KCDSA)

**Grover's Algorithm에 취약한 대칭키 암호** (보안강도 절반 감소):
- AES-128 → 64비트 보안강도
- 3DES, DES, RC4
- MD5, SHA-1, SHA-256 (해시 함수)

**한국 표준 암호** (양자 내성 평가 필요):
- SEED, ARIA, HIGHT, LEA (대칭키)
- HAS-160, LSH (해시 함수)

## 🧪 테스트 모델

### 상용 API 모델
1. **Google Gemini**: `gemini-2.5-flash`
2. **OpenAI GPT**: `gpt-4.1`
3. **xAI Grok**: `grok-3-mini`

### 로컬 Ollama 모델
1. **LLaMA 3**: `llama3:8b`
2. **Qwen 3**: `qwen3:8b`
3. **Code Llama**: `codellama:7b`

## 📊 평가 대상 에이전트

### 1. Source Code Agent (`source_code`)
- **목적**: 소스 코드에서 양자 취약 암호 알고리즘 탐지
- **파일 위치**: `data/test_files/source_code/`
- **지원 언어**: Python, Java, C/C++, JavaScript
- **탐지 대상**: 양자 취약 공개키 암호 (RSA, ECC, DH, DSA), 한국 알고리즘(SEED, ARIA, HIGHT, LEA, KCDSA)

### 2. Assembly Binary Agent (`assembly_binary`)
- **목적**: 어셈블리/바이너리 코드에서 암호 연산 탐지
- **파일 위치**: `data/test_files/assembly_binary/`
- **지원 형식**: 어셈블리, 바이너리 덤프, 디스어셈블리
- **탐지 대상**: 양자 취약 암호 연산 (큰 정수 연산, 타원곡선 연산, 모듈러 지수)

### 3. Logs Config Agent (`logs_config`)
- **목적**: 설정 파일과 로그에서 암호 설정 탐지
- **파일 위치**: `data/test_files/logs_config/`
- **지원 형식**: 설정 파일, 시스템 로그, 애플리케이션 로그
- **탐지 대상**: 양자 취약 SSL/TLS 설정, 인증서 구성, 암호 라이브러리 설정

## 🔧 설정

### API 키 설정

`config/config.yaml` 파일에 API 키들을 설정하세요:

```yaml
llm_providers:
  openai:
    api_key: "your_openai_api_key_here"
    model: "gpt-4.1"
    base_url: "https://api.openai.com/v1"

  google:
    api_key: "your_google_api_key_here"
    model: "gemini-2.5-flash"
    base_url: "https://generativelanguage.googleapis.com/v1beta"

  xai:
    api_key: "your_xai_api_key_here"
    model: "grok-3-mini"
    base_url: "https://api.x.ai/v1"

  ollama:
    api_key: "not_required"
    base_url: "http://localhost:11434"
    models:
      - "llama3:8b"
      - "qwen3:8b"
      - "codellama:7b"
```

### Ollama 설정

로컬 Ollama 서버가 실행 중이어야 합니다:

```bash
# Ollama 설치 (macOS)
brew install ollama

# 모델 다운로드
ollama pull llama3:8b
ollama pull qwen3:8b
ollama pull codellama:7b

# Ollama 서버 실행
ollama serve
```

## 🚀 실행 방법

### 1. 전체 벤치마크 실행

```bash
python run_benchmark.py
```

### 2. 특정 모델 테스트

```bash
# Google Gemini 테스트
python test_model.py --provider google --model gemini-2.0-flash
# OpenAI GPT 테스트
python test_model.py --provider openai --model gpt-4.1

# Ollama 로컬 모델 테스트
python test_model.py --provider ollama --model llama3:8b
```

### 3. 특정 에이전트 테스트

```bash
# Source Code Agent만 테스트
python test_agent.py --agent source_code --all-models

# Assembly Agent만 테스트
python test_agent.py --agent assembly_binary --model gemini-2.0-flash```

### 4. 단일 파일 테스트

```bash
# 특정 파일만 테스트
python test_single_file.py --file data/test_files/source_code/rsa_public_key_system.java --model gemini-2.0-flash```

## 📈 평가 지표

### 1. 양자 취약 알고리즘 탐지 정확도 (Quantum-Vulnerable Algorithm Detection Accuracy)
- **정의**: 실제 양자 취약 알고리즘 대비 정확히 탐지된 비율
- **계산**: (정확히 탐지된 양자 취약 알고리즘 수) / (전체 양자 취약 알고리즘 수)

### 2. 정밀도 (Precision)
- **정의**: 탐지된 것 중 실제 양자 취약 알고리즘인 비율
- **계산**: (참 양성) / (참 양성 + 거짓 양성)

### 3. 재현율 (Recall)
- **정의**: 실제 양자 취약 알고리즘 중 탐지된 비율
- **계산**: (참 양성) / (참 양성 + 거짓 음성)

### 4. F1 점수
- **정의**: 정밀도와 재현율의 조화 평균
- **계산**: 2 × (정밀도 × 재현율) / (정밀도 + 재현율)

### 5. 응답 시간 (Response Time)
- **정의**: API 호출부터 응답까지의 시간
- **단위**: 초

### 6. 토큰 효율성
- **정의**: 사용된 토큰 대비 탐지 성능
- **계산**: F1 점수 / 총 토큰 수

### 7. JSON 유효성
- **정의**: 구조화된 응답 생성 능력
- **계산**: 유효한 JSON 응답 비율

## 📋 결과 분석

### 통합 분석 및 시각화 도구

벤치마크 실행 후, 통합 분석 도구를 사용하여 결과를 분석하고 시각화할 수 있습니다:

```bash
# 전체 분석 및 시각화 (권장)
python analyze_and_visualize.py benchmark_results.json

# 출력 디렉토리 지정
python analyze_and_visualize.py benchmark_results.json --output-dir my_analysis

# 최소 테스트 수 설정 (통계적 신뢰도)
python analyze_and_visualize.py benchmark_results.json --min-tests 20

# 텍스트 리포트만 생성
python analyze_and_visualize.py benchmark_results.json --text-only

# 시각화만 생성
python analyze_and_visualize.py benchmark_results.json --visualize-only
```

### 생성되는 분석 결과

#### 📄 텍스트 리포트
- **COMPREHENSIVE_REPORT.txt**: 전체 결과를 요약한 종합 보고서
  - 실행 요약 (총 테스트 수, 성공률, 평균 응답시간)
  - 모델별 성능 비교 (F1 Score, Precision, Recall 기준)
  - 에이전트별 성능 분석
  - 알고리즘 탐지율 분석
  - 성능 분석 (응답시간, 상관관계)

#### 📊 시각화 그래프
1. **model_f1_comparison.png**: 모델별 F1 Score 비교 (가로 막대 그래프)
2. **precision_recall_f1.png**: Precision, Recall, F1 Score 함께 비교 (그룹 막대 그래프)
3. **agent_performance.png**: 에이전트별 성능 비교
4. **model_response_time.png**: 모델별 평균 응답시간 (에러바 포함)
5. **algorithm_detection_overall.png**: 알고리즘별 탐지율 (전체 모델 통합)
6. **model_agent_heatmap.png**: 모델-에이전트 조합별 성능 히트맵

### 개별 분석 도구 (레거시)

기존 개별 분석 도구들도 계속 사용 가능합니다:

```bash
# 모델별 성능 비교 (구버전)
python analyze_results.py benchmark_results.json --compare-models

# 알고리즘 탐지 분석
python analyze_algorithm_detection.py --file benchmark_results.json

# Precision/Recall 상세 분석
python analyze_precision_recall.py --file benchmark_results.json

# 에이전트별 성능 시각화
python visualize_agent_performance.py benchmark_results.json --all

# 응답시간 시각화
python visualize_response_time.py benchmark_results.json --all

# F1 Score 시각화
python visualize_f1_score.py --file benchmark_results.json
```

**⚠️ 권장사항**: 새로운 `analyze_and_visualize.py` 도구를 사용하는 것을 권장합니다.
모든 분석 기능이 통합되어 있으며, 일관된 결과 형식과 더 나은 사용성을 제공합니다.

## 📁 프로젝트 구조

```
AI--Benchmark/
├── agents/                     # 분석 에이전트들
│   ├── base_agent.py          # 기본 에이전트 클래스
│   ├── source_code_agent.py   # 소스 코드 분석
│   ├── assembly_agent.py      # 어셈블리 분석
│   ├── logs_config_agent.py   # 로그/설정 분석
│   └── agent_factory.py       # 에이전트 팩토리
├── clients/                   # LLM API 클라이언트들
│   ├── base_client.py         # 기본 클라이언트
│   ├── google_client.py       # Google Gemini
│   ├── openai_client.py       # OpenAI GPT
│   ├── xai_client.py          # xAI Grok
│   └── ollama_client.py       # Ollama 로컬
├── config/                    # 설정 파일들
│   ├── config.yaml           # 메인 설정
│   └── config_loader.py       # 설정 로더
├── data/                      # 테스트 데이터
│   ├── test_files/           # 실제 테스트 파일들
│   │   ├── source_code/      # 소스 코드 샘플
│   │   ├── assembly_binary/  # 어셈블리/바이너리
│   │   └── logs_config/      # 로그/설정 파일
│   └── ground_truth/         # 정답 데이터
├── utils/                     # 유틸리티들
│   ├── test_case_manager.py  # 테스트 케이스 관리
│   ├── result_analyzer.py    # 결과 분석
│   └── benchmark_runner.py   # 벤치마크 실행기
├── results/                   # 테스트 결과들
├── test_*.py                 # 개별 테스트 스크립트들
├── run_benchmark.py          # 메인 벤치마크 실행기
├── analyze_and_visualize.py  # 통합 분석 및 시각화 도구 (권장)
├── analyze_*.py              # 개별 분석 도구들 (레거시)
├── visualize_*.py            # 개별 시각화 도구들 (레거시)
└── CLAUDE.md                 # 이 파일
```

## 🔍 문제 해결

### 1. API 연결 문제

```bash
# Google API 키 확인
python -c "from config.config_loader import ConfigLoader; print(ConfigLoader().get_llm_config('google'))"

# Ollama 서버 상태 확인
curl http://localhost:11434/api/tags
```

### 2. 메모리 부족

```bash
# 배치 크기 줄이기
export BATCH_SIZE=3

# 컨텍스트 길이 제한
export MAX_CONTEXT_LENGTH=3000
```

### 3. 느린 응답 시간

```bash
# 타임아웃 설정
export REQUEST_TIMEOUT=30

# 병렬 처리 활성화
export PARALLEL_REQUESTS=true
```

## 📊 예상 결과

### 모델별 예상 성능

| 모델 | F1 Score | 응답시간 | 토큰효율성 | 특징 |
|------|----------|----------|------------|------|
| gemini-2.5-flash | 0.85-0.90 | 8-12초 | 높음 | 높은 정확도, 빠른 응답 |
| gpt-4.1 | 0.80-0.85 | 8-12초 | 중간 | 균형잡힌 성능 |
| grok-3-mini | 0.75-0.80 | 5-8초 | 높음 | 빠른 응답, 경량화 |
| llama3:8b | 0.70-0.75 | 3-5초 | 매우높음 | 로컬 실행, 빠름 |
| qwen3:8b | 0.65-0.70 | 4-6초 | 높음 | 멀티모달 특화 |
| codellama:7b | 0.60-0.65 | 2-4초 | 매우높음 | 코드 특화, 빠름 |

### 에이전트별 예상 난이도

1. **Source Code** (쉬움): 명시적 알고리즘 사용, 높은 탐지율
2. **Assembly Binary** (어려움): 컴파일된 코드, 패턴 인식 필요
3. **Logs Config** (중간): 설정 이해, 간접적 증거 수집

## 🎯 기대 효과

1. **모델 선택 가이드**: 용도별 최적 모델 추천
2. **성능 벤치마크**: 객관적 성능 비교 데이터
3. **양자 취약 알고리즘 탐지 도구**: 실무에서 활용 가능한 도구
4. **연구 기여**: 양자 취약 암호 분석 AI 연구 발전

## 🔄 업데이트 계획

- [ ] 추가 모델 지원 (Claude, LLaMA 등)
- [ ] 더 많은 테스트 케이스 추가
- [ ] 실시간 대시보드 개발
- [ ] 자동화된 CI/CD 파이프라인
- [ ] 웹 인터페이스 개발

---

## 🧪 고도화된 테스트 케이스 생성 지침

벤치마크의 정확성을 높이기 위한 고급 테스트 케이스 요구사항입니다.

### 1. 패턴 회피 (Pattern Evasion)
- **목적**: 단순한 문자열 매칭이나 정규식 패턴으로는 탐지할 수 없는 복잡한 구현
- **방법**:
  - 변수명과 함수명에 암호화 관련 키워드 직접 사용 금지
  - 우회적 네이밍 컨벤션 사용 (예: `processData()`, `transform()`, `calculate()`)
  - 암호화 상수를 계산된 값이나 배열 인덱스로 표현
  - 분산된 구현 (여러 함수/클래스에 걸쳐 구현)

### 2. 직접적 암호화 문자열 사용 금지
- **금지 패턴**: "RSA", "AES", "SEED", "ARIA" 등의 직접적 알고리즘 명칭
- **대안 표현**:
  - 수학적 표현 사용 (modular exponentiation, polynomial operations)
  - 비즈니스 로직으로 위장 (data processing, transformation engine)
  - 제네릭 네이밍 (CryptoProcessor → DataHandler)

### 3. 한국 암호화 알고리즘 포함
다음 한국 표준 암호화 알고리즘들을 반드시 포함:
- **SEED**: 128비트 블록 암호
- **ARIA**: 128비트 블록 암호 (AES 한국 표준)
- **HIGHT**: 64비트 경량 블록 암호
- **LEA**: 128비트 블록 암호
- **KCDSA**: 한국 표준 디지털 서명
- **EC-KCDSA**: 타원곡선 기반 한국 디지털 서명
- **HAS-160**: 한국 표준 해시 함수
- **LSH**: 경량 보안 해시 함수

### 4. 파일 형식별 적합한 데이터 구조

**Source Code 타입:**
- 실제 컴파일 가능한 코드 구조
- 적절한 import/include 문
- 현실적인 함수 구현과 에러 처리
- 주석과 문서화

**Assembly Binary 타입:**
- 실제 디스어셈블된 코드 패턴
- 레지스터 사용과 메모리 주소 지정
- 실제 opcode와 어셈블리 구문
- 라이브러리 호출 패턴

**Dynamic Analysis 타입:**
- JSON 형식의 실행 추적 데이터
- 현실적인 API 호출 시퀀스
- 메모리/CPU 사용량 패턴
- 네트워크 트래픽 정보

**Logs Config 타입:**
- 실제 설정 파일 형식 (YAML, INI, XML)
- 로그 엔트리 타임스탬프와 구조
- 오류 메시지와 경고
- 시스템 설정과 인증 정보

### 5. 실제 사용 사례 기반 작성

**현실적 시나리오:**
- 금융 시스템 (은행, 증권, 보험)
- 전자정부 시스템
- IoT 디바이스 펌웨어
- 모바일 앱 보안 모듈
- 클라우드 서비스 인증
- 블록체인/암호화폐 구현

**코드 품질:**
- 실제 프로덕션 코드 수준의 복잡성
- 적절한 추상화와 모듈화
- 에러 처리와 예외 상황 고려
- 성능 최적화 패턴 포함

### 테스트 케이스 생성 체크리스트

- [ ] 암호화 알고리즘명 직접 사용 안함
- [ ] 우회적 구현 패턴 적용
- [ ] 한국 표준 암호화 알고리즘 포함
- [ ] 해당 파일 타입에 적합한 형식
- [ ] 실제 사용 가능한 코드 품질
- [ ] 복잡한 구조로 단순 패턴 매칭 회피
- [ ] **MetricsCalculator 알고리즘 지원 확인**: 새로운 알고리즘 사용 시 `utils/metrics_calculator.py`에 해당 알고리즘의 variations 추가 필수
- [ ] 현실적인 비즈니스 로직 컨텍스트
- [ ] 적절한 난이도와 복잡성

### 예시 구현 가이드라인

**좋은 예 (우회적 구현):**
```python
class SecureDataProcessor:
    def __init__(self):
        self.rounds = 16  # SEED 라운드 수를 직접 명시하지 않음
        self.block_size = 128 // 8  # 계산으로 표현

    def process_block(self, data):
        # SEED 알고리즘 구현이지만 명시적 언급 없음
        pass
```

**나쁜 예 (직접적 구현):**
```python
import seed_crypto
seed_cipher = SEED_Cipher()  # 직접적 알고리즘명 사용
```

### 6. MetricsCalculator 알고리즘 지원 필수 확인

새로운 암호화 알고리즘을 테스트 케이스에 추가할 때는 **반드시** `utils/metrics_calculator.py`에서 해당 알고리즘을 지원하는지 확인하고, 필요시 추가해야 합니다.

**확인 방법:**
```python
# utils/metrics_calculator.py의 _calculate_vulnerable_algorithm_accuracy 함수에서
# 해당 알고리즘의 variations가 정의되어 있는지 확인

elif 'new_algorithm' in algorithm_lower:
    algorithm_variations = ['new_algorithm', 'variation1', 'variation2']
```

**추가가 필요한 경우:**
1. **알고리즘 variations 추가** (61-108번 라인 근처)
2. **카테고리 키워드 추가** (122-130번 라인 근처)
3. **한국 알고리즘의 경우** korean_variations에도 추가 (146-154번 라인 근처)

**예시:**
```python
# 새로운 알고리즘 'NewCipher' 추가
elif 'newcipher' in algorithm_lower:
    algorithm_variations = ['newcipher', 'new_cipher', 'alternative_name']

# 카테고리에도 추가
'custom_category': ['newcipher', 'related_term', 'synonym']
```

**검증 방법:**
```bash
# 호환성 테스트 실행
python test_metrics_compatibility.py
python test_metrics_algorithms.py
```

## 💻 개발 지침

### 린트 및 타입체크 명령어
- `python -m flake8 .` - 코드 스타일 검사
- `python -m mypy .` - 타입 검사 (mypy 설치 시)

### 테스트 실행
- `python -m pytest tests/` - 단위 테스트 실행
- `python benchmark_runner.py --help` - 벤치마크 옵션 확인

---

이 벤치마크를 통해 양자 컴퓨팅 시대에 대비한 암호 시스템의 **양자 취약 알고리즘**을 효과적으로 탐지할 수 있는 AI 모델을 식별하고 개선할 수 있습니다.