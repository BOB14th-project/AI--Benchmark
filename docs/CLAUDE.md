# AI Benchmark - 양자 취약 암호 알고리즘 탐지 벤치마크

이 시스템은 다양한 LLM 모델들의 양자 취약 암호 알고리즘 탐지 성능을 평가하는 벤치마크 도구입니다.

## 🎯 목표

포스트 양자 암호(Post-Quantum Cryptography) 전환을 위한 기존 시스템의 취약점 식별 능력을 LLM 모델별로 비교 평가합니다.

## 🧪 테스트 모델

### 상용 API 모델
1. **Google Gemini**: `gemini-2.0-flash-exp`
2. **OpenAI GPT**: `gpt-4.1`
3. **xAI Grok**: `grok-3-mini`

### 로컬 Ollama 모델
1. **LLaMA 3**: `llama3:8b`
2. **Gemma 3**: `gemma3:12b`
3. **Code Llama**: `codellama:7b`

## 📊 평가 대상 에이전트

### 1. Source Code Agent (`source_code`)
- **목적**: 소스 코드에서 양자 취약 암호 알고리즘 탐지
- **파일 위치**: `data/test_files/source_code/`
- **지원 언어**: Python, Java, C/C++, JavaScript
- **탐지 대상**: RSA, ECC, DH, DSA, 한국 알고리즘(SEED, ARIA, HIGHT, LEA, KCDSA)

### 2. Assembly Binary Agent (`assembly_binary`)
- **목적**: 어셈블리/바이너리 코드에서 암호 연산 탐지
- **파일 위치**: `data/test_files/assembly_binary/`
- **지원 형식**: 어셈블리, 바이너리 덤프, 디스어셈블리
- **탐지 대상**: 큰 정수 연산, 타원곡선 연산, 모듈러 지수

### 3. Dynamic Analysis Agent (`dynamic_analysis`)
- **목적**: 런타임 동작에서 암호 API 사용 탐지
- **파일 위치**: `data/test_files/dynamic_analysis/`
- **지원 형식**: JSON, 로그, 트레이스 파일
- **탐지 대상**: API 호출, 메모리 패턴, 성능 특성

### 4. Logs Config Agent (`logs_config`)
- **목적**: 설정 파일과 로그에서 암호 설정 탐지
- **파일 위치**: `data/test_files/logs_config/`
- **지원 형식**: 설정 파일, 시스템 로그, 애플리케이션 로그
- **탐지 대상**: SSL/TLS 설정, 인증서 구성, 암호 라이브러리 설정

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
    model: "gemini-2.0-flash-exp"
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
      - "gemma3:12b"
      - "codellama:7b"
```

### Ollama 설정

로컬 Ollama 서버가 실행 중이어야 합니다:

```bash
# Ollama 설치 (macOS)
brew install ollama

# 모델 다운로드
ollama pull llama3:8b
ollama pull gemma3:12b
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
python test_model.py --provider google --model gemini-2.0-flash-exp

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
python test_agent.py --agent assembly_binary --model gemini-2.0-flash-exp
```

### 4. 단일 파일 테스트

```bash
# 특정 파일만 테스트
python test_single_file.py --file data/test_files/source_code/rsa_public_key_system.java --model gemini-2.0-flash-exp
```

## 📈 평가 지표

### 1. 탐지 정확도 (Detection Accuracy)
- **정의**: 실제 취약점 대비 정확히 탐지된 비율
- **계산**: (정확히 탐지된 취약점 수) / (전체 취약점 수)

### 2. 정밀도 (Precision)
- **정의**: 탐지된 것 중 실제 취약점인 비율
- **계산**: (참 양성) / (참 양성 + 거짓 양성)

### 3. 재현율 (Recall)
- **정의**: 실제 취약점 중 탐지된 비율
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

### 1. 모델별 성능 비교

```python
# 결과 분석 스크립트 실행
python analyze_results.py --compare-models

# 출력 예시:
# Model Performance Comparison
# ============================
# 1. gemini-2.0-flash-exp    F1: 0.89  Time: 12.3s  Tokens: 1,850
# 2. gpt-4.1                 F1: 0.87  Time: 8.7s   Tokens: 2,100
# 3. llama3:8b               F1: 0.82  Time: 3.2s   Tokens: 1,200
```

### 2. 에이전트별 성능

```python
# 에이전트별 분석
python analyze_results.py --compare-agents

# 출력 예시:
# Agent Performance Analysis
# ==========================
# Source Code:      Easy to detect, high accuracy
# Assembly Binary:  Medium difficulty, variable performance
# Dynamic Analysis: Complex patterns, lower accuracy
# Logs Config:      High false positive rate
```

### 3. 취약점 유형별 분석

```python
# 취약점 유형별 분석
python analyze_results.py --vulnerability-analysis

# 출력 예시:
# Vulnerability Detection Rates
# =============================
# RSA:              95% detection rate
# ECC:              88% detection rate
# Korean Algorithms: 76% detection rate
# Hash Functions:    82% detection rate
```

## 📁 프로젝트 구조

```
AI--Benchmark/
├── agents/                     # 분석 에이전트들
│   ├── base_agent.py          # 기본 에이전트 클래스
│   ├── source_code_agent.py   # 소스 코드 분석
│   ├── assembly_agent.py      # 어셈블리 분석
│   ├── dynamic_analysis_agent.py # 동적 분석
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
│   │   ├── dynamic_analysis/ # 동적 분석 데이터
│   │   └── logs_config/      # 로그/설정 파일
│   └── ground_truth/         # 정답 데이터
├── utils/                     # 유틸리티들
│   ├── test_case_manager.py  # 테스트 케이스 관리
│   ├── result_analyzer.py    # 결과 분석
│   └── benchmark_runner.py   # 벤치마크 실행기
├── results/                   # 테스트 결과들
├── test_*.py                 # 개별 테스트 스크립트들
├── run_benchmark.py          # 메인 벤치마크 실행기
├── analyze_results.py        # 결과 분석 도구
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
| gemini-2.0-flash-exp | 0.85-0.90 | 10-15초 | 높음 | 높은 정확도, 상세한 분석 |
| gpt-4.1 | 0.80-0.85 | 8-12초 | 중간 | 균형잡힌 성능 |
| grok-3-mini | 0.75-0.80 | 5-8초 | 높음 | 빠른 응답, 경량화 |
| llama3:8b | 0.70-0.75 | 3-5초 | 매우높음 | 로컬 실행, 빠름 |
| gemma3:12b | 0.65-0.70 | 4-6초 | 높음 | 코드 이해 특화 |
| codellama:7b | 0.60-0.65 | 2-4초 | 매우높음 | 코드 특화, 빠름 |

### 에이전트별 예상 난이도

1. **Source Code** (쉬움): 명시적 알고리즘 사용, 높은 탐지율
2. **Assembly Binary** (어려움): 컴파일된 코드, 패턴 인식 필요
3. **Dynamic Analysis** (중간): API 호출 패턴, 성능 특성 분석
4. **Logs Config** (중간): 설정 이해, 간접적 증거 수집

## 🎯 기대 효과

1. **모델 선택 가이드**: 용도별 최적 모델 추천
2. **성능 벤치마크**: 객관적 성능 비교 데이터
3. **취약점 탐지 도구**: 실무에서 활용 가능한 도구
4. **연구 기여**: 암호 분석 AI 연구 발전

## 🔄 업데이트 계획

- [ ] 추가 모델 지원 (Claude, LLaMA 등)
- [ ] 더 많은 테스트 케이스 추가
- [ ] 실시간 대시보드 개발
- [ ] 자동화된 CI/CD 파이프라인
- [ ] 웹 인터페이스 개발

---

이 벤치마크를 통해 양자 컴퓨팅 시대에 대비한 암호 시스템의 취약점을 효과적으로 탐지할 수 있는 AI 모델을 식별하고 개선할 수 있습니다.